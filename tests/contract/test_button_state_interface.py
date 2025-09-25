"""
Contract tests for ButtonState interface.

Tests the interface contract for ButtonState model to ensure proper
button state management functionality across the application.
"""

import pytest
from decimal import Decimal
import sys
import os

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from risk_calculator.models.button_state import ButtonState, ButtonStateModel, ButtonStateReason


class TestButtonStateInterface:
    """Test the ButtonState interface contract."""

    def test_button_state_model_creation(self):
        """Test ButtonStateModel can be created with default values."""
        button_state = ButtonStateModel(button_id="test_button")

        assert button_state is not None
        assert hasattr(button_state, 'current_state')
        assert hasattr(button_state, 'current_reason')
        assert hasattr(button_state, 'tooltip_message')
        assert button_state.button_id == "test_button"

    def test_button_state_enum_values(self):
        """Test ButtonState enum has expected values."""
        assert hasattr(ButtonState, 'ENABLED')
        assert hasattr(ButtonState, 'DISABLED')

        # Test enum values
        assert ButtonState.ENABLED.value == "enabled"
        assert ButtonState.DISABLED.value == "disabled"

    def test_button_state_model_enabled_disabled(self):
        """Test ButtonStateModel enabled/disabled state management."""
        button_state = ButtonStateModel(button_id="test_button")

        # Should start disabled
        assert button_state.current_state == ButtonState.DISABLED

        # Test enabling
        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE,
            tooltip="All fields valid"
        )

        assert button_state.current_state == ButtonState.ENABLED
        assert button_state.current_reason == ButtonStateReason.FORM_COMPLETE
        assert button_state.tooltip_message == "All fields valid"

    def test_button_state_reason_enum(self):
        """Test ButtonStateReason enum works correctly."""
        assert hasattr(ButtonStateReason, 'FORM_COMPLETE')
        assert hasattr(ButtonStateReason, 'FORM_INCOMPLETE')
        assert hasattr(ButtonStateReason, 'VALIDATION_ERROR')

        # Test enum values
        assert ButtonStateReason.FORM_COMPLETE.value == "form_complete"
        assert ButtonStateReason.VALIDATION_ERROR.value == "validation_error"

    def test_button_state_tooltip_management(self):
        """Test ButtonStateModel tooltip management."""
        button_state = ButtonStateModel(button_id="test_button")

        # Test setting tooltip
        button_state.update_state(
            ButtonState.DISABLED,
            ButtonStateReason.MISSING_REQUIRED_FIELD,
            tooltip="Please fill in Account Size"
        )

        assert button_state.tooltip_message == "Please fill in Account Size"

        # Test clearing tooltip
        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE,
            tooltip=None
        )

        assert button_state.tooltip_message is None

    def test_button_state_transition_history(self):
        """Test button state transition tracking."""
        button_state = ButtonStateModel(button_id="test_button")

        # Should start with no history
        assert len(button_state.state_history) == 0

        # Make a state change
        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE
        )

        # Should have one transition recorded
        assert len(button_state.state_history) == 1
        transition = button_state.state_history[0]

        assert transition.from_state == ButtonState.DISABLED
        assert transition.to_state == ButtonState.ENABLED
        assert transition.reason == ButtonStateReason.FORM_COMPLETE

    def test_button_state_interface_consistency(self):
        """Test that ButtonStateModel interface is consistent."""
        button_state = ButtonStateModel(button_id="validation_test")

        # Test that all expected methods exist
        required_methods = ['update_state']
        for method in required_methods:
            assert hasattr(button_state, method), f"ButtonStateModel missing method: {method}"
            assert callable(getattr(button_state, method)), f"Method {method} should be callable"

        # Test that all expected properties exist
        required_properties = ['current_state', 'current_reason', 'tooltip_message', 'button_id']
        for prop in required_properties:
            assert hasattr(button_state, prop), f"ButtonStateModel missing property: {prop}"

    def test_button_state_validation_scenarios(self):
        """Test typical button state validation scenarios."""
        button_state = ButtonStateModel(button_id="calculate_button")

        # Scenario 1: Form incomplete (change the reason to trigger update)
        button_state.update_state(
            ButtonState.DISABLED,
            ButtonStateReason.MISSING_REQUIRED_FIELD,
            tooltip="Please complete all required fields"
        )

        assert button_state.current_state == ButtonState.DISABLED
        assert "required fields" in button_state.tooltip_message

        # Scenario 2: Validation error
        button_state.update_state(
            ButtonState.DISABLED,
            ButtonStateReason.VALIDATION_ERROR,
            tooltip="Account size must be positive"
        )

        assert button_state.current_state == ButtonState.DISABLED
        assert button_state.current_reason == ButtonStateReason.VALIDATION_ERROR

        # Scenario 3: Form complete and valid
        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE,
            tooltip="Click to calculate position"
        )

        assert button_state.current_state == ButtonState.ENABLED
        assert button_state.current_reason == ButtonStateReason.FORM_COMPLETE

    def test_button_state_metadata_support(self):
        """Test ButtonStateModel metadata functionality."""
        button_state = ButtonStateModel(button_id="metadata_test")

        # Should have metadata attribute
        assert hasattr(button_state, 'metadata')
        assert isinstance(button_state.metadata, dict)

        # Test adding metadata
        button_state.metadata['validation_time'] = 0.05
        button_state.metadata['field_count'] = 5

        assert button_state.metadata['validation_time'] == 0.05
        assert button_state.metadata['field_count'] == 5

    def test_button_state_timing_properties(self):
        """Test ButtonStateModel timing-related properties."""
        button_state = ButtonStateModel(button_id="timing_test")

        # Should have last_updated timestamp
        assert hasattr(button_state, 'last_updated')
        assert isinstance(button_state.last_updated, (int, float))

        # Should update timestamp when state changes
        original_time = button_state.last_updated

        import time
        time.sleep(0.01)  # Small delay to ensure time difference

        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE
        )

        assert button_state.last_updated > original_time

    def test_button_state_context_tracking(self):
        """Test button state context information."""
        button_state = ButtonStateModel(button_id="context_test")

        # Test state change with context
        context = {'form_fields': 5, 'validation_method': 'realtime'}

        button_state.update_state(
            ButtonState.ENABLED,
            ButtonStateReason.FORM_COMPLETE,
            context=context
        )

        # Should have recorded the transition with context
        assert len(button_state.state_history) == 1
        transition = button_state.state_history[0]

        assert 'form_fields' in transition.context
        assert transition.context['form_fields'] == 5
        assert transition.context['validation_method'] == 'realtime'


if __name__ == "__main__":
    pytest.main([__file__])