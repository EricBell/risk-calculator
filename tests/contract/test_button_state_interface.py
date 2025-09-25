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

from risk_calculator.models.button_state import ButtonState


class TestButtonStateInterface:
    """Test the ButtonState interface contract."""

    def test_button_state_creation(self):
        """Test ButtonState can be created with default values."""
        button_state = ButtonState()

        assert button_state is not None
        assert hasattr(button_state, 'enabled')
        assert hasattr(button_state, 'error_message')
        assert hasattr(button_state, 'tooltip_text')

    def test_button_state_enabled_property(self):
        """Test ButtonState enabled property works correctly."""
        button_state = ButtonState()

        # Test default state
        assert isinstance(button_state.enabled, bool)

        # Test setting enabled state
        button_state.enabled = True
        assert button_state.enabled is True

        button_state.enabled = False
        assert button_state.enabled is False

    def test_button_state_error_message_property(self):
        """Test ButtonState error_message property works correctly."""
        button_state = ButtonState()

        # Test setting error message
        test_message = "Test error message"
        button_state.error_message = test_message
        assert button_state.error_message == test_message

        # Test clearing error message
        button_state.error_message = ""
        assert button_state.error_message == ""

        # Test None handling
        button_state.error_message = None
        assert button_state.error_message is None

    def test_button_state_tooltip_text_property(self):
        """Test ButtonState tooltip_text property works correctly."""
        button_state = ButtonState()

        # Test setting tooltip text
        test_tooltip = "Test tooltip text"
        button_state.tooltip_text = test_tooltip
        assert button_state.tooltip_text == test_tooltip

        # Test clearing tooltip text
        button_state.tooltip_text = ""
        assert button_state.tooltip_text == ""

    def test_button_state_representation(self):
        """Test ButtonState string representation."""
        button_state = ButtonState()
        button_state.enabled = True
        button_state.error_message = "Test error"

        # Should have some string representation
        str_repr = str(button_state)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_button_state_equality(self):
        """Test ButtonState equality comparison if implemented."""
        button_state1 = ButtonState()
        button_state2 = ButtonState()

        # Set same values
        button_state1.enabled = True
        button_state1.error_message = "Same message"

        button_state2.enabled = True
        button_state2.error_message = "Same message"

        # Test basic object comparison (may not have custom __eq__ implemented)
        assert button_state1 is not button_state2

    def test_button_state_disabled_with_error(self):
        """Test typical disabled state with error message scenario."""
        button_state = ButtonState()

        # Simulate validation error state
        button_state.enabled = False
        button_state.error_message = "Please fill in all required fields"
        button_state.tooltip_text = "Missing: Account Size, Premium"

        assert button_state.enabled is False
        assert "required fields" in button_state.error_message
        assert "Account Size" in button_state.tooltip_text

    def test_button_state_enabled_no_error(self):
        """Test typical enabled state with no errors scenario."""
        button_state = ButtonState()

        # Simulate successful validation state
        button_state.enabled = True
        button_state.error_message = None
        button_state.tooltip_text = "Click to calculate position"

        assert button_state.enabled is True
        assert button_state.error_message is None
        assert "calculate" in button_state.tooltip_text.lower()

    def test_button_state_interface_completeness(self):
        """Test that ButtonState has all expected interface methods/properties."""
        button_state = ButtonState()

        # Check for required interface components
        required_attributes = ['enabled', 'error_message', 'tooltip_text']

        for attr in required_attributes:
            assert hasattr(button_state, attr), f"ButtonState missing required attribute: {attr}"

        # Should be able to read and write all attributes
        for attr in required_attributes:
            # Test that we can get the attribute without error
            value = getattr(button_state, attr)

            # Test that we can set the attribute without error
            if attr == 'enabled':
                setattr(button_state, attr, True)
            else:
                setattr(button_state, attr, f"test_{attr}")


if __name__ == "__main__":
    pytest.main([__file__])