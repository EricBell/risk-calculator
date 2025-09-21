"""
Configuration Service Contract
API contract for window configuration persistence and management
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WindowConfiguration:
    """Window configuration data structure"""
    width: int
    height: int
    x: int
    y: int
    maximized: bool
    last_updated: datetime

    def validate(self) -> bool:
        """Validate window configuration values"""
        return (
            self.width >= 800 and
            self.height >= 600 and
            isinstance(self.x, int) and
            isinstance(self.y, int) and
            isinstance(self.maximized, bool)
        )


class ConfigurationService(ABC):
    """Abstract interface for configuration management"""

    @abstractmethod
    def load_window_config(self) -> WindowConfiguration:
        """
        Load window configuration from persistent storage

        Returns:
            WindowConfiguration: Current window settings, or defaults if not found

        Raises:
            ConfigurationError: If configuration file is corrupted beyond recovery
        """
        pass

    @abstractmethod
    def save_window_config(self, config: WindowConfiguration) -> bool:
        """
        Save window configuration to persistent storage

        Args:
            config: WindowConfiguration to persist

        Returns:
            bool: True if save successful, False otherwise

        Raises:
            ConfigurationError: If unable to write configuration file
        """
        pass

    @abstractmethod
    def validate_window_bounds(self, config: WindowConfiguration) -> WindowConfiguration:
        """
        Validate and adjust window configuration for current screen bounds

        Args:
            config: WindowConfiguration to validate

        Returns:
            WindowConfiguration: Adjusted configuration that fits current screen
        """
        pass

    @abstractmethod
    def get_default_config(self) -> WindowConfiguration:
        """
        Get default window configuration

        Returns:
            WindowConfiguration: Default window settings (1024x768, centered)
        """
        pass

    @abstractmethod
    def backup_config(self) -> bool:
        """
        Create backup of current configuration file

        Returns:
            bool: True if backup successful, False otherwise
        """
        pass


class ConfigurationError(Exception):
    """Exception raised for configuration management errors"""
    pass