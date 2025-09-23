"""
Contract test for ButtonStateInterface
These tests MUST FAIL until the interface is implemented.
"""

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from unittest.mock import Mock
from enum import Enum


class ButtonState(Enum):
    """Button state enumeration."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    LOADING = "loading"


class ButtonStateInterface(ABC):
    """Contract interface for button state management functionality."""

    @abstractmethod
    def get_button_state(self, form_data: Dict[str, Any], risk_method: str) -> ButtonState:
        """
        Get current button state based on form data and risk method.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            ButtonState enum value
        """
        pass

    @abstractmethod
    def should_enable_button(self, form_data: Dict[str, Any], risk_method: str) -> bool:
        """
        Determine if button should be enabled.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            True if button should be enabled, False otherwise
        """
        pass

    @abstractmethod
    def get_button_tooltip(self, form_data: Dict[str, Any], risk_method: str) -> Optional[str]:
        """
        Get tooltip message for button based on current state.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method

        Returns:
            Tooltip message string or None if no tooltip needed
        """
        pass

    @abstractmethod
    def register_state_change_callback(self, callback: Callable[[ButtonState], None]) -> None:
        """
        Register callback to be called when button state changes.

        Args:
            callback: Function to call with new ButtonState
        """
        pass

    @abstractmethod
    def update_button_state(self, form_data: Dict[str, Any], risk_method: str) -> None:
        """
        Update button state and notify callbacks.

        Args:
            form_data: Dictionary of field names to values
            risk_method: Current risk calculation method
        """
        pass

    @abstractmethod
    def reset_button_state(self) -> None:
        """Reset button to default disabled state."""
        pass


class TestButtonStateInterface:
    """Contract tests for ButtonStateInterface implementation."""

    def setup_method(self):
        """Setup test method - this will fail until interface is implemented."""
        # This import will fail until the interface is implemented
        try:
            from risk_calculator.services.button_state_service import ButtonStateService
            self.button_service = ButtonStateService()
        except ImportError:
            pytest.fail("ButtonStateService not implemented yet")

    def test_implements_interface(self):
        """Test that implementation conforms to ButtonStateInterface."""
        assert isinstance(self.button_service, ButtonStateInterface)

    def test_get_button_state_complete_form(self):
        """Test button state with complete valid form."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        state = self.button_service.get_button_state(form_data, "percentage")
        assert state == ButtonState.ENABLED

    def test_get_button_state_incomplete_form(self):
        """Test button state with incomplete form."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        state = self.button_service.get_button_state(form_data, "percentage")
        assert state == ButtonState.DISABLED

    def test_get_button_state_invalid_data(self):
        """Test button state with invalid data."""
        form_data = {
            "account_size": "not_a_number",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        state = self.button_service.get_button_state(form_data, "percentage")
        assert state == ButtonState.DISABLED

    def test_should_enable_button_valid_percentage_method(self):
        """Test button enablement for valid percentage method."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        should_enable = self.button_service.should_enable_button(form_data, "percentage")
        assert should_enable is True

    def test_should_enable_button_valid_fixed_amount_method(self):
        """Test button enablement for valid fixed amount method."""
        form_data = {
            "account_size": "10000",
            "fixed_risk_amount": "200",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        should_enable = self.button_service.should_enable_button(form_data, "fixed_amount")
        assert should_enable is True

    def test_should_enable_button_valid_level_method(self):
        """Test button enablement for valid level method."""
        form_data = {
            "account_size": "10000",
            "level": "48.50",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        should_enable = self.button_service.should_enable_button(form_data, "level")
        assert should_enable is True

    def test_should_enable_button_missing_required_field(self):
        """Test button disabled when required field missing."""
        form_data = {
            "account_size": "",  # Missing required field
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        should_enable = self.button_service.should_enable_button(form_data, "percentage")
        assert should_enable is False

    def test_should_enable_button_wrong_fields_for_method(self):
        """Test button disabled when wrong fields provided for method."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",  # Wrong for fixed_amount method
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        should_enable = self.button_service.should_enable_button(form_data, "fixed_amount")
        assert should_enable is False

    def test_get_button_tooltip_disabled_missing_field(self):
        """Test tooltip when button disabled due to missing field."""
        form_data = {
            "account_size": "",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        tooltip = self.button_service.get_button_tooltip(form_data, "percentage")
        assert tooltip is not None
        assert "required" in tooltip.lower() or "missing" in tooltip.lower()

    def test_get_button_tooltip_disabled_invalid_data(self):
        """Test tooltip when button disabled due to invalid data."""
        form_data = {
            "account_size": "not_a_number",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        tooltip = self.button_service.get_button_tooltip(form_data, "percentage")
        assert tooltip is not None
        assert "invalid" in tooltip.lower() or "error" in tooltip.lower()

    def test_get_button_tooltip_enabled_no_tooltip(self):
        """Test no tooltip when button is enabled."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        tooltip = self.button_service.get_button_tooltip(form_data, "percentage")
        assert tooltip is None or tooltip == ""

    def test_register_state_change_callback(self):
        """Test registering state change callback."""
        callback_called = {"count": 0, "state": None}

        def test_callback(state: ButtonState):
            callback_called["count"] += 1
            callback_called["state"] = state

        self.button_service.register_state_change_callback(test_callback)

        # Trigger state change
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        self.button_service.update_button_state(form_data, "percentage")

        assert callback_called["count"] >= 1
        assert callback_called["state"] is not None

    def test_update_button_state_calls_callback(self):
        """Test that updating button state calls registered callbacks."""
        callback_states = []

        def state_callback(state: ButtonState):
            callback_states.append(state)

        self.button_service.register_state_change_callback(state_callback)

        # Update with valid data
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        self.button_service.update_button_state(form_data, "percentage")

        assert len(callback_states) >= 1
        assert ButtonState.ENABLED in callback_states

    def test_reset_button_state(self):
        """Test resetting button to default state."""
        # First enable button
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }
        self.button_service.update_button_state(form_data, "percentage")

        # Reset button
        self.button_service.reset_button_state()

        # Check state is disabled
        empty_form = {}
        state = self.button_service.get_button_state(empty_form, "percentage")
        assert state == ButtonState.DISABLED

    def test_state_consistency_between_methods(self):
        """Test consistency between get_button_state and should_enable_button."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }

        state = self.button_service.get_button_state(form_data, "percentage")
        should_enable = self.button_service.should_enable_button(form_data, "percentage")

        if state == ButtonState.ENABLED:
            assert should_enable is True
        else:
            assert should_enable is False

    def test_multiple_callback_registration(self):
        """Test registering multiple callbacks."""
        callback1_calls = {"count": 0}
        callback2_calls = {"count": 0}

        def callback1(state: ButtonState):
            callback1_calls["count"] += 1

        def callback2(state: ButtonState):
            callback2_calls["count"] += 1

        self.button_service.register_state_change_callback(callback1)
        self.button_service.register_state_change_callback(callback2)

        # Trigger state change
        form_data = {"account_size": "10000"}
        self.button_service.update_button_state(form_data, "percentage")

        assert callback1_calls["count"] >= 1
        assert callback2_calls["count"] >= 1

    def test_edge_case_empty_form_data(self):
        """Test button state with completely empty form."""
        form_data = {}
        state = self.button_service.get_button_state(form_data, "percentage")
        assert state == ButtonState.DISABLED

        should_enable = self.button_service.should_enable_button(form_data, "percentage")
        assert should_enable is False

    def test_edge_case_unknown_risk_method(self):
        """Test button state with unknown risk method."""
        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss_price": "48.00"
        }

        # Should handle unknown method gracefully
        state = self.button_service.get_button_state(form_data, "unknown_method")
        assert state == ButtonState.DISABLED