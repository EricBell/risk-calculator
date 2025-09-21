"""
Unit tests for FormValidationState model.
Tests form-level validation state management.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFormValidationState(unittest.TestCase):
    """Test FormValidationState model functionality."""

    def test_form_validation_state_creation(self):
        """Test creating FormValidationState with field states."""
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
                value="2.0",
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

        self.assertEqual(form_state.form_id, "equity_tab")
        self.assertEqual(len(form_state.field_states), 2)
        self.assertFalse(form_state.has_errors)
        self.assertTrue(form_state.all_required_filled)
        self.assertTrue(form_state.is_submittable)

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
            )
        }

        form_state = FormValidationState(
            form_id="equity_tab",
            field_states=field_states,
            has_errors=True,
            all_required_filled=False,
            is_submittable=False
        )

        self.assertTrue(form_state.has_errors)
        self.assertFalse(form_state.is_submittable)


if __name__ == '__main__':
    unittest.main()
