"""
Button state management service implementation.
Part of Phase 3.4: Validation Services implementation.
"""

from typing import Dict, List, Any, Optional, Callable
import time

from ..models.button_state import ButtonStateModel, ButtonState, ButtonStateReason
from .enhanced_form_validation_service import EnhancedFormValidationService


class ButtonStateService:
    """
    Button state management service implementing ButtonStateInterface.

    This service manages button states based on form validation results,
    provides appropriate tooltips, and handles state change callbacks.
    """

    def __init__(self):
        """Initialize the button state service."""
        self.validation_service = EnhancedFormValidationService()
        self._button_states: Dict[str, ButtonStateModel] = {}
        self._global_callbacks: List[Callable[[ButtonState], None]] = []

    def get_button_state(self, form_data: Dict[str, Any], risk_method: str) -> ButtonState:
        """
        Get current button state based on form data and risk method.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            ButtonState enum value
        """
        # Set risk method in validation service
        self.validation_service.set_risk_method(risk_method)

        # Validate form
        errors = self.validation_service.validate_form(form_data)

        if len(errors) == 0:
            return ButtonState.ENABLED
        else:
            return ButtonState.DISABLED

    def should_enable_button(self, form_data: Dict[str, Any], risk_method: str) -> bool:
        """
        Determine if button should be enabled.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            True if button should be enabled, False otherwise
        """
        state = self.get_button_state(form_data, risk_method)
        return state == ButtonState.ENABLED

    def get_button_tooltip(self, form_data: Dict[str, Any], risk_method: str) -> Optional[str]:
        """
        Get tooltip message for button based on current state.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            Tooltip message string or None if no tooltip needed
        """
        # Set risk method in validation service
        self.validation_service.set_risk_method(risk_method)

        # Check if button should be enabled
        if self.should_enable_button(form_data, risk_method):
            return None  # No tooltip when enabled

        # Get validation errors
        errors = self.validation_service.validate_form(form_data)
        required_fields = self.validation_service.get_required_fields(risk_method, form_data)

        # Generate appropriate tooltip based on errors
        if len(errors) == 0:
            return None

        # Check for missing required fields
        missing_fields = []
        for field in required_fields:
            if field not in form_data or not str(form_data[field]).strip():
                missing_fields.append(self._format_field_name(field))

        if missing_fields:
            if len(missing_fields) == 1:
                return f"Please enter {missing_fields[0]}"
            elif len(missing_fields) == 2:
                return f"Please enter {missing_fields[0]} and {missing_fields[1]}"
            else:
                return f"Please enter {', '.join(missing_fields[:-1])}, and {missing_fields[-1]}"

        # Show specific validation errors
        error_messages = list(errors.values())
        if len(error_messages) == 1:
            return error_messages[0]
        elif len(error_messages) <= 3:
            return "; ".join(error_messages)
        else:
            return f"Please fix {len(error_messages)} validation errors"

    def register_state_change_callback(self, callback: Callable[[ButtonState], None]) -> None:
        """
        Register callback to be called when button state changes.

        Args:
            callback: Function to call with new ButtonState
        """
        if callback not in self._global_callbacks:
            self._global_callbacks.append(callback)

    def update_button_state(self, form_data: Dict[str, Any], risk_method: str) -> None:
        """
        Update button state and notify callbacks.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method
        """
        new_state = self.get_button_state(form_data, risk_method)

        # Notify global callbacks
        for callback in self._global_callbacks:
            try:
                callback(new_state)
            except Exception:
                # Silently ignore callback errors
                pass

    def reset_button_state(self) -> None:
        """Reset button to default disabled state."""
        # Notify callbacks that button is disabled
        for callback in self._global_callbacks:
            try:
                callback(ButtonState.DISABLED)
            except Exception:
                pass

    def get_button_model(self, button_id: str) -> ButtonStateModel:
        """
        Get or create button state model for a specific button.

        Args:
            button_id: Unique identifier for the button

        Returns:
            ButtonStateModel for the specified button
        """
        if button_id not in self._button_states:
            self._button_states[button_id] = ButtonStateModel.create_disabled(button_id)

        return self._button_states[button_id]

    def update_button_model(self, button_id: str, form_data: Dict[str, Any], risk_method: str) -> None:
        """
        Update button state model with current form data.

        Args:
            button_id: Unique identifier for the button
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method
        """
        button_model = self.get_button_model(button_id)

        # Determine new state and reason
        new_state = self.get_button_state(form_data, risk_method)
        tooltip = self.get_button_tooltip(form_data, risk_method)

        # Determine reason for state
        if new_state == ButtonState.ENABLED:
            reason = ButtonStateReason.FORM_COMPLETE
        else:
            reason = self._determine_disable_reason(form_data, risk_method)

        # Update button model
        context = {
            'form_data': form_data,
            'risk_method': risk_method,
            'field_count': len(form_data),
            'timestamp': time.time()
        }

        button_model.update_state(new_state, reason, tooltip, context)

    def _determine_disable_reason(self, form_data: Dict[str, Any], risk_method: str) -> ButtonStateReason:
        """
        Determine the specific reason why button is disabled.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            ButtonStateReason indicating why button is disabled
        """
        self.validation_service.set_risk_method(risk_method)
        errors = self.validation_service.validate_form(form_data)
        required_fields = self.validation_service.get_required_fields(risk_method, form_data)

        # Check for missing required fields
        missing_fields = []
        for field in required_fields:
            if field not in form_data or not str(form_data[field]).strip():
                missing_fields.append(field)

        if missing_fields:
            return ButtonStateReason.MISSING_REQUIRED_FIELD

        # Check for validation errors
        if errors:
            # Check if any errors are due to invalid data format
            for error_msg in errors.values():
                if any(keyword in error_msg.lower() for keyword in ['invalid', 'must be', 'cannot']):
                    return ButtonStateReason.INVALID_DATA

            return ButtonStateReason.VALIDATION_ERROR

        # Check for method mismatch (wrong fields for current method)
        form_fields = set(form_data.keys())
        required_fields_set = set(required_fields)

        if not required_fields_set.issubset(form_fields):
            return ButtonStateReason.METHOD_MISMATCH

        return ButtonStateReason.FORM_INCOMPLETE

    def get_all_button_states(self) -> Dict[str, ButtonStateModel]:
        """
        Get all currently managed button states.

        Returns:
            Dictionary mapping button IDs to their state models
        """
        return self._button_states.copy()

    def remove_button(self, button_id: str) -> None:
        """
        Remove a button from state management.

        Args:
            button_id: Unique identifier for the button to remove
        """
        if button_id in self._button_states:
            del self._button_states[button_id]

    def clear_all_buttons(self) -> None:
        """Clear all button states."""
        self._button_states.clear()

    def register_button_callback(self, button_id: str, callback: Callable[[ButtonState, ButtonStateReason], None]) -> None:
        """
        Register a callback for a specific button.

        Args:
            button_id: Unique identifier for the button
            callback: Function to call when button state changes
        """
        button_model = self.get_button_model(button_id)
        button_model.register_state_callback(callback)

    def unregister_button_callback(self, button_id: str, callback: Callable[[ButtonState, ButtonStateReason], None]) -> None:
        """
        Unregister a callback for a specific button.

        Args:
            button_id: Unique identifier for the button
            callback: Function to remove from callbacks
        """
        if button_id in self._button_states:
            self._button_states[button_id].unregister_state_callback(callback)

    def get_button_performance_metrics(self, button_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a button.

        Args:
            button_id: Unique identifier for the button

        Returns:
            Dictionary with performance metrics
        """
        if button_id not in self._button_states:
            return {}

        button_model = self._button_states[button_id]
        recent_transitions = button_model.get_recent_transitions(10)

        # Calculate transition frequency
        if len(recent_transitions) >= 2:
            time_span = recent_transitions[-1].timestamp - recent_transitions[0].timestamp
            transition_frequency = len(recent_transitions) / max(time_span, 1)
        else:
            transition_frequency = 0

        # Calculate time to first enable
        time_to_first_enable = None
        for transition in button_model.state_history:
            if transition.to_state == ButtonState.ENABLED:
                time_to_first_enable = transition.timestamp - button_model.state_history[0].timestamp
                break

        return {
            'button_id': button_id,
            'total_transitions': button_model.get_transition_count(),
            'time_in_current_state': button_model.get_time_in_current_state(),
            'transition_frequency_per_second': transition_frequency,
            'has_been_enabled': button_model.has_been_enabled(),
            'last_enabled_time': button_model.get_last_enabled_time(),
            'time_to_first_enable': time_to_first_enable,
            'current_state': button_model.current_state.value,
            'current_reason': button_model.current_reason.value
        }

    def _format_field_name(self, field_name: str) -> str:
        """
        Format field name for display in tooltips.

        Args:
            field_name: Raw field name

        Returns:
            Formatted field name
        """
        field_name_mapping = {
            'account_size': 'Account Size',
            'risk_percentage': 'Risk Percentage',
            'fixed_risk_amount': 'Risk Amount',
            'level': 'Level',
            'entry_price': 'Entry Price',
            'stop_loss_price': 'Stop Loss Price',
            'premium': 'Option Premium',
            'option_premium': 'Option Premium',
            'tick_value': 'Tick Value',
            'ticks_at_risk': 'Ticks at Risk'
        }

        return field_name_mapping.get(field_name, field_name.replace('_', ' ').title())

    def validate_button_state_consistency(self, button_id: str, form_data: Dict[str, Any], risk_method: str) -> bool:
        """
        Validate that button state is consistent with form data.

        Args:
            button_id: Unique identifier for the button
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            True if button state is consistent, False otherwise
        """
        if button_id not in self._button_states:
            return True  # No state to be inconsistent with

        button_model = self._button_states[button_id]
        expected_state = self.get_button_state(form_data, risk_method)

        return button_model.current_state == expected_state

    def get_state_change_history(self, button_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get state change history for a button.

        Args:
            button_id: Unique identifier for the button
            limit: Maximum number of history entries to return

        Returns:
            List of state change history entries
        """
        if button_id not in self._button_states:
            return []

        button_model = self._button_states[button_id]
        transitions = button_model.state_history[-limit:] if limit > 0 else button_model.state_history

        return [
            {
                'from_state': t.from_state.value,
                'to_state': t.to_state.value,
                'reason': t.reason.value,
                'timestamp': t.timestamp,
                'duration_since': t.duration_since,
                'context': t.context
            }
            for t in transitions
        ]