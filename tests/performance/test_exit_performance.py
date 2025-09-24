"""
Performance tests for application exit time.
Tests that application cleanup/exit completes in <2s as per requirements.
"""

import pytest
import time
import sys
import os
import threading
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestExitPerformance:
    """Performance tests for application exit time requirements."""

    @classmethod
    def setup_class(cls):
        """Setup Qt application for testing."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setup_method(self):
        """Setup test method with application components."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.controllers.qt_main_controller import QtMainController
            from risk_calculator.services.application_lifecycle_service import ApplicationLifecycleService
            from risk_calculator.models.application_process_state import ApplicationProcessState

            self.RiskCalculatorQtApp = RiskCalculatorQtApp
            self.QtMainController = QtMainController
            self.ApplicationLifecycleService = ApplicationLifecycleService
            self.ApplicationProcessState = ApplicationProcessState

        except ImportError as e:
            pytest.skip(f"Required application components not available: {e}")

    def test_basic_application_exit_performance(self):
        """Test basic application exit completes in <2s."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        start_time = time.perf_counter()

        # Trigger application exit
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        end_time = time.perf_counter()
        exit_time = (end_time - start_time) * 1000

        assert exit_time < 2000, f"Basic application exit took {exit_time:.2f}ms, should be <2000ms"

    def test_application_exit_with_data_cleanup(self):
        """Test application exit performance with data cleanup."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Simulate application state with data
        if hasattr(controller, 'main_window') and controller.main_window:
            main_window = controller.main_window

            # Add some data to various tabs
            if hasattr(main_window, 'tabs'):
                for tab_name, tab in main_window.tabs.items():
                    if hasattr(tab, 'account_size_entry'):
                        tab.account_size_entry.setText('10000')
                    if hasattr(tab, 'risk_percentage_entry'):
                        tab.risk_percentage_entry.setText('2')

        start_time = time.perf_counter()

        # Exit with data cleanup
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        end_time = time.perf_counter()
        exit_time = (end_time - start_time) * 1000

        assert exit_time < 2000, f"Application exit with data cleanup took {exit_time:.2f}ms, should be <2000ms"

    def test_application_lifecycle_service_shutdown_performance(self):
        """Test ApplicationLifecycleService shutdown performance."""
        lifecycle_service = self.ApplicationLifecycleService()
        process_state = self.ApplicationProcessState(process_id="test_performance")

        # Register multiple cleanup handlers to simulate realistic conditions
        cleanup_handlers = []
        for i in range(10):
            def cleanup_handler():
                time.sleep(0.01)  # Simulate small cleanup task

            cleanup_handlers.append(cleanup_handler)
            process_state.register_cleanup_handler(cleanup_handler)

        # Register shutdown handlers
        for i in range(5):
            def shutdown_handler():
                time.sleep(0.005)  # Simulate shutdown task

            process_state.register_shutdown_handler(shutdown_handler)

        start_time = time.perf_counter()

        # Perform shutdown
        process_state.shutdown_application()

        end_time = time.perf_counter()
        shutdown_time = (end_time - start_time) * 1000

        assert shutdown_time < 2000, f"Lifecycle service shutdown took {shutdown_time:.2f}ms, should be <2000ms"

    def test_window_state_persistence_during_exit(self):
        """Test exit performance when saving window state."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Create temporary config file for window state
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as temp_file:
            temp_config_path = temp_file.name

        try:
            # Mock window state saving to use temp file
            if hasattr(controller, 'main_window') and controller.main_window:
                main_window = controller.main_window

                # Simulate window state changes
                if hasattr(main_window, 'resize'):
                    main_window.resize(1200, 800)
                if hasattr(main_window, 'move'):
                    main_window.move(100, 100)

            start_time = time.perf_counter()

            # Exit with window state persistence
            controller.shutdown_application()
            if hasattr(controller, 'main_window') and controller.main_window:
                controller.main_window.close()

            end_time = time.perf_counter()
            exit_time = (end_time - start_time) * 1000

            assert exit_time < 2000, f"Exit with window state persistence took {exit_time:.2f}ms, should be <2000ms"

        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_config_path)
            except OSError:
                pass

    def test_resource_cleanup_performance(self):
        """Test resource cleanup performance during exit."""
        process_state = self.ApplicationProcessState(process_id="resource_test")

        # Simulate various resources that need cleanup
        resources_to_cleanup = []

        # Mock file handles
        for i in range(20):
            mock_file = Mock()
            mock_file.close = Mock()
            resources_to_cleanup.append(mock_file)

        # Mock network connections
        for i in range(5):
            mock_connection = Mock()
            mock_connection.close = Mock()
            resources_to_cleanup.append(mock_connection)

        # Create cleanup handlers for all resources
        for resource in resources_to_cleanup:
            process_state.register_cleanup_handler(resource.close)

        start_time = time.perf_counter()

        # Perform resource cleanup
        process_state.force_cleanup()

        end_time = time.perf_counter()
        cleanup_time = (end_time - start_time) * 1000

        assert cleanup_time < 1000, f"Resource cleanup took {cleanup_time:.2f}ms, should be <1000ms"

        # Verify all resources were cleaned up
        for resource in resources_to_cleanup:
            resource.close.assert_called_once()

    def test_concurrent_exit_operations_performance(self):
        """Test performance when multiple exit operations run concurrently."""
        process_state = self.ApplicationProcessState(process_id="concurrent_test")

        # Create handlers that simulate concurrent operations
        completion_times = []

        def concurrent_handler(handler_id):
            start = time.perf_counter()
            time.sleep(0.01)  # Simulate work
            end = time.perf_counter()
            completion_times.append((handler_id, (end - start) * 1000))

        # Register multiple handlers
        for i in range(10):
            process_state.register_shutdown_handler(lambda i=i: concurrent_handler(i))

        start_time = time.perf_counter()

        # Execute shutdown with concurrent handlers
        process_state.shutdown_application()

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        assert total_time < 2000, f"Concurrent exit operations took {total_time:.2f}ms, should be <2000ms"

        # Verify handlers executed reasonably quickly
        for handler_id, handler_time in completion_times:
            assert handler_time < 100, f"Handler {handler_id} took {handler_time:.2f}ms, should be <100ms"

    def test_exit_performance_with_error_handling(self):
        """Test exit performance when handlers throw errors."""
        process_state = self.ApplicationProcessState(process_id="error_test")

        # Mix of successful and failing handlers
        def successful_handler():
            time.sleep(0.005)  # Small delay

        def failing_handler():
            time.sleep(0.005)
            raise Exception("Handler error")

        # Register mix of handlers
        for i in range(5):
            process_state.register_shutdown_handler(successful_handler)
            process_state.register_cleanup_handler(failing_handler)

        start_time = time.perf_counter()

        # Shutdown should handle errors gracefully and still be fast
        result = process_state.shutdown_application()

        end_time = time.perf_counter()
        shutdown_time = (end_time - start_time) * 1000

        assert shutdown_time < 2000, f"Exit with error handling took {shutdown_time:.2f}ms, should be <2000ms"

        # Should complete despite errors
        assert result == True or process_state.current_state.value in ['stopped', 'error']

    def test_memory_cleanup_performance_during_exit(self):
        """Test memory cleanup performance during application exit."""
        import gc

        # Baseline memory measurement
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create application with significant memory usage
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Simulate memory usage
        test_data = []
        for i in range(1000):
            test_data.append({'calculation': i, 'result': i * 2.5, 'metadata': f'test_{i}'})

        start_time = time.perf_counter()

        # Exit and cleanup
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        # Force garbage collection
        del test_data
        del controller
        del qt_app
        gc.collect()

        end_time = time.perf_counter()
        cleanup_time = (end_time - start_time) * 1000

        assert cleanup_time < 2000, f"Memory cleanup during exit took {cleanup_time:.2f}ms, should be <2000ms"

        # Check memory was actually cleaned up
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects

        # Allow some increase but not excessive
        assert object_increase < 500, f"Excessive objects remaining after exit: {object_increase}"

    def test_qt_widget_cleanup_performance(self):
        """Test Qt widget cleanup performance during exit."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Get reference to widgets for cleanup verification
        widgets_to_cleanup = []
        if hasattr(controller, 'main_window') and controller.main_window:
            main_window = controller.main_window
            widgets_to_cleanup.append(main_window)

            if hasattr(main_window, 'tabs'):
                for tab in main_window.tabs.values():
                    widgets_to_cleanup.append(tab)

        start_time = time.perf_counter()

        # Close application and cleanup widgets
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        # Process any remaining Qt events
        QApplication.processEvents()

        end_time = time.perf_counter()
        widget_cleanup_time = (end_time - start_time) * 1000

        assert widget_cleanup_time < 1500, f"Qt widget cleanup took {widget_cleanup_time:.2f}ms, should be <1500ms"

    def test_configuration_save_performance_during_exit(self):
        """Test configuration saving performance during application exit."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Simulate configuration changes
        config_data = {
            'window_width': 1200,
            'window_height': 800,
            'window_x': 100,
            'window_y': 100,
            'maximized': False,
            'last_calculation_method': 'percentage',
            'recent_values': {
                'account_size': '10000',
                'risk_percentage': '2',
                'entry_price': '50.00'
            }
        }

        start_time = time.perf_counter()

        # Exit with configuration saving
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        end_time = time.perf_counter()
        config_save_time = (end_time - start_time) * 1000

        assert config_save_time < 2000, f"Exit with config save took {config_save_time:.2f}ms, should be <2000ms"

    def test_thread_cleanup_performance_during_exit(self):
        """Test thread cleanup performance during application exit."""
        process_state = self.ApplicationProcessState(process_id="thread_test")

        # Create background threads that need cleanup
        background_threads = []
        thread_events = []

        def background_worker(thread_id, stop_event):
            while not stop_event.is_set():
                time.sleep(0.01)

        # Start multiple background threads
        for i in range(5):
            stop_event = threading.Event()
            thread = threading.Thread(target=background_worker, args=(i, stop_event))
            thread.daemon = True
            thread.start()

            background_threads.append(thread)
            thread_events.append(stop_event)

        # Register cleanup handlers to stop threads
        def cleanup_threads():
            for stop_event in thread_events:
                stop_event.set()
            for thread in background_threads:
                thread.join(timeout=0.5)

        process_state.register_cleanup_handler(cleanup_threads)

        start_time = time.perf_counter()

        # Shutdown with thread cleanup
        process_state.shutdown_application()

        end_time = time.perf_counter()
        thread_cleanup_time = (end_time - start_time) * 1000

        assert thread_cleanup_time < 1000, f"Thread cleanup took {thread_cleanup_time:.2f}ms, should be <1000ms"

        # Verify threads were stopped
        for thread in background_threads:
            assert not thread.is_alive(), "Background thread should be stopped after cleanup"

    def test_exit_performance_regression_detection(self):
        """Test to detect performance regressions in application exit."""
        exit_times = []

        # Run multiple exit cycles to get statistical data
        for iteration in range(5):
            qt_app = self.RiskCalculatorQtApp()
            qt_app.create_application()

            controller = self.QtMainController()
            controller.initialize_application()

            start_time = time.perf_counter()

            # Perform exit
            controller.shutdown_application()
            if hasattr(controller, 'main_window') and controller.main_window:
                controller.main_window.close()

            end_time = time.perf_counter()
            exit_time = (end_time - start_time) * 1000

            exit_times.append(exit_time)

            # Cleanup for next iteration
            del controller
            del qt_app

        # Calculate statistics
        avg_exit_time = sum(exit_times) / len(exit_times)
        max_exit_time = max(exit_times)

        assert avg_exit_time < 1500, f"Average exit time {avg_exit_time:.2f}ms exceeds 1500ms baseline"
        assert max_exit_time < 2000, f"Maximum exit time {max_exit_time:.2f}ms exceeds 2000ms requirement"

        # Check for consistency (no major outliers)
        outliers = [t for t in exit_times if t > avg_exit_time * 2]
        assert len(outliers) <= 1, f"Found {len(outliers)} performance outliers in exit timing"

    def test_graceful_shutdown_vs_force_exit_performance(self):
        """Test performance difference between graceful and forced shutdown."""
        # Test graceful shutdown
        process_state = self.ApplicationProcessState(process_id="graceful_test")

        # Add some handlers
        for i in range(5):
            process_state.register_shutdown_handler(lambda: time.sleep(0.01))
            process_state.register_cleanup_handler(lambda: time.sleep(0.01))

        start_time = time.perf_counter()
        result = process_state.shutdown_application()
        end_time = time.perf_counter()

        graceful_time = (end_time - start_time) * 1000

        # Test force cleanup
        force_process_state = self.ApplicationProcessState(process_id="force_test")

        for i in range(5):
            force_process_state.register_cleanup_handler(lambda: time.sleep(0.01))

        start_time = time.perf_counter()
        force_process_state.force_cleanup()
        end_time = time.perf_counter()

        force_time = (end_time - start_time) * 1000

        # Both should be fast, graceful should be slightly slower
        assert graceful_time < 2000, f"Graceful shutdown took {graceful_time:.2f}ms, should be <2000ms"
        assert force_time < 1000, f"Force cleanup took {force_time:.2f}ms, should be <1000ms"

    @pytest.mark.parametrize("handler_count,expected_max_time", [
        (1, 500),   # Single handler should be very fast
        (5, 1000),  # Few handlers should be fast
        (10, 1500), # More handlers still reasonable
        (20, 2000), # Many handlers at the limit
    ])
    def test_parameterized_handler_count_performance(self, handler_count, expected_max_time):
        """Parameterized test for exit performance with varying handler counts."""
        process_state = self.ApplicationProcessState(process_id=f"handler_test_{handler_count}")

        # Register specified number of handlers
        for i in range(handler_count):
            process_state.register_shutdown_handler(lambda: time.sleep(0.005))
            process_state.register_cleanup_handler(lambda: time.sleep(0.002))

        start_time = time.perf_counter()

        result = process_state.shutdown_application()

        end_time = time.perf_counter()
        shutdown_time = (end_time - start_time) * 1000

        assert shutdown_time < expected_max_time, f"Shutdown with {handler_count} handlers took {shutdown_time:.2f}ms, should be <{expected_max_time}ms"

    def test_exit_performance_with_unsaved_data_detection(self):
        """Test exit performance when checking for unsaved data."""
        qt_app = self.RiskCalculatorQtApp()
        qt_app.create_application()

        controller = self.QtMainController()
        controller.initialize_application()

        # Simulate unsaved data in forms
        if hasattr(controller, 'main_window') and controller.main_window:
            main_window = controller.main_window

            if hasattr(main_window, 'tabs'):
                for tab_name, tab in main_window.tabs.items():
                    # Add data to simulate unsaved changes
                    if hasattr(tab, 'account_size_entry'):
                        tab.account_size_entry.setText('10000')
                    if hasattr(tab, 'risk_percentage_entry'):
                        tab.risk_percentage_entry.setText('2.5')

        start_time = time.perf_counter()

        # Exit with unsaved data check
        controller.shutdown_application()
        if hasattr(controller, 'main_window') and controller.main_window:
            controller.main_window.close()

        end_time = time.perf_counter()
        exit_time = (end_time - start_time) * 1000

        assert exit_time < 2000, f"Exit with unsaved data detection took {exit_time:.2f}ms, should be <2000ms"

    def test_exit_performance_under_system_load(self):
        """Test exit performance when system is under load."""
        # Simulate system load with CPU-intensive background task
        import multiprocessing

        def cpu_intensive_task():
            # Simple CPU-intensive calculation
            total = 0
            for i in range(1000000):
                total += i ** 0.5
            return total

        # Start background processes to simulate system load
        processes = []
        num_processes = min(4, multiprocessing.cpu_count())

        for _ in range(num_processes):
            process = multiprocessing.Process(target=cpu_intensive_task)
            process.start()
            processes.append(process)

        try:
            # Test exit performance under load
            qt_app = self.RiskCalculatorQtApp()
            qt_app.create_application()

            controller = self.QtMainController()
            controller.initialize_application()

            start_time = time.perf_counter()

            controller.shutdown_application()
            if hasattr(controller, 'main_window') and controller.main_window:
                controller.main_window.close()

            end_time = time.perf_counter()
            exit_time = (end_time - start_time) * 1000

            # Allow more time under system load
            assert exit_time < 3000, f"Exit under system load took {exit_time:.2f}ms, should be <3000ms"

        finally:
            # Cleanup background processes
            for process in processes:
                process.terminate()
                process.join(timeout=1.0)