"""
FieldValidationState model implementation.
Tracks validation status for individual form fields.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class FieldValidationState:
    """Validation state for a single form field."""

    field_name: str
    value: str
    is_valid: bool
    error_message: str
    is_required: bool

    def validate(self) -> bool:
        """
        Validate the field validation state itself.

        Returns:
            bool: True if the state is valid
        """
        # Field name cannot be empty
        if not self.field_name or not isinstance(self.field_name, str):
            return False

        # Value should be a string (may be empty)
        if not isinstance(self.value, str):
            return False

        # Error message required when is_valid is False
        if not self.is_valid and not self.error_message:
            return False

        # Boolean fields should be actual booleans
        if not isinstance(self.is_valid, bool) or not isinstance(self.is_required, bool):
            return False

        return True

    def auto_validate(self) -> 'FieldValidationState':
        """
        Auto-validate and correct state based on field requirements.

        Returns:
            FieldValidationState: Corrected validation state
        """
        # Required field with empty value should be invalid
        if self.is_required and not self.value.strip():
            return FieldValidationState(
                field_name=self.field_name,
                value=self.value,
                is_valid=False,
                error_message=f"{self.field_name.replace('_', ' ').title()} is required",
                is_required=self.is_required
            )

        # If currently marked as valid, keep as is
        if self.is_valid:
            return self

        # If marked as invalid but no error message, provide generic message
        if not self.is_valid and not self.error_message:
            return FieldValidationState(
                field_name=self.field_name,
                value=self.value,
                is_valid=False,
                error_message=f"Invalid value for {self.field_name.replace('_', ' ').title()}",
                is_required=self.is_required
            )

        return self

    def update_value(self, new_value: str, auto_validate: bool = False) -> 'FieldValidationState':
        """
        Update field value and optionally re-validate.

        Args:
            new_value: New field value
            auto_validate: Whether to auto-validate after update

        Returns:
            FieldValidationState: Updated state
        """
        # Ensure value is string
        value_str = str(new_value) if new_value is not None else ""

        updated_state = FieldValidationState(
            field_name=self.field_name,
            value=value_str,
            is_valid=self.is_valid,
            error_message=self.error_message,
            is_required=self.is_required
        )

        if auto_validate:
            return updated_state.auto_validate()
        return updated_state

    def clear_error(self) -> 'FieldValidationState':
        """
        Clear error state and mark as valid.

        Returns:
            FieldValidationState: State with error cleared
        """
        return FieldValidationState(
            field_name=self.field_name,
            value=self.value,
            is_valid=True,
            error_message="",
            is_required=self.is_required
        )

    def set_error(self, error_message: str) -> 'FieldValidationState':
        """
        Set error state with message.

        Args:
            error_message: Error message to set

        Returns:
            FieldValidationState: State with error set
        """
        return FieldValidationState(
            field_name=self.field_name,
            value=self.value,
            is_valid=False,
            error_message=error_message,
            is_required=self.is_required
        )

    def has_valid_field_name(self) -> bool:
        """
        Check if field name is valid (non-empty).

        Returns:
            bool: True if field name is valid
        """
        return bool(self.field_name and self.field_name.strip())

    def equals(self, other: 'FieldValidationState') -> bool:
        """
        Compare with another field validation state.

        Args:
            other: Other field validation state

        Returns:
            bool: True if states are equal
        """
        return (self.field_name == other.field_name and
                self.value == other.value and
                self.is_valid == other.is_valid and
                self.error_message == other.error_message and
                self.is_required == other.is_required)

    def copy(self) -> 'FieldValidationState':
        """
        Create a copy of the field validation state.

        Returns:
            FieldValidationState: Copy of this state
        """
        return FieldValidationState(
            field_name=self.field_name,
            value=self.value,
            is_valid=self.is_valid,
            error_message=self.error_message,
            is_required=self.is_required
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize field validation state to dictionary.

        Returns:
            Dict[str, Any]: Serialized state
        """
        return {
            'field_name': self.field_name,
            'value': self.value,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'is_required': self.is_required
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldValidationState':
        """
        Deserialize field validation state from dictionary.

        Args:
            data: Dictionary containing state data

        Returns:
            FieldValidationState: Deserialized state
        """
        return cls(
            field_name=data.get('field_name', ''),
            value=data.get('value', ''),
            is_valid=data.get('is_valid', True),
            error_message=data.get('error_message', ''),
            is_required=data.get('is_required', False)
        )

    @classmethod
    def create_initial(cls, field_name: str, value: Optional[str],
                      is_required: bool) -> 'FieldValidationState':
        """
        Create initial field validation state.

        Args:
            field_name: Name of the field
            value: Initial field value
            is_required: Whether field is required

        Returns:
            FieldValidationState: Initial state
        """
        # Convert None to empty string
        value_str = str(value) if value is not None else ""

        # Auto-validate initial state
        initial_state = cls(
            field_name=field_name,
            value=value_str,
            is_valid=True,  # Will be corrected by auto_validate if needed
            error_message="",
            is_required=is_required
        )

        return initial_state.auto_validate()

    @classmethod
    def create_valid(cls, field_name: str, value: str, is_required: bool) -> 'FieldValidationState':
        """
        Create valid field validation state.

        Args:
            field_name: Name of the field
            value: Field value
            is_required: Whether field is required

        Returns:
            FieldValidationState: Valid state
        """
        return cls(
            field_name=field_name,
            value=value,
            is_valid=True,
            error_message="",
            is_required=is_required
        )

    @classmethod
    def create_invalid(cls, field_name: str, value: str, error_message: str,
                      is_required: bool) -> 'FieldValidationState':
        """
        Create invalid field validation state.

        Args:
            field_name: Name of the field
            value: Field value
            error_message: Error message
            is_required: Whether field is required

        Returns:
            FieldValidationState: Invalid state
        """
        return cls(
            field_name=field_name,
            value=value,
            is_valid=False,
            error_message=error_message,
            is_required=is_required
        )

    @classmethod
    def create_required_empty(cls, field_name: str) -> 'FieldValidationState':
        """
        Create state for required field that is empty.

        Args:
            field_name: Name of the field

        Returns:
            FieldValidationState: Invalid state for required empty field
        """
        return cls(
            field_name=field_name,
            value="",
            is_valid=False,
            error_message=f"{field_name.replace('_', ' ').title()} is required",
            is_required=True
        )