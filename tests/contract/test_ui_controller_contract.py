"""
Contract tests for UIController interface.
These tests verify that any implementation of UIController follows the contract.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the contract interface
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from specs.contracts.ui_controller import UIController, WindowController, MenuController
from specs.contracts.validation_service import FormValidationState, FieldValidationState


class TestUIControllerContract:
    """Test contract compliance for UIController implementations."""

    def test_update_button_state_accepts_form_validation_state(self):
        """Test that update_button_state accepts FormValidationState."""
        controller = self._get_ui_controller_implementation()

        # Create mock form validation state
        form_state = self._create_mock_form_state(is_submittable=True)

        # Should not raise an exception
        controller.update_button_state(form_state)

    def test_show_field_error_accepts_field_and_message(self):
        """Test that show_field_error accepts field name and error message."""
        controller = self._get_ui_controller_implementation()

        # Should not raise an exception
        controller.show_field_error("account_size", "Account size must be positive")

    def test_hide_field_error_accepts_field_name(self):
        """Test that hide_field_error accepts field name."""
        controller = self._get_ui_controller_implementation()

        # Should not raise an exception
        controller.hide_field_error("account_size")

    def test_update_form_validation_returns_form_validation_state(self):
        """Test that update_form_validation returns FormValidationState."""
        controller = self._get_ui_controller_implementation()

        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00"
        }

        result = controller.update_form_validation(form_data)

        assert isinstance(result, FormValidationState)
        assert hasattr(result, 'is_submittable')
        assert hasattr(result, 'has_errors')
        assert hasattr(result, 'field_states')

    def test_handle_field_change_accepts_field_and_value(self):
        """Test that handle_field_change accepts field name and value."""
        controller = self._get_ui_controller_implementation()

        # Should not raise an exception
        controller.handle_field_change("account_size", "15000")

    def test_execute_calculation_returns_bool(self):
        """Test that execute_calculation returns boolean."""
        controller = self._get_ui_controller_implementation()

        result = controller.execute_calculation()

        assert isinstance(result, bool)

    def test_configure_responsive_layout_exists(self):
        """Test that configure_responsive_layout method exists and can be called."""
        controller = self._get_ui_controller_implementation()

        # Should not raise an exception
        controller.configure_responsive_layout()

    def test_handle_window_resize_accepts_event(self):
        """Test that handle_window_resize accepts event parameter."""
        controller = self._get_ui_controller_implementation()

        # Mock event object
        mock_event = Mock()

        # Should not raise an exception
        controller.handle_window_resize(mock_event)

    def test_controller_coordinates_validation_and_ui_updates(self):
        """Test that controller properly coordinates validation with UI updates."""
        controller = self._get_ui_controller_implementation()

        # Test sequence of operations that should work together
        form_data = {"account_size": "10000"}

        # Update validation
        form_state = controller.update_form_validation(form_data)

        # Update button state based on validation
        controller.update_button_state(form_state)

        # Handle individual field change
        controller.handle_field_change("account_size", "15000")

        # All operations should complete without exceptions

    def _get_ui_controller_implementation(self) -> UIController:
        """Get an implementation of UIController for testing."""
        try:
            from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
            return EnhancedBaseController()
        except ImportError:
            pytest.fail("UIController implementation not found. Implement EnhancedBaseController first.")

    def _create_mock_form_state(self, is_submittable: bool = True) -> FormValidationState:
        """Create a mock FormValidationState for testing."""
        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000",
                is_valid=True,
                error_message="",
                is_required=True
            )
        }

        return FormValidationState(
            form_id="test_form",
            field_states=field_states,
            has_errors=not is_submittable,
            all_required_filled=is_submittable,
            is_submittable=is_submittable
        )


class TestWindowControllerContract:
    """Test contract compliance for WindowController implementations."""

    def test_save_window_state_returns_bool(self):
        """Test that save_window_state returns boolean."""
        controller = self._get_window_controller_implementation()

        result = controller.save_window_state()

        assert isinstance(result, bool)

    def test_restore_window_state_returns_bool(self):
        """Test that restore_window_state returns boolean."""
        controller = self._get_window_controller_implementation()

        result = controller.restore_window_state()

        assert isinstance(result, bool)

    def test_validate_window_bounds_returns_tuple(self):
        """Test that validate_window_bounds returns adjusted bounds tuple."""
        controller = self._get_window_controller_implementation()

        result = controller.validate_window_bounds(1024, 768, 100, 100)

        assert isinstance(result, tuple)
        assert len(result) == 4
        # Should return (width, height, x, y)
        assert all(isinstance(val, int) for val in result)

    def test_validate_window_bounds_adjusts_invalid_bounds(self):
        """Test that validate_window_bounds adjusts invalid window bounds."""
        controller = self._get_window_controller_implementation()

        # Test with negative positions (off-screen)
        result = controller.validate_window_bounds(1024, 768, -100, -100)

        width, height, x, y = result
        assert x >= 0
        assert y >= 0

    def test_setup_window_event_handlers_exists(self):
        """Test that setup_window_event_handlers method exists."""
        controller = self._get_window_controller_implementation()

        # Should not raise an exception
        controller.setup_window_event_handlers()

    def test_apply_minimum_size_constraints_exists(self):
        """Test that apply_minimum_size_constraints method exists."""
        controller = self._get_window_controller_implementation()

        # Should not raise an exception
        controller.apply_minimum_size_constraints()

    def test_window_state_persistence_cycle(self):
        """Test that window state can be saved and restored."""
        controller = self._get_window_controller_implementation()

        # Save current state
        save_result = controller.save_window_state()

        # Restore state
        restore_result = controller.restore_window_state()

        # Both operations should succeed
        assert isinstance(save_result, bool)
        assert isinstance(restore_result, bool)

    def _get_window_controller_implementation(self) -> WindowController:
        """Get an implementation of WindowController for testing."""
        try:
            from risk_calculator.controllers.enhanced_main_controller import EnhancedMainController
            return EnhancedMainController()
        except ImportError:
            pytest.fail("WindowController implementation not found. Implement EnhancedMainController first.")


class TestMenuControllerContract:
    """Test contract compliance for MenuController implementations."""

    def test_handle_calculate_menu_action_exists(self):
        """Test that handle_calculate_menu_action method exists."""
        controller = self._get_menu_controller_implementation()

        # Should not raise an exception
        controller.handle_calculate_menu_action()

    def test_update_menu_state_accepts_form_validation_state(self):
        """Test that update_menu_state accepts FormValidationState."""
        controller = self._get_menu_controller_implementation()

        form_state = self._create_mock_form_state()

        # Should not raise an exception
        controller.update_menu_state(form_state)

    def test_show_menu_validation_dialog_accepts_error_dict(self):
        """Test that show_menu_validation_dialog accepts error message dict."""
        controller = self._get_menu_controller_implementation()

        error_messages = {
            "account_size": "Account size is required",
            "risk_percentage": "Risk percentage must be positive"
        }

        # Should not raise an exception
        controller.show_menu_validation_dialog(error_messages)

    def test_menu_integration_with_validation(self):
        """Test that menu controller integrates with validation system."""
        controller = self._get_menu_controller_implementation()

        # Test sequence of menu operations
        form_state = self._create_mock_form_state(is_submittable=False)

        # Update menu state based on validation
        controller.update_menu_state(form_state)

        # Attempt menu action (should handle invalid state gracefully)
        controller.handle_calculate_menu_action()

    def _get_menu_controller_implementation(self) -> MenuController:
        """Get an implementation of MenuController for testing."""
        try:
            from risk_calculator.controllers.enhanced_menu_controller import EnhancedMenuController
            return EnhancedMenuController()
        except ImportError:
            pytest.fail("MenuController implementation not found. Implement EnhancedMenuController first.")

    def _create_mock_form_state(self, is_submittable: bool = True) -> FormValidationState:
        """Create a mock FormValidationState for testing."""
        field_states = {
            "account_size": FieldValidationState(
                field_name="account_size",
                value="10000" if is_submittable else "",
                is_valid=is_submittable,
                error_message="" if is_submittable else "Required field",
                is_required=True
            )
        }

        return FormValidationState(
            form_id="test_form",
            field_states=field_states,
            has_errors=not is_submittable,
            all_required_filled=is_submittable,
            is_submittable=is_submittable
        )


class TestContractInterfaceDefinitions:
    """Test that all contract interfaces are properly defined."""

    def test_ui_controller_interface_exists(self):
        """Test that UIController interface is properly defined."""
        assert hasattr(UIController, 'update_button_state')
        assert hasattr(UIController, 'show_field_error')
        assert hasattr(UIController, 'hide_field_error')
        assert hasattr(UIController, 'update_form_validation')
        assert hasattr(UIController, 'handle_field_change')
        assert hasattr(UIController, 'execute_calculation')
        assert hasattr(UIController, 'configure_responsive_layout')
        assert hasattr(UIController, 'handle_window_resize')

        # Should not be instantiable (abstract)
        with pytest.raises(TypeError):
            UIController()

    def test_window_controller_interface_exists(self):
        """Test that WindowController interface is properly defined."""
        assert hasattr(WindowController, 'save_window_state')
        assert hasattr(WindowController, 'restore_window_state')
        assert hasattr(WindowController, 'validate_window_bounds')
        assert hasattr(WindowController, 'setup_window_event_handlers')
        assert hasattr(WindowController, 'apply_minimum_size_constraints')

        # Should not be instantiable (abstract)
        with pytest.raises(TypeError):
            WindowController()

    def test_menu_controller_interface_exists(self):
        """Test that MenuController interface is properly defined."""
        assert hasattr(MenuController, 'handle_calculate_menu_action')
        assert hasattr(MenuController, 'update_menu_state')
        assert hasattr(MenuController, 'show_menu_validation_dialog')

        # Should not be instantiable (abstract)
        with pytest.raises(TypeError):
            MenuController()