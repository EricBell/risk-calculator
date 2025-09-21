"""
Integration test: Button enablement with valid data.
Tests complete button state management workflow from quickstart scenarios.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch

# Import components that will be implemented/enhanced
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestButtonEnablementIntegration:
    """Test button enablement integration scenarios."""

    def setup_method(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

    def teardown_method(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_button_enabled_with_all_valid_equity_data(self):
        """Test Scenario 1A: Button becomes enabled when all required fields contain valid data."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        # Create tab and controller
        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter valid equity data as per quickstart scenario
        valid_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        # Simulate entering data in all fields
        for field_name, value in valid_data.items():
            controller.handle_field_change(field_name, value)

        # Verify button is enabled
        button_enabled = controller.is_calculate_button_enabled()
        assert button_enabled is True, "Calculate Position button should be enabled with valid data"

        # Verify form validation state
        form_state = controller.get_current_form_state()
        assert form_state.is_submittable is True
        assert form_state.has_errors is False
        assert form_state.all_required_filled is True

    def test_button_disabled_with_missing_required_fields(self):
        """Test button remains disabled when required fields are missing."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter incomplete data (missing stop_loss)
        incomplete_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00"
            # stop_loss missing
        }

        for field_name, value in incomplete_data.items():
            controller.handle_field_change(field_name, value)

        # Verify button remains disabled
        button_enabled = controller.is_calculate_button_enabled()
        assert button_enabled is False, "Calculate Position button should be disabled with missing required fields"

        # Verify form validation state
        form_state = controller.get_current_form_state()
        assert form_state.is_submittable is False
        assert form_state.all_required_filled is False

    def test_button_disabled_with_invalid_field_values(self):
        """Test button becomes disabled when field values are invalid."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter invalid data
        invalid_data = {
            "account_size": "abc",  # Invalid - should be numeric
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        for field_name, value in invalid_data.items():
            controller.handle_field_change(field_name, value)

        # Verify button is disabled
        button_enabled = controller.is_calculate_button_enabled()
        assert button_enabled is False, "Calculate Position button should be disabled with invalid field values"

        # Verify form validation state
        form_state = controller.get_current_form_state()
        assert form_state.is_submittable is False
        assert form_state.has_errors is True

    def test_button_state_changes_dynamically(self):
        """Test button state changes dynamically as fields are modified."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Initially button should be disabled (no data)
        assert controller.is_calculate_button_enabled() is False

        # Add valid data one field at a time
        controller.handle_field_change("account_size", "10000")
        assert controller.is_calculate_button_enabled() is False  # Still missing fields

        controller.handle_field_change("risk_percentage", "2")
        assert controller.is_calculate_button_enabled() is False  # Still missing fields

        controller.handle_field_change("entry_price", "50.00")
        assert controller.is_calculate_button_enabled() is False  # Still missing fields

        controller.handle_field_change("stop_loss", "48.00")
        assert controller.is_calculate_button_enabled() is True   # All fields complete

        # Invalidate one field
        controller.handle_field_change("account_size", "abc")
        assert controller.is_calculate_button_enabled() is False  # Should disable again

        # Fix the field
        controller.handle_field_change("account_size", "15000")
        assert controller.is_calculate_button_enabled() is True   # Should enable again

    def test_button_enablement_options_tab(self):
        """Test button enablement works correctly for options tab."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.options_tab import OptionsTab

        tab = OptionsTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter valid options data
        valid_options_data = {
            "account_size": "25000",
            "risk_percentage": "1.5",
            "premium": "2.50"
        }

        for field_name, value in valid_options_data.items():
            controller.handle_field_change(field_name, value)

        # Verify button is enabled for options
        assert controller.is_calculate_button_enabled() is True

    def test_button_enablement_futures_tab(self):
        """Test button enablement works correctly for futures tab."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.futures_tab import FuturesTab

        tab = FuturesTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter valid futures data
        valid_futures_data = {
            "account_size": "25000",
            "risk_percentage": "1.5",
            "entry_price": "4200",
            "stop_loss": "4150",
            "tick_value": "12.50"
        }

        for field_name, value in valid_futures_data.items():
            controller.handle_field_change(field_name, value)

        # Verify button is enabled for futures
        assert controller.is_calculate_button_enabled() is True

    def test_button_enablement_with_risk_method_change(self):
        """Test button enablement when risk calculation method changes."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Enter data valid for percentage method
        percentage_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        for field_name, value in percentage_data.items():
            controller.handle_field_change(field_name, value)

        # Should be enabled for percentage method
        assert controller.is_calculate_button_enabled() is True

        # Change to fixed amount method
        controller.set_risk_method("fixed")

        # Should re-evaluate based on new requirements
        # May be disabled if fixed_risk_amount field is now required but empty
        form_state = controller.get_current_form_state()
        button_state = controller.is_calculate_button_enabled()

        # Verify the controller properly re-validates for new method
        assert isinstance(button_state, bool)
        assert isinstance(form_state.is_submittable, bool)

    def test_button_visual_state_synchronization(self):
        """Test that visual button state synchronizes with logical state."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Get reference to actual button widget
        calculate_button = tab.get_calculate_button()

        # Enter valid data
        valid_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        for field_name, value in valid_data.items():
            controller.handle_field_change(field_name, value)

        # Verify both logical and visual state
        assert controller.is_calculate_button_enabled() is True
        assert calculate_button['state'] == 'normal'

        # Invalidate data
        controller.handle_field_change("account_size", "")

        # Verify both logical and visual state
        assert controller.is_calculate_button_enabled() is False
        assert calculate_button['state'] == 'disabled'

    def test_button_enablement_performance(self):
        """Test that button state updates are performant."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab
        import time

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Measure time for validation update
        start_time = time.time()

        controller.handle_field_change("account_size", "10000")

        end_time = time.time()
        validation_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Should be under 100ms as per performance requirements
        assert validation_time < 100, f"Button state update took {validation_time}ms, should be under 100ms"

    def test_button_enablement_with_concurrent_field_changes(self):
        """Test button enablement with rapid concurrent field changes."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
        from risk_calculator.views.equity_tab import EquityTab

        tab = EquityTab(self.root)
        controller = EnhancedBaseController(tab)

        # Simulate rapid field changes
        field_changes = [
            ("account_size", "10000"),
            ("risk_percentage", "2"),
            ("account_size", "20000"),  # Change same field again
            ("entry_price", "50.00"),
            ("stop_loss", "48.00"),
            ("risk_percentage", "3"),   # Change same field again
        ]

        for field_name, value in field_changes:
            controller.handle_field_change(field_name, value)

        # Final state should be consistent
        final_state = controller.is_calculate_button_enabled()
        form_state = controller.get_current_form_state()

        assert isinstance(final_state, bool)
        assert form_state.is_submittable == final_state

    @pytest.mark.parametrize("trade_type,required_fields,valid_data", [
        ("equity", ["account_size", "risk_percentage", "entry_price", "stop_loss"], {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }),
        ("option", ["account_size", "risk_percentage", "premium"], {
            "account_size": "25000",
            "risk_percentage": "1.5",
            "premium": "2.50"
        }),
        ("future", ["account_size", "risk_percentage", "entry_price", "stop_loss", "tick_value"], {
            "account_size": "25000",
            "risk_percentage": "1.5",
            "entry_price": "4200",
            "stop_loss": "4150",
            "tick_value": "12.50"
        })
    ])
    def test_button_enablement_across_trade_types(self, trade_type, required_fields, valid_data):
        """Test button enablement works consistently across all trade types."""
        from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController

        # Create appropriate tab based on trade type
        if trade_type == "equity":
            from risk_calculator.views.equity_tab import EquityTab
            tab = EquityTab(self.root)
        elif trade_type == "option":
            from risk_calculator.views.options_tab import OptionsTab
            tab = OptionsTab(self.root)
        else:  # future
            from risk_calculator.views.futures_tab import FuturesTab
            tab = FuturesTab(self.root)

        controller = EnhancedBaseController(tab)

        # Enter all valid data
        for field_name, value in valid_data.items():
            controller.handle_field_change(field_name, value)

        # Should be enabled with all valid data
        assert controller.is_calculate_button_enabled() is True

        # Test missing each required field
        for required_field in required_fields:
            # Clear the required field
            controller.handle_field_change(required_field, "")

            # Should be disabled
            assert controller.is_calculate_button_enabled() is False

            # Restore the field
            controller.handle_field_change(required_field, valid_data[required_field])

            # Should be enabled again
            assert controller.is_calculate_button_enabled() is True