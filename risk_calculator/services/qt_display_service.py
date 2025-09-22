"""
Qt Display Profile Service
Detects display characteristics using Qt framework for responsive UI.
"""

from typing import Optional, Tuple, List
import platform

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QScreen
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..models.display_profile import DisplayProfile


class QtDisplayService:
    """Qt-based display detection and profiling service."""

    def __init__(self):
        """Initialize Qt display service."""
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt display service not supported")

    def detect_display_profile(self) -> DisplayProfile:
        """
        Detect current display profile using Qt.

        Returns:
            DisplayProfile: Current display characteristics
        """
        app = QApplication.instance()
        if not app:
            # Fallback to basic detection if no Qt app
            return DisplayProfile.detect_current()

        primary_screen = app.primaryScreen()

        # Get screen geometry
        screen_geometry = primary_screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Get DPI information
        logical_dpi = primary_screen.logicalDotsPerInch()
        device_pixel_ratio = primary_screen.devicePixelRatio()

        # Calculate DPI scale factor
        # Standard DPI is typically 96 on Windows, 72 on macOS
        standard_dpi = 96.0
        dpi_scale = logical_dpi / standard_dpi

        # Device pixel ratio is another scaling indicator
        if device_pixel_ratio > 1.0:
            dpi_scale = max(dpi_scale, device_pixel_ratio)

        # Determine if high DPI
        is_high_dpi = dpi_scale >= 1.25 or device_pixel_ratio >= 1.25

        # Get platform
        system_platform = platform.system()
        platform_map = {
            "Windows": "Windows",
            "Linux": "Linux",
            "Darwin": "Darwin"
        }
        detected_platform = platform_map.get(system_platform, "Other")

        return DisplayProfile(
            screen_width=screen_width,
            screen_height=screen_height,
            dpi_scale=dpi_scale,
            is_high_dpi=is_high_dpi,
            platform=detected_platform
        )

    def is_high_dpi_display(self) -> bool:
        """
        Check if current display is high-DPI.

        Returns:
            bool: True if high-DPI display
        """
        try:
            profile = self.detect_display_profile()
            return profile.is_high_dpi
        except Exception:
            return False

    def get_dpi_scale_factor(self) -> float:
        """
        Get DPI scale factor for current display.

        Returns:
            float: DPI scale factor
        """
        try:
            profile = self.detect_display_profile()
            return profile.dpi_scale
        except Exception:
            return 1.0

    def get_screen_geometry(self) -> Tuple[int, int, int, int]:
        """
        Get screen geometry (x, y, width, height).

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        app = QApplication.instance()
        if not app:
            # Fallback values
            return (0, 0, 1920, 1080)

        primary_screen = app.primaryScreen()
        geometry = primary_screen.geometry()

        return (geometry.x(), geometry.y(), geometry.width(), geometry.height())

    def get_available_geometry(self) -> Tuple[int, int, int, int]:
        """
        Get available screen geometry excluding taskbars, etc.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        app = QApplication.instance()
        if not app:
            # Fallback values
            return (0, 0, 1920, 1040)  # Assume 40px for taskbar

        primary_screen = app.primaryScreen()
        geometry = primary_screen.availableGeometry()

        return (geometry.x(), geometry.y(), geometry.width(), geometry.height())

    def get_all_screens(self) -> List[dict]:
        """
        Get information about all available screens.

        Returns:
            List[dict]: List of screen information
        """
        app = QApplication.instance()
        if not app:
            return [{"name": "Unknown", "width": 1920, "height": 1080, "is_primary": True}]

        screens_info = []
        primary_screen = app.primaryScreen()

        for screen in app.screens():
            geometry = screen.geometry()
            available = screen.availableGeometry()

            screen_info = {
                "name": screen.name(),
                "geometry": {
                    "x": geometry.x(),
                    "y": geometry.y(),
                    "width": geometry.width(),
                    "height": geometry.height()
                },
                "available_geometry": {
                    "x": available.x(),
                    "y": available.y(),
                    "width": available.width(),
                    "height": available.height()
                },
                "dpi": screen.logicalDotsPerInch(),
                "device_pixel_ratio": screen.devicePixelRatio(),
                "is_primary": screen == primary_screen,
                "orientation": screen.orientation().name if hasattr(screen.orientation(), 'name') else "Unknown"
            }
            screens_info.append(screen_info)

        return screens_info

    def get_recommended_window_size(self) -> Tuple[int, int]:
        """
        Get recommended window size for current display.

        Returns:
            Tuple[int, int]: (width, height)
        """
        try:
            profile = self.detect_display_profile()
            return profile.get_recommended_window_size()
        except Exception:
            return (1024, 768)

    def supports_minimum_size(self, min_width: int = 800, min_height: int = 600) -> bool:
        """
        Check if current display can support minimum window size.

        Args:
            min_width: Minimum required width
            min_height: Minimum required height

        Returns:
            bool: True if display can support minimum size
        """
        try:
            profile = self.detect_display_profile()
            return profile.supports_minimum_size(min_width, min_height)
        except Exception:
            # Conservative fallback
            _, _, width, height = self.get_available_geometry()
            return width >= min_width and height >= min_height

    def get_display_summary(self) -> dict:
        """
        Get comprehensive display information summary.

        Returns:
            dict: Display information for debugging/logging
        """
        try:
            profile = self.detect_display_profile()
            app = QApplication.instance()

            summary = {
                "profile": {
                    "resolution": f"{profile.screen_width}x{profile.screen_height}",
                    "category": profile.get_resolution_category(),
                    "aspect_ratio": profile.get_aspect_ratio(),
                    "is_widescreen": profile.is_widescreen(),
                    "dpi_scale": profile.dpi_scale,
                    "dpi_category": profile.get_dpi_category(),
                    "is_high_dpi": profile.is_high_dpi,
                    "platform": profile.platform
                },
                "recommended": {
                    "window_size": profile.get_recommended_window_size(),
                    "platform_defaults": profile.get_platform_specific_defaults()
                }
            }

            if app:
                summary["qt_info"] = {
                    "screens_count": len(app.screens()),
                    "primary_screen": app.primaryScreen().name(),
                    "available_geometry": self.get_available_geometry(),
                    "full_geometry": self.get_screen_geometry()
                }

            return summary

        except Exception as e:
            return {
                "error": str(e),
                "fallback": {
                    "resolution": "1920x1080",
                    "dpi_scale": 1.0,
                    "recommended_size": (1024, 768)
                }
            }