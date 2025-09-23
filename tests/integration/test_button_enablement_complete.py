"""
Integration test for calculate button enablement with complete form
This test MUST FAIL until button enablement is properly implemented.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import QTimer


class TestButtonEnablementComplete:
    """Integration tests for calculate button enablement with complete forms."""

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

            # Create controller and main window
            self.controller = QtMainController()
            self.controller.initialize_application()
            self.main_window = self.controller.main_window

        except ImportError as e:
            pytest.fail(f"Required Qt components not implemented: {e}")

    def teardown_method(self):
        """Cleanup after each test."""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.close()

    def test_button_enabled_with_complete_equity_percentage_form(self):
        """Test button enables with complete equity percentage form."""
        # Get equity tab
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        # Fill all required fields for percentage method
        form_data = {
            'account_size': '10000',
            'risk_percentage': '2',
            'entry_price': '50.00',
            'stop_loss_price': '48.00'
        }

        # Set risk method to percentage
        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Fill form fields
        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        # Process events to trigger validation
        QApplication.processEvents()

        # Button should be enabled
        assert calculate_button.isEnabled(), "Calculate button should be enabled with complete form"

    def test_button_enabled_with_complete_equity_fixed_amount_form(self):
        """Test button enables with complete equity fixed amount form."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        # Set risk method to fixed amount
        equity_tab.risk_method_combo.setCurrentText('Fixed Amount')

        # Fill all required fields for fixed amount method
        form_data = {
            'account_size': '10000',
            'fixed_risk_amount': '200',
            'entry_price': '50.00',
            'stop_loss_price': '48.00'
        }

        # Fill form fields
        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Calculate button should be enabled with complete fixed amount form"

    def test_button_enabled_with_complete_equity_level_form(self):
        """Test button enables with complete equity level form."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        # Set risk method to level
        equity_tab.risk_method_combo.setCurrentText('Level')

        # Fill all required fields for level method
        form_data = {
            'account_size': '10000',
            'level': '48.50',
            'entry_price': '50.00',
            'stop_loss_price': '48.00'
        }

        # Fill form fields
        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Calculate button should be enabled with complete level form"

    def test_button_enabled_with_complete_options_form(self):
        """Test button enables with complete options form."""
        options_tab = self.main_window.tabs['options']
        calculate_button = options_tab.calculate_button

        # Fill all required fields for options
        form_data = {
            'account_size': '10000',
            'fixed_risk_amount': '200',
            'option_premium': '2.50'
        }

        # Fill form fields
        for field_name, value in form_data.items():
            field_widget = getattr(options_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Calculate button should be enabled with complete options form"

    def test_button_enabled_with_complete_futures_form(self):
        """Test button enables with complete futures form."""
        futures_tab = self.main_window.tabs['futures']
        calculate_button = futures_tab.calculate_button

        # Fill all required fields for futures
        form_data = {
            'account_size': '25000',
            'fixed_risk_amount': '500',
            'tick_value': '12.50',
            'ticks_at_risk': '8'
        }

        # Fill form fields
        for field_name, value in form_data.items():
            field_widget = getattr(futures_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Calculate button should be enabled with complete futures form"

    def test_button_state_immediate_response(self):
        """Test that button state responds immediately to form completion."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        # Initially should be disabled
        assert not calculate_button.isEnabled(), "Button should start disabled"

        # Set risk method
        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Fill fields one by one and check button state
        fields = [
            ('account_size', '10000'),
            ('risk_percentage', '2'),
            ('entry_price', '50.00')
        ]

        for field_name, value in fields:
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)
                QApplication.processEvents()
                # Should still be disabled until all fields filled
                assert not calculate_button.isEnabled(), f"Button should be disabled after filling {field_name}"

        # Fill last required field
        equity_tab.stop_loss_price_entry.setText('48.00')
        QApplication.processEvents()

        # Now should be enabled
        assert calculate_button.isEnabled(), "Button should be enabled after filling all required fields"

    def test_button_enablement_with_whitespace_handling(self):
        """Test button enablement handles whitespace correctly."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Fill fields with leading/trailing whitespace
        form_data = {
            'account_size': '  10000  ',
            'risk_percentage': '2 ',
            'entry_price': ' 50.00',
            'stop_loss_price': '48.00 '
        }

        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Button should be enabled with whitespace-padded valid values"

    def test_button_enablement_with_decimal_variations(self):
        """Test button enablement with various decimal formats."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Test various valid decimal formats
        test_cases = [
            {'account_size': '10000', 'risk_percentage': '2.0', 'entry_price': '50', 'stop_loss_price': '48.00'},
            {'account_size': '10000.00', 'risk_percentage': '2', 'entry_price': '50.0', 'stop_loss_price': '48'},
            {'account_size': '10000.0', 'risk_percentage': '2.5', 'entry_price': '50.50', 'stop_loss_price': '48.25'}
        ]

        for case_data in test_cases:
            # Clear fields first
            for field_name in case_data.keys():
                field_widget = getattr(equity_tab, f'{field_name}_entry', None)
                if field_widget:
                    field_widget.clear()

            QApplication.processEvents()
            assert not calculate_button.isEnabled(), "Button should be disabled with cleared fields"

            # Fill with test case data
            for field_name, value in case_data.items():
                field_widget = getattr(equity_tab, f'{field_name}_entry', None)
                if field_widget:
                    field_widget.setText(value)

            QApplication.processEvents()
            assert calculate_button.isEnabled(), f"Button should be enabled with decimal case: {case_data}"

    def test_button_enablement_performance_under_100ms(self):
        """Test that button enablement response is under 100ms."""
        import time

        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Fill all but one field
        form_data = {
            'account_size': '10000',
            'risk_percentage': '2',
            'entry_price': '50.00'
        }

        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        # Measure time to enable button when last field is filled
        start_time = time.time()
        equity_tab.stop_loss_price_entry.setText('48.00')
        QApplication.processEvents()
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        assert calculate_button.isEnabled(), "Button should be enabled"
        assert response_time < 100, f"Button enablement should respond in <100ms, took {response_time:.2f}ms"

    def test_button_enablement_across_all_tabs(self):
        """Test button enablement works consistently across all tabs."""
        tabs_data = {
            'equity': {
                'method': 'Percentage',
                'fields': {
                    'account_size': '10000',
                    'risk_percentage': '2',
                    'entry_price': '50.00',
                    'stop_loss_price': '48.00'
                }
            },
            'options': {
                'fields': {
                    'account_size': '10000',
                    'fixed_risk_amount': '200',
                    'option_premium': '2.50'
                }
            },
            'futures': {
                'fields': {
                    'account_size': '25000',
                    'fixed_risk_amount': '500',
                    'tick_value': '12.50',
                    'ticks_at_risk': '8'
                }
            }
        }

        for tab_name, tab_config in tabs_data.items():
            tab = self.main_window.tabs[tab_name]
            calculate_button = tab.calculate_button

            # Set risk method if specified
            if 'method' in tab_config:
                tab.risk_method_combo.setCurrentText(tab_config['method'])

            # Fill form fields
            for field_name, value in tab_config['fields'].items():
                field_widget = getattr(tab, f'{field_name}_entry', None)
                if field_widget:
                    field_widget.setText(value)

            QApplication.processEvents()

            assert calculate_button.isEnabled(), f"Calculate button should be enabled in {tab_name} tab"

    def test_button_tooltip_when_enabled(self):
        """Test button tooltip when enabled shows appropriate message."""
        equity_tab = self.main_window.tabs['equity']
        calculate_button = equity_tab.calculate_button

        equity_tab.risk_method_combo.setCurrentText('Percentage')

        # Fill complete form
        form_data = {
            'account_size': '10000',
            'risk_percentage': '2',
            'entry_price': '50.00',
            'stop_loss_price': '48.00'
        }

        for field_name, value in form_data.items():
            field_widget = getattr(equity_tab, f'{field_name}_entry', None)
            if field_widget:
                field_widget.setText(value)

        QApplication.processEvents()

        assert calculate_button.isEnabled(), "Button should be enabled"

        tooltip = calculate_button.toolTip()
        # When enabled, tooltip should be empty or show calculation-ready message
        assert tooltip == "" or "calculate" in tooltip.lower(), f"Enabled button tooltip should be appropriate: '{tooltip}'"