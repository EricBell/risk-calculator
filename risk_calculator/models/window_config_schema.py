"""
JSON schema validation for window configuration.
Provides validation and default values for window configuration persistence.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class WindowConfigSchema:
    """Handles validation and schema management for window configuration JSON."""

    # Default window configuration
    DEFAULT_CONFIG = {
        "window": {
            "width": 1024,
            "height": 768,
            "x": None,  # Will be calculated to center on screen
            "y": None,  # Will be calculated to center on screen
            "maximized": False,
            "last_updated": None  # Will be set to current time
        }
    }

    # Minimum and maximum constraints
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    MAX_WIDTH = 7680  # Support up to 8K displays
    MAX_HEIGHT = 4320

    @classmethod
    def validate_config(cls, config_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate window configuration data against schema.

        Args:
            config_data: Configuration data to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Check if window section exists
            if "window" not in config_data:
                return False, "Missing 'window' section in configuration"

            window_config = config_data["window"]

            # Validate required fields
            required_fields = ["width", "height", "x", "y", "maximized"]
            for field in required_fields:
                if field not in window_config:
                    return False, f"Missing required field: {field}"

            # Validate data types
            if not isinstance(window_config["width"], int):
                return False, "Width must be an integer"
            if not isinstance(window_config["height"], int):
                return False, "Height must be an integer"
            if window_config["x"] is not None and not isinstance(window_config["x"], int):
                return False, "X position must be an integer or null"
            if window_config["y"] is not None and not isinstance(window_config["y"], int):
                return False, "Y position must be an integer or null"
            if not isinstance(window_config["maximized"], bool):
                return False, "Maximized must be a boolean"

            # Validate value ranges
            if window_config["width"] < cls.MIN_WIDTH:
                return False, f"Width must be at least {cls.MIN_WIDTH} pixels"
            if window_config["height"] < cls.MIN_HEIGHT:
                return False, f"Height must be at least {cls.MIN_HEIGHT} pixels"
            if window_config["width"] > cls.MAX_WIDTH:
                return False, f"Width cannot exceed {cls.MAX_WIDTH} pixels"
            if window_config["height"] > cls.MAX_HEIGHT:
                return False, f"Height cannot exceed {cls.MAX_HEIGHT} pixels"

            return True, None

        except Exception as e:
            return False, f"Configuration validation error: {str(e)}"

    @classmethod
    def get_default_config(cls, screen_width: Optional[int] = None,
                          screen_height: Optional[int] = None) -> Dict[str, Any]:
        """
        Get default window configuration with optional screen size for centering.

        Args:
            screen_width: Screen width for centering calculation
            screen_height: Screen height for centering calculation

        Returns:
            Dict[str, Any]: Default configuration dictionary
        """
        config = cls.DEFAULT_CONFIG.copy()
        config["window"] = config["window"].copy()

        # Calculate centered position if screen dimensions provided
        if screen_width and screen_height:
            config["window"]["x"] = max(0, (screen_width - config["window"]["width"]) // 2)
            config["window"]["y"] = max(0, (screen_height - config["window"]["height"]) // 2)

        # Set current timestamp
        config["window"]["last_updated"] = datetime.now().isoformat()

        return config

    @classmethod
    def sanitize_config(cls, config_data: Dict[str, Any],
                       screen_width: Optional[int] = None,
                       screen_height: Optional[int] = None) -> Dict[str, Any]:
        """
        Sanitize configuration data by applying constraints and defaults.

        Args:
            config_data: Configuration data to sanitize
            screen_width: Current screen width for validation
            screen_height: Current screen height for validation

        Returns:
            Dict[str, Any]: Sanitized configuration
        """
        try:
            if "window" not in config_data:
                return cls.get_default_config(screen_width, screen_height)

            window_config = config_data["window"].copy()

            # Apply size constraints
            window_config["width"] = max(cls.MIN_WIDTH,
                                       min(window_config.get("width", cls.DEFAULT_CONFIG["window"]["width"]),
                                          cls.MAX_WIDTH))
            window_config["height"] = max(cls.MIN_HEIGHT,
                                        min(window_config.get("height", cls.DEFAULT_CONFIG["window"]["height"]),
                                           cls.MAX_HEIGHT))

            # Validate position against screen bounds if provided
            if screen_width and screen_height:
                x = window_config.get("x")
                y = window_config.get("y")

                # If position would put window off-screen, center it
                if (x is None or y is None or
                    x + window_config["width"] > screen_width or
                    y + window_config["height"] > screen_height or
                    x < 0 or y < 0):
                    # Center the window
                    window_config["x"] = max(0, (screen_width - window_config["width"]) // 2)
                    window_config["y"] = max(0, (screen_height - window_config["height"]) // 2)

            # Ensure boolean type for maximized
            window_config["maximized"] = bool(window_config.get("maximized", False))

            # Update timestamp
            window_config["last_updated"] = datetime.now().isoformat()

            return {"window": window_config}

        except Exception:
            # If sanitization fails, return defaults
            return cls.get_default_config(screen_width, screen_height)

    @classmethod
    def is_valid_json_file(cls, file_path: str) -> bool:
        """
        Check if a file contains valid JSON that can be parsed.

        Args:
            file_path: Path to JSON file

        Returns:
            bool: True if file contains valid JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
            return False