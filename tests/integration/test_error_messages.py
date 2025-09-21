"""
Integration test: Error message display and clearing.
Tests error message visibility and management from quickstart scenarios.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch

# Import components that will be implemented/enhanced
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestErrorMessageIntegration:
    """Test error message display integration scenarios."""

    def setup_method(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

    def teardown_method(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_error_messages_appear_near_invalid_fields(self):
        """Test Scenario 2A: Clear error messages appear near problematic fields."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.options_tab import OptionsTab

        tab = OptionsTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter invalid data as per quickstart scenario
        controller.handle_field_change("account_size", "abc")  # Invalid - should be numeric
        controller.handle_field_change("premium", "-5")        # Invalid - should be positive

        # Verify error messages appear
        form_state = controller.get_current_form_state()
        error_messages = form_state.get_error_messages()

        assert "account_size" in error_messages
        assert "premium" in error_messages
        assert "positive number" in error_messages["account_size"].lower()
        assert "greater than 0" in error_messages["premium"].lower()

        # Verify error messages are visually displayed
        assert controller.is_error_visible("account_size") is True
        assert controller.is_error_visible("premium") is True

    def test_error_messages_clear_when_fields_become_valid(self):
        """Test error messages clear when fields become valid."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter invalid data
        controller.handle_field_change("account_size", "abc")

        # Verify error appears
        assert controller.is_error_visible("account_size") is True

        # Fix the data
        controller.handle_field_change("account_size", "10000")

        # Verify error clears
        assert controller.is_error_visible("account_size") is False

    def test_error_message_visibility_during_window_resize(self):
        """Test Scenario 2B: Error messages remain visible during window resize."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter invalid data to generate errors
        controller.handle_field_change("account_size", "abc")
        controller.handle_field_change("risk_percentage", "-2")

        # Verify errors are visible
        assert controller.is_error_visible("account_size") is True
        assert controller.is_error_visible("risk_percentage") is True

        # Simulate window resize events
        resize_event = Mock()
        resize_event.width = 1024
        resize_event.height = 600

        controller.handle_window_resize(resize_event)

        # Verify errors are still visible after resize
        assert controller.is_error_visible("account_size") is True
        assert controller.is_error_visible("risk_percentage") is True

        # Simulate larger resize
        resize_event.width = 1600
        resize_event.height = 1000

        controller.handle_window_resize(resize_event)

        # Verify errors are still visible
        assert controller.is_error_visible("account_size") is True
        assert controller.is_error_visible("risk_percentage") is True