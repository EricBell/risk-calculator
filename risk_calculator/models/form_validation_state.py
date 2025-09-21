"""
FormValidationState model implementation.
Aggregates validation state across all form fields.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from .field_validation_state import FieldValidationState


@dataclass
class FormValidationState:
    """Aggregated validation state for entire form."""

    form_id: str
    field_states: Dict[str, FieldValidationState]
    has_errors: bool
    all_required_filled: bool
    is_submittable: bool

    def _recalculate_aggregated_state(self) -> None:
        """Recalculate aggregated state based on field states."""
        # Check if any field has errors
        self.has_errors = any(
            not field_state.is_valid
            for field_state in self.field_states.values()
        )

        # Check if all required fields are filled and valid
        self.all_required_filled = all(
            not field_state.is_required or
            (field_state.value.strip() and field_state.is_valid)
            for field_state in self.field_states.values()
        )

        # Form is submittable if no errors and all required fields filled
        self.is_submittable = not self.has_errors and self.all_required_filled

    def update_field(self, field_name: str, field_state: FieldValidationState) -> 'FormValidationState':
        """
        Update a single field in the form state.

        Args:
            field_name: Name of field to update
            field_state: New field validation state

        Returns:
            FormValidationState: Updated form state
        """
        new_field_states = self.field_states.copy()
        new_field_states[field_name] = field_state

        new_form_state = FormValidationState(
            form_id=self.form_id,
            field_states=new_field_states,
            has_errors=self.has_errors,
            all_required_filled=self.all_required_filled,
            is_submittable=self.is_submittable
        )

        new_form_state._recalculate_aggregated_state()
        return new_form_state

    def add_field(self, field_name: str, field_state: FieldValidationState) -> 'FormValidationState':
        """
        Add a new field to the form state.

        Args:
            field_name: Name of field to add
            field_state: Field validation state

        Returns:
            FormValidationState: Updated form state
        """
        return self.update_field(field_name, field_state)

    def remove_field(self, field_name: str) -> 'FormValidationState':
        """
        Remove a field from the form state.

        Args:
            field_name: Name of field to remove

        Returns:
            FormValidationState: Updated form state
        """
        if field_name not in self.field_states:
            return self

        new_field_states = self.field_states.copy()
        del new_field_states[field_name]

        new_form_state = FormValidationState(
            form_id=self.form_id,
            field_states=new_field_states,
            has_errors=self.has_errors,
            all_required_filled=self.all_required_filled,
            is_submittable=self.is_submittable
        )

        new_form_state._recalculate_aggregated_state()
        return new_form_state

    def get_error_fields(self) -> List[str]:
        """
        Get list of field names that have errors.

        Returns:
            List[str]: Names of fields with errors
        """
        return [
            field_name for field_name, field_state in self.field_states.items()
            if not field_state.is_valid
        ]

    def get_error_messages(self) -> Dict[str, str]:
        """
        Get error messages for all fields with errors.

        Returns:
            Dict[str, str]: Map of field_name -> error_message
        """
        return {
            field_name: field_state.error_message
            for field_name, field_state in self.field_states.items()
            if not field_state.is_valid and field_state.error_message
        }

    def get_field_state(self, field_name: str) -> FieldValidationState:
        """
        Get validation state for a specific field.

        Args:
            field_name: Name of field

        Returns:
            FieldValidationState: Field validation state or None if not found
        """
        return self.field_states.get(field_name)

    def has_field(self, field_name: str) -> bool:
        """
        Check if form has a specific field.

        Args:
            field_name: Name of field

        Returns:
            bool: True if field exists
        """
        return field_name in self.field_states

    def update_required_fields(self, required_field_names: List[str]) -> 'FormValidationState':
        """
        Update which fields are required and re-evaluate form state.

        Args:
            required_field_names: List of field names that should be required

        Returns:
            FormValidationState: Updated form state
        """
        new_field_states = {}

        for field_name, field_state in self.field_states.items():
            is_required = field_name in required_field_names

            # Update the required status of the field
            new_field_state = FieldValidationState(
                field_name=field_state.field_name,
                value=field_state.value,
                is_valid=field_state.is_valid,
                error_message=field_state.error_message,
                is_required=is_required
            )

            # Re-validate if required status changed
            if is_required != field_state.is_required:
                new_field_state = new_field_state.auto_validate()

            new_field_states[field_name] = new_field_state

        new_form_state = FormValidationState(
            form_id=self.form_id,
            field_states=new_field_states,
            has_errors=self.has_errors,
            all_required_filled=self.all_required_filled,
            is_submittable=self.is_submittable
        )

        new_form_state._recalculate_aggregated_state()
        return new_form_state

    def copy(self) -> 'FormValidationState':
        """
        Create a copy of the form validation state.

        Returns:
            FormValidationState: Copy of this state
        """
        # Deep copy field states
        field_states_copy = {
            field_name: field_state.copy()
            for field_name, field_state in self.field_states.items()
        }

        return FormValidationState(
            form_id=self.form_id,
            field_states=field_states_copy,
            has_errors=self.has_errors,
            all_required_filled=self.all_required_filled,
            is_submittable=self.is_submittable
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize form validation state to dictionary.

        Returns:
            Dict[str, Any]: Serialized state
        """
        return {
            'form_id': self.form_id,
            'field_states': {
                field_name: field_state.to_dict()
                for field_name, field_state in self.field_states.items()
            },
            'has_errors': self.has_errors,
            'all_required_filled': self.all_required_filled,
            'is_submittable': self.is_submittable
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormValidationState':
        """
        Deserialize form validation state from dictionary.

        Args:
            data: Dictionary containing state data

        Returns:
            FormValidationState: Deserialized state
        """
        field_states = {}
        field_states_data = data.get('field_states', {})

        for field_name, field_data in field_states_data.items():
            field_states[field_name] = FieldValidationState.from_dict(field_data)

        form_state = cls(
            form_id=data.get('form_id', ''),
            field_states=field_states,
            has_errors=data.get('has_errors', False),
            all_required_filled=data.get('all_required_filled', True),
            is_submittable=data.get('is_submittable', True)
        )

        # Recalculate to ensure consistency
        form_state._recalculate_aggregated_state()
        return form_state

    @classmethod
    def from_field_states(cls, form_id: str,
                         field_states: Dict[str, FieldValidationState]) -> 'FormValidationState':
        """
        Create form validation state from field states.

        Args:
            form_id: Unique identifier for the form
            field_states: Dictionary of field validation states

        Returns:
            FormValidationState: Form state with calculated aggregates
        """
        form_state = cls(
            form_id=form_id,
            field_states=field_states.copy(),
            has_errors=False,
            all_required_filled=True,
            is_submittable=True
        )

        form_state._recalculate_aggregated_state()
        return form_state

    @classmethod
    def create_empty(cls, form_id: str) -> 'FormValidationState':
        """
        Create empty form validation state.

        Args:
            form_id: Unique identifier for the form

        Returns:
            FormValidationState: Empty form state
        """
        return cls(
            form_id=form_id,
            field_states={},
            has_errors=False,
            all_required_filled=True,  # No required fields = all filled
            is_submittable=True
        )

    @classmethod
    def create_with_errors(cls, form_id: str,
                          error_messages: Dict[str, str]) -> 'FormValidationState':
        """
        Create form validation state with specific error messages.

        Args:
            form_id: Unique identifier for the form
            error_messages: Map of field_name -> error_message

        Returns:
            FormValidationState: Form state with errors
        """
        field_states = {}

        for field_name, error_message in error_messages.items():
            field_states[field_name] = FieldValidationState.create_invalid(
                field_name=field_name,
                value="",
                error_message=error_message,
                is_required=True
            )

        return cls.from_field_states(form_id, field_states)