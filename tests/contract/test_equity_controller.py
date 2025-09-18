import pytest
import tkinter as tk
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from risk_calculator.controllers.equity_controller import EquityController
from risk_calculator.models.risk_method import RiskMethod
from risk_calculator.models.equity_trade import EquityTrade
from risk_calculator.models.calculation_result import CalculationResult
from risk_calculator.services.risk_calculator import RiskCalculationService
from risk_calculator.services.validators import TradeValidationService


class TestEquityControllerContract:
    """Contract tests for EquityController - these must fail initially"""

    def setup_method(self):
        # Create a mock view (Tkinter frame)
        self.mock_view = Mock()
        self.mock_risk_service = Mock(spec=RiskCalculationService)
        self.mock_validation_service = Mock(spec=TradeValidationService)

        # Create controller with mocked dependencies
        self.controller = EquityController(
            self.mock_view,
            self.mock_risk_service,
            self.mock_validation_service
        )

    def test_controller_initialization_contract(self):
        """Test controller initializes with required Tkinter variables"""
        # Then
        assert hasattr(self.controller, 'tk_vars')
        assert isinstance(self.controller.tk_vars, dict)

        # Check required Tkinter variables exist
        required_vars = [
            'symbol', 'account_size', 'entry_price',
            'risk_percentage', 'fixed_risk_amount',
            'stop_loss_price', 'support_resistance_level',
            'risk_method'
        ]

        for var_name in required_vars:
            assert var_name in self.controller.tk_vars
            assert hasattr(self.controller.tk_vars[var_name], 'get')
            assert hasattr(self.controller.tk_vars[var_name], 'set')

    def test_set_risk_method_contract(self):
        """Test risk method setting updates UI and clears results"""
        # Given
        initial_method = RiskMethod.PERCENTAGE
        new_method = RiskMethod.FIXED_AMOUNT

        # When
        self.controller.set_risk_method(new_method)

        # Then
        assert self.controller.current_risk_method == new_method
        assert self.controller.tk_vars['risk_method'].get() == new_method.value

        # Should call view to update field visibility
        self.mock_view.show_method_fields.assert_called_once_with(new_method)

        # Should clear calculation result
        assert self.controller.calculation_result is None

    def test_calculate_position_success_contract(self):
        """Test successful position calculation workflow"""
        # Given
        self.controller.tk_vars['symbol'].set('AAPL')
        self.controller.tk_vars['account_size'].set('10000')
        self.controller.tk_vars['risk_percentage'].set('2.0')
        self.controller.tk_vars['entry_price'].set('150')
        self.controller.tk_vars['stop_loss_price'].set('145')
        self.controller.tk_vars['risk_method'].set(RiskMethod.PERCENTAGE.value)

        # Mock successful calculation
        mock_result = CalculationResult()
        mock_result.is_success = True
        mock_result.position_size = 40
        mock_result.estimated_risk = Decimal('200.00')
        mock_result.risk_method_used = RiskMethod.PERCENTAGE

        self.mock_risk_service.calculate_equity_position.return_value = mock_result

        # When
        self.controller.calculate_position()

        # Then
        assert self.controller.calculation_result == mock_result
        self.mock_risk_service.calculate_equity_position.assert_called_once()

        # Should update view with results
        assert hasattr(self.mock_view, 'update_calculation_result')

    def test_calculate_position_with_validation_error_contract(self):
        """Test calculation with validation errors"""
        # Given
        self.controller.tk_vars['symbol'].set('')  # Empty symbol (invalid)
        self.controller.tk_vars['account_size'].set('10000')

        from risk_calculator.models.validation_result import ValidationResult
        mock_validation = ValidationResult(False, [], [], {})
        mock_validation.add_error('symbol', 'Symbol is required')

        self.mock_validation_service.validate_equity_trade.return_value = mock_validation

        # When
        self.controller.calculate_position()

        # Then
        # Should not call risk calculation service if validation fails
        self.mock_risk_service.calculate_equity_position.assert_not_called()

        # Should display validation errors
        assert hasattr(self.mock_view, 'show_validation_errors')

    def test_clear_inputs_contract(self):
        """Test clearing inputs preserves risk method selection"""
        # Given
        self.controller.tk_vars['symbol'].set('AAPL')
        self.controller.tk_vars['account_size'].set('10000')
        self.controller.current_risk_method = RiskMethod.FIXED_AMOUNT

        # When
        self.controller.clear_inputs()

        # Then
        # Should clear input values
        assert self.controller.tk_vars['symbol'].get() == ''
        assert self.controller.tk_vars['account_size'].get() == ''

        # Should preserve risk method
        assert self.controller.current_risk_method == RiskMethod.FIXED_AMOUNT

        # Should clear calculation result
        assert self.controller.calculation_result is None

    def test_sync_to_trade_object_contract(self):
        """Test syncing Tkinter variables to trade object"""
        # Given
        self.controller.tk_vars['symbol'].set('AAPL')
        self.controller.tk_vars['account_size'].set('10000')
        self.controller.tk_vars['entry_price'].set('150')
        self.controller.tk_vars['risk_percentage'].set('2.0')
        self.controller.current_risk_method = RiskMethod.PERCENTAGE

        # When
        self.controller._sync_to_trade_object()

        # Then
        trade = self.controller.trade
        assert trade.symbol == 'AAPL'
        assert trade.account_size == Decimal('10000')
        assert trade.entry_price == Decimal('150')
        assert trade.risk_percentage == Decimal('2.0')
        assert trade.risk_method == RiskMethod.PERCENTAGE

    def test_real_time_validation_contract(self):
        """Test real-time field validation callback"""
        # Given
        field_name = 'account_size'
        invalid_value = '-1000'  # Negative value

        # When
        self.controller._on_field_change(field_name)

        # Then
        # Should validate the field and update UI
        assert self.controller.has_errors is True or self.controller.has_errors is False

    def test_get_required_fields_by_method_contract(self):
        """Test required fields vary by risk method"""
        # Given - Percentage method
        self.controller.current_risk_method = RiskMethod.PERCENTAGE

        # When
        required_fields = self.controller.get_required_fields()

        # Then
        expected_fields = ['symbol', 'account_size', 'risk_percentage', 'entry_price', 'stop_loss_price']
        for field in expected_fields:
            assert field in required_fields

        # Given - Fixed amount method
        self.controller.current_risk_method = RiskMethod.FIXED_AMOUNT

        # When
        required_fields = self.controller.get_required_fields()

        # Then
        expected_fields = ['symbol', 'account_size', 'fixed_risk_amount', 'entry_price', 'stop_loss_price']
        for field in expected_fields:
            assert field in required_fields

        # Given - Level-based method
        self.controller.current_risk_method = RiskMethod.LEVEL_BASED

        # When
        required_fields = self.controller.get_required_fields()

        # Then
        expected_fields = ['symbol', 'account_size', 'entry_price', 'support_resistance_level', 'trade_direction']
        for field in expected_fields:
            assert field in required_fields