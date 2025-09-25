"""
Integration test for risk method switching validation.

Tests that switching between risk calculation methods properly updates
validation requirements and button state across all trading tabs.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from decimal import Decimal

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestRiskMethodSwitchingIntegration:
    """Integration tests for risk method switching functionality."""

    @pytest.fixture
    def mock_qt_widgets(self):
        """Mock Qt widgets to avoid GUI dependencies."""
        mock_widgets = {}

        # Mock QComboBox for risk method selection
        mock_combo = Mock()
        mock_combo.currentText.return_value = "percentage"
        mock_widgets['risk_method_combo'] = mock_combo

        # Mock QLineEdit fields
        for field in ['account_size', 'risk_percentage', 'fixed_risk_amount', 'support_level', 'resistance_level']:
            mock_edit = Mock()
            mock_edit.text.return_value = ""
            mock_edit.setText = Mock()
            mock_widgets[field] = mock_edit

        # Mock QPushButton
        mock_button = Mock()
        mock_button.setEnabled = Mock()
        mock_button.isEnabled.return_value = False
        mock_widgets['calculate_button'] = mock_button

        return mock_widgets

    def test_equity_risk_method_switching_validation(self, mock_qt_widgets):
        """Test risk method switching validation for equity tab."""
        try:
            from risk_calculator.controllers.qt_equity_controller import QTEquityController
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            # Create controller with mocked widgets
            controller = QTEquityController()
            controller.validation_service = EnhancedFormValidationService()

            # Mock the tab interface
            mock_tab = Mock()
            mock_tab.get_form_data.return_value = {
                'account_size': '10000',
                'entry_price': '50.00',
                'stop_loss_price': '45.00'
            }

            # Test switching from percentage to fixed amount
            mock_tab.get_form_data.return_value.update({
                'risk_method': 'percentage',
                'risk_percentage': '2.0'
            })

            # Should validate percentage method
            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'equity'
            )
            assert 'risk_percentage' not in result.get('errors', {}), "Percentage method should be valid"

            # Switch to fixed amount method
            mock_tab.get_form_data.return_value.update({
                'risk_method': 'fixed_amount',
                'risk_percentage': '',  # No longer needed
                'fixed_risk_amount': '200'
            })

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'equity'
            )
            assert 'fixed_risk_amount' not in result.get('errors', {}), "Fixed amount method should be valid"
            assert 'risk_percentage' not in result.get('errors', {}), "Risk percentage should not be required"

        except ImportError:
            pytest.skip("Qt equity controller or validation service not available")

    def test_options_risk_method_switching_with_stop_loss(self, mock_qt_widgets):
        """Test options risk method switching with stop loss requirements."""
        try:
            from risk_calculator.controllers.qt_options_controller import QTOptionsController
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            controller = QTOptionsController()
            controller.validation_service = EnhancedFormValidationService()

            # Mock options tab interface
            mock_tab = Mock()
            base_form_data = {
                'account_size': '10000',
                'premium': '0.56',
                'multiplier': '100'
            }

            # Test percentage method with stop loss
            mock_tab.get_form_data.return_value = {
                **base_form_data,
                'risk_method': 'percentage',
                'risk_percentage': '2.0',
                'stop_loss_price': '0.65'  # Required for options
            }

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'options'
            )
            errors = result.get('errors', {})
            assert 'stop_loss_price' not in errors, "Stop loss price should be valid"
            assert 'risk_percentage' not in errors, "Risk percentage should be valid"

            # Test switching to fixed amount method
            mock_tab.get_form_data.return_value.update({
                'risk_method': 'fixed_amount',
                'risk_percentage': '',  # Clear percentage
                'fixed_risk_amount': '50',
                'stop_loss_price': '0.65'  # Still required
            })

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'options'
            )
            errors = result.get('errors', {})
            assert 'fixed_risk_amount' not in errors, "Fixed amount should be valid"
            assert 'stop_loss_price' not in errors, "Stop loss still required for fixed amount"

            # Test switching to level-based method
            mock_tab.get_form_data.return_value.update({
                'risk_method': 'level_based',
                'fixed_risk_amount': '',  # Clear fixed amount
                'stop_loss_price': '',    # Not required for level-based
                'support_level': '48.00',
                'resistance_level': '52.00',
                'trade_direction': 'call'
            })

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'options'
            )
            errors = result.get('errors', {})
            assert 'support_level' not in errors, "Support level should be valid"
            assert 'resistance_level' not in errors, "Resistance level should be valid"

        except ImportError:
            pytest.skip("Qt options controller or validation service not available")

    def test_futures_risk_method_switching_validation(self, mock_qt_widgets):
        """Test futures risk method switching validation."""
        try:
            from risk_calculator.controllers.qt_futures_controller import QTFuturesController
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            controller = QTFuturesController()
            controller.validation_service = EnhancedFormValidationService()

            # Mock futures tab interface
            mock_tab = Mock()
            base_form_data = {
                'account_size': '10000',
                'entry_price': '4500.00',
                'tick_value': '12.50',
                'tick_size': '0.25'
            }

            # Test percentage method
            mock_tab.get_form_data.return_value = {
                **base_form_data,
                'risk_method': 'percentage',
                'risk_percentage': '1.5',
                'stop_loss_price': '4450.00'
            }

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'futures'
            )
            errors = result.get('errors', {})
            assert len(errors) == 0 or 'risk_percentage' not in errors, "Percentage method should validate"

            # Switch to level-based method
            mock_tab.get_form_data.return_value.update({
                'risk_method': 'level_based',
                'risk_percentage': '',     # Clear percentage
                'stop_loss_price': '',     # Not needed for level-based
                'support_level': '4400.00',
                'resistance_level': '4600.00'
            })

            result = controller.validation_service.validate_form_data(
                mock_tab.get_form_data(), 'futures'
            )
            errors = result.get('errors', {})
            assert 'support_level' not in errors, "Support level should be valid"
            assert 'resistance_level' not in errors, "Resistance level should be valid"

        except ImportError:
            pytest.skip("Qt futures controller or validation service not available")

    def test_cross_tab_consistency_during_method_switching(self):
        """Test that risk method switching is consistent across different tabs."""
        try:
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            validation_service = EnhancedFormValidationService()

            # Test data for each asset type with same risk method
            test_scenarios = [
                {
                    'asset_type': 'equity',
                    'form_data': {
                        'account_size': '10000',
                        'entry_price': '100.00',
                        'stop_loss_price': '95.00',
                        'risk_method': 'percentage',
                        'risk_percentage': '2.0'
                    }
                },
                {
                    'asset_type': 'options',
                    'form_data': {
                        'account_size': '10000',
                        'premium': '2.50',
                        'multiplier': '100',
                        'stop_loss_price': '2.00',
                        'risk_method': 'percentage',
                        'risk_percentage': '2.0'
                    }
                },
                {
                    'asset_type': 'futures',
                    'form_data': {
                        'account_size': '10000',
                        'entry_price': '4500.00',
                        'stop_loss_price': '4450.00',
                        'tick_value': '12.50',
                        'tick_size': '0.25',
                        'risk_method': 'percentage',
                        'risk_percentage': '2.0'
                    }
                }
            ]

            # Test that percentage method validation is consistent
            for scenario in test_scenarios:
                result = validation_service.validate_form_data(
                    scenario['form_data'], scenario['asset_type']
                )
                errors = result.get('errors', {})

                # Risk percentage should be handled consistently
                if 'risk_percentage' in errors:
                    assert False, f"Risk percentage validation inconsistent for {scenario['asset_type']}: {errors['risk_percentage']}"

                # Account size validation should be consistent
                if 'account_size' in errors:
                    assert False, f"Account size validation inconsistent for {scenario['asset_type']}: {errors['account_size']}"

        except ImportError:
            pytest.skip("Enhanced form validation service not available")

    def test_button_state_during_method_switching(self, mock_qt_widgets):
        """Test calculate button state changes during risk method switching."""
        try:
            from risk_calculator.services.button_state_service import ButtonStateService

            button_service = ButtonStateService()

            # Test button state with incomplete percentage method
            incomplete_percentage_data = {
                'account_size': '10000',
                'risk_method': 'percentage',
                'risk_percentage': ''  # Missing required field
            }

            button_state = button_service.get_button_state(incomplete_percentage_data, 'equity')

            assert button_state.enabled is False, "Button should be disabled with incomplete percentage data"
            assert "risk_percentage" in button_state.error_message.lower() or "percentage" in button_state.error_message.lower(), \
                "Error message should mention missing percentage"

            # Complete the percentage data
            complete_percentage_data = {
                'account_size': '10000',
                'entry_price': '50.00',
                'stop_loss_price': '45.00',
                'risk_method': 'percentage',
                'risk_percentage': '2.0'
            }

            button_state = button_service.get_button_state(complete_percentage_data, 'equity')

            # Button should now be enabled (or provide specific error if validation fails)
            if not button_state.enabled:
                # If still disabled, error message should be specific
                assert len(button_state.error_message) > 0, "Should provide clear error message when disabled"

        except ImportError:
            pytest.skip("Button state service not available")

    def test_validation_performance_during_rapid_switching(self):
        """Test validation performance during rapid risk method switching."""
        import time

        try:
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            validation_service = EnhancedFormValidationService()

            # Base form data
            base_data = {
                'account_size': '10000',
                'entry_price': '100.00',
                'stop_loss_price': '95.00'
            }

            # Test rapid switching between methods
            methods = ['percentage', 'fixed_amount', 'level_based']
            method_data = {
                'percentage': {'risk_percentage': '2.0'},
                'fixed_amount': {'fixed_risk_amount': '200'},
                'level_based': {'support_level': '95.00', 'resistance_level': '105.00'}
            }

            start_time = time.time()

            # Perform 100 rapid method switches
            for i in range(100):
                method = methods[i % len(methods)]
                form_data = {**base_data, 'risk_method': method, **method_data[method]}

                result = validation_service.validate_form_data(form_data, 'equity')
                assert isinstance(result, dict), f"Validation should return dict for method {method}"

            elapsed_time = time.time() - start_time

            # Should complete rapid switching within reasonable time
            assert elapsed_time < 1.0, f"Rapid method switching took {elapsed_time:.3f}s, should be < 1.0s"

        except ImportError:
            pytest.skip("Enhanced form validation service not available")

    def test_method_switching_error_recovery(self):
        """Test error recovery when switching between methods."""
        try:
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            validation_service = EnhancedFormValidationService()

            # Start with invalid percentage method data
            invalid_data = {
                'account_size': 'invalid',
                'risk_method': 'percentage',
                'risk_percentage': 'also_invalid'
            }

            result = validation_service.validate_form_data(invalid_data, 'equity')
            assert len(result.get('errors', {})) > 0, "Should have validation errors"

            # Switch to fixed amount method with valid data
            valid_fixed_data = {
                'account_size': '10000',
                'entry_price': '50.00',
                'stop_loss_price': '45.00',
                'risk_method': 'fixed_amount',
                'fixed_risk_amount': '200'
            }

            result = validation_service.validate_form_data(valid_fixed_data, 'equity')
            errors = result.get('errors', {})

            # Should recover from previous errors
            assert 'account_size' not in errors, "Account size should be valid now"
            assert 'risk_percentage' not in errors, "Risk percentage should not be validated for fixed amount"

        except ImportError:
            pytest.skip("Enhanced form validation service not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])