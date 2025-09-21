"""
Contract tests for ValidationService interface.
Verifies any implementation follows the validation contract.
"""

import unittest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from validation_service import ValidationService, ValidationResult, FieldValidationState, FormValidationState, TradeType
except ImportError:
    from enum import Enum
    class TradeType(Enum):
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"

    class ValidationResult:
        def __init__(self, is_valid, error_message=""):
            self.is_valid = is_valid
            self.error_message = error_message


class TestValidationServiceContract(unittest.TestCase):
    """Test contract compliance for ValidationService implementations."""

    def test_validate_field_returns_validation_result(self):
        """Test that validate_field returns ValidationResult."""
        service = self._get_service_implementation()

        result = service.validate_field("account_size", "10000", TradeType.EQUITY)

        # Check if result is either the contract ValidationResult or the implementation's ValidationResult
        try:
            from risk_calculator.services.enhanced_validation_service import ValidationResult as ImplValidationResult
            self.assertTrue(isinstance(result, (ValidationResult, ImplValidationResult)))
        except ImportError:
            self.assertIsInstance(result, ValidationResult)

        self.assertIsInstance(result.is_valid, bool)
        self.assertIsInstance(result.error_message, str)

    def test_validate_field_handles_valid_input(self):
        """Test that validate_field correctly identifies valid input."""
        service = self._get_service_implementation()

        # Test valid account size
        result = service.validate_field("account_size", "10000", TradeType.EQUITY)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_message, "")

    def test_validate_field_handles_invalid_input(self):
        """Test that validate_field correctly identifies invalid input."""
        service = self._get_service_implementation()

        # Test invalid account size (negative)
        result = service.validate_field("account_size", "-5000", TradeType.EQUITY)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.error_message), 0)

    def _get_service_implementation(self):
        """Get an implementation of ValidationService for testing."""
        try:
            from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
            return EnhancedValidationService()
        except ImportError:
            self.fail("ValidationService implementation not found")


if __name__ == '__main__':
    unittest.main()
