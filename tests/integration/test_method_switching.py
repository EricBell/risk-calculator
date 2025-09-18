import pytest
import tkinter as tk
from risk_calculator.main import RiskCalculatorApp
from risk_calculator.models.risk_method import RiskMethod


class TestMethodSwitchingIntegration:
    """Integration test for risk method switching UI - from quickstart.md scenario 4"""

    def setup_method(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def teardown_method(self):
        if self.root:
            self.root.destroy()

    def test_risk_method_switching_ui_behavior(self):
        """
        Test Scenario 4: Risk Method Switching
        Given: User has data entered for percentage method
        When: User switches to "Fixed Amount" method
        Then: UI shows fixed amount field and hides percentage field, calculation clears
        """
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_tab = app.equity_tab

        # Start with percentage method and enter data
        equity_controller.set_risk_method(RiskMethod.PERCENTAGE)
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['risk_percentage'].set('2.0')

        # When - Switch to fixed amount method
        equity_controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

        # Then
        # Fixed amount field should now be visible
        assert equity_tab.widgets['fixed_risk_entry'].winfo_manager() == 'grid'
        # Percentage field should be hidden
        assert equity_tab.widgets['risk_percentage_entry'].winfo_manager() == ''
        # Calculation should be cleared
        assert equity_controller.calculation_result is None

    def test_method_switching_preserves_common_fields(self):
        """Test common fields are preserved when switching methods"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller

        # Enter common data in percentage method
        equity_controller.set_risk_method(RiskMethod.PERCENTAGE)
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['entry_price'].set('150')

        # When - Switch to level-based method
        equity_controller.set_risk_method(RiskMethod.LEVEL_BASED)

        # Then - Common fields preserved
        assert equity_controller.tk_vars['symbol'].get() == 'AAPL'
        assert equity_controller.tk_vars['account_size'].get() == '10000'
        assert equity_controller.tk_vars['entry_price'].get() == '150'