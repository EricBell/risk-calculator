"""
Unit tests for WindowConfiguration model.
Tests all validation rules, state transitions, and serialization.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

# Import the model that will be implemented
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestWindowConfiguration:
    """Test WindowConfiguration model functionality."""

    def test_window_configuration_creation_with_valid_data(self):
        """Test creating WindowConfiguration with valid data."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config = WindowConfiguration(
            width=1024,
            height=768,
            x=100,
            y=100,
            maximized=False,
            last_updated=datetime.now()
        )

        assert config.width == 1024
        assert config.height == 768
        assert config.x == 100
        assert config.y == 100
        assert config.maximized is False
        assert isinstance(config.last_updated, datetime)

    def test_window_configuration_validation_minimum_width(self):
        """Test width validation enforces minimum constraint."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Valid width
        valid_config = WindowConfiguration(
            width=800, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert valid_config.validate() is True

        # Invalid width (too small)
        invalid_config = WindowConfiguration(
            width=799, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert invalid_config.validate() is False

    def test_window_configuration_validation_minimum_height(self):
        """Test height validation enforces minimum constraint."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Valid height
        valid_config = WindowConfiguration(
            width=800, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert valid_config.validate() is True

        # Invalid height (too small)
        invalid_config = WindowConfiguration(
            width=800, height=599, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert invalid_config.validate() is False

    def test_window_configuration_validation_maximum_constraints(self):
        """Test validation enforces maximum size constraints."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Test maximum width constraint
        max_width_config = WindowConfiguration(
            width=7680, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert max_width_config.validate() is True

        # Exceed maximum width
        exceed_width_config = WindowConfiguration(
            width=7681, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert exceed_width_config.validate() is False

        # Test maximum height constraint
        max_height_config = WindowConfiguration(
            width=800, height=4320, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert max_height_config.validate() is True

        # Exceed maximum height
        exceed_height_config = WindowConfiguration(
            width=800, height=4321, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        assert exceed_height_config.validate() is False

    def test_window_configuration_screen_bounds_validation(self):
        """Test screen bounds validation."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        # Test within bounds (1920x1080 screen)
        assert config.is_within_screen_bounds(1920, 1080) is True

        # Test outside bounds
        assert config.is_within_screen_bounds(800, 600) is False

        # Test partially outside
        config.x = 1000
        config.y = 500
        assert config.is_within_screen_bounds(1920, 1080) is True
        assert config.is_within_screen_bounds(1200, 800) is False

    def test_window_configuration_adjust_to_screen(self):
        """Test adjustment to screen bounds."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Configuration that's off-screen
        config = WindowConfiguration(
            width=1024, height=768, x=-100, y=-100,
            maximized=False, last_updated=datetime.now()
        )

        adjusted = config.adjust_to_screen(1920, 1080)

        assert adjusted.x >= 0
        assert adjusted.y >= 0
        assert adjusted.x + adjusted.width <= 1920
        assert adjusted.y + adjusted.height <= 1080

    def test_window_configuration_adjust_oversized_window(self):
        """Test adjustment of oversized windows."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Window larger than screen
        config = WindowConfiguration(
            width=2000, height=1200, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )

        adjusted = config.adjust_to_screen(1920, 1080)

        # Should be resized to 80% of screen and centered
        expected_width = int(1920 * 0.8)
        expected_height = int(1080 * 0.8)

        assert adjusted.width == expected_width
        assert adjusted.height == expected_height
        assert adjusted.x == (1920 - expected_width) // 2
        assert adjusted.y == (1080 - expected_height) // 2

    def test_window_configuration_center_on_screen(self):
        """Test centering window on screen."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config = WindowConfiguration(
            width=800, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )

        centered = config.center_on_screen(1920, 1080)

        expected_x = (1920 - 800) // 2
        expected_y = (1080 - 600) // 2

        assert centered.x == expected_x
        assert centered.y == expected_y
        assert centered.width == 800
        assert centered.height == 600

    def test_window_configuration_to_dict(self):
        """Test serialization to dictionary."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        now = datetime.now()
        config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=True, last_updated=now
        )

        config_dict = config.to_dict()

        assert config_dict['width'] == 1024
        assert config_dict['height'] == 768
        assert config_dict['x'] == 100
        assert config_dict['y'] == 100
        assert config_dict['maximized'] is True
        assert config_dict['last_updated'] == now.isoformat()

    def test_window_configuration_from_dict(self):
        """Test deserialization from dictionary."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config_dict = {
            'width': 1024,
            'height': 768,
            'x': 100,
            'y': 100,
            'maximized': True,
            'last_updated': '2023-09-20T10:30:00.123456'
        }

        config = WindowConfiguration.from_dict(config_dict)

        assert config.width == 1024
        assert config.height == 768
        assert config.x == 100
        assert config.y == 100
        assert config.maximized is True
        assert isinstance(config.last_updated, datetime)

    def test_window_configuration_from_dict_with_invalid_data(self):
        """Test deserialization handles invalid data gracefully."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Missing required fields
        incomplete_dict = {
            'width': 1024,
            'height': 768
        }

        config = WindowConfiguration.from_dict(incomplete_dict)
        # Should fill in defaults
        assert config.width == 1024
        assert config.height == 768
        assert config.x is not None
        assert config.y is not None
        assert isinstance(config.maximized, bool)

    def test_window_configuration_state_transitions(self):
        """Test state transitions as specified in data model."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Created state - should have valid defaults
        config = WindowConfiguration.create_default()
        assert config.width >= 800
        assert config.height >= 600
        assert isinstance(config.x, int)
        assert isinstance(config.y, int)
        assert isinstance(config.maximized, bool)
        assert isinstance(config.last_updated, datetime)

        # Modified state - should update timestamp
        original_timestamp = config.last_updated
        modified_config = config.update_size(1200, 900)
        assert modified_config.width == 1200
        assert modified_config.height == 900
        assert modified_config.last_updated > original_timestamp

    def test_window_configuration_invalid_state_recovery(self):
        """Test recovery from invalid state."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Start with invalid configuration
        invalid_config = WindowConfiguration(
            width=100, height=100, x=-1000, y=-1000,
            maximized=False, last_updated=datetime.now()
        )

        # Should detect as invalid
        assert invalid_config.validate() is False

        # Recovery should return valid configuration
        recovered = invalid_config.recover_to_defaults(1920, 1080)
        assert recovered.validate() is True
        assert recovered.width >= 800
        assert recovered.height >= 600

    def test_window_configuration_equality(self):
        """Test equality comparison between configurations."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config1 = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        config2 = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        # Should be equal based on window properties (not timestamp)
        assert config1.equals_window_properties(config2) is True

        # Different properties should not be equal
        config3 = WindowConfiguration(
            width=800, height=600, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        assert config1.equals_window_properties(config3) is False

    def test_window_configuration_copy(self):
        """Test copying configuration."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        original = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=True, last_updated=datetime.now()
        )

        copy = original.copy()

        # Should have same values
        assert copy.width == original.width
        assert copy.height == original.height
        assert copy.x == original.x
        assert copy.y == original.y
        assert copy.maximized == original.maximized

        # But be different objects
        assert copy is not original

    def test_window_configuration_json_serialization(self):
        """Test complete JSON serialization/deserialization cycle."""
        from risk_calculator.models.window_configuration import WindowConfiguration
        import json

        original = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=True, last_updated=datetime.now()
        )

        # Serialize to JSON
        json_str = json.dumps(original.to_dict())

        # Deserialize from JSON
        loaded_dict = json.loads(json_str)
        restored = WindowConfiguration.from_dict(loaded_dict)

        # Should preserve all properties
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.x == original.x
        assert restored.y == original.y
        assert restored.maximized == original.maximized

    @pytest.fixture
    def sample_config(self):
        """Fixture providing a sample window configuration."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        return WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )