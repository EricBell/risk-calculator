"""Equity controller with risk method switching logic and trade management."""

from decimal import Decimal
from typing import Optional, Dict, List
from .base_controller import BaseController
from ..models.equity_trade import EquityTrade
from ..models.risk_method import RiskMethod
from ..models.validation_result import ValidationResult
from ..models.calculation_result import CalculationResult
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService
from ..services.realtime_validator import RealTimeValidationService


class EquityController(BaseController):
    """Controller for equity trading with all three risk methods supported."""

    def __init__(self, view):
        # Initialize services
        self.risk_calculator = RiskCalculationService()
        self.trade_validator = TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)

        # Initialize trade object
        self.trade = EquityTrade()

        # Call parent constructor first
        super().__init__(view)

        # Initialize field values with defaults
        self.field_values = {
            'account_size': '',
            'risk_method': RiskMethod.PERCENTAGE.value,
            'risk_percentage': '',
            'fixed_risk_amount': '',
            'symbol': '',
            'entry_price': '',
            'stop_loss_price': '',
            'support_resistance_level': '',
            'trade_direction': 'LONG'
        }

    def _setup_view_bindings(self) -> None:
        """Setup view bindings and event handlers."""
        # View will call set_field_value which triggers validation
        pass

    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        base_fields = ['account_size', 'symbol', 'entry_price', 'trade_direction']

        if self.current_risk_method == RiskMethod.PERCENTAGE:
            return base_fields + ['risk_percentage', 'stop_loss_price']
        elif self.current_risk_method == RiskMethod.FIXED_AMOUNT:
            return base_fields + ['fixed_risk_amount', 'stop_loss_price']
        elif self.current_risk_method == RiskMethod.LEVEL_BASED:
            return base_fields + ['support_resistance_level']

        return base_fields

    def calculate_position(self) -> None:
        """Calculate equity position size based on current inputs."""
        if self.is_busy:
            return

        self.set_busy_state(True)

        try:
            # Sync UI to trade object
            self._sync_to_trade_object()

            # Validate trade
            validation_result = self.trade_validator.validate_equity_trade(self.trade)

            if not validation_result.is_valid:
                self._show_validation_errors(validation_result)
                return

            # Perform calculation
            calculation_result = self.risk_calculator.calculate_equity_position(self.trade)

            # Show results
            if calculation_result.success:
                self._show_calculation_result(calculation_result)

                # Show warnings if any
                if calculation_result.warnings:
                    self._show_warnings(calculation_result.warnings)
            else:
                self._show_calculation_error(calculation_result.error_message)

        except Exception as e:
            self._show_calculation_error(f"Calculation failed: {str(e)}")

        finally:
            self.set_busy_state(False)

    def _sync_to_trade_object(self) -> None:
        """Sync field values to equity trade object."""
        try:
            # Common fields
            account_size_str = self.field_values.get('account_size', '').strip()
            if account_size_str:
                self.trade.account_size = Decimal(account_size_str)

            self.trade.risk_method = RiskMethod(self.field_values.get('risk_method', RiskMethod.PERCENTAGE.value))
            self.trade.symbol = self.field_values.get('symbol', '').strip()
            self.trade.trade_direction = self.field_values.get('trade_direction', 'LONG')

            # Entry price
            entry_price_str = self.field_values.get('entry_price', '').strip()
            if entry_price_str:
                self.trade.entry_price = Decimal(entry_price_str)

            # Method-specific fields
            if self.trade.risk_method == RiskMethod.PERCENTAGE:
                risk_pct_str = self.field_values.get('risk_percentage', '').strip()
                if risk_pct_str:
                    self.trade.risk_percentage = Decimal(risk_pct_str)

                stop_loss_str = self.field_values.get('stop_loss_price', '').strip()
                if stop_loss_str:
                    self.trade.stop_loss_price = Decimal(stop_loss_str)

            elif self.trade.risk_method == RiskMethod.FIXED_AMOUNT:
                fixed_amount_str = self.field_values.get('fixed_risk_amount', '').strip()
                if fixed_amount_str:
                    self.trade.fixed_risk_amount = Decimal(fixed_amount_str)

                stop_loss_str = self.field_values.get('stop_loss_price', '').strip()
                if stop_loss_str:
                    self.trade.stop_loss_price = Decimal(stop_loss_str)

            elif self.trade.risk_method == RiskMethod.LEVEL_BASED:
                level_str = self.field_values.get('support_resistance_level', '').strip()
                if level_str:
                    self.trade.support_resistance_level = Decimal(level_str)

        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid input data: {str(e)}")

    def _reset_trade_object(self) -> None:
        """Reset trade object to defaults."""
        self.trade = EquityTrade()
        self.trade.risk_method = self.current_risk_method

    def _validate_single_field(self, field_name: str, value: str) -> Optional[str]:
        """Validate a single field using real-time validator."""
        return self.realtime_validator.validate_field(
            field_name, value, "equity", self.trade
        )

    def _clear_calculation_result(self) -> None:
        """Clear calculation results in the view."""
        if hasattr(self.view, 'clear_results'):
            self.view.clear_results()

    def _show_validation_errors(self, validation_result: ValidationResult) -> None:
        """Show validation errors in the view."""
        if hasattr(self.view, 'show_validation_errors'):
            self.view.show_validation_errors(validation_result.field_errors)

        if validation_result.warnings and hasattr(self.view, 'show_warnings'):
            self.view.show_warnings(validation_result.warnings)

    def _show_calculation_result(self, result: CalculationResult) -> None:
        """Show calculation result in the view."""
        if hasattr(self.view, 'show_calculation_result'):
            self.view.show_calculation_result({
                'position_size': result.position_size,
                'estimated_risk': result.estimated_risk,
                'risk_method': result.risk_method.value,
                'position_value': result.position_size * self.trade.entry_price if self.trade.entry_price else 0
            })

    def _show_calculation_error(self, error_message: str) -> None:
        """Show calculation error in the view."""
        if hasattr(self.view, 'show_calculation_error'):
            self.view.show_calculation_error(error_message)

    def _show_warnings(self, warnings: List[str]) -> None:
        """Show warnings in the view."""
        if hasattr(self.view, 'show_warnings'):
            self.view.show_warnings(warnings)

    def _on_method_changed(self, old_method: RiskMethod, new_method: RiskMethod) -> None:
        """Handle risk method change for equity-specific behavior."""
        # Clear method-specific fields when switching
        method_fields = {
            RiskMethod.PERCENTAGE: ['risk_percentage', 'stop_loss_price'],
            RiskMethod.FIXED_AMOUNT: ['fixed_risk_amount', 'stop_loss_price'],
            RiskMethod.LEVEL_BASED: ['support_resistance_level']
        }

        # Clear old method fields
        if old_method in method_fields:
            for field in method_fields[old_method]:
                self.field_values[field] = ''

        # Update trade object
        self.trade.risk_method = new_method
        self._reset_method_specific_trade_fields(old_method)

    def _reset_method_specific_trade_fields(self, old_method: RiskMethod) -> None:
        """Reset method-specific fields in trade object."""
        if old_method == RiskMethod.PERCENTAGE:
            self.trade.risk_percentage = None
            self.trade.stop_loss_price = None
        elif old_method == RiskMethod.FIXED_AMOUNT:
            self.trade.fixed_risk_amount = None
            self.trade.stop_loss_price = None
        elif old_method == RiskMethod.LEVEL_BASED:
            self.trade.support_resistance_level = None

    def get_current_trade_data(self) -> Dict:
        """Get current trade data for debugging or export."""
        self._sync_to_trade_object()
        return {
            'symbol': self.trade.symbol,
            'account_size': float(self.trade.account_size),
            'risk_method': self.trade.risk_method.value,
            'entry_price': float(self.trade.entry_price) if self.trade.entry_price else None,
            'trade_direction': self.trade.trade_direction,
            'risk_percentage': float(self.trade.risk_percentage) if self.trade.risk_percentage else None,
            'fixed_risk_amount': float(self.trade.fixed_risk_amount) if self.trade.fixed_risk_amount else None,
            'stop_loss_price': float(self.trade.stop_loss_price) if self.trade.stop_loss_price else None,
            'support_resistance_level': float(self.trade.support_resistance_level) if self.trade.support_resistance_level else None
        }

    def load_trade_data(self, trade_data: Dict) -> None:
        """Load trade data into the controller (for session persistence)."""
        try:
            # Set risk method first
            if 'risk_method' in trade_data:
                risk_method = RiskMethod(trade_data['risk_method'])
                self.set_risk_method(risk_method)

            # Set other fields
            field_mapping = {
                'account_size': 'account_size',
                'symbol': 'symbol',
                'entry_price': 'entry_price',
                'trade_direction': 'trade_direction',
                'risk_percentage': 'risk_percentage',
                'fixed_risk_amount': 'fixed_risk_amount',
                'stop_loss_price': 'stop_loss_price',
                'support_resistance_level': 'support_resistance_level'
            }

            for data_key, field_name in field_mapping.items():
                if data_key in trade_data and trade_data[data_key] is not None:
                    value = str(trade_data[data_key])
                    self.set_field_value(field_name, value)

        except Exception as e:
            # If loading fails, reset to defaults
            self.clear_inputs()
            raise ValueError(f"Failed to load trade data: {str(e)}")