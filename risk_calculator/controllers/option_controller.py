"""Option controller with level-based method disabled and contract calculations."""

import tkinter as tk
from decimal import Decimal
from typing import Optional, Dict, List
from .base_controller import BaseController
from ..models.option_trade import OptionTrade
from ..models.risk_method import RiskMethod
from ..models.validation_result import ValidationResult
from ..models.calculation_result import CalculationResult
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService
from ..services.realtime_validator import RealTimeValidationService


class OptionController(BaseController):
    """Controller for option trading with level-based method disabled."""

    def __init__(self, view, risk_calculator=None, trade_validator=None):
        # Initialize services (dependency injection or default creation)
        self.risk_calculator = risk_calculator or RiskCalculationService()
        self.trade_validator = trade_validator or TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)

        # Initialize trade object
        self.trade = OptionTrade()

        # Initialize Tkinter variables
        self.tk_vars: Dict[str, tk.StringVar] = {
            'account_size': tk.StringVar(),
            'risk_method': tk.StringVar(value=RiskMethod.PERCENTAGE.value),
            'risk_percentage': tk.StringVar(),
            'fixed_risk_amount': tk.StringVar(),
            'option_symbol': tk.StringVar(),
            'premium': tk.StringVar(),
            'contract_multiplier': tk.StringVar(value='100'),  # Standard options multiplier
            'trade_direction': tk.StringVar(value='LONG')
        }

        # Call parent constructor which will setup view bindings
        super().__init__(view)

    def _setup_view_bindings(self) -> None:
        """Setup Tkinter variable bindings and event handlers."""
        # Bind variable traces for real-time validation
        for var_name, var in self.tk_vars.items():
            var.trace_add('write', lambda *args, vn=var_name: self._on_field_change(vn))

    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        base_fields = ['account_size', 'option_symbol', 'premium', 'contract_multiplier', 'trade_direction']

        if self.current_risk_method == RiskMethod.PERCENTAGE:
            return base_fields + ['risk_percentage']
        elif self.current_risk_method == RiskMethod.FIXED_AMOUNT:
            return base_fields + ['fixed_risk_amount']
        elif self.current_risk_method == RiskMethod.LEVEL_BASED:
            # Level-based not supported for options
            return base_fields

        return base_fields

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if the risk method is supported by options."""
        return method != RiskMethod.LEVEL_BASED

    def calculate_position(self) -> None:
        """Calculate option position size based on current inputs."""
        if self.is_busy:
            return

        # Check if level-based method is selected (should be disabled in UI)
        if self.current_risk_method == RiskMethod.LEVEL_BASED:
            self._show_calculation_error("Level-based method not supported for options trading")
            return

        self.set_busy_state(True)

        try:
            # Sync UI to trade object
            self._sync_to_trade_object()

            # Validate trade
            validation_result = self.trade_validator.validate_option_trade(self.trade)

            if not validation_result.is_valid:
                self._show_validation_errors(validation_result)
                return

            # Perform calculation
            calculation_result = self.risk_calculator.calculate_option_position(self.trade)

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
        """Sync Tkinter variables to option trade object."""
        try:
            # Common fields
            account_size_str = self.tk_vars['account_size'].get().strip()
            if account_size_str:
                self.trade.account_size = Decimal(account_size_str)

            self.trade.risk_method = RiskMethod(self.tk_vars['risk_method'].get())
            self.trade.option_symbol = self.tk_vars['option_symbol'].get().strip()
            self.trade.trade_direction = self.tk_vars['trade_direction'].get()

            # Premium
            premium_str = self.tk_vars['premium'].get().strip()
            if premium_str:
                self.trade.premium = Decimal(premium_str)

            # Contract multiplier
            multiplier_str = self.tk_vars['contract_multiplier'].get().strip()
            if multiplier_str:
                self.trade.contract_multiplier = int(multiplier_str)

            # Method-specific fields
            if self.trade.risk_method == RiskMethod.PERCENTAGE:
                risk_pct_str = self.tk_vars['risk_percentage'].get().strip()
                if risk_pct_str:
                    self.trade.risk_percentage = Decimal(risk_pct_str)

            elif self.trade.risk_method == RiskMethod.FIXED_AMOUNT:
                fixed_amount_str = self.tk_vars['fixed_risk_amount'].get().strip()
                if fixed_amount_str:
                    self.trade.fixed_risk_amount = Decimal(fixed_amount_str)

        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid input data: {str(e)}")

    def _reset_trade_object(self) -> None:
        """Reset trade object to defaults."""
        self.trade = OptionTrade()
        self.trade.risk_method = self.current_risk_method

    def _validate_single_field(self, field_name: str, value: str) -> Optional[str]:
        """Validate a single field using real-time validator."""
        # Check for level-based method compatibility
        if field_name == 'risk_method' and value == RiskMethod.LEVEL_BASED.value:
            return "Level-based method not supported for options trading"

        return self.realtime_validator.validate_field(
            field_name, value, "option", self.trade
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
            total_premium_cost = result.position_size * self.trade.premium * self.trade.contract_multiplier
            self.view.show_calculation_result({
                'position_size': result.position_size,
                'estimated_risk': result.estimated_risk,
                'risk_method': result.risk_method.value,
                'total_premium_cost': total_premium_cost,
                'contracts': result.position_size,
                'premium_per_share': self.trade.premium,
                'contract_multiplier': self.trade.contract_multiplier
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
        """Handle risk method change for option-specific behavior."""
        # Prevent switching to level-based method
        if new_method == RiskMethod.LEVEL_BASED:
            # Revert to previous method
            if hasattr(self, 'tk_vars') and 'risk_method' in self.tk_vars:
                self.tk_vars['risk_method'].set(old_method.value)
            self.current_risk_method = old_method

            # Show error
            self._show_unsupported_method_error(new_method)
            return

        # Clear method-specific fields when switching
        method_fields = {
            RiskMethod.PERCENTAGE: ['risk_percentage'],
            RiskMethod.FIXED_AMOUNT: ['fixed_risk_amount']
        }

        # Clear old method fields
        if old_method in method_fields:
            for field in method_fields[old_method]:
                if field in self.tk_vars:
                    self.tk_vars[field].set('')

        # Update trade object
        self.trade.risk_method = new_method
        self._reset_method_specific_trade_fields(old_method)

    def _reset_method_specific_trade_fields(self, old_method: RiskMethod) -> None:
        """Reset method-specific fields in trade object."""
        if old_method == RiskMethod.PERCENTAGE:
            self.trade.risk_percentage = None
        elif old_method == RiskMethod.FIXED_AMOUNT:
            self.trade.fixed_risk_amount = None

    def get_current_trade_data(self) -> Dict:
        """Get current trade data for debugging or export."""
        self._sync_to_trade_object()
        return {
            'option_symbol': self.trade.option_symbol,
            'account_size': float(self.trade.account_size),
            'risk_method': self.trade.risk_method.value,
            'premium': float(self.trade.premium) if self.trade.premium else None,
            'contract_multiplier': self.trade.contract_multiplier,
            'trade_direction': self.trade.trade_direction,
            'risk_percentage': float(self.trade.risk_percentage) if self.trade.risk_percentage else None,
            'fixed_risk_amount': float(self.trade.fixed_risk_amount) if self.trade.fixed_risk_amount else None
        }

    def load_trade_data(self, trade_data: Dict) -> None:
        """Load trade data into the controller (for session persistence)."""
        try:
            # Set risk method first (but not level-based)
            if 'risk_method' in trade_data:
                risk_method = RiskMethod(trade_data['risk_method'])
                if risk_method != RiskMethod.LEVEL_BASED:
                    self.set_risk_method(risk_method)
                else:
                    # Default to percentage method if trying to load level-based
                    self.set_risk_method(RiskMethod.PERCENTAGE)

            # Set other fields
            field_mapping = {
                'account_size': 'account_size',
                'option_symbol': 'option_symbol',
                'premium': 'premium',
                'contract_multiplier': 'contract_multiplier',
                'trade_direction': 'trade_direction',
                'risk_percentage': 'risk_percentage',
                'fixed_risk_amount': 'fixed_risk_amount'
            }

            for data_key, var_name in field_mapping.items():
                if data_key in trade_data and trade_data[data_key] is not None:
                    value = str(trade_data[data_key])
                    if var_name in self.tk_vars:
                        self.tk_vars[var_name].set(value)

        except Exception as e:
            # If loading fails, reset to defaults
            self.clear_inputs()
            raise ValueError(f"Failed to load trade data: {str(e)}")

    def get_supported_risk_methods(self) -> List[RiskMethod]:
        """Get list of risk methods supported by options trading."""
        return [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]

    def is_level_based_available(self) -> bool:
        """Check if level-based method is available for this asset type."""
        return False