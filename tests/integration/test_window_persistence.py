"""
Integration test: Window configuration persistence.
Tests window state save/restore from quickstart scenarios.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path

# Import components that will be implemented/enhanced
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestWindowPersistenceIntegration:
    """Test window persistence integration scenarios."""

    def setup_method(self):
        """Setup test environment with temporary config directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".risk_calculator"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "window_config.json"

    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_window_state_persistence_cycle(self):
        """Test Scenario 5A: Window size and position are saved and restored."""
        from risk_calculator.services.configuration_service import JsonConfigurationService

        # Create service with test config directory
        service = JsonConfigurationService(config_dir=self.config_dir)

        # Simulate window resize and move
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime

        custom_config = WindowConfiguration(
            width=1400,
            height=900,
            x=100,
            y=50,
            maximized=False,
            last_updated=datetime.now()
        )

        # Save configuration
        save_result = service.save_window_config(custom_config)
        assert save_result is True

        # Simulate application restart - load configuration
        loaded_config = service.load_window_config()

        # Should restore same values
        assert loaded_config.width == 1400
        assert loaded_config.height == 900
        assert loaded_config.x == 100
        assert loaded_config.y == 50
        assert loaded_config.maximized is False

    def test_invalid_configuration_recovery(self):
        """Test Scenario 5B: Application recovers from invalid saved window settings."""
        from risk_calculator.services.configuration_service import JsonConfigurationService

        # Create invalid configuration file
        invalid_config = {
            "window": {
                "width": 50000,
                "height": 50000,
                "x": -10000,
                "y": -10000,
                "maximized": False
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(invalid_config, f)

        # Create service with test config directory
        service = JsonConfigurationService(config_dir=self.config_dir)

        # Load configuration - should recover gracefully
        loaded_config = service.load_window_config()

        # Should have reasonable defaults (80% of screen, centered)
        # Assuming 1920x1080 screen for test
        expected_width = int(1920 * 0.8)
        expected_height = int(1080 * 0.8)

        assert loaded_config.width == expected_width
        assert loaded_config.height == expected_height
        assert loaded_config.x >= 0
        assert loaded_config.y >= 0

    def test_missing_configuration_file_handling(self):
        """Test Scenario 5C: Application creates configuration when file is missing."""
        from risk_calculator.services.configuration_service import JsonConfigurationService

        # Ensure no config file exists
        if self.config_file.exists():
            self.config_file.unlink()

        # Create service with test config directory
        service = JsonConfigurationService(config_dir=self.config_dir)

        # Load configuration - should create defaults
        loaded_config = service.load_window_config()

        # Should have default values
        assert loaded_config.width == 1024
        assert loaded_config.height == 768
        assert isinstance(loaded_config.x, int)
        assert isinstance(loaded_config.y, int)
        assert isinstance(loaded_config.maximized, bool)

        # Configuration file should be created
        assert self.config_file.exists()

    def test_configuration_backup_and_recovery(self):
        """Test configuration backup and recovery functionality."""
        from risk_calculator.services.configuration_service import JsonConfigurationService

        service = JsonConfigurationService(config_dir=self.config_dir)

        # Create initial configuration
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime

        original_config = WindowConfiguration(
            width=1200,
            height=800,
            x=200,
            y=100,
            maximized=True,
            last_updated=datetime.now()
        )

        # Save configuration
        service.save_window_config(original_config)

        # Create backup
        backup_result = service.backup_config()
        assert backup_result is True

        # Verify backup file exists
        backup_file = self.config_dir / "window_config.json.bak"
        assert backup_file.exists()

        # Corrupt main configuration file
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")

        # Load configuration - should recover from backup
        loaded_config = service.load_window_config()

        # Should have recovered original values
        assert loaded_config.width == 1200
        assert loaded_config.height == 800
        assert loaded_config.maximized is True

    def test_concurrent_configuration_access(self):
        """Test handling of concurrent configuration file access."""
        from risk_calculator.services.configuration_service import JsonConfigurationService
        import threading
        import time

        service = JsonConfigurationService(config_dir=self.config_dir)

        results = []
        errors = []

        def save_config(config_data):
            try:
                from risk_calculator.models.window_configuration import WindowConfiguration
                from datetime import datetime

                config = WindowConfiguration(
                    width=config_data["width"],
                    height=config_data["height"],
                    x=config_data["x"],
                    y=config_data["y"],
                    maximized=False,
                    last_updated=datetime.now()
                )
                result = service.save_window_config(config)
                results.append(result)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads trying to save different configurations
        threads = []
        configs = [
            {"width": 1024, "height": 768, "x": 100, "y": 100},
            {"width": 1200, "height": 900, "x": 200, "y": 150},
            {"width": 800, "height": 600, "x": 300, "y": 200},
        ]

        for config_data in configs:
            thread = threading.Thread(target=save_config, args=(config_data,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0
        # At least one save should succeed
        assert any(results)

    def test_configuration_validation_during_persistence(self):
        """Test configuration validation during save/load operations."""
        from risk_calculator.services.configuration_service import JsonConfigurationService

        service = JsonConfigurationService(config_dir=self.config_dir)

        # Try to save invalid configuration
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime

        invalid_config = WindowConfiguration(
            width=100,  # Too small
            height=100,  # Too small
            x=0,
            y=0,
            maximized=False,
            last_updated=datetime.now()
        )

        # Should either reject or sanitize the configuration
        try:
            result = service.save_window_config(invalid_config)
            # If save succeeds, loaded config should be sanitized
            if result:
                loaded_config = service.load_window_config()
                assert loaded_config.width >= 800
                assert loaded_config.height >= 600
        except Exception:
            # Rejection is also acceptable
            pass