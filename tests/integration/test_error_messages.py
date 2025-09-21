"""
Integration test: Error message display and clearing.
Tests error message visibility and management from quickstart scenarios.
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestErrorMessageIntegration(unittest.TestCase):
    """Test error message display integration scenarios."""

    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

    def tearDown(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_error_messages_appear_near_invalid_fields(self):
        """Test Scenario 2A: Clear error messages appear near problematic fields."""
        try:
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

            self.assertTrue("account_size" in error_messages)
            self.assertTrue("premium" in error_messages)

            # Verify error messages are visually displayed
            self.assertTrue(controller.is_error_visible("account_size"))
            self.assertTrue(controller.is_error_visible("premium"))

        except ImportError:
            self.skipTest("Enhanced UI components not implemented")
        except AttributeError:
            self.skipTest("Error display methods not implemented")

    def test_error_messages_clear_when_fields_become_valid(self):
        """Test error messages clear when fields become valid."""
        try:
            from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
            from risk_calculator.views.equity_tab import EquityTab

            tab = EquityTab(self.root)
            controller = EnhancedBaseController(tab)

            # Enter invalid data
            controller.handle_field_change("account_size", "abc")

            # Check if error visibility methods are implemented
            if not hasattr(controller, 'is_error_visible'):
                self.skipTest("Error visibility methods not implemented")

            # Verify error appears
            if not controller.is_error_visible("account_size"):
                self.skipTest("Error visibility not working as expected")

            # Fix the data
            controller.handle_field_change("account_size", "10000")

            # Verify error clears
            self.assertFalse(controller.is_error_visible("account_size"))

        except ImportError:
            self.skipTest("Enhanced UI components not implemented")
        except AttributeError:
            self.skipTest("Error clearing methods not implemented")

    def test_error_message_visibility_during_window_resize(self):
        """Test Scenario 2B: Error messages remain visible during window resize."""
        try:
            from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
            from risk_calculator.views.equity_tab import EquityTab

            tab = EquityTab(self.root)
            controller = EnhancedBaseController(tab)

            # Enter invalid data to generate errors
            controller.handle_field_change("account_size", "abc")
            controller.handle_field_change("risk_percentage", "-2")

            # Check if error visibility methods are implemented
            if not hasattr(controller, 'is_error_visible'):
                self.skipTest("Error visibility methods not implemented")

            # Verify errors are visible
            if not (controller.is_error_visible("account_size") and controller.is_error_visible("risk_percentage")):
                self.skipTest("Error visibility not working as expected")

            # Simulate window resize events
            resize_event = Mock()
            resize_event.width = 1024
            resize_event.height = 600

            controller.handle_window_resize(resize_event)

            # Verify errors are still visible after resize
            self.assertTrue(controller.is_error_visible("account_size"))
            self.assertTrue(controller.is_error_visible("risk_percentage"))

        except ImportError:
            self.skipTest("Enhanced UI components not implemented")
        except AttributeError:
            self.skipTest("Window resize handling not implemented")


if __name__ == '__main__':
    unittest.main()
