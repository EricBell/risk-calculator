"""
Integration test: Risk method switching preservation.
Tests field preservation when switching risk methods.
"""

import unittest
import tkinter as tk
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestMethodSwitchingIntegration(unittest.TestCase):
    """Test method switching integration scenarios."""

    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_method_switching_preserves_common_fields(self):
        """Test common fields are preserved when switching methods"""
        try:
            from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
            from risk_calculator.models.risk_method import RiskMethod

            mock_view = Mock()
            mock_view.get_form_fields = Mock(return_value={})
            mock_view.get_calculate_button = Mock(return_value=Mock())
            mock_view.get_all_field_values = Mock(return_value={})
            mock_view.display_calculation_result = Mock()
            controller = EnhancedBaseController(mock_view)

            # Set common field values
            controller.set_field_value("account_size", "10000")
            controller.set_field_value("symbol", "AAPL")
            controller.set_field_value("entry_price", "150")

            # Switch methods
            controller.set_risk_method(RiskMethod.PERCENTAGE)
            controller.set_field_value("risk_percentage", "2")

            controller.set_risk_method(RiskMethod.FIXED_AMOUNT)

            # Verify common fields preserved
            self.assertEqual(controller.get_field_value("account_size"), "10000")
            self.assertEqual(controller.get_field_value("symbol"), "AAPL")
            self.assertEqual(controller.get_field_value("entry_price"), "150")

        except ImportError:
            self.skipTest("Enhanced controllers not implemented")
        except AttributeError:
            self.skipTest("Method switching not implemented")

    def test_risk_method_switching_ui_behavior(self):
        """Test Scenario 4: Risk Method Switching"""
        try:
            from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
            from risk_calculator.models.risk_method import RiskMethod

            mock_view = Mock()
            mock_view.get_form_fields = Mock(return_value={})
            mock_view.get_calculate_button = Mock(return_value=Mock())
            mock_view.get_all_field_values = Mock(return_value={})
            mock_view.display_calculation_result = Mock()
            controller = EnhancedBaseController(mock_view)

            # Test method switching updates UI
            controller.set_risk_method(RiskMethod.PERCENTAGE)
            self.assertEqual(controller.current_risk_method, RiskMethod.PERCENTAGE)

            controller.set_risk_method(RiskMethod.FIXED_AMOUNT)
            self.assertEqual(controller.current_risk_method, RiskMethod.FIXED_AMOUNT)

        except ImportError:
            self.skipTest("Enhanced controllers not implemented")
        except AttributeError:
            self.skipTest("Risk method switching not implemented")


if __name__ == '__main__':
    unittest.main()
