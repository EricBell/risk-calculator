"""
Contract tests for ConfigurationService interface.
Verifies configuration persistence and window management.
"""

import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from configuration_service import ConfigurationService, WindowConfiguration
except ImportError:
    from abc import ABC, abstractmethod
    class ConfigurationService(ABC):
        pass


class TestConfigurationServiceContract(unittest.TestCase):
    """Test contract compliance for ConfigurationService implementations."""

    def test_save_window_config_returns_bool(self):
        """Test that save_window_config returns boolean."""
        service = self._get_service_implementation()

        from risk_calculator.models.window_configuration import WindowConfiguration
        config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        result = service.save_window_config(config)
        self.assertIsInstance(result, bool)

    def test_load_window_config_returns_window_configuration(self):
        """Test that load_window_config returns WindowConfiguration."""
        service = self._get_service_implementation()

        result = service.load_window_config()

        from risk_calculator.models.window_configuration import WindowConfiguration
        self.assertIsInstance(result, WindowConfiguration)
        self.assertGreaterEqual(result.width, 800)
        self.assertGreaterEqual(result.height, 600)

    def test_validate_window_bounds_returns_adjusted_config(self):
        """Test that validate_window_bounds returns adjusted configuration."""
        service = self._get_service_implementation()

        from risk_calculator.models.window_configuration import WindowConfiguration
        config = WindowConfiguration(
            width=1024, height=768, x=-100, y=-100,  # Off-screen position
            maximized=False, last_updated=datetime.now()
        )

        result = service.validate_window_bounds(config)

        self.assertIsInstance(result, WindowConfiguration)
        # Should adjust off-screen positions
        self.assertGreaterEqual(result.x, 0)
        self.assertGreaterEqual(result.y, 0)

    def _get_service_implementation(self):
        """Get an implementation of ConfigurationService for testing."""
        try:
            from risk_calculator.services.configuration_service import JsonConfigurationService
            return JsonConfigurationService()
        except ImportError:
            self.fail("ConfigurationService implementation not found")


if __name__ == '__main__':
    unittest.main()
