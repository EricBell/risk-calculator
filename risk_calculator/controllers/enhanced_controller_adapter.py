"""
Enhanced Controller Adapter.
Bridges enhanced services with existing controller architecture.
"""

import tkinter as tk
from typing import Dict, Optional, Any, List
from enum import Enum

# Import existing models and services
from risk_calculator.models.risk_method import RiskMethod
from risk_calculator.models.validation_result import ValidationResult

# Import enhanced services
from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
from risk_calculator.views.error_display import FieldErrorManager, ErrorDisplayConfig

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from validation_service import TradeType
except ImportError:
    # Fallback definition
    class TradeType(Enum):
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"


class EnhancedControllerAdapter:
    """Adapter to integrate enhanced services with existing controllers."""

    def __init__(self, base_controller, view):
        """
        Initialize adapter for an existing controller.

        Args:
            base_controller: Existing controller instance
            view: View instance
        """
        self.base_controller = base_controller
        self.view = view

        # Initialize enhanced services
        self.enhanced_validation = EnhancedValidationService()
        self.error_manager = FieldErrorManager(ErrorDisplayConfig())

        # Determine trade type from controller
        self.trade_type = self._determine_trade_type()

        # State tracking
        self.current_risk_method = "percentage"
        self.enhanced_validation_enabled = True

        # Setup integration
        self._setup_integration()

    def _determine_trade_type(self) -> TradeType:
        """Determine trade type from controller class name."""
        class_name = self.base_controller.__class__.__name__.lower()
        if "equity" in class_name:
            return TradeType.EQUITY
        elif "option" in class_name:
            return TradeType.OPTION
        elif "future" in class_name:
            return TradeType.FUTURE
        else:
            return TradeType.EQUITY  # Default

    def _setup_integration(self):
        """Setup integration between enhanced and existing services."""
        # Replace existing field change handler if possible
        if hasattr(self.base_controller, '_on_field_change'):
            self.original_field_change = self.base_controller._on_field_change
            self.base_controller._on_field_change = self._enhanced_field_change

        # Replace validation methods if possible
        if hasattr(self.base_controller, '_validate_single_field'):
            self.original_validate_field = self.base_controller._validate_single_field
            self.base_controller._validate_single_field = self._enhanced_validate_field

        # Setup error display integration
        self._setup_error_display_integration()

    def _setup_error_display_integration(self):
        """Setup error display integration with existing view."""
        try:
            # Register form fields with error manager
            if hasattr(self.base_controller, 'tk_vars'):
                for field_name, tk_var in self.base_controller.tk_vars.items():
                    # Create error label for this field
                    error_label = self.error_manager.create_error_label(self.view, field_name)

                    # Try to find the corresponding widget
                    widget = self._find_widget_for_field(field_name)
                    if widget:
                        self.error_manager.register_field(field_name, widget, error_label)
        except Exception:
            # Error display setup is not critical
            pass

    def _find_widget_for_field(self, field_name: str) -> Optional[tk.Widget]:
        """Find the widget associated with a field name."""
        # Common field name to widget attribute mappings
        widget_mappings = {
            'account_size': ['account_size_entry', 'account_entry'],
            'risk_percentage': ['risk_percentage_entry', 'percentage_entry'],
            'fixed_risk_amount': ['fixed_risk_amount_entry', 'fixed_amount_entry'],
            'entry_price': ['entry_price_entry', 'entry_entry'],
            'stop_loss_price': ['stop_loss_entry', 'stop_entry'],
            'premium': ['premium_entry'],
            'tick_value': ['tick_value_entry', 'tick_entry'],
            'support_resistance_level': ['level_entry', 'support_resistance_entry']
        }

        possible_names = widget_mappings.get(field_name, [field_name + '_entry'])

        for widget_name in possible_names:
            if hasattr(self.view, widget_name):
                return getattr(self.view, widget_name)

        return None

    def _enhanced_field_change(self, var_name: str, *args):
        """Enhanced field change handler with improved validation."""
        try:
            # Call original handler first
            if hasattr(self, 'original_field_change'):
                self.original_field_change(var_name, *args)

            # Enhanced validation if enabled
            if self.enhanced_validation_enabled:
                self._perform_enhanced_validation(var_name)

        except Exception:
            # Fall back to original behavior if enhanced validation fails
            if hasattr(self, 'original_field_change'):
                self.original_field_change(var_name, *args)

    def _enhanced_validate_field(self, field_name: str, value: str) -> Optional[str]:
        """Enhanced field validation using new validation service."""
        try:
            if self.enhanced_validation_enabled:
                # Use enhanced validation service
                validation_result = self.enhanced_validation.validate_field(
                    field_name, value, self.trade_type
                )

                # Update error display
                if validation_result.is_valid:
                    self.error_manager.hide_error(field_name)
                    return None
                else:
                    self.error_manager.show_error(field_name, validation_result.error_message)
                    return validation_result.error_message
            else:
                # Fall back to original validation
                if hasattr(self, 'original_validate_field'):
                    return self.original_validate_field(field_name, value)

        except Exception:
            # Fall back to original validation on error
            if hasattr(self, 'original_validate_field'):
                return self.original_validate_field(field_name, value)

        return None

    def _perform_enhanced_validation(self, field_name: str):
        """Perform enhanced validation for a specific field."""
        try:
            if not hasattr(self.base_controller, 'tk_vars'):
                return

            # Get current value
            if field_name not in self.base_controller.tk_vars:
                return

            current_value = self.base_controller.tk_vars[field_name].get()

            # Validate using enhanced service
            validation_result = self.enhanced_validation.validate_field(
                field_name, current_value, self.trade_type
            )

            # Update error display
            if validation_result.is_valid:
                self.error_manager.hide_error(field_name)
            else:
                self.error_manager.show_error(field_name, validation_result.error_message)

            # Update form-level validation
            self._update_form_validation()

        except Exception:
            # Enhanced validation failed, continue silently
            pass

    def _update_form_validation(self):
        """Update overall form validation state."""
        try:
            if not hasattr(self.base_controller, 'tk_vars'):
                return

            # Get all field values
            form_data = {}
            for field_name, tk_var in self.base_controller.tk_vars.items():
                form_data[field_name] = tk_var.get()

            # Validate entire form
            form_state = self.enhanced_validation.validate_form(form_data, self.trade_type)

            # Update button state if method exists
            if hasattr(self.view, 'set_calculate_button_enabled'):
                self.view.set_calculate_button_enabled(form_state.is_submittable)

        except Exception:
            # Form validation failed, continue silently
            pass

    def set_risk_method(self, risk_method: str):
        """
        Update risk method for enhanced validation.

        Args:
            risk_method: New risk method (percentage, fixed, level)
        """
        self.current_risk_method = risk_method

        # Re-validate form with new requirements if enhanced validation is enabled
        if self.enhanced_validation_enabled:
            self._update_form_validation()

    def enable_enhanced_validation(self, enabled: bool = True):
        """
        Enable or disable enhanced validation.

        Args:
            enabled: Whether to enable enhanced validation
        """
        self.enhanced_validation_enabled = enabled

        if enabled:
            # Perform immediate validation of all fields
            self._validate_all_fields()
        else:
            # Clear enhanced error displays
            self.error_manager.hide_all_errors()

    def _validate_all_fields(self):
        """Validate all current field values."""
        if not hasattr(self.base_controller, 'tk_vars'):
            return

        for field_name in self.base_controller.tk_vars:
            self._perform_enhanced_validation(field_name)

    def get_validation_state(self) -> Dict[str, Any]:
        """
        Get current validation state.

        Returns:
            Dict containing validation state information
        """
        try:
            if not hasattr(self.base_controller, 'tk_vars'):
                return {"has_errors": False, "error_count": 0}

            # Get all field values
            form_data = {}
            for field_name, tk_var in self.base_controller.tk_vars.items():
                form_data[field_name] = tk_var.get()

            # Validate form
            form_state = self.enhanced_validation.validate_form(form_data, self.trade_type)

            return {
                "has_errors": form_state.has_errors,
                "is_submittable": form_state.is_submittable,
                "error_count": len([f for f in form_state.field_states.values() if not f.is_valid]),
                "error_fields": [f.field_name for f in form_state.field_states.values() if not f.is_valid],
                "all_required_filled": form_state.all_required_filled
            }

        except Exception:
            return {"has_errors": False, "error_count": 0}

    def show_field_error(self, field_name: str, error_message: str):
        """
        Show error for specific field.

        Args:
            field_name: Name of field with error
            error_message: Error message to display
        """
        self.error_manager.show_error(field_name, error_message)

    def hide_field_error(self, field_name: str):
        """
        Hide error for specific field.

        Args:
            field_name: Name of field to clear error for
        """
        self.error_manager.hide_error(field_name)

    def clear_all_errors(self):
        """Clear all error messages."""
        self.error_manager.hide_all_errors()

    def get_enhanced_validation_service(self) -> EnhancedValidationService:
        """Get the enhanced validation service."""
        return self.enhanced_validation

    def get_error_manager(self) -> FieldErrorManager:
        """Get the field error manager."""
        return self.error_manager


def create_enhanced_adapter(controller, view) -> EnhancedControllerAdapter:
    """
    Create enhanced adapter for an existing controller.

    Args:
        controller: Existing controller instance
        view: View instance

    Returns:
        EnhancedControllerAdapter: Configured adapter
    """
    return EnhancedControllerAdapter(controller, view)


def integrate_enhanced_services(controller, view,
                               enable_validation: bool = True,
                               enable_error_display: bool = True) -> EnhancedControllerAdapter:
    """
    Integrate enhanced services with existing controller.

    Args:
        controller: Existing controller instance
        view: View instance
        enable_validation: Whether to enable enhanced validation
        enable_error_display: Whether to enable enhanced error display

    Returns:
        EnhancedControllerAdapter: Configured adapter
    """
    adapter = create_enhanced_adapter(controller, view)

    if not enable_validation:
        adapter.enable_enhanced_validation(False)

    return adapter