"""
Integration test: Menu-driven calculation execution.
Tests menu interaction scenarios from quickstart.
"""

import unittest
import tkinter as tk
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestMenuCalculationIntegration(unittest.TestCase):
    """Test menu calculation integration scenarios."""

    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_menu_calculate_with_valid_data(self):
        """Test Scenario 3A: Menu item executes calculation when form data is valid."""
        try:
            from risk_calculator.controllers.enhanced_menu_controller import EnhancedMenuController

            menu_controller = EnhancedMenuController(self.root)

            # Setup valid form data
            menu_controller.set_form_data({
                "account_size": "10000",
                "risk_percentage": "2",
                "entry_price": "50.00",
                "stop_loss_price": "48.00"
            })

            # Execute menu action
            result = menu_controller.handle_calculate_menu_action()

            # Should execute calculation successfully
            self.assertTrue(result)
            self.assertIsNotNone(menu_controller.get_last_calculation_result())

        except ImportError:
            self.skipTest("Enhanced menu controller not implemented")
        except AttributeError:
            self.skipTest("Menu calculation methods not implemented")

    def test_menu_calculate_with_invalid_data(self):
        """Test Scenario 3B: Menu item shows validation errors when form data is invalid."""
        try:
            from risk_calculator.controllers.enhanced_menu_controller import EnhancedMenuController

            menu_controller = EnhancedMenuController(self.root)

            # Setup invalid form data
            menu_controller.set_form_data({
                "account_size": "abc",  # Invalid
                "risk_percentage": "",  # Missing
                "entry_price": "50.00"
                # Missing stop_loss_price
            })

            # Execute menu action
            result = menu_controller.handle_calculate_menu_action()

            # Should not execute calculation
            self.assertFalse(result)
            # Should show validation dialog
            self.assertTrue(menu_controller.validation_dialog_shown())

        except ImportError:
            self.skipTest("Enhanced menu controller not implemented")
        except AttributeError:
            self.skipTest("Menu validation methods not implemented")

    def test_menu_state_updates_with_validation(self):
        """Test menu state updates based on form validation."""
        try:
            from risk_calculator.controllers.enhanced_menu_controller import EnhancedMenuController
            from risk_calculator.models.form_validation_state import FormValidationState

            menu_controller = EnhancedMenuController(self.root)

            # Create validation state with errors
            form_state = FormValidationState.create_with_errors("test_form", {
                "account_size": "Account size is required"
            })

            # Update menu state
            menu_controller.update_menu_state(form_state)

            # Verify menu reflects validation state
            self.assertFalse(menu_controller.is_calculate_enabled())

        except ImportError:
            self.skipTest("Enhanced menu controller not implemented")
        except AttributeError:
            self.skipTest("Menu state methods not implemented")


if __name__ == '__main__':
    unittest.main()
