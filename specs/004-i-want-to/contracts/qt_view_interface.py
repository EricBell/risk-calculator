"""
Qt View Interface Contract
Defines the interface for Qt-based views replacing Tkinter components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from PyQt6.QtWidgets import QWidget


class QtViewInterface(ABC):
    """Base interface for Qt-based views"""

    @abstractmethod
    def setup_ui(self) -> None:
        """Initialize and configure UI components"""
        pass

    @abstractmethod
    def connect_signals(self) -> None:
        """Connect Qt signals to appropriate slots"""
        pass

    @abstractmethod
    def get_form_data(self) -> Dict[str, str]:
        """
        Get current form field values.

        Returns:
            Dict[str, str]: Field name to value mapping
        """
        pass

    @abstractmethod
    def set_field_value(self, field_name: str, value: str) -> None:
        """
        Set value for a specific form field.

        Args:
            field_name: Name of field to update
            value: New value to set
        """
        pass

    @abstractmethod
    def show_field_error(self, field_name: str, error_message: str) -> None:
        """
        Display error message for specific field.

        Args:
            field_name: Field that has error
            error_message: Error message to display
        """
        pass

    @abstractmethod
    def hide_field_error(self, field_name: str) -> None:
        """
        Hide error message for specific field.

        Args:
            field_name: Field to clear error for
        """
        pass

    @abstractmethod
    def set_calculate_button_enabled(self, enabled: bool) -> None:
        """
        Enable/disable the calculate button.

        Args:
            enabled: True to enable, False to disable
        """
        pass


class QtMainWindowInterface(ABC):
    """Interface for main Qt window"""

    @abstractmethod
    def setup_menu_bar(self) -> None:
        """Setup application menu bar"""
        pass

    @abstractmethod
    def setup_tab_widget(self) -> None:
        """Setup tabbed interface for different asset types"""
        pass

    @abstractmethod
    def add_trading_tab(self, tab_name: str, tab_widget: QWidget) -> None:
        """
        Add a trading tab to the main interface.

        Args:
            tab_name: Display name for tab
            tab_widget: Widget to display in tab
        """
        pass

    @abstractmethod
    def show_status_message(self, message: str, timeout: int = 0) -> None:
        """
        Show message in status bar.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 = permanent)
        """
        pass

    @abstractmethod
    def save_window_state(self) -> None:
        """Save current window state to configuration"""
        pass

    @abstractmethod
    def restore_window_state(self) -> None:
        """Restore window state from configuration"""
        pass


class QtTradingTabInterface(ABC):
    """Interface for individual trading tabs (Equity, Options, Futures)"""

    @abstractmethod
    def setup_input_fields(self) -> None:
        """Setup input fields specific to trading type"""
        pass

    @abstractmethod
    def setup_result_display(self) -> None:
        """Setup result display area"""
        pass

    @abstractmethod
    def setup_risk_method_selection(self) -> None:
        """Setup risk method radio buttons/dropdown"""
        pass

    @abstractmethod
    def update_required_fields(self, risk_method: str) -> None:
        """
        Update which fields are required based on risk method.

        Args:
            risk_method: Selected risk calculation method
        """
        pass

    @abstractmethod
    def display_calculation_result(self, result: Dict[str, Any]) -> None:
        """
        Display calculation results.

        Args:
            result: Calculation result data
        """
        pass

    @abstractmethod
    def clear_results(self) -> None:
        """Clear displayed calculation results"""
        pass

    @abstractmethod
    def register_field_change_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Register callback for field value changes.

        Args:
            callback: Function to call when field changes (field_name, new_value)
        """
        pass

    @abstractmethod
    def register_calculate_callback(self, callback: Callable[[], None]) -> None:
        """
        Register callback for calculate button clicks.

        Args:
            callback: Function to call when calculate is clicked
        """
        pass