"""
Enhanced form validation service implementation.
Part of Phase 3.4: Validation Services implementation.
"""

from typing import Dict, List, Any, Optional
import re
import time
from decimal import Decimal, InvalidOperation
from abc import ABC, abstractmethod

from ..models.form_validation_state import FormValidationState
# from .validation_service import ValidationService  # Commented out for now


class FormValidationInterface(ABC):
    """Contract interface for form validation functionality."""

    @abstractmethod
    def validate_field(self, field_name: str, field_value: Any) -> Optional[str]:
        pass

    @abstractmethod
    def validate_form(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        pass

    @abstractmethod
    def is_form_valid(self, form_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_required_fields(self, risk_method: str) -> List[str]:
        pass

    @abstractmethod
    def clear_validation_errors(self) -> None:
        pass


class EnhancedFormValidationService(FormValidationInterface):
    """
    Enhanced form validation service implementing FormValidationInterface.

    This service provides comprehensive validation for all form fields with
    support for different risk calculation methods and real-time validation.
    """

    def __init__(self):
        """Initialize the enhanced form validation service."""
        # self.validation_service = ValidationService()  # Commented out for now
        self._current_risk_method = "percentage"
        self._cached_required_fields = {}

        # Field validation patterns
        self._validation_patterns = {
            'numeric': re.compile(r'^-?\d*\.?\d+$'),
            'positive_numeric': re.compile(r'^\d*\.?\d+$'),
            'integer': re.compile(r'^\d+$'),
            'decimal': re.compile(r'^\d*\.\d+$')
        }

        # Field validation rules
        self._field_rules = {
            'account_size': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 10000000000,  # 10 billion
                'decimal_places': 2
            },
            'risk_percentage': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 100,
                'decimal_places': 2
            },
            'fixed_risk_amount': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 1000000000,  # 1 billion
                'decimal_places': 2
            },
            'level': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 1000000,
                'decimal_places': 4
            },
            'entry_price': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 1000000,
                'decimal_places': 4
            },
            'stop_loss_price': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 1000000,
                'decimal_places': 4
            },
            'option_premium': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 10000,
                'decimal_places': 4
            },
            'tick_value': {
                'required': True,
                'type': 'positive_numeric',
                'min_value': 0.01,
                'max_value': 1000,
                'decimal_places': 4
            },
            'ticks_at_risk': {
                'required': True,
                'type': 'integer',
                'min_value': 1,
                'max_value': 10000
            }
        }

    def validate_field(self, field_name: str, field_value: Any) -> Optional[str]:
        """
        Validate a single field and return error message if invalid.

        Args:
            field_name: Name of the field to validate
            field_value: Value to validate

        Returns:
            None if valid, error message string if invalid
        """
        # Convert value to string and strip whitespace
        value_str = str(field_value).strip() if field_value is not None else ""

        # Get field rules - return None for unknown fields instead of error
        rules = self._field_rules.get(field_name)
        if not rules:
            return None  # Ignore unknown fields

        # Check if field is required and empty
        if rules.get('required', False) and not value_str:
            return f"{self._format_field_name(field_name)} is required"

        # If field is empty and not required, it's valid
        if not value_str:
            return None

        # Validate field type
        field_type = rules.get('type', 'text')
        type_error = self._validate_field_type(field_name, value_str, field_type)
        if type_error:
            return type_error

        # Validate numeric constraints
        if field_type in ['numeric', 'positive_numeric', 'integer', 'decimal']:
            numeric_error = self._validate_numeric_constraints(field_name, value_str, rules)
            if numeric_error:
                return numeric_error

        # Validate percentage-specific constraints
        if field_name == 'risk_percentage':
            percentage_error = self._validate_percentage(value_str)
            if percentage_error:
                return percentage_error

        # Validate logical constraints (e.g., stop loss vs entry price)
        logical_error = self._validate_logical_constraints(field_name, value_str)
        if logical_error:
            return logical_error

        return None

    def validate_form(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate entire form and return all errors.

        Args:
            form_data: Dictionary of field names to values

        Returns:
            Dictionary mapping field names to error messages
        """
        errors = {}

        # Get required fields for current risk method
        required_fields = self.get_required_fields(self._current_risk_method)

        # Only validate required fields for current risk method
        for required_field in required_fields:
            field_value = form_data.get(required_field)

            # Check if required field is missing or empty
            if not field_value or not str(field_value).strip():
                errors[required_field] = f"{self._format_field_name(required_field)} is required"
            else:
                # Validate the field value
                error = self.validate_field(required_field, field_value)
                if error:
                    errors[required_field] = error

        # Cross-field validation
        cross_field_errors = self._validate_cross_field_constraints(form_data)
        errors.update(cross_field_errors)

        return errors

    def is_form_valid(self, form_data: Dict[str, Any]) -> bool:
        """
        Check if entire form is valid.

        Args:
            form_data: Dictionary of field names to values

        Returns:
            True if all fields are valid, False otherwise
        """
        errors = self.validate_form(form_data)
        return len(errors) == 0

    def get_required_fields(self, risk_method: str) -> List[str]:
        """
        Get list of required fields for a specific risk method.

        Args:
            risk_method: Risk calculation method ('percentage', 'fixed_amount', 'level')

        Returns:
            List of required field names
        """
        # Cache required fields to avoid recalculation
        if risk_method in self._cached_required_fields:
            return self._cached_required_fields[risk_method]

        base_fields = ['account_size']

        if risk_method == 'percentage':
            required_fields = base_fields + ['risk_percentage', 'entry_price', 'stop_loss_price']
        elif risk_method == 'fixed_amount':
            required_fields = base_fields + ['fixed_risk_amount', 'entry_price', 'stop_loss_price']
        elif risk_method == 'level':
            required_fields = base_fields + ['level', 'entry_price', 'stop_loss_price']
        elif risk_method == 'options':
            required_fields = base_fields + ['fixed_risk_amount', 'option_premium']
        elif risk_method == 'futures':
            required_fields = base_fields + ['fixed_risk_amount', 'tick_value', 'ticks_at_risk']
        else:
            required_fields = base_fields

        self._cached_required_fields[risk_method] = required_fields
        return required_fields

    def clear_validation_errors(self) -> None:
        """Clear all stored validation errors."""
        # This service is stateless, so no stored errors to clear
        pass

    def set_risk_method(self, risk_method: str) -> None:
        """
        Set the current risk method for validation.

        Args:
            risk_method: Risk calculation method
        """
        self._current_risk_method = risk_method

    def _validate_field_type(self, field_name: str, value: str, field_type: str) -> Optional[str]:
        """
        Validate field type constraints.

        Args:
            field_name: Name of the field
            value: Field value
            field_type: Expected field type

        Returns:
            Error message if invalid, None if valid
        """
        if field_type == 'numeric':
            if not self._validation_patterns['numeric'].match(value):
                return f"{self._format_field_name(field_name)} must be a valid number"

        elif field_type == 'positive_numeric':
            if not self._validation_patterns['positive_numeric'].match(value):
                return f"{self._format_field_name(field_name)} must be a positive number"
            try:
                if float(value) <= 0:
                    return f"{self._format_field_name(field_name)} must be greater than zero"
            except ValueError:
                return f"{self._format_field_name(field_name)} must be a valid number"

        elif field_type == 'integer':
            if not self._validation_patterns['integer'].match(value):
                return f"{self._format_field_name(field_name)} must be a whole number"

        elif field_type == 'decimal':
            if not self._validation_patterns['decimal'].match(value) and not self._validation_patterns['integer'].match(value):
                return f"{self._format_field_name(field_name)} must be a decimal number"

        return None

    def _validate_numeric_constraints(self, field_name: str, value: str, rules: Dict[str, Any]) -> Optional[str]:
        """
        Validate numeric constraints like min/max values and decimal places.

        Args:
            field_name: Name of the field
            value: Field value
            rules: Field validation rules

        Returns:
            Error message if invalid, None if valid
        """
        try:
            numeric_value = Decimal(value)
        except InvalidOperation:
            return f"{self._format_field_name(field_name)} must be a valid number"

        # Check minimum value
        min_value = rules.get('min_value')
        if min_value is not None and numeric_value < Decimal(str(min_value)):
            return f"{self._format_field_name(field_name)} must be at least {min_value}"

        # Check maximum value
        max_value = rules.get('max_value')
        if max_value is not None and numeric_value > Decimal(str(max_value)):
            return f"{self._format_field_name(field_name)} cannot exceed {max_value}"

        # Check decimal places
        decimal_places = rules.get('decimal_places')
        if decimal_places is not None:
            try:
                # Count decimal places
                decimal_str = str(numeric_value)
                if '.' in decimal_str:
                    actual_decimal_places = len(decimal_str.split('.')[1])
                    if actual_decimal_places > decimal_places:
                        return f"{self._format_field_name(field_name)} can have at most {decimal_places} decimal places"
            except:
                pass

        return None

    def _validate_percentage(self, value: str) -> Optional[str]:
        """
        Validate percentage-specific constraints.

        Args:
            value: Percentage value

        Returns:
            Error message if invalid, None if valid
        """
        try:
            percentage = float(value)
            if percentage <= 0:
                return "Risk percentage must be greater than 0"
            if percentage > 100:
                return "Risk percentage cannot exceed 100%"
        except ValueError:
            return "Risk percentage must be a valid number"

        return None

    def _validate_logical_constraints(self, field_name: str, value: str) -> Optional[str]:
        """
        Validate logical constraints specific to trading fields.

        Args:
            field_name: Name of the field
            value: Field value

        Returns:
            Error message if invalid, None if valid
        """
        # For now, just validate that prices are reasonable
        if field_name in ['entry_price', 'stop_loss_price', 'level']:
            try:
                price = float(value)
                if price <= 0:
                    return f"{self._format_field_name(field_name)} must be greater than zero"
                if price > 1000000:  # Very high price guard
                    return f"{self._format_field_name(field_name)} seems unusually high"
            except ValueError:
                return f"{self._format_field_name(field_name)} must be a valid price"

        return None

    def _validate_cross_field_constraints(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate constraints that span multiple fields.

        Args:
            form_data: Dictionary of field names to values

        Returns:
            Dictionary of field names to error messages
        """
        errors = {}

        # Validate entry price vs stop loss relationship
        entry_price_str = str(form_data.get('entry_price', '')).strip()
        stop_loss_str = str(form_data.get('stop_loss_price', '')).strip()

        if entry_price_str and stop_loss_str:
            try:
                entry_price = float(entry_price_str)
                stop_loss = float(stop_loss_str)

                # For long positions, stop loss should be below entry
                # For simplicity, we'll assume long positions for now
                if stop_loss >= entry_price:
                    errors['stop_loss_price'] = "Stop loss must be below entry price for long positions"

                # Check that the difference is reasonable
                risk_per_share = entry_price - stop_loss
                if risk_per_share / entry_price > 0.5:  # More than 50% risk per share
                    errors['stop_loss_price'] = "Risk per share is very high (>50%)"

            except ValueError:
                pass  # Individual field validation will catch invalid numbers

        # Validate risk amount vs account size
        account_size_str = str(form_data.get('account_size', '')).strip()
        fixed_risk_str = str(form_data.get('fixed_risk_amount', '')).strip()

        if account_size_str and fixed_risk_str:
            try:
                account_size = float(account_size_str)
                fixed_risk = float(fixed_risk_str)

                if fixed_risk > account_size:
                    errors['fixed_risk_amount'] = "Risk amount cannot exceed account size"

                risk_percentage = (fixed_risk / account_size) * 100
                if risk_percentage > 50:
                    errors['fixed_risk_amount'] = f"Risk amount is {risk_percentage:.1f}% of account (very high)"

            except ValueError:
                pass

        return errors

    def _format_field_name(self, field_name: str) -> str:
        """
        Format field name for display in error messages.

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
            'option_premium': 'Option Premium',
            'tick_value': 'Tick Value',
            'ticks_at_risk': 'Ticks at Risk'
        }

        return field_name_mapping.get(field_name, field_name.replace('_', ' ').title())

    def create_form_validation_state(self, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a form validation state summary from form data.

        Args:
            form_id: Unique identifier for the form
            form_data: Dictionary of field names to values

        Returns:
            Dictionary with validation results summary
        """
        errors = self.validate_form(form_data)
        return {
            'form_id': form_id,
            'risk_method': self._current_risk_method,
            'errors': errors,
            'is_valid': len(errors) == 0,
            'timestamp': time.time()
        }