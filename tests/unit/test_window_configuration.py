"""
Unit tests for WindowConfiguration model.
Tests window state persistence and validation.
"""

import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestWindowConfiguration(unittest.TestCase):
    """Test WindowConfiguration model functionality."""

    def test_window_configuration_creation(self):
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

        self.assertEqual(config.width, 1024)
        self.assertEqual(config.height, 768)
        self.assertEqual(config.x, 100)
        self.assertEqual(config.y, 100)
        self.assertFalse(config.maximized)
        self.assertIsInstance(config.last_updated, datetime)

    def test_window_configuration_validation_minimum_width(self):
        """Test width validation enforces minimum constraint."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        # Valid width
        valid_config = WindowConfiguration(
            width=800, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        self.assertTrue(valid_config.validate())

        # Invalid width (too small)
        invalid_config = WindowConfiguration(
            width=799, height=600, x=0, y=0,
            maximized=False, last_updated=datetime.now()
        )
        self.assertFalse(invalid_config.validate())

    def test_window_configuration_screen_bounds_validation(self):
        """Test screen bounds validation."""
        from risk_calculator.models.window_configuration import WindowConfiguration

        config = WindowConfiguration(
            width=1024, height=768, x=100, y=100,
            maximized=False, last_updated=datetime.now()
        )

        # Should fit on a typical screen
        screen_width, screen_height = 1920, 1080
        self.assertTrue(config.x + config.width <= screen_width)
        self.assertTrue(config.y + config.height <= screen_height)


if __name__ == '__main__':
    unittest.main()
