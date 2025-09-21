"""
Enhanced Validation Service Contract
API contract for form validation with error message support
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ValidationResult:
    """Result of field validation"""

    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message

    def __bool__(self) -> bool:
        return self.is_valid


@dataclass
class FieldValidationState:
    """Validation state for a single form field"""
    field_name: str
    value: str
    is_valid: bool
    error_message: str
    is_required: bool


@dataclass
class FormValidationState:
    """Aggregated validation state for entire form"""
    form_id: str
    field_states: Dict[str, FieldValidationState]
    has_errors: bool
    all_required_filled: bool
    is_submittable: bool


class TradeType(Enum):
    """Trade types for validation context"""
    EQUITY = "equity"
    OPTION = "option"
    FUTURE = "future"


class ValidationService(ABC):
    """Abstract interface for enhanced validation with error messaging"""

    @abstractmethod
    def validate_field(self, field_name: str, value: str, trade_type: TradeType) -> ValidationResult:
        """
        Validate individual field value with detailed error messaging

        Args:
            field_name: Name of field being validated
            value: Field value to validate
            trade_type: Type of trade for context-specific validation

        Returns:
            ValidationResult: Validation result with error message if invalid
        """
        pass

    @abstractmethod
    def validate_form(self, form_data: Dict[str, str], trade_type: TradeType) -> FormValidationState:
        """
        Validate entire form and return aggregated state

        Args:
            form_data: Dictionary of field_name -> value pairs
            trade_type: Type of trade for validation context

        Returns:
            FormValidationState: Complete validation state for form
        """
        pass

    @abstractmethod
    def get_required_fields(self, trade_type: TradeType, risk_method: str) -> List[str]:
        """
        Get list of required fields for given trade type and risk method

        Args:
            trade_type: Type of trade (equity, option, future)
            risk_method: Risk calculation method (percentage, fixed, level)

        Returns:
            List[str]: Names of required fields
        """
        pass

    @abstractmethod
    def get_validation_rules(self, field_name: str) -> Dict[str, Any]:
        """
        Get validation rules for specific field

        Args:
            field_name: Name of field to get rules for

        Returns:
            Dict[str, Any]: Validation rules (min, max, type, pattern, etc.)
        """
        pass

    @abstractmethod
    def format_error_message(self, field_name: str, error_type: str, **kwargs) -> str:
        """
        Format user-friendly error message for field validation failure

        Args:
            field_name: Name of field with error
            error_type: Type of validation error (required, invalid, out_of_range)
            **kwargs: Additional context for error message formatting

        Returns:
            str: Formatted error message for display to user
        """
        pass


class ValidationError(Exception):
    """Exception raised for validation service errors"""
    pass