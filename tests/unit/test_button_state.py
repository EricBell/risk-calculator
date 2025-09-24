"""
Unit tests for ButtonState model.
Tests button state management, transitions, and callback functionality.
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestButtonState(unittest.TestCase):
    """Test ButtonState model functionality."""

    def setUp(self):
        """Set up test fixtures."""
        from risk_calculator.models.button_state import (
            ButtonStateModel, ButtonState, ButtonStateReason
        )
        self.ButtonStateModel = ButtonStateModel
        self.ButtonState = ButtonState
        self.ButtonStateReason = ButtonStateReason

    def test_button_state_model_creation(self):
        """Test creating ButtonStateModel with default values."""
        button_state = self.ButtonStateModel(button_id="test_button")

        self.assertEqual(button_state.button_id, "test_button")
        self.assertEqual(button_state.current_state, self.ButtonState.DISABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_INCOMPLETE)
        self.assertIsNone(button_state.tooltip_message)
        self.assertEqual(len(button_state.state_history), 0)
        self.assertEqual(len(button_state.state_callbacks), 0)
        self.assertIsInstance(button_state.last_updated, float)
        self.assertIsInstance(button_state.metadata, dict)

    def test_button_state_model_creation_with_custom_values(self):
        """Test creating ButtonStateModel with custom initial values."""
        custom_metadata = {'theme': 'dark', 'priority': 'high'}
        button_state = self.ButtonStateModel(
            button_id="custom_button",
            current_state=self.ButtonState.ENABLED,
            current_reason=self.ButtonStateReason.FORM_COMPLETE,
            tooltip_message="Custom tooltip",
            metadata=custom_metadata
        )

        self.assertEqual(button_state.button_id, "custom_button")
        self.assertEqual(button_state.current_state, self.ButtonState.ENABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_COMPLETE)
        self.assertEqual(button_state.tooltip_message, "Custom tooltip")
        self.assertEqual(button_state.metadata, custom_metadata)

    def test_update_state_with_state_change(self):
        """Test updating button state creates transition record."""
        button_state = self.ButtonStateModel(button_id="test_button")
        initial_time = button_state.last_updated

        time.sleep(0.01)  # Ensure time difference

        button_state.update_state(
            self.ButtonState.ENABLED,
            self.ButtonStateReason.FORM_COMPLETE,
            "Form is complete",
            {'source': 'test'}
        )

        # Check state updated
        self.assertEqual(button_state.current_state, self.ButtonState.ENABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_COMPLETE)
        self.assertEqual(button_state.tooltip_message, "Form is complete")
        self.assertGreater(button_state.last_updated, initial_time)

        # Check transition recorded
        self.assertEqual(len(button_state.state_history), 1)
        transition = button_state.state_history[0]
        self.assertEqual(transition.from_state, self.ButtonState.DISABLED)
        self.assertEqual(transition.to_state, self.ButtonState.ENABLED)
        self.assertEqual(transition.reason, self.ButtonStateReason.FORM_COMPLETE)
        self.assertEqual(transition.context, {'source': 'test'})

    def test_update_state_no_change_ignored(self):
        """Test updating to same state and reason is ignored."""
        button_state = self.ButtonStateModel(button_id="test_button")
        initial_history_count = len(button_state.state_history)
        initial_time = button_state.last_updated

        time.sleep(0.01)

        # Update to same state
        button_state.update_state(
            self.ButtonState.DISABLED,
            self.ButtonStateReason.FORM_INCOMPLETE
        )

        # Should not create transition
        self.assertEqual(len(button_state.state_history), initial_history_count)
        self.assertEqual(button_state.last_updated, initial_time)

    def test_state_callback_registration_and_notification(self):
        """Test callback registration and notification on state change."""
        button_state = self.ButtonStateModel(button_id="test_button")
        callback_mock = Mock()

        # Register callback
        button_state.register_state_callback(callback_mock)
        self.assertIn(callback_mock, button_state.state_callbacks)

        # Trigger state change
        button_state.update_state(
            self.ButtonState.ENABLED,
            self.ButtonStateReason.FORM_COMPLETE
        )

        # Check callback was called
        callback_mock.assert_called_once_with(
            self.ButtonState.ENABLED,
            self.ButtonStateReason.FORM_COMPLETE
        )

    def test_callback_duplicate_registration_prevented(self):
        """Test that duplicate callback registration is prevented."""
        button_state = self.ButtonStateModel(button_id="test_button")
        callback_mock = Mock()

        # Register callback twice
        button_state.register_state_callback(callback_mock)
        button_state.register_state_callback(callback_mock)

        # Should only appear once
        callback_count = button_state.state_callbacks.count(callback_mock)
        self.assertEqual(callback_count, 1)

    def test_callback_unregistration(self):
        """Test callback unregistration."""
        button_state = self.ButtonStateModel(button_id="test_button")
        callback_mock = Mock()

        # Register and unregister callback
        button_state.register_state_callback(callback_mock)
        button_state.unregister_state_callback(callback_mock)

        self.assertNotIn(callback_mock, button_state.state_callbacks)

    def test_callback_error_handling(self):
        """Test that callback errors don't prevent state updates."""
        button_state = self.ButtonStateModel(button_id="test_button")

        def failing_callback(state, reason):
            raise Exception("Callback error")

        button_state.register_state_callback(failing_callback)

        # State update should succeed despite callback error
        button_state.update_state(
            self.ButtonState.ENABLED,
            self.ButtonStateReason.FORM_COMPLETE
        )

        self.assertEqual(button_state.current_state, self.ButtonState.ENABLED)

    def test_state_check_methods(self):
        """Test state checking convenience methods."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Initial state - disabled
        self.assertTrue(button_state.is_disabled())
        self.assertFalse(button_state.is_enabled())
        self.assertFalse(button_state.is_loading())
        self.assertFalse(button_state.is_hidden())

        # Change to enabled
        button_state.update_state(self.ButtonState.ENABLED, self.ButtonStateReason.FORM_COMPLETE)
        self.assertTrue(button_state.is_enabled())
        self.assertFalse(button_state.is_disabled())

        # Change to loading
        button_state.update_state(self.ButtonState.LOADING, self.ButtonStateReason.PROCESSING)
        self.assertTrue(button_state.is_loading())
        self.assertFalse(button_state.is_enabled())

        # Change to hidden
        button_state.update_state(self.ButtonState.HIDDEN, self.ButtonStateReason.USER_DISABLED)
        self.assertTrue(button_state.is_hidden())
        self.assertFalse(button_state.is_enabled())

    def test_tooltip_generation(self):
        """Test tooltip message generation based on state and reason."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Test default tooltips for different reasons
        test_cases = [
            (self.ButtonStateReason.FORM_INCOMPLETE, "Please complete all required fields"),
            (self.ButtonStateReason.VALIDATION_ERROR, "Please fix validation errors"),
            (self.ButtonStateReason.MISSING_REQUIRED_FIELD, "Required fields are missing"),
            (self.ButtonStateReason.INVALID_DATA, "Please enter valid data"),
            (self.ButtonStateReason.PROCESSING, "Processing..."),
            (self.ButtonStateReason.METHOD_MISMATCH, "Please select appropriate fields for current method"),
            (self.ButtonStateReason.SYSTEM_ERROR, "System error - please try again"),
            (self.ButtonStateReason.USER_DISABLED, "Button disabled by user")
        ]

        for reason, expected_tooltip in test_cases:
            button_state.update_state(self.ButtonState.DISABLED, reason)
            self.assertEqual(button_state.get_tooltip(), expected_tooltip)

        # Test enabled state has no tooltip
        button_state.update_state(self.ButtonState.ENABLED, self.ButtonStateReason.FORM_COMPLETE)
        self.assertEqual(button_state.get_tooltip(), "")

        # Test custom tooltip override
        button_state.update_state(
            self.ButtonState.DISABLED,
            self.ButtonStateReason.VALIDATION_ERROR,
            "Custom error message"
        )
        self.assertEqual(button_state.get_tooltip(), "Custom error message")

    def test_convenience_state_change_methods(self):
        """Test convenience methods for common state changes."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Test enable method
        button_state.enable()
        self.assertEqual(button_state.current_state, self.ButtonState.ENABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_COMPLETE)

        # Test disable method
        button_state.disable(self.ButtonStateReason.VALIDATION_ERROR, "Test error")
        self.assertEqual(button_state.current_state, self.ButtonState.DISABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.VALIDATION_ERROR)
        self.assertEqual(button_state.tooltip_message, "Test error")

        # Test set_loading method
        button_state.set_loading()
        self.assertEqual(button_state.current_state, self.ButtonState.LOADING)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.PROCESSING)
        self.assertEqual(button_state.tooltip_message, "Processing...")

        # Test hide method
        button_state.hide()
        self.assertEqual(button_state.current_state, self.ButtonState.HIDDEN)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.USER_DISABLED)

        # Test show method
        button_state.show()
        self.assertEqual(button_state.current_state, self.ButtonState.DISABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_INCOMPLETE)

    def test_state_history_management(self):
        """Test state history tracking and retrieval."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Create multiple state changes
        state_changes = [
            (self.ButtonState.ENABLED, self.ButtonStateReason.FORM_COMPLETE),
            (self.ButtonState.LOADING, self.ButtonStateReason.PROCESSING),
            (self.ButtonState.DISABLED, self.ButtonStateReason.VALIDATION_ERROR),
            (self.ButtonState.ENABLED, self.ButtonStateReason.FORM_COMPLETE),
        ]

        for state, reason in state_changes:
            button_state.update_state(state, reason)

        # Test transition count
        self.assertEqual(button_state.get_transition_count(), len(state_changes))

        # Test recent transitions
        recent = button_state.get_recent_transitions(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[-1].to_state, self.ButtonState.ENABLED)

        # Test all recent transitions
        all_recent = button_state.get_recent_transitions(10)
        self.assertEqual(len(all_recent), len(state_changes))

    def test_time_tracking(self):
        """Test time tracking functionality."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Test time in current state
        initial_time = button_state.get_time_in_current_state()
        time.sleep(0.01)
        later_time = button_state.get_time_in_current_state()
        self.assertGreater(later_time, initial_time)

        # Test has_been_enabled
        self.assertFalse(button_state.has_been_enabled())
        button_state.enable()
        self.assertTrue(button_state.has_been_enabled())

        # Test last enabled time
        enabled_time = button_state.get_last_enabled_time()
        self.assertIsNotNone(enabled_time)
        self.assertIsInstance(enabled_time, float)

        # Test transition duration
        transition = button_state.state_history[-1]
        duration = transition.duration_since
        self.assertGreaterEqual(duration, 0)

    def test_state_reset_and_clear(self):
        """Test state reset and history clearing."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Make some changes
        button_state.enable()
        button_state.disable(self.ButtonStateReason.VALIDATION_ERROR)
        self.assertGreater(len(button_state.state_history), 0)

        # Test reset
        button_state.reset_state()
        self.assertEqual(button_state.current_state, self.ButtonState.DISABLED)
        self.assertEqual(button_state.current_reason, self.ButtonStateReason.FORM_INCOMPLETE)

        # Test clear history
        button_state.clear_history()
        self.assertEqual(len(button_state.state_history), 0)

    def test_state_summary(self):
        """Test state summary generation."""
        button_state = self.ButtonStateModel(button_id="test_button")
        button_state.metadata['version'] = '1.0'
        button_state.enable()

        summary = button_state.get_state_summary()

        expected_keys = [
            'button_id', 'current_state', 'current_reason', 'tooltip',
            'is_enabled', 'last_updated', 'time_in_state', 'transition_count',
            'has_been_enabled', 'metadata'
        ]

        for key in expected_keys:
            self.assertIn(key, summary)

        self.assertEqual(summary['button_id'], 'test_button')
        self.assertEqual(summary['current_state'], 'enabled')
        self.assertTrue(summary['is_enabled'])
        self.assertTrue(summary['has_been_enabled'])
        self.assertEqual(summary['metadata']['version'], '1.0')

    def test_button_state_copy(self):
        """Test button state copying functionality."""
        button_state = self.ButtonStateModel(button_id="test_button")
        button_state.metadata['test'] = 'value'
        button_state.enable()
        button_state.disable(self.ButtonStateReason.VALIDATION_ERROR)

        # Create copy
        copied_state = button_state.copy()

        # Test basic attributes copied
        self.assertEqual(copied_state.button_id, button_state.button_id)
        self.assertEqual(copied_state.current_state, button_state.current_state)
        self.assertEqual(copied_state.current_reason, button_state.current_reason)
        self.assertEqual(copied_state.tooltip_message, button_state.tooltip_message)
        self.assertEqual(copied_state.metadata, button_state.metadata)

        # Test history copied
        self.assertEqual(len(copied_state.state_history), len(button_state.state_history))

        # Test independence (modifying copy doesn't affect original)
        copied_state.enable()
        self.assertNotEqual(copied_state.current_state, button_state.current_state)

    def test_class_methods(self):
        """Test class factory methods."""
        # Test create_disabled
        disabled_button = self.ButtonStateModel.create_disabled(
            "disabled_test",
            self.ButtonStateReason.MISSING_REQUIRED_FIELD
        )
        self.assertEqual(disabled_button.button_id, "disabled_test")
        self.assertEqual(disabled_button.current_state, self.ButtonState.DISABLED)
        self.assertEqual(disabled_button.current_reason, self.ButtonStateReason.MISSING_REQUIRED_FIELD)

        # Test create_enabled
        enabled_button = self.ButtonStateModel.create_enabled("enabled_test")
        self.assertEqual(enabled_button.button_id, "enabled_test")
        self.assertEqual(enabled_button.current_state, self.ButtonState.ENABLED)
        self.assertEqual(enabled_button.current_reason, self.ButtonStateReason.FORM_COMPLETE)

    def test_string_representation(self):
        """Test string representation of button state."""
        button_state = self.ButtonStateModel(button_id="test_button")

        repr_str = repr(button_state)
        self.assertIn("test_button", repr_str)
        self.assertIn("disabled", repr_str)
        self.assertIn("form_incomplete", repr_str)
        self.assertIn("enabled=False", repr_str)

        # Test with enabled state
        button_state.enable()
        repr_str = repr(button_state)
        self.assertIn("enabled=True", repr_str)

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        button_state = self.ButtonStateModel(button_id="test_button")

        # Test with None context
        button_state.update_state(
            self.ButtonState.ENABLED,
            self.ButtonStateReason.FORM_COMPLETE,
            context=None
        )
        self.assertEqual(len(button_state.state_history), 1)
        self.assertEqual(button_state.state_history[0].context, {})

        # Test recent transitions with no history
        empty_button = self.ButtonStateModel(button_id="empty")
        recent = empty_button.get_recent_transitions(5)
        self.assertEqual(len(recent), 0)

        # Test last enabled time with no enabled history
        self.assertIsNone(empty_button.get_last_enabled_time())

        # Test unregistering non-existent callback
        fake_callback = Mock()
        button_state.unregister_state_callback(fake_callback)  # Should not raise error


if __name__ == '__main__':
    unittest.main()