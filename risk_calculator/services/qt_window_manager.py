"""
Qt Window Manager Service
Handles window size persistence and validation using Qt framework.
"""

from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QScreen
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..models.window_configuration import WindowConfiguration
from ..models.display_profile import DisplayProfile


class QtWindowManagerService:
    """Qt-based window management service for configuration persistence."""

    def __init__(self):
        """Initialize Qt window manager service."""
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt window management not supported")

        self.settings = QSettings("RiskCalculator", "WindowConfig")

    def save_window_configuration(self, config: WindowConfiguration) -> bool:
        """
        Save window configuration to Qt settings.

        Args:
            config: Window configuration to save

        Returns:
            bool: True if saved successfully
        """
        try:
            self.settings.setValue("window/width", config.width)
            self.settings.setValue("window/height", config.height)
            self.settings.setValue("window/x", config.x)
            self.settings.setValue("window/y", config.y)
            self.settings.setValue("window/maximized", config.maximized)
            self.settings.setValue("window/last_updated", config.last_updated.isoformat())

            self.settings.sync()
            return True

        except Exception:
            return False

    def load_window_configuration(self) -> Optional[WindowConfiguration]:
        """
        Load window configuration from Qt settings.

        Returns:
            WindowConfiguration or None if not found
        """
        try:
            if not self.settings.contains("window/width"):
                return None

            width = self.settings.value("window/width", type=int)
            height = self.settings.value("window/height", type=int)
            x = self.settings.value("window/x", type=int)
            y = self.settings.value("window/y", type=int)
            maximized = self.settings.value("window/maximized", type=bool)
            last_updated_str = self.settings.value("window/last_updated", type=str)

            last_updated = datetime.fromisoformat(last_updated_str)

            return WindowConfiguration(
                width=width,
                height=height,
                x=x,
                y=y,
                maximized=maximized,
                last_updated=last_updated
            )

        except Exception:
            return None

    def validate_window_bounds(self, config: WindowConfiguration) -> WindowConfiguration:
        """
        Validate and adjust window bounds for current display setup.

        Args:
            config: Window configuration to validate

        Returns:
            WindowConfiguration: Validated/adjusted configuration
        """
        app = QApplication.instance()
        if not app:
            # If no Qt app, preserve user's size preferences and only ensure reasonable position
            return WindowConfiguration(
                width=config.width,  # Preserve user's width
                height=config.height,  # Preserve user's height
                x=max(config.x, 0),  # Only ensure not negative
                y=max(config.y, 0),  # Only ensure not negative
                maximized=config.maximized,
                last_updated=datetime.now()
            )

        # Get primary screen
        primary_screen = app.primaryScreen()
        screen_geometry = primary_screen.availableGeometry()

        # PRESERVE user's window size - don't override with minimum constraints
        # Qt will enforce minimum size constraints when the window is created
        adjusted_width = config.width
        adjusted_height = config.height

        # Only ensure window fits on screen (but don't override user size preferences)
        max_width = screen_geometry.width() - 50  # Leave margin
        max_height = screen_geometry.height() - 50  # Leave margin

        # Only adjust if window is larger than screen (but preserve smaller sizes)
        if adjusted_width > max_width:
            adjusted_width = max_width
        if adjusted_height > max_height:
            adjusted_height = max_height

        # Ensure window is on screen
        adjusted_x = max(config.x, screen_geometry.x())
        adjusted_y = max(config.y, screen_geometry.y())

        # Ensure window doesn't extend beyond screen
        if adjusted_x + adjusted_width > screen_geometry.right():
            adjusted_x = screen_geometry.right() - adjusted_width
        if adjusted_y + adjusted_height > screen_geometry.bottom():
            adjusted_y = screen_geometry.bottom() - adjusted_height

        return WindowConfiguration(
            width=adjusted_width,
            height=adjusted_height,
            x=adjusted_x,
            y=adjusted_y,
            maximized=config.maximized,
            last_updated=datetime.now()
        )

    def get_default_window_size(self) -> Tuple[int, int]:
        """
        Get default window size based on current display.

        Returns:
            Tuple[int, int]: (width, height) for default window
        """
        try:
            # Try to detect display profile for intelligent defaults
            display_profile = DisplayProfile.detect_current()
            return display_profile.get_recommended_window_size()

        except Exception:
            # Fallback to conservative defaults
            return (1024, 768)

    def get_current_screen_info(self) -> dict:
        """
        Get information about the current screen setup.

        Returns:
            dict: Screen information for debugging/logging
        """
        app = QApplication.instance()
        if not app:
            return {"error": "No Qt application instance"}

        primary_screen = app.primaryScreen()
        screen_geometry = primary_screen.geometry()
        available_geometry = primary_screen.availableGeometry()

        return {
            "screen_count": len(app.screens()),
            "primary_screen": {
                "geometry": {
                    "width": screen_geometry.width(),
                    "height": screen_geometry.height(),
                    "x": screen_geometry.x(),
                    "y": screen_geometry.y()
                },
                "available_geometry": {
                    "width": available_geometry.width(),
                    "height": available_geometry.height(),
                    "x": available_geometry.x(),
                    "y": available_geometry.y()
                },
                "dpi": primary_screen.logicalDotsPerInch(),
                "device_pixel_ratio": primary_screen.devicePixelRatio(),
                "name": primary_screen.name()
            }
        }

    def clear_saved_configuration(self) -> bool:
        """
        Clear all saved window configuration.

        Returns:
            bool: True if cleared successfully
        """
        try:
            self.settings.beginGroup("window")
            self.settings.remove("")  # Remove all keys in the group
            self.settings.endGroup()
            self.settings.sync()
            return True

        except Exception:
            return False