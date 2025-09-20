"""Base controller with common functionality for all controllers."""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from ..models.validation_result import ValidationResult
from ..models.risk_method import RiskMethod


class BaseController(ABC):
    """Base controller with common functionality for all asset controllers."""

    def __init__(self, view):
        """Initialize base controller with view reference."""
        self.view = view
        self.is_busy: bool = False
        self.has_errors: bool = False
        self.validation_result: Optional[ValidationResult] = None
        self.calculation_result: Optional[Any] = None  # Store last calculation result
        self.current_risk_method: RiskMethod = RiskMethod.PERCENTAGE  # Default method

        # Initialize after subclass sets up tk_vars
        self._setup_view_bindings()

    @abstractmethod
    def _setup_view_bindings(self) -> None:
        """Setup Tkinter variable bindings and event handlers."""
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        pass

    def set_risk_method(self, method: RiskMethod) -> None:
        """Change the risk calculation method and update UI."""
        if not self._is_method_supported(method):
            # Show error and revert to previous method
            self._show_unsupported_method_error(method)
            return

        # Update method
        old_method = self.current_risk_method
        self.current_risk_method = method

        # Update Tkinter variable if it exists
        if hasattr(self, 'tk_vars') and 'risk_method' in self.tk_vars:
            self.tk_vars['risk_method'].set(method.value)

        # Update UI field visibility
        if hasattr(self.view, 'show_method_fields'):
            self.view.show_method_fields(method)

        # Clear calculation result and validation errors
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Notify view of method change
        self._on_method_changed(old_method, method)

    def clear_inputs(self) -> None:
        """Clear all input fields while preserving risk method selection."""
        if hasattr(self, 'tk_vars'):
            # Clear all variables except risk_method
            for var_name, var in self.tk_vars.items():
                if var_name != 'risk_method':
                    var.set('')

        # Reset trade object to defaults
        self._reset_trade_object()

        # Clear results and validation
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Update view
        if hasattr(self.view, 'clear_all_inputs'):
            self.view.clear_all_inputs()

    def _on_field_change(self, var_name: str, *args) -> None:
        """Handle Tkinter variable change for real-time validation."""
        if not hasattr(self, 'tk_vars') or var_name not in self.tk_vars:
            return

        # Get current value
        current_value = self.tk_vars[var_name].get()

        # Perform real-time validation
        error_message = self._validate_single_field(var_name, current_value)

        # Update field error display
        if error_message:
            self._show_field_error(var_name, error_message)
        else:
            self._clear_field_error(var_name)

        # Update overall validation status
        self._update_validation_status()

        # Update calculate button state
        self._update_calculate_button_state()

    def _validate_single_field(self, field_name: str, value: str) -> Optional[str]:
        """Validate a single field and return error message if invalid."""
        if hasattr(self, 'realtime_validator'):
            return self.realtime_validator.validate_field(
                field_name, value, self._get_trade_type(), self.trade
            )
        return None

    def _show_field_error(self, field_name: str, error_message: str) -> None:
        """Show error for a specific field."""
        if hasattr(self.view, 'show_validation_errors'):
            self.view.show_validation_errors({field_name: error_message})

    def _clear_field_error(self, field_name: str) -> None:
        """Clear error for a specific field."""
        if hasattr(self.view, 'clear_field_error'):
            self.view.clear_field_error(field_name)

    def _clear_validation_errors(self) -> None:
        """Clear all validation errors."""
        self.has_errors = False
        self.validation_result = None

        if hasattr(self.view, 'show_validation_errors'):
            self.view.show_validation_errors({})

    def _clear_calculation_result(self) -> None:
        """Clear calculation results."""
        self.calculation_result = None
        # Clear results display in view if available
        if hasattr(self.view, 'clear_results'):
            self.view.clear_results()

    def _update_validation_status(self) -> None:
        """Update overall validation status based on current field errors."""
        # Check all fields for errors by validating them
        self.has_errors = False
        for field_name, var in self.tk_vars.items():
            error_message = self._validate_single_field(field_name, var.get())
            if error_message:
                self.has_errors = True
                break

    def _update_calculate_button_state(self) -> None:
        """Enable/disable calculate button based on validation status."""
        if hasattr(self.view, 'set_calculate_button_enabled'):
            enabled = not self.has_errors and self._are_required_fields_filled()
            self.view.set_calculate_button_enabled(enabled)

    def _are_required_fields_filled(self) -> bool:
        """Check if all required fields for current method are filled."""
        if not hasattr(self, 'tk_vars'):
            return False

        required_fields = self.get_required_fields()
        for field_name in required_fields:
            if field_name in self.tk_vars:
                value = self.tk_vars[field_name].get().strip()
                if not value:
                    return False

        return True

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if the risk method is supported by this asset type."""
        # Default: all methods supported (overridden in subclasses)
        return True

    def _show_unsupported_method_error(self, method: RiskMethod) -> None:
        """Show error message for unsupported risk method."""
        asset_type = self.__class__.__name__.replace('Controller', '').lower()
        error_msg = f"{method.value.replace('_', ' ').title()} method not supported for {asset_type} trading"

        if hasattr(self.view, 'show_validation_errors'):
            self.view.show_validation_errors({'risk_method': error_msg})

    def _get_trade_type(self) -> str:
        """Get the trade type string for validation purposes."""
        # Extract from class name: EquityController -> equity
        return self.__class__.__name__.replace('Controller', '').lower()

    def _on_method_changed(self, old_method: RiskMethod, new_method: RiskMethod) -> None:
        """Handle method change notifications."""
        # Can be overridden by subclasses for additional behavior
        pass

    def _reset_trade_object(self) -> None:
        """Reset trade object to defaults (implemented by subclasses)."""
        pass

    def clear_inputs(self) -> None:
        """Clear all input fields except risk method selection."""
        if hasattr(self, 'tk_vars'):
            for field_name, var in self.tk_vars.items():
                if field_name != 'risk_method':  # Preserve risk method selection
                    var.set('')

        # Clear calculation result and validation errors
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Reset trade object
        self._reset_trade_object()

        # Clear view inputs if available
        if hasattr(self.view, 'clear_all_inputs'):
            self.view.clear_all_inputs()

    def set_busy_state(self, is_busy: bool) -> None:
        """Set busy state and update UI."""
        self.is_busy = is_busy

        if hasattr(self.view, 'set_busy_state'):
            self.view.set_busy_state(is_busy)

    @abstractmethod
    def calculate_position(self) -> None:
        """Calculate position size (implemented by subclasses)."""
        pass

    @abstractmethod
    def _sync_to_trade_object(self) -> None:
        """Sync Tkinter variables to trade object (implemented by subclasses)."""
        pass