"""
Unit tests for FieldValidationState model.
Tests validation status tracking for individual form fields.
"""

import pytest
from datetime import datetime

# Import the model that will be implemented
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFieldValidationState:
    """Test FieldValidationState model functionality."""

    def test_field_validation_state_creation(self):
        """Test creating FieldValidationState with valid data."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        state = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert state.field_name == "account_size"
        assert state.value == "10000"
        assert state.is_valid is True
        assert state.error_message == ""
        assert state.is_required is True

    def test_field_validation_state_with_error(self):
        """Test creating FieldValidationState with validation error."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        state = FieldValidationState(
            field_name="account_size",
            value="abc",
            is_valid=False,
            error_message="Account size must be a number",
            is_required=True
        )

        assert state.field_name == "account_size"
        assert state.value == "abc"
        assert state.is_valid is False
        assert state.error_message == "Account size must be a number"
        assert state.is_required is True

    def test_field_validation_state_validation_rules(self):
        """Test validation rules for FieldValidationState."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Valid state
        valid_state = FieldValidationState(
            field_name="test_field",
            value="test_value",
            is_valid=True,
            error_message="",
            is_required=False
        )
        assert valid_state.validate() is True

        # Invalid state - field_name cannot be empty
        invalid_state = FieldValidationState(
            field_name="",
            value="test_value",
            is_valid=True,
            error_message="",
            is_required=False
        )
        assert invalid_state.validate() is False

        # Invalid state - error_message required when is_valid is False
        invalid_state2 = FieldValidationState(
            field_name="test_field",
            value="test_value",
            is_valid=False,
            error_message="",
            is_required=False
        )
        assert invalid_state2.validate() is False

    def test_field_validation_state_required_field_empty_value(self):
        """Test validation of required fields with empty values."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Required field with empty value should be invalid
        state = FieldValidationState(
            field_name="account_size",
            value="",
            is_valid=True,  # This should be automatically corrected
            error_message="",
            is_required=True
        )

        # Should auto-correct to invalid state
        corrected_state = state.auto_validate()
        assert corrected_state.is_valid is False
        assert len(corrected_state.error_message) > 0

    def test_field_validation_state_transitions(self):
        """Test state transitions as specified in data model."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Created state - initial validation
        initial_state = FieldValidationState.create_initial("account_size", "", True)
        assert initial_state.field_name == "account_size"
        assert initial_state.value == ""
        assert initial_state.is_required is True

        # Value changed state - re-validation
        updated_state = initial_state.update_value("10000")
        assert updated_state.value == "10000"
        assert updated_state.field_name == initial_state.field_name
        assert updated_state.is_required == initial_state.is_required

        # Should re-validate automatically if auto_validate is True
        auto_validated = updated_state.update_value("abc", auto_validate=True)
        assert auto_validated.value == "abc"

    def test_field_validation_state_error_message_handling(self):
        """Test error message handling and clearing."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # State with error
        error_state = FieldValidationState(
            field_name="account_size",
            value="abc",
            is_valid=False,
            error_message="Invalid value",
            is_required=True
        )

        # Clear error
        cleared_state = error_state.clear_error()
        assert cleared_state.is_valid is True
        assert cleared_state.error_message == ""
        assert cleared_state.value == error_state.value  # Value preserved

        # Set error
        new_error_state = cleared_state.set_error("New error message")
        assert new_error_state.is_valid is False
        assert new_error_state.error_message == "New error message"

    def test_field_validation_state_to_dict(self):
        """Test serialization to dictionary."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        state = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        state_dict = state.to_dict()

        assert state_dict['field_name'] == "account_size"
        assert state_dict['value'] == "10000"
        assert state_dict['is_valid'] is True
        assert state_dict['error_message'] == ""
        assert state_dict['is_required'] is True

    def test_field_validation_state_from_dict(self):
        """Test deserialization from dictionary."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        state_dict = {
            'field_name': "risk_percentage",
            'value': "2.5",
            'is_valid': True,
            'error_message': "",
            'is_required': True
        }

        state = FieldValidationState.from_dict(state_dict)

        assert state.field_name == "risk_percentage"
        assert state.value == "2.5"
        assert state.is_valid is True
        assert state.error_message == ""
        assert state.is_required is True

    def test_field_validation_state_from_dict_with_missing_fields(self):
        """Test deserialization handles missing fields gracefully."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        incomplete_dict = {
            'field_name': "test_field",
            'value': "test_value"
        }

        state = FieldValidationState.from_dict(incomplete_dict)

        assert state.field_name == "test_field"
        assert state.value == "test_value"
        # Should have sensible defaults
        assert isinstance(state.is_valid, bool)
        assert isinstance(state.error_message, str)
        assert isinstance(state.is_required, bool)

    def test_field_validation_state_equality(self):
        """Test equality comparison between field validation states."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        state1 = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        state2 = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert state1.equals(state2) is True

        # Different values should not be equal
        state3 = FieldValidationState(
            field_name="account_size",
            value="20000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert state1.equals(state3) is False

    def test_field_validation_state_copy(self):
        """Test copying field validation state."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        original = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        copy = original.copy()

        # Should have same values
        assert copy.field_name == original.field_name
        assert copy.value == original.value
        assert copy.is_valid == original.is_valid
        assert copy.error_message == original.error_message
        assert copy.is_required == original.is_required

        # But be different objects
        assert copy is not original

    def test_field_validation_state_immutability_pattern(self):
        """Test that state updates return new instances (immutability pattern)."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        original = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        # Update operations should return new instances
        updated = original.update_value("20000")
        assert updated is not original
        assert original.value == "10000"  # Original unchanged
        assert updated.value == "20000"   # New instance has new value

        # Error operations should return new instances
        error_state = original.set_error("Error message")
        assert error_state is not original
        assert original.error_message == ""           # Original unchanged
        assert error_state.error_message == "Error message"  # New instance has error

    def test_field_validation_state_field_name_uniqueness(self):
        """Test field_name uniqueness validation."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Field names should be non-empty and unique identifiers
        state = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert state.has_valid_field_name() is True

        # Empty field name should be invalid
        invalid_state = FieldValidationState(
            field_name="",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert invalid_state.has_valid_field_name() is False

    def test_field_validation_state_value_type_handling(self):
        """Test handling of different value types."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # String value
        string_state = FieldValidationState.create_initial("text_field", "hello", False)
        assert string_state.value == "hello"

        # Numeric string
        numeric_state = FieldValidationState.create_initial("number_field", "123.45", False)
        assert numeric_state.value == "123.45"

        # Empty string
        empty_state = FieldValidationState.create_initial("empty_field", "", False)
        assert empty_state.value == ""

        # None value (should be converted to empty string)
        none_state = FieldValidationState.create_initial("none_field", None, False)
        assert none_state.value == ""

    def test_field_validation_state_factory_methods(self):
        """Test factory methods for common field validation state patterns."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        # Valid field
        valid_field = FieldValidationState.create_valid("account_size", "10000", True)
        assert valid_field.is_valid is True
        assert valid_field.error_message == ""

        # Invalid field
        invalid_field = FieldValidationState.create_invalid(
            "account_size", "abc", "Must be a number", True
        )
        assert invalid_field.is_valid is False
        assert invalid_field.error_message == "Must be a number"

        # Required empty field
        required_empty = FieldValidationState.create_required_empty("account_size")
        assert required_empty.is_valid is False
        assert required_empty.is_required is True
        assert len(required_empty.error_message) > 0

    @pytest.fixture
    def sample_field_state(self):
        """Fixture providing a sample field validation state."""
        from risk_calculator.models.field_validation_state import FieldValidationState

        return FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )