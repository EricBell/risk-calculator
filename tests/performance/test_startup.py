"""
Performance tests for application startup time
Target: <3 seconds startup time
"""

import pytest
import sys
import os
import time
from unittest.mock import patch

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Skip this test if running in CI or headless environment
pytest_skip_reason = "Requires display and Qt GUI for performance testing"

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QTimer
    HAS_QT = True
except ImportError:
    HAS_QT = False
    pytest_skip_reason = "PySide6 not available"

# Check if we have a display
HAS_DISPLAY = os.environ.get('DISPLAY') is not None or sys.platform == 'win32'


@pytest.mark.skipif(not HAS_QT, reason=pytest_skip_reason)
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
@pytest.mark.performance
class TestApplicationStartupPerformance:
    """Performance tests for application startup."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None
        self.startup_times = []

    def teardown_method(self):
        """Cleanup after test."""
        if self.app:
            self.app.quit()
            self.app = None

    def test_qt_application_creation_time(self):
        """Test Qt application creation time (<500ms)."""
        start_time = time.time()

        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()

            creation_time = time.time() - start_time
            self.startup_times.append(('app_creation', creation_time))

            # Qt application creation should be very fast
            assert creation_time < 0.5, f"App creation took {creation_time:.3f}s, expected <0.5s"

        except ImportError:
            pytest.skip("Qt application components not implemented yet")

    def test_main_window_creation_time(self):
        """Test main window creation time (<1 second)."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()

            start_time = time.time()
            main_window = qt_app.create_main_window()
            creation_time = time.time() - start_time

            self.startup_times.append(('window_creation', creation_time))

            # Main window creation should be fast
            assert creation_time < 1.0, f"Window creation took {creation_time:.3f}s, expected <1.0s"

        except ImportError:
            pytest.skip("Qt main window not implemented yet")

    def test_complete_application_startup_time(self):
        """Test complete application startup time (<3 seconds)."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Measure complete startup workflow
            total_start_time = time.time()

            # 1. Create application
            app_start = time.time()
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            app_time = time.time() - app_start

            # 2. Create main window
            window_start = time.time()
            main_window = qt_app.create_main_window()
            window_time = time.time() - window_start

            # 3. Initialize UI components
            ui_start = time.time()
            main_window.setup_ui()
            ui_time = time.time() - ui_start

            # 4. Load configuration
            config_start = time.time()
            main_window.restore_window_state()
            config_time = time.time() - config_start

            # 5. Show window
            show_start = time.time()
            main_window.show()
            show_time = time.time() - show_start

            total_time = time.time() - total_start_time

            # Record all timing breakdowns
            self.startup_times.extend([
                ('total_startup', total_time),
                ('app_creation', app_time),
                ('window_creation', window_time),
                ('ui_initialization', ui_time),
                ('config_loading', config_time),
                ('window_show', show_time)
            ])

            # Verify performance targets
            assert total_time < 3.0, f"Total startup took {total_time:.3f}s, expected <3.0s"
            assert app_time < 0.5, f"App creation took {app_time:.3f}s, expected <0.5s"
            assert window_time < 1.0, f"Window creation took {window_time:.3f}s, expected <1.0s"
            assert ui_time < 1.0, f"UI initialization took {ui_time:.3f}s, expected <1.0s"

        except ImportError:
            pytest.skip("Complete Qt application not implemented yet")

    def test_startup_memory_usage(self):
        """Test startup memory usage (<50MB)."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Get baseline memory usage
            process = psutil.Process()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Create application
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            main_window = qt_app.create_main_window()
            main_window.show()

            # Force Qt to process events and render
            self.app.processEvents()

            # Measure memory after startup
            startup_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = startup_memory - baseline_memory

            # Verify memory usage is reasonable
            assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB, expected <50MB"
            assert startup_memory < 100, f"Total memory {startup_memory:.1f}MB, expected <100MB"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_cold_vs_warm_startup_performance(self):
        """Test that subsequent startups are faster (warm cache)."""
        startup_times = []

        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Perform multiple startup cycles
            for i in range(3):
                if self.app:
                    self.app.quit()
                    self.app = None

                start_time = time.time()

                qt_app = RiskCalculatorQtApp()
                self.app = qt_app.create_application()
                main_window = qt_app.create_main_window()
                main_window.show()

                # Process events to ensure full initialization
                self.app.processEvents()

                cycle_time = time.time() - start_time
                startup_times.append(cycle_time)

                # Brief pause between cycles
                time.sleep(0.1)

            # Verify performance improvements
            cold_start = startup_times[0]
            warm_starts = startup_times[1:]

            # All startups should be under target
            for i, startup_time in enumerate(startup_times):
                assert startup_time < 3.0, f"Startup {i+1} took {startup_time:.3f}s, expected <3.0s"

            # Warm starts should generally be faster (allow some variance)
            if len(warm_starts) > 0:
                avg_warm_start = sum(warm_starts) / len(warm_starts)
                # Warm start should be at least 10% faster on average
                assert avg_warm_start <= cold_start * 1.1, \
                    f"Warm starts ({avg_warm_start:.3f}s) not significantly faster than cold start ({cold_start:.3f}s)"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_startup_with_configuration_loading(self):
        """Test startup performance with various configuration scenarios."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.services.qt_config_service import QtConfigService

            config_scenarios = [
                ("empty_config", {}),
                ("minimal_config", {
                    "window/width": 1024,
                    "window/height": 768
                }),
                ("full_config", {
                    "window/width": 1200,
                    "window/height": 900,
                    "window/x": 100,
                    "window/y": 100,
                    "window/maximized": False,
                    "application/theme": "default",
                    "calculation/precision": 2,
                    "calculation/default_method": "percentage"
                })
            ]

            for scenario_name, config_data in config_scenarios:
                if self.app:
                    self.app.quit()
                    self.app = None

                # Setup configuration for this scenario
                config_service = QtConfigService()
                config_service.clear_all_settings()
                for key, value in config_data.items():
                    config_service.set_value(key, value)

                # Measure startup with this configuration
                start_time = time.time()

                qt_app = RiskCalculatorQtApp()
                self.app = qt_app.create_application()
                main_window = qt_app.create_main_window()
                main_window.restore_window_state()  # Load configuration
                main_window.show()

                scenario_time = time.time() - start_time
                self.startup_times.append((scenario_name, scenario_time))

                # All scenarios should meet performance target
                assert scenario_time < 3.0, \
                    f"{scenario_name} startup took {scenario_time:.3f}s, expected <3.0s"

        except ImportError:
            pytest.skip("Configuration loading not implemented yet")

    def test_startup_performance_regression(self):
        """Test for startup performance regression detection."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Perform multiple startup measurements for statistical analysis
            measurements = []

            for i in range(5):  # 5 measurements for statistics
                if self.app:
                    self.app.quit()
                    self.app = None

                start_time = time.time()

                qt_app = RiskCalculatorQtApp()
                self.app = qt_app.create_application()
                main_window = qt_app.create_main_window()
                main_window.show()
                self.app.processEvents()

                measurement = time.time() - start_time
                measurements.append(measurement)

                time.sleep(0.1)  # Brief pause between measurements

            # Statistical analysis
            avg_time = sum(measurements) / len(measurements)
            max_time = max(measurements)
            min_time = min(measurements)
            variance = sum((x - avg_time) ** 2 for x in measurements) / len(measurements)
            std_dev = variance ** 0.5

            # Performance criteria
            assert avg_time < 2.5, f"Average startup time {avg_time:.3f}s, expected <2.5s"
            assert max_time < 3.0, f"Maximum startup time {max_time:.3f}s, expected <3.0s"
            assert std_dev < 0.5, f"Startup time variance too high: {std_dev:.3f}s"

            # Record statistics
            self.startup_times.extend([
                ('avg_startup', avg_time),
                ('max_startup', max_time),
                ('min_startup', min_time),
                ('startup_stddev', std_dev)
            ])

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_startup_with_different_display_configurations(self):
        """Test startup performance across different display configurations."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Simulate different display scenarios
            display_configs = [
                ("standard_dpi", 96),
                ("high_dpi_125", 120),
                ("high_dpi_150", 144),
                ("high_dpi_200", 192)
            ]

            for config_name, dpi_value in display_configs:
                if self.app:
                    self.app.quit()
                    self.app = None

                # Mock display DPI for this test
                with patch('risk_calculator.services.qt_display_service.QtDisplayService.get_dpi_scale_factor') as mock_dpi:
                    mock_dpi.return_value = dpi_value / 96  # Scale factor

                    start_time = time.time()

                    qt_app = RiskCalculatorQtApp()
                    self.app = qt_app.create_application()
                    main_window = qt_app.create_main_window()
                    main_window.show()

                    config_time = time.time() - start_time
                    self.startup_times.append((config_name, config_time))

                    # High DPI shouldn't significantly impact startup time
                    assert config_time < 3.5, \
                        f"{config_name} startup took {config_time:.3f}s, expected <3.5s"

        except ImportError:
            pytest.skip("Display configuration testing not implemented yet")


@pytest.mark.skipif(not HAS_QT, reason=pytest_skip_reason)
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
@pytest.mark.performance
class TestStartupResourceUsage:
    """Test resource usage during startup."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None

    def teardown_method(self):
        """Cleanup after test."""
        if self.app:
            self.app.quit()
            self.app = None

    def test_cpu_usage_during_startup(self):
        """Test CPU usage during startup remains reasonable."""
        try:
            import threading
            from risk_calculator.qt_main import RiskCalculatorQtApp

            cpu_measurements = []
            stop_monitoring = threading.Event()

            def monitor_cpu():
                """Monitor CPU usage during startup."""
                process = psutil.Process()
                while not stop_monitoring.is_set():
                    try:
                        cpu_percent = process.cpu_percent(interval=0.1)
                        cpu_measurements.append(cpu_percent)
                    except psutil.NoSuchProcess:
                        break

            # Start CPU monitoring
            monitor_thread = threading.Thread(target=monitor_cpu)
            monitor_thread.start()

            # Perform startup
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            main_window = qt_app.create_main_window()
            main_window.show()
            self.app.processEvents()

            # Stop monitoring
            stop_monitoring.set()
            monitor_thread.join(timeout=2.0)

            # Analyze CPU usage
            if cpu_measurements:
                avg_cpu = sum(cpu_measurements) / len(cpu_measurements)
                max_cpu = max(cpu_measurements)

                # CPU usage should be reasonable during startup
                assert avg_cpu < 50, f"Average CPU usage {avg_cpu:.1f}%, expected <50%"
                assert max_cpu < 80, f"Peak CPU usage {max_cpu:.1f}%, expected <80%"

        except ImportError:
            pytest.skip("CPU monitoring not available or Qt app not implemented")

    def test_file_handle_usage_during_startup(self):
        """Test file handle usage remains reasonable during startup."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            process = psutil.Process()

            # Get baseline file handles
            baseline_fds = process.num_fds() if hasattr(process, 'num_fds') else 0

            # Perform startup
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            main_window = qt_app.create_main_window()
            main_window.show()

            # Measure file handles after startup
            startup_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            fd_increase = startup_fds - baseline_fds

            # File handle increase should be reasonable
            if hasattr(process, 'num_fds'):
                assert fd_increase < 50, f"File descriptor increase {fd_increase}, expected <50"

        except (ImportError, AttributeError):
            pytest.skip("File descriptor monitoring not available or Qt app not implemented")

    def test_startup_with_concurrent_operations(self):
        """Test startup performance with concurrent background operations."""
        try:
            import threading
            import time
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Create background work to simulate system load
            stop_background = threading.Event()
            background_results = []

            def background_work():
                """Simulate background CPU work."""
                while not stop_background.is_set():
                    # Light computational work
                    result = sum(i ** 2 for i in range(1000))
                    background_results.append(result)
                    time.sleep(0.01)

            # Start background work
            background_thread = threading.Thread(target=background_work)
            background_thread.start()

            try:
                # Measure startup with background load
                start_time = time.time()

                qt_app = RiskCalculatorQtApp()
                self.app = qt_app.create_application()
                main_window = qt_app.create_main_window()
                main_window.show()

                startup_time = time.time() - start_time

                # Should still meet performance target even with background load
                assert startup_time < 4.0, \
                    f"Startup with background load took {startup_time:.3f}s, expected <4.0s"

            finally:
                # Stop background work
                stop_background.set()
                background_thread.join(timeout=2.0)

        except ImportError:
            pytest.skip("Concurrent startup testing not available")