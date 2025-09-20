"""
Contract: Button Validation Service Interface
Purpose: Define the interface for button enablement validation logic
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RiskMethod(Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    LEVEL_BASED = "level_based"


class TabType(Enum):
    EQUITY = "equity"
    OPTIONS = "options"
    FUTURES = "futures"


@dataclass
class FieldValidationResult:
    """Result of validating a single form field."""
    field_name: str
    value: str
    is_valid: bool
    error_message: Optional[str]
    is_required: bool
    is_filled: bool


@dataclass
class ButtonValidationState:
    """State of the Calculate Position button enablement."""
    has_errors: bool
    required_fields_filled: bool
    validation_errors: Dict[str, str]
    
    @property
    def is_enabled(self) -> bool:
        """Button is enabled when no errors and all required fields filled."""
        return not self.has_errors and self.required_fields_filled


class IButtonValidationService(ABC):
    """Interface for Calculate Position button validation logic."""
    
    @abstractmethod
    def validate_field(self, field_name: str, value: str, 
                      tab_type: TabType, method: RiskMethod) -> FieldValidationResult:
        """
        Validate a single form field.
        
        Args:
            field_name: Name of the field being validated
            value: Current field value
            tab_type: Which calculation tab (equity/options/futures)
            method: Current risk calculation method
            
        Returns:
            FieldValidationResult with validation status and error message
            
        Raises:
            ValueError: If field_name is not recognized
        """
        pass
    
    @abstractmethod
    def get_required_fields(self, tab_type: TabType, method: RiskMethod) -> List[str]:
        """
        Get list of required field names for the given tab and method.
        
        Args:
            tab_type: Which calculation tab
            method: Current risk calculation method
            
        Returns:
            List of field names that must be filled
            
        Raises:
            ValueError: If method is not supported for tab_type
        """
        pass
    
    @abstractmethod
    def calculate_button_state(self, field_values: Dict[str, str],
                             tab_type: TabType, method: RiskMethod) -> ButtonValidationState:
        """
        Calculate the overall button enablement state.
        
        Args:
            field_values: Current values of all form fields
            tab_type: Which calculation tab
            method: Current risk calculation method
            
        Returns:
            ButtonValidationState with complete validation status
        """
        pass
    
    @abstractmethod
    def is_method_supported(self, tab_type: TabType, method: RiskMethod) -> bool:
        """
        Check if a risk method is supported on the given tab.
        
        Args:
            tab_type: Which calculation tab
            method: Risk calculation method to check
            
        Returns:
            True if method is supported, False otherwise
        """
        pass


class IButtonStateController(ABC):
    """Interface for controlling button state in the UI."""
    
    @abstractmethod
    def update_button_state(self, enabled: bool) -> None:
        """
        Update the Calculate Position button enabled/disabled state.
        
        Args:
            enabled: True to enable button, False to disable
        """
        pass
    
    @abstractmethod
    def display_field_error(self, field_name: str, error_message: str) -> None:
        """
        Display validation error for a specific field.
        
        Args:
            field_name: Name of the field with error
            error_message: Error message to display
        """
        pass
    
    @abstractmethod
    def clear_field_error(self, field_name: str) -> None:
        """
        Clear validation error display for a specific field.
        
        Args:
            field_name: Name of the field to clear
        """
        pass
    
    @abstractmethod
    def on_field_change(self, field_name: str, new_value: str) -> None:
        """
        Handle real-time field change events.
        
        Args:
            field_name: Name of the field that changed
            new_value: New field value
        """
        pass
    
    @abstractmethod
    def on_method_change(self, new_method: RiskMethod) -> None:
        """
        Handle risk method selection change.
        
        Args:
            new_method: Newly selected risk method
        """
        pass


# Expected behavior contracts for testing

class ButtonValidationBehaviorContract:
    """Contract defining expected button validation behaviors."""
    
    def test_button_starts_disabled(self) -> None:
        """Button must start in disabled state when form is empty."""
        pass
    
    def test_button_enables_with_valid_complete_form(self) -> None:
        """Button enables when all required fields are valid and filled."""
        pass
    
    def test_button_disables_on_validation_error(self) -> None:
        """Button disables immediately when any field becomes invalid."""
        pass
    
    def test_button_disables_on_required_field_clear(self) -> None:
        """Button disables when any required field is cleared."""
        pass
    
    def test_button_updates_on_method_change(self) -> None:
        """Button state recalculates when risk method changes."""
        pass
    
    def test_method_specific_requirements(self) -> None:
        """Different methods require different field combinations."""
        pass
    
    def test_tab_specific_support(self) -> None:
        """Options tab does not support level-based method."""
        pass
    
    def test_real_time_validation_performance(self) -> None:
        """Validation updates must complete within 100ms."""
        pass