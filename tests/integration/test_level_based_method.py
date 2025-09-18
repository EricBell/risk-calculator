import pytest
import tkinter as tk
from decimal import Decimal
from risk_calculator.main import RiskCalculatorApp
from risk_calculator.models.risk_method import RiskMethod


class TestLevelBasedMethodIntegration:
    """Integration test for level-based risk calculation - from quickstart.md scenario 3"""

    def setup_method(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def teardown_method(self):
        if self.root:
            self.root.destroy()

    def test_level_based_risk_calculation_end_to_end(self):
        """
        Test Scenario 3: Level-Based Risk Calculation
        Given: Application is running
        When: User selects "Level-based" method and enters:
        - Symbol: "AAPL"
        - Account Size: $10,000
        - Entry Price: $50
        - Support/Resistance: $47

        Then: Clicking Calculate shows:
        - Method Used: Level Based
        - Calculated Shares: 66
        - Estimated Risk: $198.00
        - Risk Amount: $200.00 (2% default)
        """
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.LEVEL_BASED)

        # When
        equity_controller.tk_vars['symbol'].set('AAPL')
        equity_controller.tk_vars['account_size'].set('10000')
        equity_controller.tk_vars['entry_price'].set('50')
        equity_controller.tk_vars['support_resistance_level'].set('47')
        equity_controller.trade.trade_direction = 'LONG'

        equity_controller.calculate_position()

        # Then
        result = equity_controller.calculation_result
        assert result.is_success is True
        assert result.position_size == 66  # (10000 * 0.02) / (50 - 47) = 66.67 -> 66
        assert result.estimated_risk == Decimal('198.00')
        assert result.risk_method_used == RiskMethod.LEVEL_BASED

    def test_level_based_ui_field_visibility(self):
        """Test UI shows correct fields for level-based method"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_tab = app.equity_tab
        equity_controller = app.equity_controller

        # When
        equity_controller.set_risk_method(RiskMethod.LEVEL_BASED)

        # Then
        assert equity_tab.widgets['level_entry'].winfo_manager() == 'grid'
        assert equity_tab.widgets['stop_loss_entry'].winfo_manager() == ''
        assert equity_tab.widgets['risk_percentage_entry'].winfo_manager() == ''

    def test_level_based_direction_validation(self):
        """Test support/resistance level direction validation"""
        # Given
        app = RiskCalculatorApp(self.root)
        equity_controller = app.equity_controller
        equity_controller.set_risk_method(RiskMethod.LEVEL_BASED)

        # When - Invalid: support level above entry for long position
        equity_controller.tk_vars['entry_price'].set('50')
        equity_controller.tk_vars['support_resistance_level'].set('55')  # Above entry
        equity_controller.trade.trade_direction = 'LONG'

        equity_controller.calculate_position()

        # Then
        assert equity_controller.has_errors is True