#!/usr/bin/env python3
"""
Test core functionality of enhanced components.
Simple validation script to ensure everything works.
"""

import unittest
import tkinter as tk
from unittest.mock import Mock

class TestCoreFunctionality(unittest.TestCase):
    """Test core enhanced UI functionality."""

    def test_enhanced_validation_service(self):
        """Test enhanced validation service works."""
        from risk_calculator.services.enhanced_validation_service import EnhancedValidationService, TradeType

        validation = EnhancedValidationService()

        # Test valid field
        result = validation.validate_field('account_size', '10000', TradeType.EQUITY)
        self.assertTrue(result.is_valid)

        # Test invalid field
        result = validation.validate_field('account_size', '-100', TradeType.EQUITY)
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.error_message) > 0)

    def test_field_validation_state(self):
        """Test field validation state model."""
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

    def test_form_validation_state(self):
        """Test form validation state model."""
        from risk_calculator.models.form_validation_state import FormValidationState
        from risk_calculator.models.field_validation_state import FieldValidationState

        field_state = FieldValidationState(
            field_name="account_size",
            value="10000",
            is_valid=True,
            error_message="",
            is_required=True
        )

        form_state = FormValidationState(
            form_id="test_form",
            field_states={"account_size": field_state},
            has_errors=False,
            all_required_filled=True,
            is_submittable=True
        )

        self.assertEqual(form_state.form_id, "test_form")
        self.assertFalse(form_state.has_errors)
        self.assertTrue(form_state.all_required_filled)
        self.assertTrue(form_state.is_submittable)

    def test_enhanced_base_controller(self):
        """Test enhanced base controller works."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController

        # Create mock view
        mock_view = Mock()
        mock_view.get_form_fields = Mock(return_value={})
        mock_view.get_calculate_button = Mock(return_value=Mock())
        mock_view.get_all_field_values = Mock(return_value={})

        controller = EnhancedBaseController(mock_view)

        # Test basic functionality
        self.assertIsNotNone(controller.validation_service)
        self.assertIsNotNone(controller.error_manager)

    def test_error_display_components(self):
        """Test error display components work."""
        from risk_calculator.views.error_display import ErrorLabel, FieldErrorManager

        root = tk.Tk()
        root.withdraw()  # Hide window

        try:
            # Test error label
            error_label = ErrorLabel(root)
            error_label.show_error("Test error message")
            self.assertTrue(error_label.has_error())

            error_label.hide()
            self.assertFalse(error_label.has_error())

            # Test error manager
            error_manager = FieldErrorManager()
            entry = tk.Entry(root)
            error_manager.register_field("test_field", entry, error_label)

            error_manager.show_error("test_field", "Test error")
            self.assertTrue(error_manager.has_errors())

            error_manager.hide_all_errors()
            self.assertFalse(error_manager.has_errors())

        finally:
            root.destroy()

    def test_configuration_service(self):
        """Test configuration service works."""
        from risk_calculator.services.configuration_service import JsonConfigurationService
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime

        service = JsonConfigurationService()

        # Test window configuration
        config = WindowConfiguration(
            width=1024,
            height=768,
            x=100,
            y=100,
            maximized=False,
            last_updated=datetime.now()
        )

        # Should not raise errors
        validated = service.validate_window_bounds(config)
        self.assertIsInstance(validated, WindowConfiguration)

    def test_complete_integration(self):
        """Test complete UI integration works."""
        from risk_calculator.integration.enhanced_ui_integration import create_enhanced_ui

        root = tk.Tk()
        root.withdraw()  # Hide window

        try:
            integration = create_enhanced_ui(root, enable_all_features=True)
            status = integration.get_integration_status()

            self.assertTrue(status['is_integrated'])
            self.assertIsNotNone(integration.get_validation_service())
            self.assertIsNotNone(integration.get_main_controller())

        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()