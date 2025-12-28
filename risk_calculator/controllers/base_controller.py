"""Base controller with common functionality for all controllers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Callable
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
        self.current_risk_method: RiskMethod = RiskMethod.PERCENTAGE  # Default method

        # Framework-agnostic field storage
        self.field_values: Dict[str, str] = {}
        self.field_callbacks: Dict[str, List[Callable]] = {}

        # Initialize after subclass sets up field values
        self._setup_view_bindings()

    @abstractmethod
    def _setup_view_bindings(self) -> None:
        """Setup view bindings and event handlers."""
        pass

    def get_field_value(self, field_name: str) -> str:
        """Get the current value of a field."""
        return self.field_values.get(field_name, '')

    def set_field_value(self, field_name: str, value: str) -> None:
        """Set the value of a field and trigger callbacks."""
        self.field_values[field_name] = value
        self._on_field_change(field_name)

    def register_field_callback(self, field_name: str, callback: Callable) -> None:
        """Register a callback for field changes."""
        if field_name not in self.field_callbacks:
            self.field_callbacks[field_name] = []
        self.field_callbacks[field_name].append(callback)

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

        # Update field value
        self.field_values['risk_method'] = method.value

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
        # Clear all field values except risk_method
        risk_method_value = self.field_values.get('risk_method', '')
        self.field_values.clear()
        if risk_method_value:
            self.field_values['risk_method'] = risk_method_value

        # Reset trade object to defaults
        self._reset_trade_object()

        # Clear results and validation
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Update view
        if hasattr(self.view, 'clear_all_inputs'):
            self.view.clear_all_inputs()

    def _on_field_change(self, field_name: str) -> None:
        """Handle field value change for real-time validation."""
        # Get current value
        current_value = self.field_values.get(field_name, '')

        # Perform real-time validation
        error_message = self._validate_single_field(field_name, current_value)

        # Update field error display
        if error_message:
            self._show_field_error(field_name, error_message)
            self.has_errors = True
        else:
            self._clear_field_error(field_name)

        # Update overall validation status
        self._update_validation_status()

        # Update calculate button state
        self._update_calculate_button_state()

        # Trigger registered callbacks
        if field_name in self.field_callbacks:
            for callback in self.field_callbacks[field_name]:
                callback(current_value)

    def _validate_single_field(self, field_name: str, value: str) -> Optional[str]:
        """Validate a single field and return error message if invalid."""
        # This will be implemented by subclasses or use the real-time validator
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
        # This will be implemented by subclasses
        pass

    def _update_validation_status(self) -> None:
        """Update overall validation status based on current field errors."""
        # Check if any fields have errors
        # This implementation depends on how errors are tracked
        pass

    def _update_calculate_button_state(self) -> None:
        """Enable/disable calculate button based on validation status."""
        if hasattr(self.view, 'set_calculate_button_enabled'):
            enabled = not self.has_errors and self._are_required_fields_filled()
            self.view.set_calculate_button_enabled(enabled)

    def _are_required_fields_filled(self) -> bool:
        """Check if all required fields for current method are filled."""
        required_fields = self.get_required_fields()
        for field_name in required_fields:
            value = self.field_values.get(field_name, '').strip()
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

    def _on_method_changed(self, old_method: RiskMethod, new_method: RiskMethod) -> None:
        """Handle method change notifications."""
        # Can be overridden by subclasses for additional behavior
        pass

    def _reset_trade_object(self) -> None:
        """Reset trade object to defaults (implemented by subclasses)."""
        pass

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
        """Sync field values to trade object (implemented by subclasses)."""
        pass