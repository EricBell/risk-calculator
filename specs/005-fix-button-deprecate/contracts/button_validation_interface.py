"""
Button Validation Interface Contract
Defines the interface for real-time form validation and button enablement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FieldValidationResult:
    """Result of individual field validation"""
    field_name: str
    is_valid: bool
    error_message: str
    is_required: bool
    validation_type: str


@dataclass
class FormValidationState:
    """Overall form validation state"""
    overall_valid: bool
    error_count: int
    missing_fields: List[str]
    invalid_fields: List[str]
    required_fields: List[str]
    risk_method: str
    last_updated: datetime


@dataclass
class ButtonState:
    """Calculate Position button state"""
    enabled: bool
    tooltip_message: str
    error_summary: str


class FormValidationInterface(ABC):
    """Interface for form validation management"""

    @abstractmethod
    def validate_field(self, field_name: str, value: str, risk_method: str) -> FieldValidationResult:
        """
        Validate a single form field.

        Args:
            field_name: Name of the field to validate
            value: Current field value
            risk_method: Selected risk calculation method

        Returns:
            FieldValidationResult: Validation result with error details
        """
        pass

    @abstractmethod
    def validate_form(self, field_values: Dict[str, str], risk_method: str) -> FormValidationState:
        """
        Validate entire form and return comprehensive state.

        Args:
            field_values: Dictionary of field names to current values
            risk_method: Selected risk calculation method

        Returns:
            FormValidationState: Complete validation state
        """
        pass

    @abstractmethod
    def get_required_fields(self, risk_method: str) -> List[str]:
        """
        Get list of required fields for given risk method.

        Args:
            risk_method: Risk calculation method

        Returns:
            List[str]: Required field names
        """
        pass

    @abstractmethod
    def is_form_complete(self, field_values: Dict[str, str], risk_method: str) -> bool:
        """
        Check if form has all required fields completed.

        Args:
            field_values: Dictionary of field names to current values
            risk_method: Selected risk calculation method

        Returns:
            bool: True if all required fields are present and valid
        """
        pass


class ButtonStateInterface(ABC):
    """Interface for Calculate Position button state management"""

    @abstractmethod
    def update_button_state(self, validation_state: FormValidationState) -> ButtonState:
        """
        Update button state based on form validation.

        Args:
            validation_state: Current form validation state

        Returns:
            ButtonState: Updated button state with enable/disable status
        """
        pass

    @abstractmethod
    def generate_error_message(self, validation_state: FormValidationState) -> str:
        """
        Generate user-friendly error message for button tooltip.

        Args:
            validation_state: Current form validation state

        Returns:
            str: Human-readable error message explaining why button is disabled
        """
        pass

    @abstractmethod
    def should_enable_button(self, validation_state: FormValidationState) -> bool:
        """
        Determine if Calculate Position button should be enabled.

        Args:
            validation_state: Current form validation state

        Returns:
            bool: True if button should be enabled
        """
        pass


class ApplicationLifecycleInterface(ABC):
    """Interface for application process management"""

    @abstractmethod
    def register_cleanup_handler(self, handler: callable) -> None:
        """
        Register cleanup function to execute on application exit.

        Args:
            handler: Cleanup function to call during shutdown
        """
        pass

    @abstractmethod
    def request_application_exit(self) -> None:
        """
        Request graceful application shutdown with cleanup.
        """
        pass

    @abstractmethod
    def force_application_exit(self) -> None:
        """
        Force immediate application termination.
        """
        pass

    @abstractmethod
    def is_exit_in_progress(self) -> bool:
        """
        Check if application exit sequence is currently running.

        Returns:
            bool: True if exit is in progress
        """
        pass


class TkinterDeprecationInterface(ABC):
    """Interface for Tkinter version deprecation"""

    @abstractmethod
    def is_tkinter_blocked(self) -> bool:
        """
        Check if Tkinter version access is blocked.

        Returns:
            bool: True if Tkinter version is inaccessible
        """
        pass

    @abstractmethod
    def get_deprecation_message(self) -> str:
        """
        Get deprecation message for Tkinter version.

        Returns:
            str: Message directing users to Qt version
        """
        pass

    @abstractmethod
    def redirect_to_qt_version(self) -> None:
        """
        Redirect user to Qt version of application.
        """
        pass