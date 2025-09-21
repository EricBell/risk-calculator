"""
ConfigurationService implementation.
Concrete implementation of the ConfigurationService interface.
"""

import json
import shutil
import tkinter as tk
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import contract interfaces with fallback
try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from configuration_service import ConfigurationService as ContractConfigurationService, WindowConfiguration as ContractWindowConfiguration, ConfigurationError

    # Use contract as base class
    class ConfigurationService(ContractConfigurationService):
        pass

except ImportError:
    # Fallback definitions for development
    from abc import ABC, abstractmethod

    class ConfigurationError(Exception):
        pass

    class ConfigurationService(ABC):
        @abstractmethod
        def save_window_config(self, config) -> bool:
            pass

        @abstractmethod
        def load_window_config(self):
            pass
from risk_calculator.utils.config_manager import ConfigDirectoryManager
from risk_calculator.models.window_config_schema import WindowConfigSchema
from risk_calculator.models.window_configuration import WindowConfiguration


class JsonConfigurationService(ConfigurationService):
    """JSON-based implementation of ConfigurationService."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration service.

        Args:
            config_dir: Optional custom config directory (for testing)
        """
        self.config_manager = ConfigDirectoryManager()

        # Override config directory if provided (for testing)
        if config_dir:
            self.config_manager.config_dir = config_dir
            self.config_manager.window_config_file = config_dir / "window_config.json"
            self.config_manager.backup_config_file = config_dir / "window_config.json.bak"

        # Initialize Tkinter root for screen dimension detection
        self._root = None
        self._screen_width = None
        self._screen_height = None

    def _get_screen_dimensions(self) -> tuple:
        """
        Get current screen dimensions.

        Returns:
            tuple: (screen_width, screen_height)
        """
        if self._screen_width is None or self._screen_height is None:
            try:
                if self._root is None:
                    self._root = tk.Tk()
                    self._root.withdraw()  # Hide the window

                self._screen_width = self._root.winfo_screenwidth()
                self._screen_height = self._root.winfo_screenheight()
            except Exception:
                # Fallback to common resolution
                self._screen_width = 1920
                self._screen_height = 1080

        return self._screen_width, self._screen_height

    def load_window_config(self) -> WindowConfiguration:
        """
        Load window configuration from persistent storage.

        Returns:
            WindowConfiguration: Current window settings, or defaults if not found
        """
        try:
            # Ensure config directory exists
            if not self.config_manager.initialize_config_structure():
                return self.get_default_config()

            config_file = self.config_manager.get_window_config_path()

            # Try to load main config file
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)

                    # Validate configuration
                    is_valid, error_message = WindowConfigSchema.validate_config(config_data)

                    if is_valid:
                        # Convert to WindowConfiguration object
                        window_data = config_data['window']
                        config = WindowConfiguration(
                            width=window_data['width'],
                            height=window_data['height'],
                            x=window_data['x'],
                            y=window_data['y'],
                            maximized=window_data['maximized'],
                            last_updated=datetime.fromisoformat(window_data['last_updated'])
                        )

                        # Validate against screen bounds
                        return self.validate_window_bounds(config)

                except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                    # Try backup file
                    return self._load_from_backup()

            else:
                # No config file exists, return defaults
                return self.get_default_config()

        except Exception as e:
            # Last resort: return defaults
            return self.get_default_config()

    def _load_from_backup(self) -> WindowConfiguration:
        """
        Try to load configuration from backup file.

        Returns:
            WindowConfiguration: Configuration from backup or defaults
        """
        try:
            backup_file = self.config_manager.get_backup_config_path()

            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                is_valid, _ = WindowConfigSchema.validate_config(config_data)

                if is_valid:
                    window_data = config_data['window']
                    config = WindowConfiguration(
                        width=window_data['width'],
                        height=window_data['height'],
                        x=window_data['x'],
                        y=window_data['y'],
                        maximized=window_data['maximized'],
                        last_updated=datetime.fromisoformat(window_data['last_updated'])
                    )

                    # Restore from backup
                    self.save_window_config(config)
                    return self.validate_window_bounds(config)

        except Exception:
            pass

        return self.get_default_config()

    def save_window_config(self, config: WindowConfiguration) -> bool:
        """
        Save window configuration to persistent storage.

        Args:
            config: WindowConfiguration to persist

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Validate configuration
            if not config.validate():
                return False

            # Ensure config directory exists
            if not self.config_manager.initialize_config_structure():
                return False

            # Create backup before saving
            self.backup_config()

            # Prepare configuration data
            config_data = {
                "window": {
                    "width": config.width,
                    "height": config.height,
                    "x": config.x,
                    "y": config.y,
                    "maximized": config.maximized,
                    "last_updated": config.last_updated.isoformat()
                }
            }

            # Validate the data structure
            is_valid, error_message = WindowConfigSchema.validate_config(config_data)
            if not is_valid:
                raise ConfigurationError(f"Invalid configuration: {error_message}")

            # Write to file
            config_file = self.config_manager.get_window_config_path()
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            return False

    def validate_window_bounds(self, config: WindowConfiguration) -> WindowConfiguration:
        """
        Validate and adjust window configuration for current screen bounds.

        Args:
            config: WindowConfiguration to validate

        Returns:
            WindowConfiguration: Adjusted configuration that fits current screen
        """
        try:
            screen_width, screen_height = self._get_screen_dimensions()

            # If configuration is within bounds, return as-is
            if config.is_within_screen_bounds(screen_width, screen_height):
                return config

            # Adjust to fit screen
            return config.adjust_to_screen(screen_width, screen_height)

        except Exception:
            # If screen detection fails, return defaults
            return self.get_default_config()

    def get_default_config(self) -> WindowConfiguration:
        """
        Get default window configuration.

        Returns:
            WindowConfiguration: Default window settings (1024x768, centered)
        """
        try:
            screen_width, screen_height = self._get_screen_dimensions()

            # Use schema to get defaults with screen centering
            config_dict = WindowConfigSchema.get_default_config(screen_width, screen_height)
            window_data = config_dict['window']

            return WindowConfiguration(
                width=window_data['width'],
                height=window_data['height'],
                x=window_data['x'],
                y=window_data['y'],
                maximized=window_data['maximized'],
                last_updated=datetime.fromisoformat(window_data['last_updated'])
            )

        except Exception:
            # Absolute fallback
            return WindowConfiguration(
                width=1024,
                height=768,
                x=100,
                y=100,
                maximized=False,
                last_updated=datetime.now()
            )

    def backup_config(self) -> bool:
        """
        Create backup of current configuration file.

        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            config_file = self.config_manager.get_window_config_path()
            backup_file = self.config_manager.get_backup_config_path()

            if config_file.exists():
                shutil.copy2(config_file, backup_file)
                return True

            return False

        except Exception:
            return False

    def __del__(self):
        """Cleanup Tkinter root on destruction."""
        if self._root:
            try:
                self._root.destroy()
            except Exception:
                pass