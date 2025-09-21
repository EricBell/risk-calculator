"""
Enhanced BaseController implementation.
Integrates with new validation system and error display components.
"""

import tkinter as tk
from typing import Optional, Dict, Any
from enum import Enum

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from ui_controller import UIController
    from validation_service import FormValidationState, TradeType
except ImportError:
    # Fallback definitions
    from abc import ABC, abstractmethod

    class UIController(ABC):
        pass

    class TradeType(Enum):
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"

    # Create placeholder FormValidationState
    FormValidationState = object

# Import local components
from risk_calculator.models.field_validation_state import FieldValidationState
from risk_calculator.models.form_validation_state import FormValidationState as LocalFormValidationState
from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
from risk_calculator.views.error_display import FieldErrorManager


class EnhancedBaseController(UIController):
    """Enhanced base controller with improved validation and error display."""

    def __init__(self, view):
        """
        Initialize enhanced controller.

        Args:
            view: View component to control
        """
        self.view = view
        self.validation_service = EnhancedValidationService()
        self.error_manager = FieldErrorManager()
        self.current_form_state: Optional[LocalFormValidationState] = None
        self.trade_type: TradeType = self._determine_trade_type()
        self.current_risk_method = "percentage"  # Default
        self.field_values: Dict[str, str] = {}  # Store field values for method switching
        self.is_busy: bool = False  # Track if calculation is in progress

        # Initialize error display
        self._setup_error_display()

    def _determine_trade_type(self) -> TradeType:
        """Determine trade type from controller/view class name."""
        class_name = self.__class__.__name__.lower()
        if "equity" in class_name:
            return TradeType.EQUITY
        elif "option" in class_name:
            return TradeType.OPTION
        elif "future" in class_name:
            return TradeType.FUTURE
        else:
            return TradeType.EQUITY  # Default

    def _setup_error_display(self):
        """Setup error display components for form fields."""
        # This will be called after view initialization
        try:
            if hasattr(self.view, 'get_form_fields'):
                form_fields = self.view.get_form_fields()
                if form_fields and hasattr(form_fields, 'items'):
                    for field_name, field_widget in form_fields.items():
                        error_label = self._create_error_label_for_field(field_name, field_widget)
                        self.error_manager.register_field(field_name, field_widget, error_label)
        except Exception:
            # Gracefully handle any setup errors (e.g., during testing with mocks)
            pass

    def _create_error_label_for_field(self, field_name: str, field_widget: tk.Widget):
        """Create error label for a specific field."""
        from risk_calculator.views.error_display import ErrorLabel

        # Skip StringVar and similar non-widget objects
        if isinstance(field_widget, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
            # For Tkinter variables, we need to find the actual widget that uses this variable
            # For now, just use the view itself as parent for the error label
            parent = self.view
        else:
            # Get parent widget for actual widgets
            try:
                parent = field_widget.master if hasattr(field_widget, 'master') else field_widget.winfo_parent()
            except Exception:
                parent = self.view

        # Create error label
        error_label = ErrorLabel(parent)

        # Position error label - for StringVar objects, we can't position properly
        # so we'll just hide it initially and let the display logic handle it
        if not isinstance(field_widget, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
            try:
                grid_info = field_widget.grid_info()
                if grid_info:
                    row = int(grid_info.get('row', 0))
                    column = int(grid_info.get('column', 0))
                    error_label.grid(row=row + 1, column=column, sticky='w', padx=5)
                else:
                    # Fallback positioning
                    error_label.pack(anchor='w', padx=5)
            except Exception:
                # If positioning fails, just pack it
                error_label.pack(anchor='w', padx=5)

        return error_label

    def update_button_state(self, form_state: LocalFormValidationState) -> None:
        """
        Update Calculate Position button state based on form validation.

        Args:
            form_state: Current form validation state
        """
        if hasattr(self.view, 'set_calculate_button_enabled'):
            # Use the view's method to set button state
            self.view.set_calculate_button_enabled(form_state.is_submittable)
        elif hasattr(self.view, 'get_calculate_button'):
            # Fallback to direct button manipulation
            button = self.view.get_calculate_button()
            if button:
                if form_state.is_submittable:
                    button.config(state='normal')
                else:
                    button.config(state='disabled')

    def show_field_error(self, field_name: str, error_message: str) -> None:
        """
        Display error message for specific field.

        Args:
            field_name: Name of field with error
            error_message: Error message to display
        """
        self.error_manager.show_error(field_name, error_message)

    def hide_field_error(self, field_name: str) -> None:
        """
        Hide error message for specific field.

        Args:
            field_name: Name of field to clear error for
        """
        self.error_manager.hide_error(field_name)

    def update_form_validation(self, form_data: Dict[str, str]) -> LocalFormValidationState:
        """
        Update form validation state and UI elements.

        Args:
            form_data: Current form field values

        Returns:
            FormValidationState: Updated validation state
        """
        # Get current risk method and determine required fields
        required_fields = self.validation_service.get_required_fields(
            self.trade_type, self.current_risk_method
        )

        # Validate the form
        form_state = self.validation_service.validate_form(form_data, self.trade_type)

        # Update required fields based on current method
        form_state = form_state.update_required_fields(required_fields)

        # Update error display
        self._update_error_display(form_state)

        # Update button state
        self.update_button_state(form_state)

        # Store current state
        self.current_form_state = form_state

        return form_state

    def _update_error_display(self, form_state: LocalFormValidationState):
        """Update error display based on form validation state."""
        # Clear all errors first
        self.error_manager.hide_all_errors()

        # Show errors for invalid fields
        for field_name, field_state in form_state.field_states.items():
            if not field_state.is_valid and field_state.error_message:
                self.show_field_error(field_name, field_state.error_message)

    def handle_field_change(self, field_name: str, value: str) -> None:
        """
        Handle individual field value change with real-time validation.

        Args:
            field_name: Name of changed field
            value: New field value
        """
        # Validate the single field
        validation_result = self.validation_service.validate_field(
            field_name, value, self.trade_type
        )

        # Update field error display
        if validation_result.is_valid:
            self.hide_field_error(field_name)
        else:
            self.show_field_error(field_name, validation_result.error_message)

        # Update overall form validation
        form_data = {}
        if hasattr(self.view, 'get_all_field_values'):
            form_data = self.view.get_all_field_values()
        elif hasattr(self, 'tk_vars'):
            # Fallback: get values from tk_vars if view doesn't have get_all_field_values
            form_data = {name: str(var.get()) for name, var in self.tk_vars.items()}

        form_data[field_name] = value  # Ensure latest value is included
        self.update_form_validation(form_data)

    def execute_calculation(self) -> bool:
        """
        Execute position calculation if form is valid.

        Returns:
            bool: True if calculation executed successfully, False otherwise
        """
        if not self.current_form_state or not self.current_form_state.is_submittable:
            return False

        try:
            # Get form data
            if hasattr(self.view, 'get_all_field_values'):
                form_data = self.view.get_all_field_values()
            else:
                return False

            # Execute calculation (delegate to existing calculation logic)
            if hasattr(self, '_perform_calculation'):
                result = self._perform_calculation(form_data)

                # Display result
                if hasattr(self.view, 'display_calculation_result'):
                    self.view.display_calculation_result(result)

                return True

        except Exception as e:
            # Show calculation error
            self.show_field_error("calculation", f"Calculation error: {str(e)}")

        return False

    def configure_responsive_layout(self) -> None:
        """Configure UI layout for responsive resizing behavior."""
        if hasattr(self.view, 'configure_responsive_grid'):
            self.view.configure_responsive_grid()

    def handle_window_resize(self, event: Any) -> None:
        """
        Handle window resize events and update layout accordingly.

        Args:
            event: Window resize event from UI framework
        """
        # Ensure error messages remain visible during resize
        if hasattr(event, 'width') and hasattr(event, 'height'):
            # Update layout constraints if needed
            if hasattr(self.view, 'handle_resize'):
                self.view.handle_resize(event.width, event.height)

        # Ensure error messages are still visible
        self._refresh_error_display()

    def _refresh_error_display(self):
        """Refresh error message display after layout changes."""
        if self.current_form_state:
            self._update_error_display(self.current_form_state)

    def set_risk_method(self, risk_method: str):
        """
        Update the risk calculation method.

        Args:
            risk_method: New risk method (percentage, fixed, level)
        """
        self.current_risk_method = risk_method

        # Re-validate form with new requirements
        if hasattr(self.view, 'get_all_field_values'):
            form_data = self.view.get_all_field_values()
            self.update_form_validation(form_data)

    def get_current_form_state(self) -> Optional[LocalFormValidationState]:
        """
        Get the current form validation state.

        Returns:
            FormValidationState: Current form state
        """
        return self.current_form_state

    def is_calculate_button_enabled(self) -> bool:
        """
        Check if Calculate Position button is enabled.

        Returns:
            bool: True if button is enabled
        """
        if self.current_form_state:
            return self.current_form_state.is_submittable
        return False

    def is_error_visible(self, field_name: str) -> bool:
        """
        Check if error message is visible for a field.

        Args:
            field_name: Name of field to check

        Returns:
            bool: True if error is visible
        """
        if field_name in self.error_manager.error_labels:
            return self.error_manager.error_labels[field_name].has_error()
        return False

    def clear_all_errors(self):
        """Clear all error messages."""
        self.error_manager.hide_all_errors()

    def get_validation_service(self) -> EnhancedValidationService:
        """
        Get the validation service instance.

        Returns:
            EnhancedValidationService: The validation service
        """
        return self.validation_service

    def set_field_value(self, field_name: str, value: str) -> None:
        """
        Set the value of a specific field.

        Args:
            field_name: Name of the field to set
            value: Value to set
        """
        # Store in controller's field values
        self.field_values[field_name] = value

        # Also try to update the UI widget if available
        try:
            if hasattr(self.view, 'input_widgets') and hasattr(self.view.input_widgets, '__contains__'):
                if field_name in self.view.input_widgets:
                    widget = self.view.input_widgets[field_name]
                    if isinstance(widget, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
                        widget.set(value)
                    elif hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                        # Entry widgets
                        widget.delete(0, tk.END)
                        widget.insert(0, value)
                    elif hasattr(widget, 'set'):
                        widget.set(value)
        except Exception:
            pass  # Ignore if setting fails - this handles Mock objects and other edge cases

    def get_field_value(self, field_name: str) -> str:
        """
        Get the value of a specific field.

        Args:
            field_name: Name of the field to get

        Returns:
            str: Field value or empty string if not found
        """
        # First check stored values
        if field_name in self.field_values:
            return self.field_values[field_name]

        # Try to get from UI widget if not in stored values
        try:
            if hasattr(self.view, 'input_widgets') and hasattr(self.view.input_widgets, '__contains__'):
                if field_name in self.view.input_widgets:
                    widget = self.view.input_widgets[field_name]
                    if isinstance(widget, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
                        value = str(widget.get())
                        self.field_values[field_name] = value  # Cache it
                        return value
                    elif hasattr(widget, 'get'):
                        value = str(widget.get())
                        self.field_values[field_name] = value  # Cache it
                        return value
        except Exception:
            pass  # Ignore if getting fails
        return ""

    def _perform_calculation(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Perform the actual calculation (to be implemented by subclasses).

        Args:
            form_data: Validated form data

        Returns:
            Dict[str, Any]: Calculation result
        """
        # This should be implemented by specific controller subclasses
        # For now, return a placeholder
        return {
            "shares": 100,
            "risk_amount": 200.0,
            "calculation_method": self.current_risk_method
        }

    def set_busy_state(self, is_busy: bool) -> None:
        """Set busy state for controller and update view."""
        self.is_busy = is_busy

        # Update view if it has the busy state method
        if hasattr(self.view, 'set_busy_state'):
            self.view.set_busy_state(is_busy)

    def _on_field_change(self, var_name: str, *args) -> None:
        """
        Handle field changes from tk_vars (backward compatibility method).
        Bridges old system to enhanced validation system.
        """
        try:
            # Get the value from tk_vars if available
            value = ""
            if hasattr(self, 'tk_vars') and var_name in self.tk_vars:
                value = str(self.tk_vars[var_name].get())

            # Use enhanced validation system
            self.handle_field_change(var_name, value)

        except Exception:
            # If enhanced system fails, fall back to basic operation
            pass