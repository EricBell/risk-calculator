"""
Performance tests for memory usage validation
Target: <100MB memory usage during normal operation
"""

import pytest
import sys
import os
import time
import gc
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
@pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
@pytest.mark.performance
class TestMemoryUsageValidation:
    """Memory usage validation tests."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None
        self.main_window = None
        self.process = psutil.Process() if HAS_PSUTIL else None
        self.baseline_memory = None

    def teardown_method(self):
        """Cleanup after test."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        if self.app:
            self.app.quit()
            self.app = None

        # Force garbage collection
        gc.collect()

    def _get_memory_usage_mb(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def _get_memory_percent(self):
        """Get memory usage as percentage of system memory."""
        return self.process.memory_percent()

    def test_application_baseline_memory_usage(self):
        """Test baseline memory usage after application startup."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Record baseline before Qt application
            self.baseline_memory = self._get_memory_usage_mb()

            # Create and initialize application
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            # Process events to ensure full initialization
            self.app.processEvents()

            # Measure memory after startup
            startup_memory = self._get_memory_usage_mb()
            memory_increase = startup_memory - self.baseline_memory

            # Verify memory usage targets
            assert startup_memory < 100, f"Startup memory {startup_memory:.1f}MB, expected <100MB"
            assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB, expected <50MB"

            # Record for subsequent tests
            self.baseline_memory = startup_memory

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_calculation_memory_stability(self):
        """Test memory stability during repeated calculations."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.services.risk_calculation_service import RiskCalculationService
            from risk_calculator.models.equity_trade import EquityTrade
            from decimal import Decimal

            # Setup application
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()

            calc_service = RiskCalculationService()
            initial_memory = self._get_memory_usage_mb()

            # Perform many calculations to test for memory leaks
            for i in range(100):
                trade = EquityTrade(
                    symbol=f"TEST{i}",
                    account_size=Decimal("10000"),
                    risk_percentage=Decimal("2.0"),
                    entry_price=Decimal(str(100.0 + i * 0.1)),
                    stop_loss=Decimal(str(95.0 + i * 0.1))
                )

                result = calc_service.calculate_position_size(trade, "percentage")
                assert result.position_size > 0

                # Check memory periodically
                if i % 20 == 0:
                    current_memory = self._get_memory_usage_mb()
                    memory_growth = current_memory - initial_memory

                    # Memory should not grow significantly
                    assert memory_growth < 10, f"Memory grew by {memory_growth:.1f}MB after {i} calculations"

            # Final memory check
            final_memory = self._get_memory_usage_mb()
            total_growth = final_memory - initial_memory

            assert total_growth < 15, f"Total memory growth {total_growth:.1f}MB after 100 calculations, expected <15MB"

        except ImportError:
            pytest.skip("Calculation services not implemented yet")

    def test_window_resize_memory_stability(self):
        """Test memory stability during window resizing operations."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            initial_memory = self._get_memory_usage_mb()

            # Perform many resize operations
            resize_patterns = [
                (800, 600), (1024, 768), (1280, 960), (1600, 1200),
                (1920, 1440), (1280, 960), (1024, 768), (800, 600)
            ]

            for cycle in range(10):  # 10 cycles of resize patterns
                for width, height in resize_patterns:
                    self.main_window.resize(width, height)
                    self.app.processEvents()

                # Check memory after each cycle
                current_memory = self._get_memory_usage_mb()
                memory_growth = current_memory - initial_memory

                # Memory should not grow from resize operations
                assert memory_growth < 5, f"Memory grew by {memory_growth:.1f}MB after {cycle+1} resize cycles"

            # Force garbage collection and final check
            gc.collect()
            final_memory = self._get_memory_usage_mb()
            final_growth = final_memory - initial_memory

            assert final_growth < 10, f"Final memory growth {final_growth:.1f}MB from resize operations"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_ui_interaction_memory_stability(self):
        """Test memory stability during extensive UI interactions."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            initial_memory = self._get_memory_usage_mb()

            # Find UI elements
            account_field = self.main_window.findChild(object, "account_size_entry")
            risk_field = self.main_window.findChild(object, "risk_percentage_entry")
            tab_widget = self.main_window.findChild(object, "tab_widget")

            if not any([account_field, risk_field, tab_widget]):
                pytest.skip("Required UI elements not found")

            # Perform extensive UI interactions
            for i in range(200):  # 200 interactions
                # Text input operations
                if account_field:
                    account_field.clear()
                    account_field.setText(str(10000 + i))

                if risk_field:
                    risk_field.clear()
                    risk_field.setText(str(2.0 + i * 0.01))

                # Tab switching
                if tab_widget and hasattr(tab_widget, 'setCurrentIndex') and hasattr(tab_widget, 'count'):
                    tab_count = tab_widget.count()
                    if tab_count > 1:
                        tab_widget.setCurrentIndex(i % tab_count)

                # Process events
                self.app.processEvents()

                # Periodic memory checks
                if i % 50 == 0:
                    current_memory = self._get_memory_usage_mb()
                    memory_growth = current_memory - initial_memory

                    assert memory_growth < 20, f"Memory grew by {memory_growth:.1f}MB after {i} interactions"

            # Final memory validation
            final_memory = self._get_memory_usage_mb()
            total_growth = final_memory - initial_memory

            assert total_growth < 25, f"Total memory growth {total_growth:.1f}MB from UI interactions"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_configuration_loading_memory_usage(self):
        """Test memory usage during configuration loading operations."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.services.qt_config_service import QtConfigService

            initial_memory = self._get_memory_usage_mb()

            # Create large configuration datasets
            config_service = QtConfigService()

            # Generate extensive configuration data
            large_config = {}
            for i in range(1000):  # 1000 configuration entries
                large_config[f"section_{i // 100}/key_{i}"] = f"value_{i}_" + "x" * 100

            # Save large configuration
            for key, value in large_config.items():
                config_service.set_value(key, value)

            config_memory = self._get_memory_usage_mb()
            config_growth = config_memory - initial_memory

            # Configuration storage should be efficient
            assert config_growth < 30, f"Configuration storage used {config_growth:.1f}MB, expected <30MB"

            # Load configuration into application
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()

            # Load configuration
            self.main_window.restore_window_state()

            final_memory = self._get_memory_usage_mb()
            total_growth = final_memory - initial_memory

            assert total_growth < 50, f"Total memory with large config {total_growth:.1f}MB, expected <50MB"

        except ImportError:
            pytest.skip("Configuration services not implemented yet")

    def test_long_running_session_memory_stability(self):
        """Test memory stability during long-running session simulation."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            initial_memory = self._get_memory_usage_mb()
            memory_samples = [initial_memory]

            # Simulate long-running session (compressed time)
            session_cycles = 50  # Represents extended usage

            for cycle in range(session_cycles):
                # Simulate typical user workflow

                # 1. Window operations
                if cycle % 5 == 0:
                    self.main_window.resize(800 + (cycle % 10) * 50, 600 + (cycle % 8) * 30)

                # 2. UI interactions
                if hasattr(self.main_window, 'findChild'):
                    account_field = self.main_window.findChild(object, "account_size_entry")
                    if account_field:
                        account_field.setText(str(10000 + cycle * 100))

                # 3. Process events
                self.app.processEvents()

                # 4. Periodic memory sampling
                if cycle % 10 == 0:
                    current_memory = self._get_memory_usage_mb()
                    memory_samples.append(current_memory)

                    memory_growth = current_memory - initial_memory
                    assert memory_growth < 40, f"Memory grew by {memory_growth:.1f}MB at cycle {cycle}"

                # 5. Simulated idle time
                time.sleep(0.001)

            # Analyze memory stability
            final_memory = self._get_memory_usage_mb()
            memory_samples.append(final_memory)

            # Calculate memory statistics
            max_memory = max(memory_samples)
            avg_memory = sum(memory_samples) / len(memory_samples)
            memory_variance = sum((x - avg_memory) ** 2 for x in memory_samples) / len(memory_samples)
            memory_std_dev = memory_variance ** 0.5

            # Memory should be stable over time
            total_growth = final_memory - initial_memory
            max_growth = max_memory - initial_memory

            assert total_growth < 30, f"Final memory growth {total_growth:.1f}MB, expected <30MB"
            assert max_growth < 40, f"Peak memory growth {max_growth:.1f}MB, expected <40MB"
            assert memory_std_dev < 10, f"Memory variance too high: {memory_std_dev:.1f}MB"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_memory_cleanup_on_close(self):
        """Test that memory is properly cleaned up when application closes."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            initial_memory = self._get_memory_usage_mb()

            # Create and use application
            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            # Use application briefly
            self.app.processEvents()
            time.sleep(0.1)

            peak_memory = self._get_memory_usage_mb()

            # Close application properly
            self.main_window.close()
            self.main_window = None
            self.app.quit()
            self.app = None

            # Force cleanup
            gc.collect()
            time.sleep(0.2)  # Allow system cleanup

            cleanup_memory = self._get_memory_usage_mb()
            memory_recovered = peak_memory - cleanup_memory

            # Most memory should be recovered after cleanup
            remaining_overhead = cleanup_memory - initial_memory

            # Should recover significant memory
            assert memory_recovered > 0, f"No memory recovered: {memory_recovered:.1f}MB"
            assert remaining_overhead < 20, f"Too much memory retained: {remaining_overhead:.1f}MB"

        except ImportError:
            pytest.skip("Qt application not implemented yet")

    def test_system_memory_percentage_usage(self):
        """Test that application uses reasonable percentage of system memory."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Get system memory info
            system_memory = psutil.virtual_memory()
            total_memory_gb = system_memory.total / (1024 ** 3)

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            # Process events to ensure full initialization
            self.app.processEvents()

            # Measure memory usage
            memory_percent = self._get_memory_percent()
            memory_mb = self._get_memory_usage_mb()

            # Application should use reasonable percentage of system memory
            if total_memory_gb >= 8:  # Systems with 8GB+ RAM
                assert memory_percent < 2.0, f"Using {memory_percent:.1f}% of system memory, expected <2%"
            elif total_memory_gb >= 4:  # Systems with 4-8GB RAM
                assert memory_percent < 3.0, f"Using {memory_percent:.1f}% of system memory, expected <3%"
            else:  # Systems with <4GB RAM
                assert memory_percent < 5.0, f"Using {memory_percent:.1f}% of system memory, expected <5%"

            # Absolute memory limit regardless of system size
            assert memory_mb < 150, f"Using {memory_mb:.1f}MB, expected <150MB"

        except ImportError:
            pytest.skip("Qt application not implemented yet")


@pytest.mark.skipif(not HAS_QT, reason=pytest_skip_reason)
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
@pytest.mark.performance
class TestMemoryLeakDetection:
    """Specific tests for memory leak detection."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None
        self.process = psutil.Process()

    def teardown_method(self):
        """Cleanup after test."""
        if self.app:
            self.app.quit()
            self.app = None
        gc.collect()

    def test_qt_object_leak_detection(self):
        """Test for Qt object memory leaks during repeated operations."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            initial_memory = self.process.memory_info().rss / 1024 / 1024

            # Repeatedly create and destroy Qt objects
            for i in range(20):  # 20 cycles
                qt_app = RiskCalculatorQtApp()
                app = qt_app.create_application()
                main_window = qt_app.create_main_window()
                main_window.show()

                # Use the objects briefly
                app.processEvents()

                # Cleanup
                main_window.close()
                app.quit()

                # Force cleanup
                del main_window, app, qt_app
                gc.collect()

                # Check for memory growth every 5 cycles
                if i % 5 == 4:
                    current_memory = self.process.memory_info().rss / 1024 / 1024
                    memory_growth = current_memory - initial_memory

                    # Minimal growth expected after proper cleanup
                    assert memory_growth < 30, f"Potential memory leak: {memory_growth:.1f}MB growth after {i+1} cycles"

        except ImportError:
            pytest.skip("Qt object leak detection not available")

    def test_calculation_service_leak_detection(self):
        """Test for memory leaks in calculation services."""
        try:
            from risk_calculator.services.risk_calculation_service import RiskCalculationService
            from risk_calculator.models.equity_trade import EquityTrade
            from decimal import Decimal

            initial_memory = self.process.memory_info().rss / 1024 / 1024

            # Repeatedly create calculation services and perform calculations
            for cycle in range(10):
                calc_service = RiskCalculationService()

                # Perform many calculations in this cycle
                for i in range(50):
                    trade = EquityTrade(
                        symbol=f"LEAK{cycle}_{i}",
                        account_size=Decimal("10000"),
                        risk_percentage=Decimal("2.0"),
                        entry_price=Decimal("100.00"),
                        stop_loss=Decimal("95.00")
                    )

                    result = calc_service.calculate_position_size(trade, "percentage")
                    del result, trade

                # Cleanup service
                del calc_service
                gc.collect()

                # Check memory growth
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory

                assert memory_growth < 15, f"Calculation service leak: {memory_growth:.1f}MB growth after cycle {cycle}"

        except ImportError:
            pytest.skip("Calculation service leak detection not available")

    def test_configuration_service_leak_detection(self):
        """Test for memory leaks in configuration services."""
        try:
            from risk_calculator.services.qt_config_service import QtConfigService

            initial_memory = self.process.memory_info().rss / 1024 / 1024

            # Repeatedly create and use configuration services
            for cycle in range(15):
                config_service = QtConfigService()

                # Perform configuration operations
                for i in range(20):
                    key = f"test_leak_{cycle}_{i}"
                    value = f"value_{i}_" + "x" * 50

                    config_service.set_value(key, value)
                    retrieved = config_service.get_value(key)
                    assert retrieved == value

                # Cleanup
                config_service.clear_all_settings()
                del config_service
                gc.collect()

                # Check memory growth
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory

                assert memory_growth < 10, f"Config service leak: {memory_growth:.1f}MB growth after cycle {cycle}"

        except ImportError:
            pytest.skip("Configuration service leak detection not available")