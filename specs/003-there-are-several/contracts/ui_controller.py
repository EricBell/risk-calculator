"""
UI Controller Contract
API contract for enhanced UI controller with responsive layout and error display
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable, Any

# Import validation service types
try:
    from .validation_service import FormValidationState, TradeType
except ImportError:
    # Import from the same directory when used as standalone
    try:
        from validation_service import FormValidationState, TradeType
    except ImportError:
        # Create placeholder types for contract testing
        FormValidationState = object
        TradeType = object


class UIController(ABC):
    """Abstract interface for UI controllers with enhanced validation and responsiveness"""

    @abstractmethod
    def update_button_state(self, form_state: FormValidationState) -> None:
        """
        Update Calculate Position button state based on form validation

        Args:
            form_state: Current form validation state
        """
        pass

    @abstractmethod
    def show_field_error(self, field_name: str, error_message: str) -> None:
        """
        Display error message for specific field

        Args:
            field_name: Name of field with error
            error_message: Error message to display
        """
        pass

    @abstractmethod
    def hide_field_error(self, field_name: str) -> None:
        """
        Hide error message for specific field

        Args:
            field_name: Name of field to clear error for
        """
        pass

    @abstractmethod
    def update_form_validation(self, form_data: Dict[str, str]) -> FormValidationState:
        """
        Update form validation state and UI elements

        Args:
            form_data: Current form field values

        Returns:
            FormValidationState: Updated validation state
        """
        pass

    @abstractmethod
    def handle_field_change(self, field_name: str, value: str) -> None:
        """
        Handle individual field value change with real-time validation

        Args:
            field_name: Name of changed field
            value: New field value
        """
        pass

    @abstractmethod
    def execute_calculation(self) -> bool:
        """
        Execute position calculation if form is valid

        Returns:
            bool: True if calculation executed successfully, False otherwise
        """
        pass

    @abstractmethod
    def configure_responsive_layout(self) -> None:
        """
        Configure UI layout for responsive resizing behavior
        """
        pass

    @abstractmethod
    def handle_window_resize(self, event: Any) -> None:
        """
        Handle window resize events and update layout accordingly

        Args:
            event: Window resize event from UI framework
        """
        pass


class WindowController(ABC):
    """Abstract interface for main window controller with configuration management"""

    @abstractmethod
    def save_window_state(self) -> bool:
        """
        Save current window size and position to configuration

        Returns:
            bool: True if save successful, False otherwise
        """
        pass

    @abstractmethod
    def restore_window_state(self) -> bool:
        """
        Restore window size and position from configuration

        Returns:
            bool: True if restore successful, False if using defaults
        """
        pass

    @abstractmethod
    def validate_window_bounds(self, width: int, height: int, x: int, y: int) -> tuple:
        """
        Validate and adjust window bounds for current screen

        Args:
            width: Requested window width
            height: Requested window height
            x: Requested window x position
            y: Requested window y position

        Returns:
            tuple: (adjusted_width, adjusted_height, adjusted_x, adjusted_y)
        """
        pass

    @abstractmethod
    def setup_window_event_handlers(self) -> None:
        """
        Setup event handlers for window resize, move, and state changes
        """
        pass

    @abstractmethod
    def apply_minimum_size_constraints(self) -> None:
        """
        Apply minimum window size constraints (800x600)
        """
        pass


class MenuController(ABC):
    """Abstract interface for menu controller with validation integration"""

    @abstractmethod
    def handle_calculate_menu_action(self) -> None:
        """
        Handle Calculate Position menu item selection
        """
        pass

    @abstractmethod
    def update_menu_state(self, form_state: FormValidationState) -> None:
        """
        Update menu item state based on form validation

        Args:
            form_state: Current form validation state
        """
        pass

    @abstractmethod
    def show_menu_validation_dialog(self, error_messages: Dict[str, str]) -> None:
        """
        Show dialog with validation errors when menu action fails

        Args:
            error_messages: Map of field_name -> error_message
        """
        pass