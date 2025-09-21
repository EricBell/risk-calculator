"""
Unit tests for FormValidationState model.
Tests aggregated validation state for entire forms.
"""

import pytest
from typing import Dict

# Import the models that will be implemented
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFormValidationState:
    """Test FormValidationState model functionality."""

    def test_form_validation_state_creation(self):
        """Test creating FormValidationState with valid data."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState(
            form_id="equity_tab",
            field_states=field_states,
            has_errors=False,
            all_required_filled=True,
            is_submittable=True
        )

        assert form_state.form_id == "equity_tab"
        assert len(form_state.field_states) == 2
        assert form_state.has_errors is False
        assert form_state.all_required_filled is True
        assert form_state.is_submittable is True

    def test_form_validation_state_with_errors(self):
        """Test FormValidationState with field errors."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="abc",
                is_valid=False,
                error_message="Must be a number",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="",
                is_valid=False,
                error_message="Required field",
                is_required=True
            )
        }

        form_state = FormValidationState(
            form_id="equity_tab",
            field_states=field_states,
            has_errors=True,
            all_required_filled=False,
            is_submittable=False
        )

        assert form_state.has_errors is True
        assert form_state.all_required_filled is False
        assert form_state.is_submittable is False

    def test_form_validation_state_aggregation_logic(self):
        """Test that aggregated state correctly reflects field states."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Mix of valid and invalid fields
        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="abc",
                is_valid=False,
                error_message="Must be a number",
                is_required=True
            ),
            "entry_price": FieldValidationState(
                field_name="entry_price",
                value="50.00",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        # Should detect that there are errors
        assert form_state.has_errors is True
        # Should detect that not all required fields are valid
        assert form_state.all_required_filled is False
        # Should not be submittable
        assert form_state.is_submittable is False

    def test_form_validation_state_all_valid_fields(self):
        """Test FormValidationState when all fields are valid."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "entry_price": FieldValidationState(
                field_name="entry_price",
                value="50.00",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        assert form_state.has_errors is False
        assert form_state.all_required_filled is True
        assert form_state.is_submittable is True

    def test_form_validation_state_optional_fields(self):
        """Test FormValidationState with optional fields."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "notes": FieldValidationState(
                field_name="notes",
                value="",  # Empty optional field
                is_valid=True,
                error_message="",
                is_required=False
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        # Should be submittable even with empty optional field
        assert form_state.has_errors is False
        assert form_state.all_required_filled is True
        assert form_state.is_submittable is True

    def test_form_validation_state_update_field(self):
        """Test updating a single field in the form state."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        initial_field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", initial_field_states)

        # Update field with new value
        new_field_state = FieldValidationState(
            field_name="account_size",
            value="20000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        updated_form_state = form_state.update_field("account_size", new_field_state)

        assert updated_form_state.field_states["account_size"].value == "20000"
        assert updated_form_state is not form_state  # Should return new instance

    def test_form_validation_state_add_field(self):
        """Test adding a new field to the form state."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        initial_field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", initial_field_states)

        # Add new field
        new_field_state = FieldValidationState(
            field_name="risk_percentage",
            value="2",
            is_valid=True,
            error_message="",
            is_required=True
        )

        updated_form_state = form_state.add_field("risk_percentage", new_field_state)

        assert len(updated_form_state.field_states) == 2
        assert "risk_percentage" in updated_form_state.field_states
        assert updated_form_state.field_states["risk_percentage"].value == "2"

    def test_form_validation_state_remove_field(self):
        """Test removing a field from the form state."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        initial_field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", initial_field_states)

        updated_form_state = form_state.remove_field("risk_percentage")

        assert len(updated_form_state.field_states) == 1
        assert "risk_percentage" not in updated_form_state.field_states
        assert "account_size" in updated_form_state.field_states

    def test_form_validation_state_get_error_fields(self):
        """Test getting list of fields with errors."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="abc",
                is_valid=False,
                error_message="Must be a number",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "entry_price": FieldValidationState(
                field_name="entry_price",
                value="",
                is_valid=False,
                error_message="Required field",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        error_fields = form_state.get_error_fields()

        assert len(error_fields) == 2
        assert "account_size" in error_fields
        assert "entry_price" in error_fields
        assert "risk_percentage" not in error_fields

    def test_form_validation_state_get_error_messages(self):
        """Test getting error messages for all fields with errors."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="abc",
                is_valid=False,
                error_message="Must be a number",
                is_required=True
            ),
            "entry_price": FieldValidationState(
                field_name="entry_price",
                value="",
                is_valid=False,
                error_message="Required field",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        error_messages = form_state.get_error_messages()

        assert len(error_messages) == 2
        assert error_messages["account_size"] == "Must be a number"
        assert error_messages["entry_price"] == "Required field"

    def test_form_validation_state_to_dict(self):
        """Test serialization to dictionary."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        form_dict = form_state.to_dict()

        assert form_dict['form_id'] == "test_form"
        assert 'field_states' in form_dict
        assert 'has_errors' in form_dict
        assert 'all_required_filled' in form_dict
        assert 'is_submittable' in form_dict

    def test_form_validation_state_from_dict(self):
        """Test deserialization from dictionary."""
        from risk_calculator.models.form_validation_state import FormValidationState

        form_dict = {
            'form_id': "equity_tab",
            'field_states': {
                "account_size": {
                    'field_name': "account_size",
                    'value': "10000",
                    'is_valid': True,
                    'error_message': "",
                    'is_required': True
                }
            },
            'has_errors': False,
            'all_required_filled': True,
            'is_submittable': True
        }

        form_state = FormValidationState.from_dict(form_dict)

        assert form_state.form_id == "equity_tab"
        assert len(form_state.field_states) == 1
        assert form_state.has_errors is False
        assert form_state.all_required_filled is True
        assert form_state.is_submittable is True

    def test_form_validation_state_method_change_impact(self):
        """Test form validation when risk calculation method changes."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Initial state for percentage method
        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        form_state = FormValidationState.from_field_states("test_form", field_states)

        # Change to fixed amount method (different required fields)
        fixed_method_fields = ["account_size", "fixed_risk_amount"]

        updated_form_state = form_state.update_required_fields(fixed_method_fields)

        # Should re-evaluate based on new requirements
        assert isinstance(updated_form_state, FormValidationState)

    def test_form_validation_state_copy(self):
        """Test copying form validation state."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        original = FormValidationState.from_field_states("test_form", field_states)

        copy = original.copy()

        # Should have same values
        assert copy.form_id == original.form_id
        assert len(copy.field_states) == len(original.field_states)
        assert copy.has_errors == original.has_errors
        assert copy.all_required_filled == original.all_required_filled
        assert copy.is_submittable == original.is_submittable

        # But be different objects
        assert copy is not original

    def test_form_validation_state_factory_methods(self):
        """Test factory methods for common form validation state patterns."""
        from risk_calculator.models.form_validation_state import FormValidationState

        # Empty form
        empty_form = FormValidationState.create_empty("test_form")
        assert empty_form.form_id == "test_form"
        assert len(empty_form.field_states) == 0
        assert empty_form.all_required_filled is True  # No required fields
        assert empty_form.is_submittable is True

        # Form with validation errors
        error_form = FormValidationState.create_with_errors("test_form", {
            "field1": "Error message 1",
            "field2": "Error message 2"
        })
        assert error_form.has_errors is True
        assert error_form.is_submittable is False

    @pytest.fixture
    def sample_form_state(self):
        """Fixture providing a sample form validation state."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            ),
            "risk_percentage": FieldValidationState(
                field_name="risk_percentage",
                value="2",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        return FormValidationState.from_field_states("equity_tab", field_states)