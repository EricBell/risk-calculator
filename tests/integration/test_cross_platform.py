"""
Integration test: Cross-platform compatibility.
Tests Windows and Linux compatibility from quickstart scenarios.
"""

import pytest
import platform
import os
from pathlib import Path
from unittest.mock import patch, Mock

# Import components that will be implemented/enhanced
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCrossPlatformIntegration:
    """Test cross-platform compatibility integration scenarios."""

    def test_configuration_directory_creation_windows(self):
        """Test Scenario 6A: Configuration directory creation on Windows."""
        if platform.system() != "Windows":
            pytest.skip("Windows-specific test")

        from risk_calculator.utils.config_manager import ConfigDirectoryManager

        manager = ConfigDirectoryManager()

        # Should create directory in Windows home folder
        result = manager.ensure_config_directory_exists()
        assert result is True

        config_path = manager.get_config_dir_path()
        assert config_path.exists()
        assert config_path.is_dir()

        # Should be in user's profile directory
        expected_parent = Path.home()
        assert config_path.parent == expected_parent

    def test_configuration_directory_creation_linux(self):
        """Test Scenario 6B: Configuration directory creation on Linux."""
        if platform.system() != "Linux":
            pytest.skip("Linux-specific test")

        from risk_calculator.utils.config_manager import ConfigDirectoryManager

        manager = ConfigDirectoryManager()

        # Should create directory in Linux home folder
        result = manager.ensure_config_directory_exists()
        assert result is True

        config_path = manager.get_config_dir_path()
        assert config_path.exists()
        assert config_path.is_dir()

        # Should be in user's home directory
        expected_parent = Path.home()
        assert config_path.parent == expected_parent

    @patch('platform.system')
    def test_path_handling_cross_platform(self, mock_platform):
        """Test path handling works correctly across platforms."""
        from risk_calculator.utils.config_manager import ConfigDirectoryManager

        # Test Windows path handling
        mock_platform.return_value = "Windows"
        manager_windows = ConfigDirectoryManager()
        windows_path = manager_windows.get_config_dir_path()

        # Test Linux path handling
        mock_platform.return_value = "Linux"
        manager_linux = ConfigDirectoryManager()
        linux_path = manager_linux.get_config_dir_path()

        # Both should use Path.home() correctly
        assert isinstance(windows_path, Path)
        assert isinstance(linux_path, Path)
        assert windows_path.name == ".risk_calculator"
        assert linux_path.name == ".risk_calculator"

    def test_file_permissions_cross_platform(self):
        """Test file permissions work correctly on both platforms."""
        from risk_calculator.utils.config_manager import ConfigDirectoryManager

        manager = ConfigDirectoryManager()
        manager.ensure_config_directory_exists()

        # Test write permissions
        writable = manager.config_directory_writable()
        assert writable is True

        # Test file creation
        test_file = manager.get_config_dir_path() / "test_file.txt"
        try:
            test_file.write_text("test content")
            assert test_file.exists()
            content = test_file.read_text()
            assert content == "test content"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_json_serialization_cross_platform(self):
        """Test JSON serialization works consistently across platforms."""
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime
        import json

        config = WindowConfiguration(
            width=1024,
            height=768,
            x=100,
            y=100,
            maximized=False,
            last_updated=datetime.now()
        )

        # Serialize to JSON
        config_dict = config.to_dict()
        json_str = json.dumps(config_dict)

        # Deserialize from JSON
        loaded_dict = json.loads(json_str)
        restored_config = WindowConfiguration.from_dict(loaded_dict)

        # Should preserve values across platforms
        assert restored_config.width == config.width
        assert restored_config.height == config.height
        assert restored_config.x == config.x
        assert restored_config.y == config.y
        assert restored_config.maximized == config.maximized

    def test_tkinter_compatibility_cross_platform(self):
        """Test Tkinter components work consistently across platforms."""
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()

        try:
            from risk_calculator.views.error_display import ErrorLabel

            # Create error label
            error_label = ErrorLabel(root)

            # Test basic functionality
            error_label.show_error("Test error message")
            assert error_label.has_error() is True

            error_label.hide_error()
            assert error_label.has_error() is False

            # Should work on both platforms
            assert True  # If we get here, basic Tkinter functionality works

        finally:
            root.destroy()

    @pytest.mark.parametrize("platform_name", ["Windows", "Linux"])
    def test_screen_dimension_detection(self, platform_name):
        """Test screen dimension detection works on both platforms."""
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()

        try:
            # Get screen dimensions using Tkinter
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Should return reasonable values on both platforms
            assert screen_width > 0
            assert screen_height > 0
            assert screen_width >= 640  # Minimum reasonable screen width
            assert screen_height >= 480  # Minimum reasonable screen height

        finally:
            root.destroy()

    def test_window_configuration_validation_cross_platform(self):
        """Test window configuration validation works on both platforms."""
        from risk_calculator.models.window_config_schema import WindowConfigSchema

        # Test with various screen sizes
        test_configs = [
            {"width": 1024, "height": 768, "x": 100, "y": 100},
            {"width": 1920, "height": 1080, "x": 0, "y": 0},
            {"width": 3840, "height": 2160, "x": 200, "y": 200},  # 4K
        ]

        for config_data in test_configs:
            config = {
                "window": {
                    **config_data,
                    "maximized": False,
                    "last_updated": "2023-09-20T10:30:00.123456"
                }
            }

            is_valid, error_message = WindowConfigSchema.validate_config(config)
            assert is_valid is True, f"Config should be valid: {error_message}"

    def test_error_message_display_cross_platform(self):
        """Test error message display works on both platforms."""
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()

        try:
            from risk_calculator.views.error_display import FieldErrorManager

            manager = FieldErrorManager()

            # Create test widgets
            test_entry = tk.Entry(root)
            test_error_label = tk.Label(root, text="", fg="red")

            # Register field
            manager.register_field("test_field", test_entry, test_error_label)

            # Test error display
            manager.show_error("test_field", "Test error message")
            assert manager.has_errors() is True

            manager.hide_error("test_field")
            assert manager.has_errors() is False

        finally:
            root.destroy()

    def test_configuration_file_encoding_cross_platform(self):
        """Test configuration file encoding works on both platforms."""
        import tempfile
        import json
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"

            # Test data with various characters
            test_data = {
                "window": {
                    "width": 1024,
                    "height": 768,
                    "x": 100,
                    "y": 100,
                    "maximized": False,
                    "last_updated": "2023-09-20T10:30:00.123456"
                }
            }

            # Write with UTF-8 encoding
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)

            # Read back
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            # Should preserve data correctly
            assert loaded_data == test_data

    @pytest.mark.skipif(platform.system() not in ["Windows", "Linux"],
                       reason="Only test on Windows and Linux")
    def test_application_startup_cross_platform(self):
        """Test application startup works on supported platforms."""
        # This test verifies that the basic application components
        # can be imported and instantiated on both platforms

        try:
            # Test imports work
            from risk_calculator.utils.config_manager import ConfigDirectoryManager
            from risk_calculator.models.window_config_schema import WindowConfigSchema
            from risk_calculator.views.error_display import ErrorLabel

            # Test basic instantiation
            manager = ConfigDirectoryManager()
            assert manager is not None

            # Test config directory creation
            result = manager.ensure_config_directory_exists()
            assert isinstance(result, bool)

            # If we get here, basic cross-platform functionality works
            assert True

        except ImportError as e:
            pytest.fail(f"Import failed on {platform.system()}: {e}")
        except Exception as e:
            pytest.fail(f"Basic functionality failed on {platform.system()}: {e}")