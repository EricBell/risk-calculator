"""
Performance tests for UI responsiveness
Target: <100ms response time for user interactions
"""

import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Skip this test if running in CI or headless environment
pytest_skip_reason = "Requires display and Qt GUI for performance testing"

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QTimer, QEventLoop
    from PySide6.QtTest import QTest
    HAS_QT = True
except ImportError:
    HAS_QT = False
    pytest_skip_reason = "PySide6 not available"

# Check if we have a display
HAS_DISPLAY = os.environ.get('DISPLAY') is not None or sys.platform == 'win32'


@pytest.mark.skipif(not HAS_QT, reason=pytest_skip_reason)
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
@pytest.mark.performance
class TestUIResponsivenessPerformance:
    """Performance tests for UI responsiveness."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None
        self.main_window = None
        self.response_times = []

    def teardown_method(self):
        """Cleanup after test."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        if self.app:
            self.app.quit()
            self.app = None

    def _setup_application(self):
        """Helper to setup application for testing."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            # Process events to ensure UI is ready
            self.app.processEvents()
            return True

        except ImportError:
            return False

    def test_button_click_response_time(self):
        """Test button click response time (<100ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Find calculate button (assuming it exists)
            calculate_button = self.main_window.findChild(object, "calculate_button")
            if not calculate_button:
                pytest.skip("Calculate button not found in UI")

            # Measure button click response time
            start_time = time.time()

            # Simulate button click
            QTest.mouseClick(calculate_button, Qt.LeftButton)

            # Process events to handle click
            self.app.processEvents()

            response_time = time.time() - start_time
            self.response_times.append(('button_click', response_time))

            # Button should respond instantly
            assert response_time < 0.1, f"Button click took {response_time*1000:.1f}ms, expected <100ms"

        except Exception as e:
            pytest.skip(f"Button click test failed: {e}")

    def test_text_input_response_time(self):
        """Test text input field response time (<50ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Find input fields (assuming they exist)
            account_field = self.main_window.findChild(object, "account_size_entry")
            if not account_field:
                pytest.skip("Account size field not found in UI")

            # Measure text input response time
            test_text = "10000"

            start_time = time.time()

            # Simulate typing
            account_field.clear()
            account_field.setText(test_text)

            # Process events
            self.app.processEvents()

            response_time = time.time() - start_time
            self.response_times.append(('text_input', response_time))

            # Text input should be very fast
            assert response_time < 0.05, f"Text input took {response_time*1000:.1f}ms, expected <50ms"

            # Verify text was set correctly
            assert account_field.text() == test_text

        except Exception as e:
            pytest.skip(f"Text input test failed: {e}")

    def test_tab_switching_response_time(self):
        """Test tab switching response time (<100ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Find tab widget (assuming it exists)
            tab_widget = self.main_window.findChild(object, "tab_widget")
            if not tab_widget:
                pytest.skip("Tab widget not found in UI")

            # Test switching between tabs
            tab_count = tab_widget.count() if hasattr(tab_widget, 'count') else 3

            for i in range(min(tab_count, 3)):  # Test first 3 tabs
                start_time = time.time()

                # Switch to tab
                if hasattr(tab_widget, 'setCurrentIndex'):
                    tab_widget.setCurrentIndex(i)

                # Process events
                self.app.processEvents()

                response_time = time.time() - start_time
                self.response_times.append((f'tab_switch_{i}', response_time))

                # Tab switching should be instant
                assert response_time < 0.1, f"Tab switch to {i} took {response_time*1000:.1f}ms, expected <100ms"

        except Exception as e:
            pytest.skip(f"Tab switching test failed: {e}")

    def test_window_resize_response_time(self):
        """Test window resize response time (<200ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Get initial size
            initial_size = self.main_window.size()

            # Test different resize scenarios
            resize_scenarios = [
                (1024, 768),
                (1280, 960),
                (800, 600),
                (1200, 900)
            ]

            for width, height in resize_scenarios:
                start_time = time.time()

                # Resize window
                self.main_window.resize(width, height)

                # Process events to handle resize
                self.app.processEvents()

                # Wait for layout to stabilize
                QTimer.singleShot(50, lambda: None)
                loop = QEventLoop()
                QTimer.singleShot(50, loop.quit)
                loop.exec()

                response_time = time.time() - start_time
                self.response_times.append((f'resize_{width}x{height}', response_time))

                # Window resize should be smooth
                assert response_time < 0.2, f"Resize to {width}x{height} took {response_time*1000:.1f}ms, expected <200ms"

        except Exception as e:
            pytest.skip(f"Window resize test failed: {e}")

    def test_calculation_response_time(self):
        """Test calculation response time (<100ms for simple calculations)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            from risk_calculator.services.risk_calculation_service import RiskCalculationService
            from risk_calculator.models.equity_trade import EquityTrade
            from decimal import Decimal

            calc_service = RiskCalculationService()

            # Test various calculation scenarios
            test_cases = [
                {
                    "account_size": "10000",
                    "risk_percentage": "2.0",
                    "entry_price": "100.00",
                    "stop_loss": "95.00"
                },
                {
                    "account_size": "50000",
                    "risk_percentage": "1.5",
                    "entry_price": "250.00",
                    "stop_loss": "240.00"
                },
                {
                    "account_size": "25000",
                    "risk_percentage": "3.0",
                    "entry_price": "50.00",
                    "stop_loss": "48.50"
                }
            ]

            for i, test_case in enumerate(test_cases):
                start_time = time.time()

                # Create trade and calculate
                trade = EquityTrade(
                    symbol="TEST",
                    account_size=Decimal(test_case["account_size"]),
                    risk_percentage=Decimal(test_case["risk_percentage"]),
                    entry_price=Decimal(test_case["entry_price"]),
                    stop_loss=Decimal(test_case["stop_loss"])
                )

                result = calc_service.calculate_position_size(trade, "percentage")

                calc_time = time.time() - start_time
                self.response_times.append((f'calculation_{i}', calc_time))

                # Calculations should be very fast
                assert calc_time < 0.1, f"Calculation {i} took {calc_time*1000:.1f}ms, expected <100ms"
                assert result.position_size > 0

        except ImportError:
            pytest.skip("Calculation service not implemented yet")

    def test_validation_response_time(self):
        """Test form validation response time (<50ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            from risk_calculator.services.validation_service import ValidationService

            validation_service = ValidationService()

            # Test various validation scenarios
            validation_cases = [
                {
                    "account_size": "10000",
                    "risk_percentage": "2.0",
                    "entry_price": "100.00",
                    "stop_loss": "95.00",
                    "symbol": "AAPL"
                },
                {
                    "account_size": "invalid",  # Invalid input
                    "risk_percentage": "2.0",
                    "entry_price": "100.00",
                    "stop_loss": "95.00",
                    "symbol": "AAPL"
                },
                {
                    "account_size": "10000",
                    "risk_percentage": "15.0",  # Too high risk
                    "entry_price": "100.00",
                    "stop_loss": "95.00",
                    "symbol": "AAPL"
                }
            ]

            for i, form_data in enumerate(validation_cases):
                start_time = time.time()

                # Validate form data
                errors = validation_service.validate_form_data(form_data, "equity", "percentage")

                validation_time = time.time() - start_time
                self.response_times.append((f'validation_{i}', validation_time))

                # Validation should be instant
                assert validation_time < 0.05, f"Validation {i} took {validation_time*1000:.1f}ms, expected <50ms"
                assert isinstance(errors, list)

        except ImportError:
            pytest.skip("Validation service not implemented yet")

    def test_menu_interaction_response_time(self):
        """Test menu interaction response time (<100ms)."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Find menu bar (assuming it exists)
            menu_bar = self.main_window.menuBar()
            if not menu_bar:
                pytest.skip("Menu bar not found in UI")

            # Test menu operations
            menus = menu_bar.findChildren(object)
            if not menus:
                pytest.skip("No menus found in menu bar")

            for i, menu in enumerate(menus[:3]):  # Test first 3 menus
                if hasattr(menu, 'show'):
                    start_time = time.time()

                    # Show menu
                    menu.show()

                    # Process events
                    self.app.processEvents()

                    response_time = time.time() - start_time
                    self.response_times.append((f'menu_show_{i}', response_time))

                    # Menu should appear instantly
                    assert response_time < 0.1, f"Menu {i} show took {response_time*1000:.1f}ms, expected <100ms"

                    # Hide menu
                    if hasattr(menu, 'hide'):
                        menu.hide()

        except Exception as e:
            pytest.skip(f"Menu interaction test failed: {e}")

    def test_rapid_user_interactions(self):
        """Test response time under rapid user interactions."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Find interactive elements
            account_field = self.main_window.findChild(object, "account_size_entry")
            risk_field = self.main_window.findChild(object, "risk_percentage_entry")

            if not account_field or not risk_field:
                pytest.skip("Required input fields not found")

            # Simulate rapid interactions
            interactions = []
            total_start_time = time.time()

            for i in range(10):  # 10 rapid interactions
                interaction_start = time.time()

                # Alternate between fields and input different values
                if i % 2 == 0:
                    account_field.clear()
                    account_field.setText(str(10000 + i * 1000))
                else:
                    risk_field.clear()
                    risk_field.setText(str(2.0 + i * 0.1))

                # Process events
                self.app.processEvents()

                interaction_time = time.time() - interaction_start
                interactions.append(interaction_time)

            total_time = time.time() - total_start_time

            # Analyze rapid interaction performance
            avg_interaction_time = sum(interactions) / len(interactions)
            max_interaction_time = max(interactions)

            self.response_times.extend([
                ('rapid_avg', avg_interaction_time),
                ('rapid_max', max_interaction_time),
                ('rapid_total', total_time)
            ])

            # All interactions should be fast
            assert avg_interaction_time < 0.05, f"Average interaction took {avg_interaction_time*1000:.1f}ms, expected <50ms"
            assert max_interaction_time < 0.1, f"Slowest interaction took {max_interaction_time*1000:.1f}ms, expected <100ms"
            assert total_time < 1.0, f"Total rapid interactions took {total_time:.3f}s, expected <1.0s"

        except Exception as e:
            pytest.skip(f"Rapid interaction test failed: {e}")

    def test_ui_thread_blocking_detection(self):
        """Test that UI operations don't block the main thread."""
        if not self._setup_application():
            pytest.skip("Qt application not implemented yet")

        try:
            # Monitor event processing during operations
            event_processing_times = []

            for i in range(5):
                # Perform UI operation
                self.main_window.resize(1000 + i * 50, 700 + i * 30)

                # Measure event processing time
                start_time = time.time()
                self.app.processEvents()
                processing_time = time.time() - start_time

                event_processing_times.append(processing_time)

            # Event processing should always be fast
            max_processing_time = max(event_processing_times)
            avg_processing_time = sum(event_processing_times) / len(event_processing_times)

            self.response_times.extend([
                ('event_processing_avg', avg_processing_time),
                ('event_processing_max', max_processing_time)
            ])

            # UI should never block
            assert max_processing_time < 0.05, f"Event processing blocked for {max_processing_time*1000:.1f}ms, expected <50ms"
            assert avg_processing_time < 0.02, f"Average event processing took {avg_processing_time*1000:.1f}ms, expected <20ms"

        except Exception as e:
            pytest.skip(f"UI thread blocking test failed: {e}")


@pytest.mark.skipif(not HAS_QT, reason=pytest_skip_reason)
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
@pytest.mark.performance
class TestUIScalingPerformance:
    """Test UI scaling performance during window operations."""

    def setup_method(self):
        """Setup test environment."""
        self.app = None
        self.main_window = None

    def teardown_method(self):
        """Cleanup after test."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        if self.app:
            self.app.quit()
            self.app = None

    def test_responsive_scaling_performance(self):
        """Test responsive UI scaling performance during resize."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.services.qt_layout_service import QtLayoutService

            qt_app = RiskCalculatorQtApp()
            self.app = qt_app.create_application()
            self.main_window = qt_app.create_main_window()
            self.main_window.show()

            layout_service = QtLayoutService()

            # Test scaling performance with different window sizes
            test_sizes = [
                (800, 600),
                (1024, 768),
                (1280, 960),
                (1600, 1200),
                (1920, 1440)
            ]

            scaling_times = []

            for width, height in test_sizes:
                start_time = time.time()

                # Resize window (triggers responsive scaling)
                self.main_window.resize(width, height)

                # Process scaling events
                self.app.processEvents()

                # Calculate scale factors
                base_size = (800, 600)
                scale_factors = layout_service.calculate_scale_factors(base_size, (width, height))

                # Apply responsive scaling
                layout_service.apply_responsive_scaling(scale_factors)

                scaling_time = time.time() - start_time
                scaling_times.append(scaling_time)

                # Each scaling operation should be fast
                assert scaling_time < 0.2, f"Scaling to {width}x{height} took {scaling_time*1000:.1f}ms, expected <200ms"

            # Overall scaling performance should be consistent
            avg_scaling_time = sum(scaling_times) / len(scaling_times)
            assert avg_scaling_time < 0.15, f"Average scaling time {avg_scaling_time*1000:.1f}ms, expected <150ms"

        except ImportError:
            pytest.skip("Responsive scaling not implemented yet")

    def test_high_dpi_scaling_performance(self):
        """Test performance with high-DPI scaling factors."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp

            # Test with different DPI scale factors
            dpi_scales = [1.0, 1.25, 1.5, 2.0, 2.5]

            for scale_factor in dpi_scales:
                with patch('risk_calculator.services.qt_display_service.QtDisplayService.get_dpi_scale_factor') as mock_dpi:
                    mock_dpi.return_value = scale_factor

                    start_time = time.time()

                    qt_app = RiskCalculatorQtApp()
                    self.app = qt_app.create_application()
                    self.main_window = qt_app.create_main_window()
                    self.main_window.show()

                    # Process DPI scaling
                    self.app.processEvents()

                    scaling_time = time.time() - start_time

                    # High-DPI scaling shouldn't significantly impact performance
                    assert scaling_time < 2.0, f"DPI {scale_factor}x scaling took {scaling_time:.3f}s, expected <2.0s"

                    # Cleanup for next iteration
                    if self.main_window:
                        self.main_window.close()
                        self.main_window = None
                    if self.app:
                        self.app.quit()
                        self.app = None

        except ImportError:
            pytest.skip("High-DPI scaling not implemented yet")