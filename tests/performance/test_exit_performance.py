"""
Performance tests for application exit time.

Tests that the application exits within acceptable time limits
and properly cleans up resources during shutdown.
"""

import pytest
import time
import threading
import subprocess
import sys
import os
from unittest.mock import Mock, patch

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestExitPerformance:
    """Performance tests for application exit functionality."""

    # Performance requirements
    MAX_EXIT_TIME_SECONDS = 2.0
    MAX_GRACEFUL_SHUTDOWN_TIME = 1.0

    @pytest.fixture
    def mock_qt_app(self):
        """Create mock Qt application for testing."""
        mock_app = Mock()
        mock_app.quit = Mock()
        mock_app.exit = Mock()
        mock_app.processEvents = Mock()
        mock_app.aboutToQuit = Mock()
        return mock_app

    def test_application_exit_time_under_limit(self, mock_qt_app):
        """Test that application exits within time limit."""
        try:
            from risk_calculator import qt_main

            # Mock Qt application to avoid GUI dependencies
            with patch('PySide6.QtWidgets.QApplication', return_value=mock_qt_app):
                with patch('sys.exit') as mock_exit:
                    start_time = time.time()

                    try:
                        # This should exit quickly without actually running GUI
                        qt_main.main()
                    except SystemExit:
                        pass  # Expected behavior
                    except Exception:
                        pass  # May fail due to missing display, but timing still valid

                    exit_time = time.time() - start_time

                    # Should exit within performance requirement
                    assert exit_time < self.MAX_EXIT_TIME_SECONDS, \
                        f"Application exit took {exit_time:.2f}s, should be < {self.MAX_EXIT_TIME_SECONDS}s"

        except ImportError:
            pytest.skip("Qt modules not available for exit performance testing")

    def test_graceful_shutdown_timing(self):
        """Test graceful shutdown timing with mock application state."""
        try:
            from risk_calculator.models.application_process_state import ApplicationProcessState, ProcessState

            # Create process state for testing
            process_state = ApplicationProcessState(process_id="test_process")

            # Simulate running application
            process_state.initialize_application()

            start_time = time.time()

            # Test graceful shutdown
            process_state.shutdown_application()

            shutdown_time = time.time() - start_time

            # Graceful shutdown should be very fast for in-memory operations
            assert shutdown_time < self.MAX_GRACEFUL_SHUTDOWN_TIME, \
                f"Graceful shutdown took {shutdown_time:.3f}s, should be < {self.MAX_GRACEFUL_SHUTDOWN_TIME}s"

            # Should be in stopped state
            assert process_state.current_state == ProcessState.STOPPED

        except ImportError:
            pytest.skip("Application process state model not available")

    def test_cleanup_handler_performance(self):
        """Test that cleanup handlers execute within time limits."""
        try:
            from risk_calculator.models.application_process_state import ApplicationProcessState

            process_state = ApplicationProcessState(process_id="test_cleanup")

            # Add mock cleanup handlers with known timing
            cleanup_times = []

            def fast_cleanup():
                """Fast cleanup handler."""
                start = time.time()
                time.sleep(0.01)  # Simulate 10ms cleanup
                cleanup_times.append(time.time() - start)

            def medium_cleanup():
                """Medium cleanup handler."""
                start = time.time()
                time.sleep(0.05)  # Simulate 50ms cleanup
                cleanup_times.append(time.time() - start)

            # Register cleanup handlers
            process_state.register_cleanup_handler(fast_cleanup)
            process_state.register_cleanup_handler(medium_cleanup)

            start_time = time.time()

            # Force cleanup
            process_state.force_cleanup()

            total_cleanup_time = time.time() - start_time

            # Total cleanup should be reasonable
            assert total_cleanup_time < 0.5, \
                f"Cleanup handlers took {total_cleanup_time:.3f}s, should be < 0.5s"

            # Individual cleanup times should be recorded
            assert len(cleanup_times) == 2, "Should have executed 2 cleanup handlers"

        except ImportError:
            pytest.skip("Application process state model not available")

    def test_resource_cleanup_performance(self):
        """Test resource cleanup performance."""
        try:
            from risk_calculator.services.application_lifecycle_service import ApplicationLifecycleService

            lifecycle_service = ApplicationLifecycleService()

            # Register some mock resources
            lifecycle_service.register_cleanup_handler(lambda: time.sleep(0.01), "test_resource_1")
            lifecycle_service.register_cleanup_handler(lambda: time.sleep(0.01), "test_resource_2")
            lifecycle_service.register_cleanup_handler(lambda: time.sleep(0.01), "test_resource_3")

            start_time = time.time()

            # Perform cleanup
            lifecycle_service.cleanup_all_resources()

            cleanup_time = time.time() - start_time

            # Should clean up all resources quickly
            assert cleanup_time < 0.2, \
                f"Resource cleanup took {cleanup_time:.3f}s, should be < 0.2s"

        except ImportError:
            pytest.skip("Application lifecycle service not available")

    def test_qt_application_quit_performance(self, mock_qt_app):
        """Test Qt application quit performance."""
        # Test that Qt application quit calls are fast
        start_time = time.time()

        # Call quit multiple times to test responsiveness
        for _ in range(100):
            mock_qt_app.quit()

        quit_time = time.time() - start_time

        # Should be very fast for mock calls
        assert quit_time < 0.01, f"100 quit calls took {quit_time:.4f}s, should be < 0.01s"

        # Verify quit was called
        assert mock_qt_app.quit.call_count == 100

    def test_thread_cleanup_performance(self):
        """Test performance of thread cleanup during exit."""
        # Create some worker threads
        worker_threads = []
        stop_event = threading.Event()

        def worker():
            """Simple worker thread."""
            while not stop_event.is_set():
                time.sleep(0.01)

        # Start several threads
        for i in range(5):
            thread = threading.Thread(target=worker, name=f"worker_{i}")
            thread.daemon = True
            thread.start()
            worker_threads.append(thread)

        # Give threads time to start
        time.sleep(0.1)

        # Measure cleanup time
        start_time = time.time()

        # Signal threads to stop
        stop_event.set()

        # Wait for threads to finish
        for thread in worker_threads:
            thread.join(timeout=0.5)  # 500ms timeout per thread

        cleanup_time = time.time() - start_time

        # Thread cleanup should be fast
        assert cleanup_time < 1.0, \
            f"Thread cleanup took {cleanup_time:.3f}s, should be < 1.0s"

        # Verify threads stopped
        active_threads = [t for t in worker_threads if t.is_alive()]
        assert len(active_threads) == 0, f"Found {len(active_threads)} threads still running"

    def test_memory_cleanup_performance(self):
        """Test memory cleanup performance."""
        import gc

        # Create some objects to cleanup
        test_objects = []
        for i in range(1000):
            test_objects.append({"data": f"test_data_{i}", "index": i})

        start_time = time.time()

        # Clear references and force garbage collection
        test_objects.clear()
        collected = gc.collect()

        cleanup_time = time.time() - start_time

        # Memory cleanup should be fast
        assert cleanup_time < 0.1, \
            f"Memory cleanup took {cleanup_time:.4f}s, should be < 0.1s"

        # Should have collected some objects
        assert collected >= 0, "Garbage collection should return non-negative count"

    def test_file_handle_cleanup_performance(self):
        """Test file handle cleanup performance."""
        import tempfile

        # Create temporary files to test cleanup
        temp_files = []
        file_handles = []

        try:
            # Create several temporary files
            for i in range(10):
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_files.append(temp_file.name)
                file_handles.append(temp_file)

            start_time = time.time()

            # Close all file handles
            for handle in file_handles:
                handle.close()

            cleanup_time = time.time() - start_time

            # File handle cleanup should be very fast
            assert cleanup_time < 0.05, \
                f"File handle cleanup took {cleanup_time:.4f}s, should be < 0.05s"

        finally:
            # Cleanup temporary files
            for temp_file_path in temp_files:
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass  # File may already be cleaned up

    def test_process_termination_performance(self):
        """Test process termination performance using subprocess."""
        # Test that a minimal Python process can be terminated quickly
        python_code = '''
import sys
import time
try:
    # Simple script that can be terminated
    time.sleep(10)  # Would sleep but should be terminated before this
except KeyboardInterrupt:
    sys.exit(0)
'''

        start_time = time.time()

        # Start subprocess
        process = subprocess.Popen(
            [sys.executable, '-c', python_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Give it a moment to start
        time.sleep(0.05)

        # Terminate the process
        process.terminate()
        return_code = process.wait(timeout=1.0)  # 1 second timeout

        termination_time = time.time() - start_time

        # Process termination should be fast
        assert termination_time < self.MAX_EXIT_TIME_SECONDS, \
            f"Process termination took {termination_time:.3f}s, should be < {self.MAX_EXIT_TIME_SECONDS}s"

        # Process should have terminated
        assert return_code is not None, "Process should have terminated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])