import pytest
import tkinter as tk
from risk_calculator.main import RiskCalculatorApp
from risk_calculator.models.risk_method import RiskMethod


class TestClearFunctionalityIntegration:
    """Integration test for clear functionality - from quickstart.md scenario 5"""

    def setup_method(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def teardown_method(self):
        if self.root:
            self.root.destroy()

    def test_clear_functionality_end_to_end(self):
        """
        Test Scenario 5: Clear Functionality
        Given: User has entered data and calculated results
        When: User clicks Clear button
        Then: All fields reset to default values, results area clears
        """
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_tab = app.equity_tab

        # Enter data and calculate
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['risk_percentage'].set('2.0')
        equity_controller.tk_vars['entry_price'].set('150')
        equity_controller.tk_vars['stop_loss_price'].set('145')
        equity_controller.calculate_position()

        # Verify we have results
        assert equity_controller.calculation_result is not None

        # When - Click clear
        equity_controller.clear_inputs()

        # Then
        # All input fields should be cleared
        assert equity_controller.tk_vars['symbol'].get() == ''
        assert equity_controller.tk_vars['account_size'].get() == ''
        assert equity_controller.tk_vars['risk_percentage'].get() == ''
        assert equity_controller.tk_vars['entry_price'].get() == ''
        assert equity_controller.tk_vars['stop_loss_price'].get() == ''

        # Results should be cleared
        assert equity_controller.calculation_result is None

        # Risk method should be preserved
        assert equity_controller.current_risk_method == RiskMethod.PERCENTAGE