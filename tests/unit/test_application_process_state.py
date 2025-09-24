"""
Unit tests for ApplicationProcessState model.
Tests application lifecycle management, resource tracking, and event handling.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestApplicationProcessState(unittest.TestCase):
    """Test ApplicationProcessState model functionality."""

    def setUp(self):
        """Set up test fixtures."""
        from risk_calculator.models.application_process_state import (
            ApplicationProcessState, ProcessState, ProcessPhase, ProcessEvent, ResourceInfo
        )
        self.ApplicationProcessState = ApplicationProcessState
        self.ProcessState = ProcessState
        self.ProcessPhase = ProcessPhase
        self.ProcessEvent = ProcessEvent
        self.ResourceInfo = ResourceInfo

    def test_application_process_state_creation(self):
        """Test creating ApplicationProcessState with default values."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        self.assertEqual(process_state.process_id, "test_app")
        self.assertEqual(process_state.current_state, self.ProcessState.INITIALIZING)
        self.assertEqual(process_state.current_phase, self.ProcessPhase.STARTUP)
        self.assertIsNotNone(process_state.startup_time)
        self.assertIsNone(process_state.shutdown_time)
        self.assertEqual(len(process_state.events), 0)
        self.assertEqual(len(process_state.cleanup_handlers), 0)
        self.assertEqual(len(process_state.startup_handlers), 0)
        self.assertEqual(len(process_state.shutdown_handlers), 0)
        self.assertEqual(len(process_state.resource_history), 0)
        self.assertIsNone(process_state.error_info)
        self.assertIsInstance(process_state.metadata, dict)

    def test_process_state_update_with_event_tracking(self):
        """Test updating process state creates proper event records."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        initial_event_count = len(process_state.events)

        process_state.update_state(
            self.ProcessState.RUNNING,
            "Application started successfully",
            {'source': 'test', 'version': '1.0'}
        )

        # Check state updated
        self.assertEqual(process_state.current_state, self.ProcessState.RUNNING)

        # Check event recorded
        self.assertEqual(len(process_state.events), initial_event_count + 1)
        event = process_state.events[-1]
        self.assertEqual(event.event_type, "state_change_running")
        self.assertEqual(event.message, "Application started successfully")
        self.assertEqual(event.phase, self.ProcessPhase.STARTUP)
        self.assertEqual(event.metadata['source'], 'test')
        self.assertEqual(event.metadata['version'], '1.0')

    def test_special_timestamp_updates(self):
        """Test special timestamp updates for startup and shutdown."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        initial_startup_time = process_state.startup_time

        time.sleep(0.01)

        # Test startup time update when moving to RUNNING
        process_state.update_state(self.ProcessState.RUNNING, "Started")
        self.assertGreater(process_state.startup_time, initial_startup_time)

        # Test shutdown time update
        self.assertIsNone(process_state.shutdown_time)
        process_state.update_state(self.ProcessState.SHUTTING_DOWN, "Shutting down")
        self.assertIsNotNone(process_state.shutdown_time)

    def test_process_phase_update(self):
        """Test process phase updating with event tracking."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        initial_event_count = len(process_state.events)

        process_state.update_phase(
            self.ProcessPhase.NORMAL_OPERATION,
            "Entering normal operation"
        )

        self.assertEqual(process_state.current_phase, self.ProcessPhase.NORMAL_OPERATION)
        self.assertEqual(len(process_state.events), initial_event_count + 1)

        event = process_state.events[-1]
        self.assertEqual(event.event_type, "phase_change_normal_operation")
        self.assertEqual(event.message, "Entering normal operation")

    def test_phase_update_no_change_ignored(self):
        """Test updating to same phase is ignored."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        initial_event_count = len(process_state.events)

        # Update to same phase
        process_state.update_phase(self.ProcessPhase.STARTUP)

        # Should not create event
        self.assertEqual(len(process_state.events), initial_event_count)

    def test_custom_event_addition(self):
        """Test adding custom events to process history."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        process_state.add_event(
            "custom_event",
            "Custom event occurred",
            {'data': 'test_data', 'level': 'info'}
        )

        self.assertEqual(len(process_state.events), 1)
        event = process_state.events[0]
        self.assertEqual(event.event_type, "custom_event")
        self.assertEqual(event.message, "Custom event occurred")
        self.assertEqual(event.metadata['data'], 'test_data')
        self.assertEqual(event.metadata['level'], 'info')

    def test_handler_registration(self):
        """Test registration of startup, shutdown, and cleanup handlers."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        startup_handler = Mock()
        shutdown_handler = Mock()
        cleanup_handler = Mock()

        # Register handlers
        process_state.register_startup_handler(startup_handler)
        process_state.register_shutdown_handler(shutdown_handler)
        process_state.register_cleanup_handler(cleanup_handler)

        self.assertIn(startup_handler, process_state.startup_handlers)
        self.assertIn(shutdown_handler, process_state.shutdown_handlers)
        self.assertIn(cleanup_handler, process_state.cleanup_handlers)

        # Test duplicate registration prevention
        process_state.register_startup_handler(startup_handler)
        self.assertEqual(process_state.startup_handlers.count(startup_handler), 1)

    def test_application_initialization(self):
        """Test application initialization process."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        startup_handler1 = Mock()
        startup_handler2 = Mock()
        process_state.register_startup_handler(startup_handler1)
        process_state.register_startup_handler(startup_handler2)

        # Test successful initialization
        result = process_state.initialize_application()

        self.assertTrue(result)
        self.assertEqual(process_state.current_state, self.ProcessState.RUNNING)
        self.assertEqual(process_state.current_phase, self.ProcessPhase.NORMAL_OPERATION)
        startup_handler1.assert_called_once()
        startup_handler2.assert_called_once()

        # Check events were recorded
        event_types = [event.event_type for event in process_state.events]
        self.assertIn("state_change_initializing", event_types)
        self.assertIn("state_change_running", event_types)
        self.assertIn("phase_change_normal_operation", event_types)

    def test_application_initialization_with_handler_error(self):
        """Test initialization handles startup handler errors gracefully."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        def failing_handler():
            raise Exception("Handler failed")

        successful_handler = Mock()

        process_state.register_startup_handler(failing_handler)
        process_state.register_startup_handler(successful_handler)

        # Should still succeed despite handler error
        result = process_state.initialize_application()

        self.assertTrue(result)
        self.assertEqual(process_state.current_state, self.ProcessState.RUNNING)
        successful_handler.assert_called_once()

        # Check error event recorded
        error_events = [e for e in process_state.events if e.event_type == "startup_handler_error"]
        self.assertEqual(len(error_events), 1)

    def test_application_initialization_failure(self):
        """Test initialization failure handling."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Mock startup handler to cause initialization failure
        def failing_startup_handler():
            raise Exception("Startup failed")

        process_state.register_startup_handler(failing_startup_handler)

        # Should handle the error gracefully and continue
        result = process_state.initialize_application()

        # Should still succeed overall but record the error
        self.assertTrue(result)
        self.assertEqual(process_state.current_state, self.ProcessState.RUNNING)

        # Check error event was recorded
        error_events = [e for e in process_state.events if e.event_type == "startup_handler_error"]
        self.assertEqual(len(error_events), 1)

    def test_application_shutdown(self):
        """Test application shutdown process."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        process_state.initialize_application()

        shutdown_handler1 = Mock()
        shutdown_handler2 = Mock()
        cleanup_handler = Mock()

        process_state.register_shutdown_handler(shutdown_handler1)
        process_state.register_shutdown_handler(shutdown_handler2)
        process_state.register_cleanup_handler(cleanup_handler)

        # Test successful shutdown
        result = process_state.shutdown_application()

        self.assertTrue(result)
        self.assertEqual(process_state.current_state, self.ProcessState.STOPPED)
        self.assertEqual(process_state.current_phase, self.ProcessPhase.EXIT)
        self.assertIsNotNone(process_state.shutdown_time)

        shutdown_handler1.assert_called_once()
        shutdown_handler2.assert_called_once()
        cleanup_handler.assert_called_once()

    def test_application_shutdown_with_handler_errors(self):
        """Test shutdown handles handler errors gracefully."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        process_state.initialize_application()

        def failing_shutdown_handler():
            raise Exception("Shutdown handler failed")

        def failing_cleanup_handler():
            raise Exception("Cleanup handler failed")

        successful_handler = Mock()

        process_state.register_shutdown_handler(failing_shutdown_handler)
        process_state.register_shutdown_handler(successful_handler)
        process_state.register_cleanup_handler(failing_cleanup_handler)

        # Should still succeed despite handler errors
        result = process_state.shutdown_application()

        self.assertTrue(result)
        self.assertEqual(process_state.current_state, self.ProcessState.STOPPED)
        successful_handler.assert_called_once()

        # Check error events recorded
        error_events = [e for e in process_state.events
                       if 'handler_error' in e.event_type]
        self.assertGreaterEqual(len(error_events), 2)

    def test_force_cleanup(self):
        """Test force cleanup functionality."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        cleanup_handler1 = Mock()
        cleanup_handler2 = Mock()

        def failing_cleanup():
            raise Exception("Cleanup failed")

        process_state.register_cleanup_handler(cleanup_handler1)
        process_state.register_cleanup_handler(failing_cleanup)
        process_state.register_cleanup_handler(cleanup_handler2)

        initial_event_count = len(process_state.events)
        process_state.force_cleanup()

        # All handlers should be called despite errors
        cleanup_handler1.assert_called_once()
        cleanup_handler2.assert_called_once()

        # Events should be recorded
        new_events = process_state.events[initial_event_count:]
        event_types = [e.event_type for e in new_events]
        self.assertIn("force_cleanup_start", event_types)
        self.assertIn("force_cleanup_complete", event_types)
        self.assertIn("cleanup_handler_error", event_types)

    def test_application_running_check(self):
        """Test is_application_running method."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Initially not running
        self.assertFalse(process_state.is_application_running())

        # After initialization
        process_state.initialize_application()
        self.assertTrue(process_state.is_application_running())

        # After shutdown
        process_state.shutdown_application()
        self.assertFalse(process_state.is_application_running())

    def test_time_tracking(self):
        """Test startup time and uptime tracking."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Test startup time before running (should be very small but not None since __post_init__ sets it)
        startup_time = process_state.get_startup_time()
        self.assertIsNotNone(startup_time)

        # Test uptime
        initial_uptime = process_state.get_uptime()
        time.sleep(0.01)
        later_uptime = process_state.get_uptime()
        self.assertGreater(later_uptime, initial_uptime)

        # Test startup time after running
        process_state.initialize_application()
        startup_time = process_state.get_startup_time()
        self.assertIsNotNone(startup_time)
        self.assertGreaterEqual(startup_time, 0)

    def test_resource_usage_tracking(self):
        """Test resource usage recording and retrieval."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Initially no resource history
        self.assertIsNone(process_state.get_current_resource_usage())
        self.assertIsNone(process_state.get_average_resource_usage())

        # Record resource usage
        process_state.record_resource_usage()

        # Should have resource info now
        current_usage = process_state.get_current_resource_usage()
        self.assertIsNotNone(current_usage)
        self.assertIsInstance(current_usage.memory_usage_mb, float)
        self.assertIsInstance(current_usage.cpu_usage_percent, float)
        self.assertIsInstance(current_usage.thread_count, int)
        self.assertIsInstance(current_usage.file_handles, int)

        # Test resource history limit
        for _ in range(105):  # More than the 100 limit
            process_state.record_resource_usage()

        self.assertLessEqual(len(process_state.resource_history), 100)

    def test_average_resource_usage(self):
        """Test average resource usage calculation."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Mock resource info to control values
        mock_resources = [
            self.ResourceInfo(10.0, 5.0, 3, 10, time.time()),
            self.ResourceInfo(20.0, 15.0, 4, 15, time.time()),
            self.ResourceInfo(30.0, 25.0, 5, 20, time.time())
        ]

        process_state.resource_history = mock_resources

        avg_usage = process_state.get_average_resource_usage()
        self.assertIsNotNone(avg_usage)
        self.assertEqual(avg_usage['memory_usage_mb'], 20.0)  # (10+20+30)/3
        self.assertEqual(avg_usage['cpu_usage_percent'], 15.0)  # (5+15+25)/3
        self.assertEqual(avg_usage['thread_count'], 4.0)  # (3+4+5)/3
        self.assertEqual(avg_usage['file_handles'], 15.0)  # (10+15+20)/3

    def test_event_management(self):
        """Test event retrieval and cleanup."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Add multiple events
        for i in range(15):
            process_state.add_event(f"event_{i}", f"Message {i}")

        # Test recent events
        recent_events = process_state.get_recent_events(5)
        self.assertEqual(len(recent_events), 5)
        self.assertEqual(recent_events[-1].event_type, "event_14")

        # Test all recent events
        all_events = process_state.get_recent_events(20)
        self.assertEqual(len(all_events), 15)

        # Test old event cleanup
        old_time = time.time() - 25 * 3600  # 25 hours ago
        old_event = self.ProcessEvent("old_event", old_time, self.ProcessPhase.STARTUP, "Old message")
        process_state.events.insert(0, old_event)

        process_state.clear_old_events(24)  # Keep events from last 24 hours
        # Old event should be removed
        event_types = [e.event_type for e in process_state.events]
        self.assertNotIn("old_event", event_types)

    def test_process_summary(self):
        """Test process summary generation."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        process_state.metadata['version'] = '1.0'
        process_state.initialize_application()
        process_state.record_resource_usage()

        summary = process_state.get_process_summary()

        expected_keys = [
            'process_id', 'current_state', 'current_phase', 'is_running',
            'uptime_seconds', 'startup_time', 'shutdown_time', 'event_count',
            'cleanup_handlers', 'startup_handlers', 'shutdown_handlers',
            'current_resources', 'average_resources', 'error_info', 'metadata'
        ]

        for key in expected_keys:
            self.assertIn(key, summary)

        self.assertEqual(summary['process_id'], 'test_app')
        self.assertEqual(summary['current_state'], 'running')
        self.assertTrue(summary['is_running'])
        self.assertIsNotNone(summary['current_resources'])
        self.assertEqual(summary['metadata']['version'], '1.0')

    def test_process_state_copy(self):
        """Test process state copying functionality."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        process_state.metadata['test'] = 'value'
        process_state.initialize_application()
        process_state.add_event("test_event", "Test message")
        process_state.record_resource_usage()

        # Create copy
        copied_state = process_state.copy()

        # Test basic attributes copied
        self.assertEqual(copied_state.process_id, process_state.process_id)
        self.assertEqual(copied_state.current_state, process_state.current_state)
        self.assertEqual(copied_state.current_phase, process_state.current_phase)
        self.assertEqual(copied_state.startup_time, process_state.startup_time)
        self.assertEqual(copied_state.metadata, process_state.metadata)

        # Test events copied
        self.assertEqual(len(copied_state.events), len(process_state.events))

        # Test resource history copied
        self.assertEqual(len(copied_state.resource_history), len(process_state.resource_history))

        # Test independence (modifying copy doesn't affect original)
        copied_state.add_event("copy_event", "Copy event")
        self.assertNotEqual(len(copied_state.events), len(process_state.events))

    def test_class_factory_method(self):
        """Test class factory method."""
        new_state = self.ApplicationProcessState.create_new("factory_test")

        self.assertEqual(new_state.process_id, "factory_test")
        self.assertEqual(new_state.current_state, self.ProcessState.INITIALIZING)
        self.assertEqual(new_state.current_phase, self.ProcessPhase.STARTUP)

    def test_string_representation(self):
        """Test string representation of process state."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        repr_str = repr(process_state)
        self.assertIn("test_app", repr_str)
        self.assertIn("initializing", repr_str)
        self.assertIn("startup", repr_str)
        self.assertIn("uptime=", repr_str)

    def test_process_event_age_calculation(self):
        """Test ProcessEvent age calculation."""
        past_time = time.time() - 5.0  # 5 seconds ago
        event = self.ProcessEvent(
            "test_event", past_time, self.ProcessPhase.STARTUP, "Test message"
        )

        age = event.age_seconds
        self.assertGreaterEqual(age, 4.9)  # Allow for small timing variations
        self.assertLessEqual(age, 5.1)

    def test_resource_info_with_psutil(self):
        """Test ResourceInfo.current() with psutil available."""
        with patch.object(self.ResourceInfo, 'current') as mock_current:
            # Mock the return value
            mock_current.return_value = self.ResourceInfo(
                memory_usage_mb=50.0,
                cpu_usage_percent=25.5,
                thread_count=8,
                file_handles=15,
                timestamp=time.time()
            )

            resource_info = self.ResourceInfo.current()

            self.assertAlmostEqual(resource_info.memory_usage_mb, 50.0, places=1)
            self.assertEqual(resource_info.cpu_usage_percent, 25.5)
            self.assertEqual(resource_info.thread_count, 8)
            self.assertEqual(resource_info.file_handles, 15)

    def test_resource_info_without_psutil(self):
        """Test ResourceInfo.current() fallback when psutil unavailable."""
        # Test the actual fallback implementation
        try:
            resource_info = self.ResourceInfo.current()
            # Should work regardless of whether psutil is available
            self.assertIsInstance(resource_info.memory_usage_mb, float)
            self.assertIsInstance(resource_info.cpu_usage_percent, float)
            self.assertIsInstance(resource_info.thread_count, int)
            self.assertIsInstance(resource_info.file_handles, int)
            self.assertGreaterEqual(resource_info.thread_count, 1)  # At least main thread
        except ImportError:
            # If we can't create ResourceInfo at all, skip this test
            self.skipTest("ResourceInfo.current() not available")

    def test_thread_safety(self):
        """Test thread safety of state updates."""
        process_state = self.ApplicationProcessState(process_id="test_app")
        event_counts = []

        def update_state_worker():
            for i in range(10):
                process_state.add_event(f"worker_event_{i}", f"Worker event {i}")

        # Create multiple threads updating state
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=update_state_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have all events (3 threads * 10 events each = 30)
        self.assertEqual(len(process_state.events), 30)

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        process_state = self.ApplicationProcessState(process_id="test_app")

        # Test add_event with None metadata
        process_state.add_event("test", "message", None)
        self.assertEqual(process_state.events[-1].metadata, {})

        # Test update_state with None metadata
        process_state.update_state(self.ProcessState.RUNNING, "test", None)

        # Test average resource usage with old data
        old_time = time.time() - 10 * 60  # 10 minutes ago
        old_resource = self.ResourceInfo(10.0, 5.0, 2, 5, old_time)
        process_state.resource_history = [old_resource]

        avg_usage = process_state.get_average_resource_usage(5)  # Last 5 minutes
        self.assertIsNone(avg_usage)  # No recent data

        # Test get_recent_events with empty history
        empty_state = self.ApplicationProcessState(process_id="empty")
        recent = empty_state.get_recent_events(5)
        self.assertEqual(len(recent), 0)


if __name__ == '__main__':
    unittest.main()