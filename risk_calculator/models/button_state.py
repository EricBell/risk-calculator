"""
Button state model for tracking button enablement and state management.
Part of Phase 3.3: Core Models implementation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time


class ButtonState(Enum):
    """Button state enumeration."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    LOADING = "loading"
    HIDDEN = "hidden"


class ButtonStateReason(Enum):
    """Reasons for button state changes."""
    FORM_COMPLETE = "form_complete"
    FORM_INCOMPLETE = "form_incomplete"
    VALIDATION_ERROR = "validation_error"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_DATA = "invalid_data"
    PROCESSING = "processing"
    METHOD_MISMATCH = "method_mismatch"
    SYSTEM_ERROR = "system_error"
    USER_DISABLED = "user_disabled"


@dataclass
class ButtonStateTransition:
    """Model for tracking button state transitions."""
    from_state: ButtonState
    to_state: ButtonState
    reason: ButtonStateReason
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_since(self) -> float:
        """Get duration since this transition in seconds."""
        return time.time() - self.timestamp


@dataclass
class ButtonStateModel:
    """
    Model for managing button state and state transitions.

    This model tracks the current state of a button, the reasons for state changes,
    and provides functionality for state management and validation.
    """

    button_id: str
    current_state: ButtonState = ButtonState.DISABLED
    current_reason: ButtonStateReason = ButtonStateReason.FORM_INCOMPLETE
    tooltip_message: Optional[str] = None
    state_history: List[ButtonStateTransition] = field(default_factory=list)
    state_callbacks: List[Callable[[ButtonState, ButtonStateReason], None]] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_state(self, new_state: ButtonState, reason: ButtonStateReason,
                    tooltip: Optional[str] = None, context: Dict[str, Any] = None) -> None:
        """
        Update button state with transition tracking.

        Args:
            new_state: New button state
            reason: Reason for state change
            tooltip: Optional tooltip message
            context: Additional context information
        """
        if context is None:
            context = {}

        # Only update if state actually changed
        if new_state != self.current_state or reason != self.current_reason:
            # Record transition
            transition = ButtonStateTransition(
                from_state=self.current_state,
                to_state=new_state,
                reason=reason,
                timestamp=time.time(),
                context=context.copy()
            )
            self.state_history.append(transition)

            # Update current state
            old_state = self.current_state
            self.current_state = new_state
            self.current_reason = reason
            self.tooltip_message = tooltip
            self.last_updated = time.time()

            # Notify callbacks
            self._notify_state_change(old_state, new_state, reason)

    def _notify_state_change(self, old_state: ButtonState, new_state: ButtonState,
                           reason: ButtonStateReason) -> None:
        """
        Notify registered callbacks of state change.

        Args:
            old_state: Previous button state
            new_state: New button state
            reason: Reason for change
        """
        for callback in self.state_callbacks:
            try:
                callback(new_state, reason)
            except Exception:
                # Silently ignore callback errors to prevent state corruption
                pass

    def register_state_callback(self, callback: Callable[[ButtonState, ButtonStateReason], None]) -> None:
        """
        Register a callback for state changes.

        Args:
            callback: Function to call when state changes
        """
        if callback not in self.state_callbacks:
            self.state_callbacks.append(callback)

    def unregister_state_callback(self, callback: Callable[[ButtonState, ButtonStateReason], None]) -> None:
        """
        Unregister a state change callback.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.state_callbacks:
            self.state_callbacks.remove(callback)

    def is_enabled(self) -> bool:
        """Check if button is currently enabled."""
        return self.current_state == ButtonState.ENABLED

    def is_disabled(self) -> bool:
        """Check if button is currently disabled."""
        return self.current_state == ButtonState.DISABLED

    def is_loading(self) -> bool:
        """Check if button is currently in loading state."""
        return self.current_state == ButtonState.LOADING

    def is_hidden(self) -> bool:
        """Check if button is currently hidden."""
        return self.current_state == ButtonState.HIDDEN

    def get_tooltip(self) -> str:
        """
        Get appropriate tooltip message for current state.

        Returns:
            Tooltip message based on current state and reason
        """
        if self.tooltip_message:
            return self.tooltip_message

        # Generate default tooltip based on state and reason
        if self.current_state == ButtonState.ENABLED:
            return ""  # No tooltip needed when enabled

        reason_messages = {
            ButtonStateReason.FORM_INCOMPLETE: "Please complete all required fields",
            ButtonStateReason.VALIDATION_ERROR: "Please fix validation errors",
            ButtonStateReason.MISSING_REQUIRED_FIELD: "Required fields are missing",
            ButtonStateReason.INVALID_DATA: "Please enter valid data",
            ButtonStateReason.PROCESSING: "Processing...",
            ButtonStateReason.METHOD_MISMATCH: "Please select appropriate fields for current method",
            ButtonStateReason.SYSTEM_ERROR: "System error - please try again",
            ButtonStateReason.USER_DISABLED: "Button disabled by user"
        }

        return reason_messages.get(self.current_reason, "Button is disabled")

    def enable(self, reason: ButtonStateReason = ButtonStateReason.FORM_COMPLETE,
              context: Dict[str, Any] = None) -> None:
        """
        Enable the button.

        Args:
            reason: Reason for enabling
            context: Additional context
        """
        self.update_state(ButtonState.ENABLED, reason, None, context)

    def disable(self, reason: ButtonStateReason, tooltip: Optional[str] = None,
               context: Dict[str, Any] = None) -> None:
        """
        Disable the button.

        Args:
            reason: Reason for disabling
            tooltip: Optional tooltip message
            context: Additional context
        """
        self.update_state(ButtonState.DISABLED, reason, tooltip, context)

    def set_loading(self, context: Dict[str, Any] = None) -> None:
        """
        Set button to loading state.

        Args:
            context: Additional context
        """
        self.update_state(ButtonState.LOADING, ButtonStateReason.PROCESSING,
                         "Processing...", context)

    def hide(self, context: Dict[str, Any] = None) -> None:
        """
        Hide the button.

        Args:
            context: Additional context
        """
        self.update_state(ButtonState.HIDDEN, ButtonStateReason.USER_DISABLED, None, context)

    def show(self, reason: ButtonStateReason = ButtonStateReason.FORM_INCOMPLETE,
            context: Dict[str, Any] = None) -> None:
        """
        Show the button (set to disabled by default).

        Args:
            reason: Reason for showing
            context: Additional context
        """
        self.update_state(ButtonState.DISABLED, reason, None, context)

    def get_recent_transitions(self, count: int = 5) -> List[ButtonStateTransition]:
        """
        Get recent state transitions.

        Args:
            count: Number of recent transitions to return

        Returns:
            List of recent transitions
        """
        return self.state_history[-count:] if self.state_history else []

    def get_transition_count(self) -> int:
        """Get total number of state transitions."""
        return len(self.state_history)

    def get_time_in_current_state(self) -> float:
        """
        Get time spent in current state in seconds.

        Returns:
            Time in seconds since last state change
        """
        return time.time() - self.last_updated

    def has_been_enabled(self) -> bool:
        """Check if button has ever been enabled."""
        return any(transition.to_state == ButtonState.ENABLED
                  for transition in self.state_history)

    def get_last_enabled_time(self) -> Optional[float]:
        """
        Get timestamp of last time button was enabled.

        Returns:
            Timestamp of last enabled state, or None if never enabled
        """
        for transition in reversed(self.state_history):
            if transition.to_state == ButtonState.ENABLED:
                return transition.timestamp
        return None

    def reset_state(self) -> None:
        """Reset button to initial disabled state."""
        self.update_state(ButtonState.DISABLED, ButtonStateReason.FORM_INCOMPLETE)

    def clear_history(self) -> None:
        """Clear state transition history."""
        self.state_history.clear()

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of current button state.

        Returns:
            Dictionary with state summary information
        """
        return {
            'button_id': self.button_id,
            'current_state': self.current_state.value,
            'current_reason': self.current_reason.value,
            'tooltip': self.get_tooltip(),
            'is_enabled': self.is_enabled(),
            'last_updated': self.last_updated,
            'time_in_state': self.get_time_in_current_state(),
            'transition_count': self.get_transition_count(),
            'has_been_enabled': self.has_been_enabled(),
            'metadata': self.metadata
        }

    def copy(self) -> 'ButtonStateModel':
        """
        Create a copy of the button state.

        Returns:
            New ButtonStateModel instance with copied data
        """
        new_state = ButtonStateModel(
            button_id=self.button_id,
            current_state=self.current_state,
            current_reason=self.current_reason,
            tooltip_message=self.tooltip_message,
            last_updated=self.last_updated,
            metadata=self.metadata.copy()
        )

        # Copy state history
        new_state.state_history = [
            ButtonStateTransition(
                from_state=t.from_state,
                to_state=t.to_state,
                reason=t.reason,
                timestamp=t.timestamp,
                context=t.context.copy()
            )
            for t in self.state_history
        ]

        return new_state

    @classmethod
    def create_disabled(cls, button_id: str, reason: ButtonStateReason = ButtonStateReason.FORM_INCOMPLETE) -> 'ButtonStateModel':
        """
        Create a new disabled button state.

        Args:
            button_id: Unique identifier for the button
            reason: Reason for initial disabled state

        Returns:
            New ButtonStateModel in disabled state
        """
        return cls(
            button_id=button_id,
            current_state=ButtonState.DISABLED,
            current_reason=reason
        )

    @classmethod
    def create_enabled(cls, button_id: str) -> 'ButtonStateModel':
        """
        Create a new enabled button state.

        Args:
            button_id: Unique identifier for the button

        Returns:
            New ButtonStateModel in enabled state
        """
        return cls(
            button_id=button_id,
            current_state=ButtonState.ENABLED,
            current_reason=ButtonStateReason.FORM_COMPLETE
        )

    def __repr__(self) -> str:
        """String representation of button state."""
        return (f"ButtonStateModel(id='{self.button_id}', "
                f"state={self.current_state.value}, "
                f"reason={self.current_reason.value}, "
                f"enabled={self.is_enabled()})")