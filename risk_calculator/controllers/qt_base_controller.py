"""Qt Base Controller with common functionality for all Qt controllers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any, Callable

try:
    from PySide6.QtCore import QObject, Signal, Slot
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..models.validation_result import ValidationResult
from ..models.risk_method import RiskMethod
from ..views.qt_base_view import QtBaseView


class QtBaseController(QObject, ABC):
    """Qt-compatible base controller with signal-based event handling."""

    # Signals for controller events
    validation_changed = Signal(bool)  # has_errors
    calculation_completed = Signal(dict)  # result_data
    error_occurred = Signal(str)  # error_message
    busy_state_changed = Signal(bool)  # is_busy

    def __init__(self, view: QtBaseView):
        """
        Initialize Qt base controller with view reference.

        Args:
            view: Qt view instance
        """
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt controllers not supported")

        super().__init__()

        self.view = view
        self.is_busy: bool = False
        self.has_errors: bool = False
        self.validation_result: Optional[ValidationResult] = None
        self.calculation_result: Optional[Dict[str, Any]] = None
        self.current_risk_method: RiskMethod = RiskMethod.PERCENTAGE

        # Field validation state
        self.field_errors: Dict[str, str] = {}

        # Services (to be injected by subclasses)
        self.realtime_validator = None
        self.risk_calculator = None

        # Setup view connections after initialization
        self._setup_view_connections()

    def _setup_view_connections(self) -> None:
        """Setup connections between view and controller signals."""
        # Connect view field changes to validation
        if hasattr(self.view, 'field_changed'):
            self.view.field_changed.connect(self._on_field_changed)

        # Connect calculate button to calculation handler
        if hasattr(self.view, 'calculate_requested'):
            self.view.calculate_requested.connect(self._on_calculate_requested)

        # Connect risk method changes if supported
        if hasattr(self.view, 'risk_method_changed'):
            self.view.risk_method_changed.connect(self._on_risk_method_changed)

        # Register controller callbacks with view
        self.view.register_field_change_callback(self._handle_field_change)
        self.view.register_calculate_callback(self._handle_calculate_request)

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        pass

    @abstractmethod
    def _get_trade_type(self) -> str:
        """Return trade type for validation (equity, option, future)."""
        pass

    @abstractmethod
    def _create_trade_object(self, form_data: Dict[str, str]) -> Any:
        """Create trade object from form data."""
        pass

    @abstractmethod
    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if risk method is supported by this controller."""
        pass

    def set_risk_method(self, method: RiskMethod) -> None:
        """
        Change the risk calculation method and update UI.

        Args:
            method: New risk method
        """
        if not self._is_method_supported(method):
            self._show_unsupported_method_error(method)
            return

        old_method = self.current_risk_method
        self.current_risk_method = method

        # Update view method display
        if hasattr(self.view, 'update_required_fields'):
            self.view.update_required_fields(method.value)

        # Clear previous results and validation
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Notify of method change
        self._on_method_changed(old_method, method)

        # Update validation status
        self._update_validation_status()

    def clear_inputs(self) -> None:
        """Clear all input fields while preserving risk method selection."""
        # Get current form data to preserve risk method
        current_method = self.current_risk_method

        # Clear view fields (implementation depends on view)
        if hasattr(self.view, 'clear_results'):
            self.view.clear_results()

        # Clear controller state
        self._clear_calculation_result()
        self._clear_validation_errors()

        # Restore risk method
        self.current_risk_method = current_method

        # Update validation status
        self._update_validation_status()

    @Slot(str, str)
    def _on_field_changed(self, field_name: str, new_value: str) -> None:
        """
        Handle field change signal from view.

        Args:
            field_name: Name of changed field
            new_value: New field value
        """
        self._handle_field_change(field_name, new_value)

    @Slot()
    def _on_calculate_requested(self) -> None:
        """Handle calculate button clicked signal from view."""
        self._handle_calculate_request()

    @Slot(str)
    def _on_risk_method_changed(self, method_value: str) -> None:
        """
        Handle risk method change signal from view.

        Args:
            method_value: New risk method value
        """
        try:
            method = RiskMethod(method_value)
            self.set_risk_method(method)
        except ValueError:
            self.error_occurred.emit(f"Invalid risk method: {method_value}")

    def _handle_field_change(self, field_name: str, new_value: str) -> None:
        """
        Handle field change with validation.

        Args:
            field_name: Name of changed field
            new_value: New field value
        """
        # Perform real-time validation
        error_message = self._validate_single_field(field_name, new_value)

        # Update field error state
        if error_message:
            self.field_errors[field_name] = error_message
            self.view.show_field_error(field_name, error_message)
        else:
            if field_name in self.field_errors:
                del self.field_errors[field_name]
            self.view.hide_field_error(field_name)

        # Update overall validation status
        self._update_validation_status()

    def _handle_calculate_request(self) -> None:
        """Handle calculate button request."""
        if self.is_busy:
            return

        # Perform calculation
        try:
            self._set_busy_state(True)

            # Get current form data
            form_data = self.view.get_form_data()

            # Validate all fields
            if not self._validate_all_fields(form_data):
                return

            # Create trade object
            trade = self._create_trade_object(form_data)

            # Perform calculation
            result = self._perform_calculation(trade)

            if result:
                self.calculation_result = result
                self.view.display_calculation_result(result)
                self.calculation_completed.emit(result)

        except Exception as e:
            error_msg = f"Calculation failed: {str(e)}"
            self.error_occurred.emit(error_msg)

        finally:
            self._set_busy_state(False)

    def _validate_single_field(self, field_name: str, value: str) -> Optional[str]:
        """
        Validate a single field and return error message if invalid.

        Args:
            field_name: Field to validate
            value: Field value

        Returns:
            str or None: Error message if invalid
        """
        if not self.realtime_validator:
            return None

        try:
            # Create minimal trade object for validation
            form_data = self.view.get_form_data()
            form_data[field_name] = value  # Update with current value

            trade = self._create_trade_object(form_data)
            return self.realtime_validator.validate_field(
                field_name, value, self._get_trade_type(), trade
            )
        except Exception:
            return None

    def _validate_all_fields(self, form_data: Dict[str, str]) -> bool:
        """
        Validate all fields and update error display.

        Args:
            form_data: Current form data

        Returns:
            bool: True if all valid
        """
        all_valid = True
        errors = {}

        for field_name, value in form_data.items():
            error_message = self._validate_single_field(field_name, value)
            if error_message:
                errors[field_name] = error_message
                all_valid = False

        # Update field error display
        self.field_errors = errors
        for field_name, error_msg in errors.items():
            self.view.show_field_error(field_name, error_msg)

        # Clear errors for fields that are now valid
        current_form_fields = set(form_data.keys())
        for field_name in list(self.field_errors.keys()):
            if field_name not in errors and field_name in current_form_fields:
                self.view.hide_field_error(field_name)

        return all_valid

    def _perform_calculation(self, trade: Any) -> Optional[Dict[str, Any]]:
        """
        Perform risk calculation.

        Args:
            trade: Trade object

        Returns:
            Dict[str, Any] or None: Calculation result
        """
        if not self.risk_calculator:
            return None

        try:
            return self.risk_calculator.calculate_position_size(trade)
        except Exception as e:
            self.error_occurred.emit(f"Calculation error: {str(e)}")
            return None

    def _update_validation_status(self) -> None:
        """Update overall validation status and button states."""
        # Check if we have any field errors
        had_errors = self.has_errors
        self.has_errors = len(self.field_errors) > 0

        # Check if required fields are filled
        form_data = self.view.get_form_data()
        required_fields = self.get_required_fields()
        required_filled = all(
            form_data.get(field, '').strip() != '' for field in required_fields
        )

        # Update calculate button state
        button_enabled = not self.has_errors and required_filled
        self.view.set_calculate_button_enabled(button_enabled)

        # Emit validation change signal if status changed
        if had_errors != self.has_errors:
            self.validation_changed.emit(self.has_errors)

    def _clear_validation_errors(self) -> None:
        """Clear all validation errors."""
        self.has_errors = False
        self.validation_result = None
        self.field_errors.clear()

        # Clear view error displays
        form_data = self.view.get_form_data()
        for field_name in form_data.keys():
            self.view.hide_field_error(field_name)

    def _clear_calculation_result(self) -> None:
        """Clear calculation results."""
        self.calculation_result = None
        self.view.clear_results()

    def _set_busy_state(self, busy: bool) -> None:
        """
        Set controller busy state.

        Args:
            busy: Whether controller is busy
        """
        if self.is_busy != busy:
            self.is_busy = busy
            self.busy_state_changed.emit(busy)

            # Update view state if supported
            if hasattr(self.view, 'set_calculate_button_enabled'):
                self.view.set_calculate_button_enabled(not busy and not self.has_errors)

    def _show_unsupported_method_error(self, method: RiskMethod) -> None:
        """
        Show error for unsupported risk method.

        Args:
            method: Unsupported method
        """
        error_msg = f"Risk method '{method.value}' is not supported for {self._get_trade_type()} trading"
        self.error_occurred.emit(error_msg)

    def _on_method_changed(self, old_method: RiskMethod, new_method: RiskMethod) -> None:
        """
        Handle risk method change event.

        Args:
            old_method: Previous risk method
            new_method: New risk method
        """
        # Clear method-specific validation errors
        self._clear_validation_errors()

        # Update validation status for new method requirements
        self._update_validation_status()

    def get_current_trade_data(self) -> Dict[str, Any]:
        """
        Get current trade data from view.

        Returns:
            Dict[str, Any]: Current trade data
        """
        form_data = self.view.get_form_data()

        # Convert string values to appropriate types where possible
        processed_data = {}
        for key, value in form_data.items():
            # Try to convert numeric fields
            if key in ['account_size', 'entry_price', 'premium', 'tick_value',
                      'tick_size', 'margin_requirement', 'risk_percentage',
                      'fixed_risk_amount', 'stop_loss_price', 'support_resistance_level',
                      'contract_multiplier', 'stop_loss_ticks']:
                try:
                    processed_data[key] = float(value) if value.strip() else 0.0
                except (ValueError, AttributeError):
                    processed_data[key] = value
            else:
                processed_data[key] = value

        return processed_data

    def inject_services(self, realtime_validator=None, risk_calculator=None) -> None:
        """
        Inject service dependencies.

        Args:
            realtime_validator: Real-time validation service
            risk_calculator: Risk calculation service
        """
        self.realtime_validator = realtime_validator
        self.risk_calculator = risk_calculator