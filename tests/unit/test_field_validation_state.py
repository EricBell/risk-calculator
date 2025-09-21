"""
Unit tests for FieldValidationState model.
Tests validation status tracking for individual form fields.
"""

import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFieldValidationState(unittest.TestCase):
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

        self.assertEqual(state.field_name, "account_size")
        self.assertEqual(state.value, "10000")
        self.assertTrue(state.is_valid)
        self.assertEqual(state.error_message, "")
        self.assertTrue(state.is_required)

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

        self.assertEqual(state.field_name, "account_size")
        self.assertEqual(state.value, "abc")
        self.assertFalse(state.is_valid)
        self.assertEqual(state.error_message, "Account size must be a number")
        self.assertTrue(state.is_required)

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
        self.assertTrue(valid_state.validate())

        # Invalid state - field_name cannot be empty
        invalid_state = FieldValidationState(
            field_name="",
            value="test_value",
            is_valid=True,
            error_message="",
            is_required=False
        )
        self.assertFalse(invalid_state.validate())


if __name__ == '__main__':
    unittest.main()
