"""
Integration test for cross-tab validation consistency
This test MUST FAIL until cross-tab validation is properly implemented.
"""

import pytest
import sys
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QTabWidget


class TestCrossTabValidation:
    """Integration tests for validation consistency across different tabs."""

    @classmethod
    def setup_class(cls):
        """Setup Qt application for testing."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setup_method(self):
        """Setup test method with Qt application components."""
        try:
            from risk_calculator.qt_main import RiskCalculatorQtApp
            from risk_calculator.controllers.qt_main_controller import QtMainController

            self.qt_app = RiskCalculatorQtApp()
            self.qt_app.create_application()

            self.controller = QtMainController()
            self.controller.initialize_application()
            self.main_window = self.controller.main_window

        except ImportError as e:
            pytest.fail(f"Required Qt components not implemented: {e}")

    def teardown_method(self):
        """Cleanup after each test."""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.close()

    def test_validation_consistency_across_tabs(self):
        """Test that validation rules are consistent across all tabs."""
        tabs = ['equity', 'options', 'futures']

        # Test same validation rule applies consistently
        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Test empty account size validation
            tab.account_size_entry.clear()
            QApplication.processEvents()

            assert not calculate_button.isEnabled(), f"Button should be disabled with empty account size in {tab_name} tab"

            tooltip = calculate_button.toolTip()
            if tooltip:  # If tooltips are implemented
                tooltip_lower = tooltip.lower()
                assert 'account' in tooltip_lower or 'required' in tooltip_lower, f"Tooltip should indicate account size issue in {tab_name} tab: '{tooltip}'"

    def test_numeric_validation_consistency(self):
        """Test that numeric field validation is consistent across tabs."""
        tabs = ['equity', 'options', 'futures']

        invalid_values = ['not_a_number', 'abc123', '12.34.56', '']

        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            for invalid_value in invalid_values:
                # Test account size with invalid value
                tab.account_size_entry.setText(invalid_value)
                QApplication.processEvents()

                assert not calculate_button.isEnabled(), f"Button should be disabled with invalid account size '{invalid_value}' in {tab_name} tab"

                # Reset for next test
                tab.account_size_entry.clear()

    def test_negative_value_validation_consistency(self):
        """Test that negative value validation is consistent across tabs."""
        tabs = ['equity', 'options', 'futures']

        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Test negative account size
            tab.account_size_entry.setText('-1000')
            QApplication.processEvents()

            assert not calculate_button.isEnabled(), f"Button should be disabled with negative account size in {tab_name} tab"

            # Reset
            tab.account_size_entry.clear()

    def test_zero_value_validation_consistency(self):
        """Test that zero value validation is consistent across tabs."""
        tabs = ['equity', 'options', 'futures']

        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Test zero account size
            tab.account_size_entry.setText('0')
            QApplication.processEvents()

            assert not calculate_button.isEnabled(), f"Button should be disabled with zero account size in {tab_name} tab"

            # Reset
            tab.account_size_entry.clear()

    def test_tab_switching_preserves_validation_state(self):
        """Test that switching tabs preserves validation state appropriately."""
        # Fill equity tab with valid data
        equity_tab = self.main_window.tabs['equity']
        equity_tab.risk_method_combo.setCurrentText('Percentage')
        equity_tab.account_size_entry.setText('10000')
        equity_tab.risk_percentage_entry.setText('2')
        equity_tab.entry_price_entry.setText('50.00')
        equity_tab.stop_loss_price_entry.setText('48.00')

        QApplication.processEvents()
        assert equity_tab.calculate_button.isEnabled(), "Equity tab button should be enabled with valid data"

        # Switch to options tab
        options_tab = self.main_window.tabs['options']
        self.main_window.tab_widget.setCurrentWidget(options_tab)
        QApplication.processEvents()

        # Options tab should have its own validation state
        assert not options_tab.calculate_button.isEnabled(), "Options tab button should be disabled with empty form"

        # Switch back to equity tab
        self.main_window.tab_widget.setCurrentWidget(equity_tab)
        QApplication.processEvents()

        # Equity tab should maintain its validation state
        assert equity_tab.calculate_button.isEnabled(), "Equity tab button should remain enabled after tab switch"

    def test_independent_validation_states_across_tabs(self):
        """Test that each tab maintains independent validation state."""
        # Setup different validation states in each tab
        tab_configs = {
            'equity': {
                'valid': True,
                'data': {
                    'risk_method': 'Percentage',
                    'account_size': '10000',
                    'risk_percentage': '2',
                    'entry_price': '50.00',
                    'stop_loss_price': '48.00'
                }
            },
            'options': {
                'valid': False,
                'data': {
                    'account_size': 'invalid',  # Invalid data
                    'fixed_risk_amount': '200',
                    'option_premium': '2.50'
                }
            },
            'futures': {
                'valid': True,
                'data': {
                    'account_size': '25000',
                    'fixed_risk_amount': '500',
                    'tick_value': '12.50',
                    'ticks_at_risk': '8'
                }
            }
        }

        # Configure each tab
        for tab_name, config in tab_configs.items():
            tab = self.main_window.tabs[tab_name]

            # Set risk method if specified
            if 'risk_method' in config['data']:
                tab.risk_method_combo.setCurrentText(config['data']['risk_method'])

            # Fill data
            for field_name, value in config['data'].items():
                if field_name != 'risk_method':
                    field_widget = getattr(tab, f'{field_name}_entry', None)
                    if field_widget:
                        field_widget.setText(value)

        QApplication.processEvents()

        # Verify each tab has expected validation state
        for tab_name, config in tab_configs.items():
            tab = self.main_window.tabs[tab_name]
            expected_enabled = config['valid']
            actual_enabled = tab.calculate_button.isEnabled()

            assert actual_enabled == expected_enabled, f"{tab_name} tab button should be {'enabled' if expected_enabled else 'disabled'}, but is {'enabled' if actual_enabled else 'disabled'}"

    def test_validation_error_types_consistency(self):
        """Test that same types of validation errors are handled consistently."""
        tabs = ['equity', 'options', 'futures']

        error_test_cases = [
            {'field': 'account_size', 'value': 'not_a_number', 'error_type': 'invalid_number'},
            {'field': 'account_size', 'value': '-1000', 'error_type': 'negative_value'},
            {'field': 'account_size', 'value': '0', 'error_type': 'zero_value'},
            {'field': 'account_size', 'value': '', 'error_type': 'empty_required'}
        ]

        for case in error_test_cases:
            for tab_name in tabs:
                tab = self.main_window.tabs[tab_name]
                calculate_button = tab.calculate_button

                # Apply error case
                field_widget = getattr(tab, f"{case['field']}_entry", None)
                if field_widget:
                    field_widget.setText(case['value'])

                QApplication.processEvents()

                # Should be disabled across all tabs
                assert not calculate_button.isEnabled(), f"Button should be disabled for {case['error_type']} in {tab_name} tab"

                # Reset
                field_widget.clear()

    def test_button_state_independence_across_tabs(self):
        """Test that button states are independent across tabs."""
        # Enable button in equity tab
        equity_tab = self.main_window.tabs['equity']
        equity_tab.risk_method_combo.setCurrentText('Percentage')
        equity_tab.account_size_entry.setText('10000')
        equity_tab.risk_percentage_entry.setText('2')
        equity_tab.entry_price_entry.setText('50.00')
        equity_tab.stop_loss_price_entry.setText('48.00')

        # Disable button in options tab
        options_tab = self.main_window.tabs['options']
        options_tab.account_size_entry.setText('invalid')

        QApplication.processEvents()

        # Verify independent states
        assert equity_tab.calculate_button.isEnabled(), "Equity tab button should be enabled"
        assert not options_tab.calculate_button.isEnabled(), "Options tab button should be disabled"

        # States should not affect each other
        equity_tab.account_size_entry.setText('invalid')
        QApplication.processEvents()

        assert not equity_tab.calculate_button.isEnabled(), "Equity tab button should now be disabled"
        # Options tab state should be unchanged
        assert not options_tab.calculate_button.isEnabled(), "Options tab button should remain disabled"

    def test_validation_message_consistency(self):
        """Test that validation messages are consistent across tabs."""
        tabs = ['equity', 'options', 'futures']

        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Create same error in each tab
            tab.account_size_entry.setText('invalid_number')
            QApplication.processEvents()

            assert not calculate_button.isEnabled(), f"Button should be disabled in {tab_name} tab"

            tooltip = calculate_button.toolTip()
            if tooltip:  # If tooltips are implemented
                # Should contain similar error messaging
                tooltip_lower = tooltip.lower()
                error_indicators = ['invalid', 'number', 'numeric', 'error']
                found_indicators = [ind for ind in error_indicators if ind in tooltip_lower]
                assert len(found_indicators) > 0, f"Tooltip should indicate numeric error in {tab_name} tab: '{tooltip}'"

    def test_field_clearing_consistency(self):
        """Test that field clearing behavior is consistent across tabs."""
        tabs = ['equity', 'options', 'futures']

        for tab_name in tabs:
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Fill and clear account size
            tab.account_size_entry.setText('10000')
            QApplication.processEvents()

            tab.account_size_entry.clear()
            QApplication.processEvents()

            # Should be disabled after clearing required field
            assert not calculate_button.isEnabled(), f"Button should be disabled after clearing account size in {tab_name} tab"

    def test_concurrent_tab_validation_performance(self):
        """Test that validation performance is consistent when multiple tabs are active."""
        import time

        # Fill all tabs with data that requires validation
        tab_data = {
            'equity': {
                'risk_method': 'Percentage',
                'account_size': '10000',
                'risk_percentage': '2',
                'entry_price': '50.00',
                'stop_loss_price': '48.00'
            },
            'options': {
                'account_size': '10000',
                'fixed_risk_amount': '200',
                'option_premium': '2.50'
            },
            'futures': {
                'account_size': '25000',
                'fixed_risk_amount': '500',
                'tick_value': '12.50',
                'ticks_at_risk': '8'
            }
        }

        start_time = time.time()

        # Configure all tabs
        for tab_name, data in tab_data.items():
            tab = self.main_window.tabs[tab_name]

            if 'risk_method' in data:
                tab.risk_method_combo.setCurrentText(data['risk_method'])

            for field_name, value in data.items():
                if field_name != 'risk_method':
                    field_widget = getattr(tab, f'{field_name}_entry', None)
                    if field_widget:
                        field_widget.setText(value)

        QApplication.processEvents()
        end_time = time.time()

        total_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Should complete validation for all tabs quickly
        assert total_time < 200, f"Concurrent tab validation should complete in <200ms, took {total_time:.2f}ms"

        # All tabs should have appropriate button states
        for tab_name in tab_data.keys():
            tab = self.main_window.tabs[tab_name]
            assert tab.calculate_button.isEnabled(), f"{tab_name} tab button should be enabled with valid data"

    def test_cross_tab_data_isolation(self):
        """Test that data in one tab doesn't affect validation in another tab."""
        equity_tab = self.main_window.tabs['equity']
        options_tab = self.main_window.tabs['options']

        # Fill equity tab with invalid data
        equity_tab.account_size_entry.setText('invalid')
        QApplication.processEvents()

        # Fill options tab with valid data
        options_tab.account_size_entry.setText('10000')
        options_tab.fixed_risk_amount_entry.setText('200')
        options_tab.option_premium_entry.setText('2.50')
        QApplication.processEvents()

        # Options tab should be enabled despite equity tab having invalid data
        assert not equity_tab.calculate_button.isEnabled(), "Equity tab should be disabled with invalid data"
        assert options_tab.calculate_button.isEnabled(), "Options tab should be enabled with valid data"

    def test_validation_recovery_independence(self):
        """Test that validation recovery in one tab doesn't affect others."""
        equity_tab = self.main_window.tabs['equity']
        options_tab = self.main_window.tabs['options']

        # Both tabs start with invalid data
        equity_tab.account_size_entry.setText('invalid')
        options_tab.account_size_entry.setText('invalid')
        QApplication.processEvents()

        assert not equity_tab.calculate_button.isEnabled(), "Equity tab should be disabled"
        assert not options_tab.calculate_button.isEnabled(), "Options tab should be disabled"

        # Fix equity tab only
        equity_tab.account_size_entry.setText('10000')
        equity_tab.risk_method_combo.setCurrentText('Percentage')
        equity_tab.risk_percentage_entry.setText('2')
        equity_tab.entry_price_entry.setText('50.00')
        equity_tab.stop_loss_price_entry.setText('48.00')
        QApplication.processEvents()

        # Only equity tab should recover
        assert equity_tab.calculate_button.isEnabled(), "Equity tab should be enabled after fixing data"
        assert not options_tab.calculate_button.isEnabled(), "Options tab should remain disabled"