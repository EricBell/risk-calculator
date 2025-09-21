"""
Configuration directory management utilities.
Handles creation and management of ~/.risk_calculator/ directory structure.
"""

import os
import json
from pathlib import Path
from typing import Optional


class ConfigDirectoryManager:
    """Manages the configuration directory structure for the risk calculator."""

    def __init__(self):
        self.config_dir = Path.home() / ".risk_calculator"
        self.window_config_file = self.config_dir / "window_config.json"
        self.backup_config_file = self.config_dir / "window_config.json.bak"

    def ensure_config_directory_exists(self) -> bool:
        """
        Create the configuration directory if it doesn't exist.

        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            print(f"Error creating config directory: {e}")
            return False

    def get_config_dir_path(self) -> Path:
        """Get the path to the configuration directory."""
        return self.config_dir

    def get_window_config_path(self) -> Path:
        """Get the path to the window configuration file."""
        return self.window_config_file

    def get_backup_config_path(self) -> Path:
        """Get the path to the backup configuration file."""
        return self.backup_config_file

    def config_directory_writable(self) -> bool:
        """
        Check if the configuration directory is writable.

        Returns:
            bool: True if directory is writable
        """
        if not self.config_dir.exists():
            return False

        try:
            # Try to create a temporary file to test write permissions
            test_file = self.config_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False

    def initialize_config_structure(self) -> bool:
        """
        Initialize the complete configuration directory structure.

        Returns:
            bool: True if initialization successful
        """
        if not self.ensure_config_directory_exists():
            return False

        if not self.config_directory_writable():
            return False

        # Create any additional subdirectories if needed in the future
        # For now, we just need the main config directory

        return True