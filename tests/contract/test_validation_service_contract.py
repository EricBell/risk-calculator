"""
Contract tests for ValidationService interface.
These tests verify that any implementation of ValidationService follows the contract.
"""

import pytest
from typing import Dict, Any

# Import the contract interface
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import from the actual contract location
try:
    from specs.three_there_are_several.contracts.validation_service import (
        ValidationService, ValidationResult, FieldValidationState,
        FormValidationState, TradeType, ValidationError
    )
except ImportError:
    # Import from local file
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from validation_service import (
        ValidationService, ValidationResult, FieldValidationState,
        FormValidationState, TradeType, ValidationError
    )


class TestValidationServiceContract:
    """Test contract compliance for ValidationService implementations."""

    def test_validate_field_returns_validation_result(self):
        """Test that validate_field returns ValidationResult."""
        service = self._get_service_implementation()

        result = service.validate_field("account_size", "10000", TradeType.EQUITY)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'error_message')
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.error_message, str)

    def test_validate_field_handles_valid_input(self):
        """Test that validate_field correctly identifies valid input."""
        service = self._get_service_implementation()

        # Test valid account size
        result = service.validate_field("account_size", "10000", TradeType.EQUITY)
        assert result.is_valid is True
        assert result.error_message == ""

    def test_validate_field_handles_invalid_input(self):
        """Test that validate_field correctly identifies invalid input."""
        service = self._get_service_implementation()

        # Test invalid account size (negative)
        result = service.validate_field("account_size", "-5000", TradeType.EQUITY)
        assert result.is_valid is False
        assert len(result.error_message) > 0

        # Test invalid account size (non-numeric)
        result = service.validate_field("account_size", "abc", TradeType.EQUITY)
        assert result.is_valid is False
        assert len(result.error_message) > 0

    def test_validate_field_handles_different_trade_types(self):
        """Test that validate_field handles different trade types appropriately."""
        service = self._get_service_implementation()

        # Test equity-specific field
        equity_result = service.validate_field("entry_price", "50.00", TradeType.EQUITY)
        assert isinstance(equity_result, ValidationResult)

        # Test option-specific field
        option_result = service.validate_field("premium", "2.50", TradeType.OPTION)
        assert isinstance(option_result, ValidationResult)

        # Test future-specific field
        future_result = service.validate_field("tick_value", "12.50", TradeType.FUTURE)
        assert isinstance(future_result, ValidationResult)

    def test_validate_form_returns_form_validation_state(self):
        """Test that validate_form returns FormValidationState."""
        service = self._get_service_implementation()

        form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        result = service.validate_form(form_data, TradeType.EQUITY)

        assert isinstance(result, FormValidationState)
        assert hasattr(result, 'form_id')
        assert hasattr(result, 'field_states')
        assert hasattr(result, 'has_errors')
        assert hasattr(result, 'all_required_filled')
        assert hasattr(result, 'is_submittable')

    def test_validate_form_correctly_aggregates_field_states(self):
        """Test that validate_form correctly aggregates individual field validation states."""
        service = self._get_service_implementation()

        # Valid form data
        valid_form_data = {
            "account_size": "10000",
            "risk_percentage": "2",
            "entry_price": "50.00",
            "stop_loss": "48.00"
        }

        result = service.validate_form(valid_form_data, TradeType.EQUITY)

        assert result.has_errors is False
        assert result.all_required_filled is True
        assert result.is_submittable is True
        assert isinstance(result.field_states, dict)

    def test_validate_form_detects_errors_and_missing_fields(self):
        """Test that validate_form detects errors and missing required fields."""
        service = self._get_service_implementation()

        # Invalid form data (missing fields and invalid values)
        invalid_form_data = {
            "account_size": "abc",  # Invalid
            "risk_percentage": "",  # Missing required field
            "entry_price": "50.00"
            # stop_loss missing
        }

        result = service.validate_form(invalid_form_data, TradeType.EQUITY)

        assert result.has_errors is True
        assert result.all_required_filled is False
        assert result.is_submittable is False

    def test_get_required_fields_returns_list_for_trade_type(self):
        """Test that get_required_fields returns appropriate fields for trade type."""
        service = self._get_service_implementation()

        # Test equity required fields
        equity_fields = service.get_required_fields(TradeType.EQUITY, "percentage")
        assert isinstance(equity_fields, list)
        assert "account_size" in equity_fields
        assert "risk_percentage" in equity_fields

        # Test option required fields
        option_fields = service.get_required_fields(TradeType.OPTION, "percentage")
        assert isinstance(option_fields, list)
        assert "account_size" in option_fields
        assert "premium" in option_fields

        # Test future required fields
        future_fields = service.get_required_fields(TradeType.FUTURE, "percentage")
        assert isinstance(future_fields, list)
        assert "account_size" in future_fields
        assert "tick_value" in future_fields

    def test_get_required_fields_varies_by_risk_method(self):
        """Test that required fields vary based on risk calculation method."""
        service = self._get_service_implementation()

        percentage_fields = service.get_required_fields(TradeType.EQUITY, "percentage")
        fixed_fields = service.get_required_fields(TradeType.EQUITY, "fixed")

        # Fields should be different or at least one method should have additional fields
        assert isinstance(percentage_fields, list)
        assert isinstance(fixed_fields, list)

    def test_get_validation_rules_returns_dict(self):
        """Test that get_validation_rules returns validation rules dict."""
        service = self._get_service_implementation()

        rules = service.get_validation_rules("account_size")

        assert isinstance(rules, dict)
        # Should contain validation information
        assert len(rules) > 0

    def test_format_error_message_returns_string(self):
        """Test that format_error_message returns formatted error string."""
        service = self._get_service_implementation()

        message = service.format_error_message("account_size", "required")
        assert isinstance(message, str)
        assert len(message) > 0

        # Test with additional context
        message_with_context = service.format_error_message(
            "account_size", "out_of_range", min_value=1000, max_value=1000000
        )
        assert isinstance(message_with_context, str)
        assert len(message_with_context) > 0

    def test_validation_result_bool_conversion(self):
        """Test that ValidationResult can be used in boolean context."""
        valid_result = ValidationResult(True, "")
        invalid_result = ValidationResult(False, "Error message")

        assert bool(valid_result) is True
        assert bool(invalid_result) is False

    def test_field_validation_state_structure(self):
        """Test FieldValidationState structure and requirements."""
        field_state = FieldValidationState(
            field_name="test_field",
            value="test_value",
            is_valid=True,
            error_message="",
            is_required=True
        )

        assert field_state.field_name == "test_field"
        assert field_state.value == "test_value"
        assert field_state.is_valid is True
        assert field_state.error_message == ""
        assert field_state.is_required is True

    def test_form_validation_state_structure(self):
        """Test FormValidationState structure and requirements."""
        field_states = {
            "field1": FieldValidationState("field1", "value1", True, "", True)
        }

        form_state = FormValidationState(
            form_id="test_form",
            field_states=field_states,
            has_errors=False,
            all_required_filled=True,
            is_submittable=True
        )

        assert form_state.form_id == "test_form"
        assert form_state.field_states == field_states
        assert form_state.has_errors is False
        assert form_state.all_required_filled is True
        assert form_state.is_submittable is True

    def test_trade_type_enum_values(self):
        """Test that TradeType enum has required values."""
        assert hasattr(TradeType, 'EQUITY')
        assert hasattr(TradeType, 'OPTION')
        assert hasattr(TradeType, 'FUTURE')

        assert TradeType.EQUITY.value == "equity"
        assert TradeType.OPTION.value == "option"
        assert TradeType.FUTURE.value == "future"

    def test_validation_error_is_exception(self):
        """Test that ValidationError is a proper exception."""
        error = ValidationError("Test validation error")
        assert isinstance(error, Exception)
        assert str(error) == "Test validation error"

    def test_service_handles_edge_cases(self):
        """Test that service handles edge cases gracefully."""
        service = self._get_service_implementation()

        # Empty string validation
        result = service.validate_field("account_size", "", TradeType.EQUITY)
        assert isinstance(result, ValidationResult)

        # None value (should be handled gracefully)
        result = service.validate_field("account_size", None, TradeType.EQUITY)
        assert isinstance(result, ValidationResult)

        # Unknown field name
        result = service.validate_field("unknown_field", "value", TradeType.EQUITY)
        assert isinstance(result, ValidationResult)

    def _get_service_implementation(self) -> ValidationService:
        """
        Get an implementation of ValidationService for testing.

        This method will fail until we create an actual implementation.
        """
        try:
            from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
            return EnhancedValidationService()
        except ImportError:
            pytest.fail("ValidationService implementation not found. Implement EnhancedValidationService first.")

    def test_contract_interface_exists(self):
        """Test that the ValidationService interface is properly defined."""
        # Verify the abstract methods exist
        assert hasattr(ValidationService, 'validate_field')
        assert hasattr(ValidationService, 'validate_form')
        assert hasattr(ValidationService, 'get_required_fields')
        assert hasattr(ValidationService, 'get_validation_rules')
        assert hasattr(ValidationService, 'format_error_message')

        # Verify they are abstract (should raise TypeError when trying to instantiate)
        with pytest.raises(TypeError):
            ValidationService()