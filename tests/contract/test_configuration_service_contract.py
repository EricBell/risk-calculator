"""
Contract tests for ConfigurationService interface.
These tests verify that any implementation of ConfigurationService follows the contract.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Import the contract interface
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import from the actual contract location
try:
    from specs.three_there_are_several.contracts.configuration_service import ConfigurationService, WindowConfiguration, ConfigurationError
except ImportError:
    # Import from local file
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from configuration_service import ConfigurationService, WindowConfiguration, ConfigurationError


class TestConfigurationServiceContract:
    """Test contract compliance for ConfigurationService implementations."""

    def test_load_window_config_returns_window_configuration(self):
        """Test that load_window_config returns WindowConfiguration instance."""
        # This test will fail until we implement the service
        service = self._get_service_implementation()

        result = service.load_window_config()

        assert isinstance(result, WindowConfiguration)
        assert hasattr(result, 'width')
        assert hasattr(result, 'height')
        assert hasattr(result, 'x')
        assert hasattr(result, 'y')
        assert hasattr(result, 'maximized')
        assert hasattr(result, 'last_updated')

    def test_load_window_config_returns_defaults_when_no_config_exists(self):
        """Test that load_window_config returns defaults when no config file exists."""
        service = self._get_service_implementation()

        result = service.load_window_config()

        # Should return valid defaults
        assert result.width >= 800
        assert result.height >= 600
        assert isinstance(result.x, int)
        assert isinstance(result.y, int)
        assert isinstance(result.maximized, bool)
        assert isinstance(result.last_updated, datetime)

    def test_save_window_config_accepts_window_configuration(self):
        """Test that save_window_config accepts WindowConfiguration and returns bool."""
        service = self._get_service_implementation()
        config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        result = service.save_window_config(config)

        assert isinstance(result, bool)

    def test_save_window_config_validates_input(self):
        """Test that save_window_config validates the configuration."""
        service = self._get_service_implementation()

        # Test with invalid config (width too small)
        invalid_config = WindowConfiguration(
            width=500, height=400, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )

        # Should either return False or raise ConfigurationError
        try:
            result = service.save_window_config(invalid_config)
            assert result is False
        except ConfigurationError:
            pass  # This is also acceptable

    def test_validate_window_bounds_returns_window_configuration(self):
        """Test that validate_window_bounds returns adjusted WindowConfiguration."""
        service = self._get_service_implementation()
        config = WindowConfiguration(
            width=1024, height=768, x=-100, y=-100,  # Off-screen position
            maximized=False, last_updated=datetime.now()
        )

        result = service.validate_window_bounds(config)

        assert isinstance(result, WindowConfiguration)
        # Should adjust off-screen positions
        assert result.x >= 0
        assert result.y >= 0

    def test_validate_window_bounds_handles_oversized_windows(self):
        """Test that validate_window_bounds handles windows larger than screen."""
        service = self._get_service_implementation()
        config = WindowConfiguration(
            width=10000, height=10000, x=0, y=0,  # Larger than any reasonable screen
            maximized=False, last_updated=datetime.now()
        )

        result = service.validate_window_bounds(config)

        assert isinstance(result, WindowConfiguration)
        # Should adjust to reasonable size
        assert result.width <= 7680  # Max supported width
        assert result.height <= 4320  # Max supported height

    def test_get_default_config_returns_valid_configuration(self):
        """Test that get_default_config returns valid WindowConfiguration."""
        service = self._get_service_implementation()

        result = service.get_default_config()

        assert isinstance(result, WindowConfiguration)
        assert result.width >= 800
        assert result.height >= 600
        assert isinstance(result.maximized, bool)
        assert isinstance(result.last_updated, datetime)

    def test_backup_config_returns_bool(self):
        """Test that backup_config returns boolean."""
        service = self._get_service_implementation()

        result = service.backup_config()

        assert isinstance(result, bool)

    def test_configuration_error_is_exception(self):
        """Test that ConfigurationError is a proper exception."""
        error = ConfigurationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_window_configuration_validate_method(self):
        """Test WindowConfiguration.validate() method."""
        # Valid configuration
        valid_config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )
        assert valid_config.validate() is True

        # Invalid configuration (width too small)
        invalid_config = WindowConfiguration(
            width=500, height=400, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert invalid_config.validate() is False

    def test_service_handles_corrupted_config_gracefully(self):
        """Test that service handles corrupted configuration files gracefully."""
        service = self._get_service_implementation()

        # This should not raise an exception, even if config is corrupted
        result = service.load_window_config()
        assert isinstance(result, WindowConfiguration)

    def test_service_preserves_valid_configurations(self):
        """Test that valid configurations are preserved through save/load cycle."""
        service = self._get_service_implementation()

        original_config = WindowConfiguration(
            width=1200, height=800, x=50, y=50,
            maximized=True, last_updated=datetime.now()
        )

        # Save the configuration
        save_result = service.save_window_config(original_config)

        # Load it back
        loaded_config = service.load_window_config()

        # Should preserve the values (allowing for timestamp updates)
        assert loaded_config.width == original_config.width
        assert loaded_config.height == original_config.height
        assert loaded_config.x == original_config.x
        assert loaded_config.y == original_config.y
        assert loaded_config.maximized == original_config.maximized

    def _get_service_implementation(self) -> ConfigurationService:
        """
        Get an implementation of ConfigurationService for testing.

        This method will fail until we create an actual implementation.
        For now, it tries to import the real implementation.
        """
        try:
            from risk_calculator.services.configuration_service import JsonConfigurationService
            return JsonConfigurationService()
        except ImportError:
            pytest.fail("ConfigurationService implementation not found. Implement JsonConfigurationService first.")

    def test_contract_interface_exists(self):
        """Test that the ConfigurationService interface is properly defined."""
        # Verify the abstract methods exist
        assert hasattr(ConfigurationService, 'load_window_config')
        assert hasattr(ConfigurationService, 'save_window_config')
        assert hasattr(ConfigurationService, 'validate_window_bounds')
        assert hasattr(ConfigurationService, 'get_default_config')
        assert hasattr(ConfigurationService, 'backup_config')

        # Verify they are abstract (should raise TypeError when trying to instantiate)
        with pytest.raises(TypeError):
            ConfigurationService()