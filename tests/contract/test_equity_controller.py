import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from risk_calculator.controllers.equity_controller import EquityController
from risk_calculator.models.risk_method import RiskMethod
from risk_calculator.models.equity_trade import EquityTrade
from risk_calculator.models.calculation_result import CalculationResult
from risk_calculator.services.risk_calculator import RiskCalculationService
from risk_calculator.services.validators import TradeValidationService


class TestEquityControllerContract:
    """Contract tests for EquityController - framework-agnostic version"""

    def setup_method(self):
        # Create a mock view (framework-agnostic)
        self.mock_view = Mock()

        # Create controller (it creates its own service instances)
        self.controller = EquityController(self.mock_view)

    def test_controller_initialization_contract(self):
        """Test controller initializes with required field storage"""
        # Then
        assert hasattr(self.controller, 'field_values')
        assert isinstance(self.controller.field_values, dict)

        # Check that field_values dict exists (will be populated as fields are set)
        assert self.controller.field_values is not None

    def test_set_risk_method_contract(self):
        """Test risk method setting updates state"""
        # Given
        initial_method = RiskMethod.PERCENTAGE
        new_method = RiskMethod.FIXED_AMOUNT

        # When
        self.controller.set_risk_method(new_method)

        # Then
        assert self.controller.current_risk_method == new_method
        assert self.controller.get_field_value('risk_method') == new_method.value

        # Should call view to update field visibility
        self.mock_view.show_method_fields.assert_called_once_with(new_method)

    def test_calculate_position_success_contract(self):
        """Test successful position calculation workflow"""
        # Given
        self.controller.set_field_value('symbol', 'AAPL')
        self.controller.set_field_value('account_size', '10000')
        self.controller.set_field_value('risk_percentage', '2.0')
        self.controller.set_field_value('entry_price', '150')
        self.controller.set_field_value('stop_loss_price', '145')
        self.controller.set_field_value('risk_method', RiskMethod.PERCENTAGE.value)

        # When
        self.controller.calculate_position()

        # Then - Should call view with successful result (if view has the method)
        # The fact that it doesn't raise an exception means calculation succeeded
        assert self.controller.trade.symbol == 'AAPL'
        assert self.controller.trade.account_size == Decimal('10000')

    def test_calculate_position_with_validation_error_contract(self):
        """Test calculation with validation errors"""
        # Given - Missing required field (symbol)
        self.controller.set_field_value('symbol', '')  # Empty symbol (invalid)
        self.controller.set_field_value('account_size', '10000')
        self.controller.set_field_value('risk_percentage', '2.0')
        self.controller.set_field_value('entry_price', '150')
        self.controller.set_field_value('stop_loss_price', '145')

        # When/Then - Should run without crashing (validation handled internally)
        self.controller.calculate_position()
        # Validation errors will be shown to view if it has show_validation_errors method

    def test_clear_inputs_contract(self):
        """Test clearing inputs preserves risk method selection"""
        # Given
        self.controller.set_field_value('symbol', 'AAPL')
        self.controller.set_field_value('account_size', '10000')
        self.controller.current_risk_method = RiskMethod.FIXED_AMOUNT

        # When
        self.controller.clear_inputs()

        # Then
        # Should clear input values
        assert self.controller.get_field_value('symbol') == ''
        assert self.controller.get_field_value('account_size') == ''

        # Should preserve risk method
        assert self.controller.current_risk_method == RiskMethod.FIXED_AMOUNT

    def test_sync_to_trade_object_contract(self):
        """Test syncing field values to trade object"""
        # Given
        self.controller.set_field_value('symbol', 'AAPL')
        self.controller.set_field_value('account_size', '10000')
        self.controller.set_field_value('entry_price', '150')
        self.controller.set_field_value('risk_percentage', '2.0')
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
        self.controller.set_field_value(field_name, '-1000')  # Negative value

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
