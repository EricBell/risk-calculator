"""
Enhanced ValidationService implementation.
Extends existing validation with detailed error messaging and form state management.
"""

import re
from typing import Dict, List, Optional, Any
from decimal import Decimal, InvalidOperation

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import contract interfaces with fallback
try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from validation_service import (
        ValidationService, ValidationResult as ContractValidationResult, FieldValidationState,
        FormValidationState, TradeType, ValidationError
    )

    # Use contract interface as base
    class ValidationService(ValidationService):
        pass

except ImportError:
    # Fallback for development
    from abc import ABC, abstractmethod
    from enum import Enum

    class TradeType(Enum):
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"

    class ValidationService(ABC):
        pass

class ValidationResult:
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message

    def __bool__(self) -> bool:
        return self.is_valid

# Import local models
from risk_calculator.models.field_validation_state import FieldValidationState
from risk_calculator.models.form_validation_state import FormValidationState


class EnhancedValidationService(ValidationService):
    """Enhanced validation service with detailed error messaging."""

    def __init__(self):
        """Initialize validation service with field rules."""
        self._field_rules = self._initialize_field_rules()
        self._required_fields_map = self._initialize_required_fields()

    def _initialize_field_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for each field."""
        return {
            "account_size": {
                "type": "decimal",
                "min": 0.01,
                "max": 100000000,  # 100 million
                "required": True,
                "label": "Account Size"
            },
            "risk_percentage": {
                "type": "decimal",
                "min": 0.01,
                "max": 100,
                "required": True,
                "label": "Risk Percentage"
            },
            "fixed_risk_amount": {
                "type": "decimal",
                "min": 0.01,
                "max": 1000000,  # 1 million
                "required": False,  # Only required for fixed amount method
                "label": "Fixed Risk Amount"
            },
            "level_amount": {
                "type": "decimal",
                "min": 0.01,
                "max": 1000000,
                "required": False,  # Only required for level-based method
                "label": "Level Amount"
            },
            "entry_price": {
                "type": "decimal",
                "min": 0.01,
                "max": 1000000,
                "required": True,
                "label": "Entry Price"
            },
            "stop_loss": {
                "type": "decimal",
                "min": 0.01,
                "max": 1000000,
                "required": True,
                "label": "Stop Loss"
            },
            "premium": {
                "type": "decimal",
                "min": 0.01,
                "max": 10000,
                "required": True,
                "label": "Premium"
            },
            "tick_value": {
                "type": "decimal",
                "min": 0.01,
                "max": 10000,
                "required": True,
                "label": "Tick Value"
            }
        }

    def _initialize_required_fields(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize required fields map for each trade type and method."""
        return {
            "equity": {
                "percentage": ["account_size", "risk_percentage", "entry_price", "stop_loss"],
                "fixed": ["account_size", "fixed_risk_amount", "entry_price", "stop_loss"],
                "level": ["account_size", "level_amount", "entry_price", "stop_loss"]
            },
            "option": {
                "percentage": ["account_size", "risk_percentage", "premium"],
                "fixed": ["account_size", "fixed_risk_amount", "premium"],
                "level": ["account_size", "level_amount", "premium"]
            },
            "future": {
                "percentage": ["account_size", "risk_percentage", "entry_price", "stop_loss", "tick_value"],
                "fixed": ["account_size", "fixed_risk_amount", "entry_price", "stop_loss", "tick_value"],
                "level": ["account_size", "level_amount", "entry_price", "stop_loss", "tick_value"]
            }
        }

    def validate_field(self, field_name: str, value: str, trade_type: TradeType) -> ValidationResult:
        """
        Validate individual field value with detailed error messaging.

        Args:
            field_name: Name of field being validated
            value: Field value to validate
            trade_type: Type of trade for context-specific validation

        Returns:
            ValidationResult: Validation result with error message if invalid
        """
        try:
            # Handle None or empty string
            if value is None:
                value = ""

            # Convert to string if not already
            value_str = str(value).strip()

            # Get field rules
            rules = self._field_rules.get(field_name, {})

            if not rules:
                # Unknown field - assume valid
                return ValidationResult(True, "")

            # Check if field is empty
            if not value_str:
                # Empty field is only invalid if it's required
                if rules.get("required", False):
                    return ValidationResult(False, f"{rules.get('label', field_name)} is required")
                else:
                    return ValidationResult(True, "")

            # Validate based on field type
            field_type = rules.get("type", "string")

            if field_type == "decimal":
                return self._validate_decimal_field(field_name, value_str, rules)
            elif field_type == "string":
                return self._validate_string_field(field_name, value_str, rules)
            else:
                return ValidationResult(True, "")

        except Exception as e:
            return ValidationResult(False, f"Validation error for {field_name}")

    def _validate_decimal_field(self, field_name: str, value: str, rules: Dict[str, Any]) -> ValidationResult:
        """Validate decimal field with range checking."""
        try:
            # Try to convert to decimal
            decimal_value = Decimal(value)

            # Check minimum value
            min_val = rules.get("min")
            if min_val is not None and decimal_value < Decimal(str(min_val)):
                return ValidationResult(
                    False,
                    f"{rules.get('label', field_name)} must be at least {min_val}"
                )

            # Check maximum value
            max_val = rules.get("max")
            if max_val is not None and decimal_value > Decimal(str(max_val)):
                return ValidationResult(
                    False,
                    f"{rules.get('label', field_name)} cannot exceed {max_val}"
                )

            # Additional business logic validation
            if field_name == "risk_percentage" and decimal_value > 50:
                return ValidationResult(
                    False,
                    "Risk percentage above 50% is not recommended"
                )

            return ValidationResult(True, "")

        except (InvalidOperation, ValueError, TypeError):
            return ValidationResult(
                False,
                f"{rules.get('label', field_name)} must be a valid number"
            )

    def _validate_string_field(self, field_name: str, value: str, rules: Dict[str, Any]) -> ValidationResult:
        """Validate string field."""
        # Basic string validation - can be extended as needed
        min_length = rules.get("min_length", 0)
        max_length = rules.get("max_length", 1000)

        if len(value) < min_length:
            return ValidationResult(
                False,
                f"{rules.get('label', field_name)} must be at least {min_length} characters"
            )

        if len(value) > max_length:
            return ValidationResult(
                False,
                f"{rules.get('label', field_name)} cannot exceed {max_length} characters"
            )

        return ValidationResult(True, "")

    def validate_form(self, form_data: Dict[str, str], trade_type: TradeType) -> FormValidationState:
        """
        Validate entire form and return aggregated state.

        Args:
            form_data: Dictionary of field_name -> value pairs
            trade_type: Type of trade for validation context

        Returns:
            FormValidationState: Complete validation state for form
        """
        field_states = {}

        # Get all possible fields for this trade type
        all_possible_fields = set()
        for method_fields in self._required_fields_map.get(trade_type.value, {}).values():
            all_possible_fields.update(method_fields)

        # Add any additional fields from form_data
        all_possible_fields.update(form_data.keys())

        # Validate each field
        for field_name in all_possible_fields:
            field_value = form_data.get(field_name, "")

            # Determine if field is required (assume percentage method for now)
            required_fields = self.get_required_fields(trade_type, "percentage")
            is_required = field_name in required_fields

            # Validate the field
            validation_result = self.validate_field(field_name, field_value, trade_type)

            # Create field validation state
            field_state = FieldValidationState(
                field_name=field_name,
                value=field_value,
                is_valid=validation_result.is_valid,
                error_message=validation_result.error_message,
                is_required=is_required
            )

            field_states[field_name] = field_state

        # Create form validation state
        form_id = f"{trade_type.value}_form"
        return FormValidationState.from_field_states(form_id, field_states)

    def get_required_fields(self, trade_type: TradeType, risk_method: str) -> List[str]:
        """
        Get list of required fields for given trade type and risk method.

        Args:
            trade_type: Type of trade (equity, option, future)
            risk_method: Risk calculation method (percentage, fixed, level)

        Returns:
            List[str]: Names of required fields
        """
        trade_type_str = trade_type.value if hasattr(trade_type, 'value') else str(trade_type)

        return self._required_fields_map.get(trade_type_str, {}).get(risk_method, [])

    def get_validation_rules(self, field_name: str) -> Dict[str, Any]:
        """
        Get validation rules for specific field.

        Args:
            field_name: Name of field to get rules for

        Returns:
            Dict[str, Any]: Validation rules (min, max, type, pattern, etc.)
        """
        return self._field_rules.get(field_name, {}).copy()

    def format_error_message(self, field_name: str, error_type: str, **kwargs) -> str:
        """
        Format user-friendly error message for field validation failure.

        Args:
            field_name: Name of field with error
            error_type: Type of validation error (required, invalid, out_of_range)
            **kwargs: Additional context for error message formatting

        Returns:
            str: Formatted error message for display to user
        """
        rules = self._field_rules.get(field_name, {})
        label = rules.get('label', field_name.replace('_', ' ').title())

        if error_type == "required":
            return f"{label} is required"

        elif error_type == "invalid":
            field_type = rules.get('type', 'string')
            if field_type == "decimal":
                return f"{label} must be a valid number"
            else:
                return f"{label} has an invalid value"

        elif error_type == "out_of_range":
            min_val = kwargs.get('min_value')
            max_val = kwargs.get('max_value')

            if min_val is not None and max_val is not None:
                return f"{label} must be between {min_val} and {max_val}"
            elif min_val is not None:
                return f"{label} must be at least {min_val}"
            elif max_val is not None:
                return f"{label} cannot exceed {max_val}"
            else:
                return f"{label} is out of valid range"

        elif error_type == "negative":
            return f"{label} must be a positive number"

        elif error_type == "too_high_risk":
            return f"{label} above 50% is not recommended for risk management"

        else:
            return f"{label} has an error"

    def validate_business_rules(self, form_data: Dict[str, str], trade_type: TradeType) -> List[str]:
        """
        Validate business-specific rules across multiple fields.

        Args:
            form_data: Form data to validate
            trade_type: Type of trade

        Returns:
            List[str]: List of business rule violation messages
        """
        violations = []

        try:
            # For equity trades, ensure stop loss is different from entry price
            if trade_type == TradeType.EQUITY:
                entry_price = form_data.get("entry_price", "")
                stop_loss = form_data.get("stop_loss", "")

                if entry_price and stop_loss:
                    try:
                        entry_decimal = Decimal(entry_price)
                        stop_decimal = Decimal(stop_loss)

                        if entry_decimal == stop_decimal:
                            violations.append("Stop loss must be different from entry price")

                    except (InvalidOperation, ValueError):
                        pass  # Individual field validation will catch this

            # Risk percentage warnings
            risk_percentage = form_data.get("risk_percentage", "")
            if risk_percentage:
                try:
                    risk_decimal = Decimal(risk_percentage)
                    if risk_decimal > 10:
                        violations.append("Risk percentage above 10% requires careful consideration")
                except (InvalidOperation, ValueError):
                    pass

        except Exception:
            pass  # Don't let business rule validation crash the application

        return violations