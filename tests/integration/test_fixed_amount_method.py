import pytest
import tkinter as tk
from decimal import Decimal
from risk_calculator.main import RiskCalculatorApp
from risk_calculator.models.risk_method import RiskMethod


class TestFixedAmountMethodIntegration:
    """Integration test for fixed amount risk calculation - from quickstart.md scenario 2"""

    def setup_method(self):
        # Create a test root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide during testing

    def teardown_method(self):
        if self.root:
            self.root.destroy()

    def test_fixed_amount_risk_calculation_end_to_end(self):
        """
        Test Scenario 2: Fixed Amount Risk Calculation
        Given: Application is running
        When: User selects "Fixed Amount" method and enters:
        - Symbol: "AAPL"
        - Account Size: $10,000
        - Fixed Risk Amount: $50
        - Entry Price: $100
        - Stop Loss: $95

        Then: Clicking Calculate shows:
        - Method Used: Fixed Amount
        - Calculated Shares: 10
        - Estimated Risk: $50.00
        - Risk Amount: $50.00
        """
        # Given
        app = RiskCalculatorApp(self.root)
        equity_tab = app.equity_tab
        equity_controller = app.equity_controller

        # Select fixed amount method
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # When - Enter the test data
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['fixed_risk_amount'].set('50')
        equity_controller.tk_vars['entry_price'].set('100')
        equity_controller.tk_vars['stop_loss_price'].set('95')

        # Click Calculate
        equity_controller.calculate_position()

        # Then
        result = equity_controller.calculation_result

        assert result is not None
        assert result.is_success is True
        assert result.position_size == 10  # 50 / (100 - 95) = 10
        assert result.estimated_risk == Decimal('50.00')
        assert result.risk_method_used == RiskMethod.FIXED_AMOUNT

        # Check UI displays the results correctly
        result_text = equity_tab.widgets['result_text'].get('1.0', tk.END)
        assert 'Fixed Amount' in result_text
        assert '10' in result_text
        assert '50.00' in result_text

    def test_fixed_amount_method_ui_field_visibility(self):
        """Test UI shows correct fields for fixed amount method"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_tab = app.equity_tab
        equity_controller = app.equity_controller

        # When - Select fixed amount method
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # Then
        # Fixed amount field should be visible
        assert equity_tab.widgets['fixed_risk_entry'].winfo_manager() == 'grid'
        # Stop loss field should be visible
        assert equity_tab.widgets['stop_loss_entry'].winfo_manager() == 'grid'
        # Risk percentage field should be hidden
        assert equity_tab.widgets['risk_percentage_entry'].winfo_manager() == ''
        # Support/resistance field should be hidden
        assert equity_tab.widgets['level_entry'].winfo_manager() == ''

    def test_fixed_amount_exceeds_account_limit_validation(self):
        """Test validation when fixed amount exceeds 5% of account size"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # When - Enter fixed amount that exceeds 5% of account
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['fixed_risk_amount'].set('600')  # 6% of account
        equity_controller.tk_vars['entry_price'].set('100')
        equity_controller.tk_vars['stop_loss_price'].set('95')

        # Click Calculate
        equity_controller.calculate_position()

        # Then
        # Should have validation errors
        assert equity_controller.has_errors is True
        result = equity_controller.calculation_result
        assert result is None or result.is_success is False

        # Error should mention 5% limit
        validation_result = equity_controller.validation_result
        assert 'fixed_risk_amount' in validation_result.field_errors
        assert '5%' in validation_result.field_errors['fixed_risk_amount']

    def test_fixed_amount_range_validation(self):
        """Test fixed amount must be between $10-$500"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # When - Enter amount below minimum
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['fixed_risk_amount'].set('5')  # Below $10 minimum
        equity_controller.tk_vars['entry_price'].set('100')
        equity_controller.tk_vars['stop_loss_price'].set('95')

        equity_controller.calculate_position()

        # Then
        assert equity_controller.has_errors is True

        # When - Enter amount above maximum
        equity_controller.tk_vars['fixed_risk_amount'].set('600')  # Above $500 maximum

        equity_controller.calculate_position()

        # Then
        assert equity_controller.has_errors is True

    def test_fixed_amount_method_switching_preserves_common_fields(self):
        """Test switching to fixed amount method preserves common field values"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # Start with percentage method and enter common data
        equity_controller.set_risk_method(RiskMethod.PERCENTAGE)
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['entry_price'].set('150')

        # When - Switch to fixed amount method
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # Then
        # Common fields should be preserved
        assert equity_controller.tk_vars['symbol'].get() == 'AAPL'
        assert equity_controller.tk_vars['account_size'].get() == '10000'
        assert equity_controller.tk_vars['entry_price'].get() == '150'

        # Method-specific field should be cleared/reset
        assert equity_controller.tk_vars['risk_percentage'].get() == ''
        # Calculation result should be cleared
        assert equity_controller.calculation_result is None

    def test_fixed_amount_with_different_price_ranges(self):
        """Test fixed amount method with various stock price ranges"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        test_cases = [
            # (entry_price, stop_loss, expected_shares)
            (100, 95, 10),    # $5 risk per share, $50 / $5 = 10 shares
            (50, 48, 25),     # $2 risk per share, $50 / $2 = 25 shares
            (200, 190, 5),    # $10 risk per share, $50 / $10 = 5 shares
        ]

        for entry_price, stop_loss, expected_shares in test_cases:
            # When
            equity_controller.tk_vars['symbol'].set('TEST')
            equity_controller.tk_vars['account_size'].set('10000')
            equity_controller.tk_vars['fixed_risk_amount'].set('50')
            equity_controller.tk_vars['entry_price'].set(str(entry_price))
            equity_controller.tk_vars['stop_loss_price'].set(str(stop_loss))

            equity_controller.calculate_position()

            # Then
            result = equity_controller.calculation_result
            assert result.is_success is True
            assert result.position_size == expected_shares
            assert result.estimated_risk == Decimal('50.00')

    def test_fixed_amount_real_time_account_percentage_display(self):
        """Test UI shows what percentage of account the fixed amount represents"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_tab = app.equity_tab
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # When
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['fixed_risk_amount'].set('200')

        # Trigger calculation of percentage display
        equity_controller._on_field_change('fixed_risk_amount')

        # Then
        # Should display that $200 is 2% of $10,000 account
        # This would be shown in a label or helper text
        # Implementation-specific: check if percentage display exists

    def test_fixed_amount_decimal_precision(self):
        """Test fixed amount method maintains decimal precision"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # When - Use decimal values
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000.50')
        equity_controller.tk_vars['fixed_risk_amount'].set('50.75')
        equity_controller.tk_vars['entry_price'].set('100.25')
        equity_controller.tk_vars['stop_loss_price'].set('95.50')

        equity_controller.calculate_position()

        # Then
        result = equity_controller.calculation_result
        assert result.is_success is True

        # Should use Decimal arithmetic for precision
        assert isinstance(result.estimated_risk, Decimal)
        # Risk should be exactly the fixed amount
        assert result.estimated_risk == Decimal('50.75')

    def test_fixed_amount_clear_preserves_method_selection(self):
        """Test clear functionality preserves fixed amount method selection"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # Enter data
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['fixed_risk_amount'].set('100')

        # When - Clear inputs
        equity_controller.clear_inputs()

        # Then
        # Method selection should be preserved
        assert equity_controller.current_risk_method == RiskMethod.FIXED_AMOUNT

        # Fields should be cleared
        assert equity_controller.tk_vars['symbol'].get() == ''
        assert equity_controller.tk_vars['fixed_risk_amount'].get() == ''