import pytest
import tkinter as tk
from decimal import Decimal
from unittest.mock import patch
from risk_calculator.main import RiskCalculatorApp


class TestPercentageMethodIntegration:
    """Integration test for percentage-based equity calculation - from quickstart.md scenario 1"""

    def setup_method(self):
        # Create a test root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide during testing

    def teardown_method(self):
        if self.root:
            self.root.destroy()

    def test_percentage_based_equity_calculation_end_to_end(self):
        """
        Test Scenario 1: Percentage-Based Equity Calculation
        Given: Application is running with "Percentage-based" method selected
        When: User enters:
        - Symbol: "AAPL"
        - Account Size: $10,000
        - Risk %: 2%
        - Entry Price: $150
        - Stop Loss: $145

        Then: Clicking Calculate shows:
        - Method Used: Percentage
        - Calculated Shares: 40
        - Estimated Risk: $200.00
        - Risk Amount: $200.00
        """
        # Given
        app = RiskCalculatorApp(self.root)

        # Ensure we're on the equity tab and percentage method is selected
        equity_tab = app.equity_tab
        equity_controller = app.equity_controller

        # Select percentage-based method
        equity_controller.set_risk_method(
            equity_controller.current_risk_method.PERCENTAGE
        )

        # When - Enter the test data
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('2.0')
        equity_controller.tk_vars['entry_price'].set('150')
        equity_controller.tk_vars['stop_loss_price'].set('145')

        # Click Calculate
        equity_controller.calculate_position()

        # Then
        result = equity_controller.calculation_result

        assert result is not None
        assert result.is_success is True
        assert result.position_size == 40  # (10000 * 0.02) / (150 - 145) = 40
        assert result.estimated_risk == Decimal('200.00')
        assert result.risk_method_used.value == 'percentage'

        # Check UI displays the results correctly
        result_text = equity_tab.widgets['result_text'].get('1.0', tk.END)
        assert 'Percentage' in result_text
        assert '40' in result_text
        assert '200.00' in result_text

    def test_percentage_method_validation_errors(self):
        """Test percentage method with validation errors"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # When - Enter invalid data (risk percentage too high)
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('6.0')  # Too high
        equity_controller.tk_vars['entry_price'].set('150')
        equity_controller.tk_vars['stop_loss_price'].set('145')

        # Click Calculate
        equity_controller.calculate_position()

        # Then
        # Should have validation errors
        assert equity_controller.has_errors is True
        # Result should be None or unsuccessful
        result = equity_controller.calculation_result
        assert result is None or result.is_success is False

    def test_percentage_method_stop_loss_direction_validation(self):
        """Test stop loss direction validation for percentage method"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # When - Enter invalid stop loss (above entry for long position)
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('2.0')
        equity_controller.tk_vars['entry_price'].set('150')
        equity_controller.tk_vars['stop_loss_price'].set('155')  # Above entry
        equity_controller.trade.trade_direction = 'LONG'

        # Click Calculate
        equity_controller.calculate_position()

        # Then
        # Should have validation errors
        assert equity_controller.has_errors is True

    def test_percentage_method_clear_functionality(self):
        """Test clear functionality preserves percentage method selection"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # Enter data and calculate
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('2.0')
        equity_controller.calculate_position()

        # When - Clear inputs
        equity_controller.clear_inputs()

        # Then
        # Inputs should be cleared
        assert equity_controller.tk_vars['symbol'].get() == ''
        assert equity_controller.tk_vars['account_size'].get() == ''

        # Method selection should be preserved
        assert equity_controller.current_risk_method.value == 'percentage'

        # Results should be cleared
        assert equity_controller.calculation_result is None

    def test_percentage_method_real_time_validation(self):
        """Test real-time validation for percentage method fields"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # When - Enter invalid risk percentage
        equity_controller.tk_vars['risk_percentage'].set('10.0')  # Too high

        # Trigger validation (would normally happen via trace callback)
        equity_controller._on_field_change('risk_percentage')

        # Then
        # Should show validation error
        assert 'risk_percentage' in equity_controller.validation_result.field_errors

    def test_percentage_method_cross_platform_behavior(self):
        """Test percentage method works consistently across platforms"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # When - Use decimal values that might behave differently on different platforms
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000.50')
        equity_controller.tk_vars['risk_percentage'].set('2.5')
        equity_controller.tk_vars['entry_price'].set('150.75')
        equity_controller.tk_vars['stop_loss_price'].set('145.25')

        equity_controller.calculate_position()

        # Then
        result = equity_controller.calculation_result
        assert result is not None
        assert result.is_success is True

        # Should use Decimal arithmetic for precision
        assert isinstance(result.estimated_risk, Decimal)
        assert isinstance(result.position_size, (int, Decimal))

    def test_percentage_method_performance_requirement(self):
        """Test percentage calculation meets <100ms performance requirement"""
        import time

        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('2.0')
        equity_controller.tk_vars['entry_price'].set('150')
        equity_controller.tk_vars['stop_loss_price'].set('145')

        # When - Measure calculation time
        start_time = time.time()
        equity_controller.calculate_position()
        end_time = time.time()

        # Then
        calculation_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert calculation_time < 100  # Must be under 100ms

        # Result should still be correct
        result = equity_controller.calculation_result
        assert result.is_success is True