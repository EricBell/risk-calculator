"""
Display Profile Model
Represents characteristics of the user's display for appropriate default sizing.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import platform


@dataclass
class DisplayProfile:
    """Display characteristics data structure for Qt applications."""

    screen_width: int
    screen_height: int
    dpi_scale: float
    is_high_dpi: bool
    platform: str

    def __post_init__(self):
        """Validate display profile values after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate display profile values."""
        # Validate screen dimensions
        if self.screen_width <= 0:
            raise ValueError(f"Screen width must be positive, got {self.screen_width}")
        if self.screen_height <= 0:
            raise ValueError(f"Screen height must be positive, got {self.screen_height}")

        # Validate DPI scale
        if self.dpi_scale <= 0 or self.dpi_scale > 5.0:
            raise ValueError(f"DPI scale must be between 0 and 5.0, got {self.dpi_scale}")

        # Validate types
        if not isinstance(self.screen_width, int):
            raise TypeError(f"Screen width must be integer, got {type(self.screen_width)}")
        if not isinstance(self.screen_height, int):
            raise TypeError(f"Screen height must be integer, got {type(self.screen_height)}")
        if not isinstance(self.dpi_scale, (int, float)):
            raise TypeError(f"DPI scale must be numeric, got {type(self.dpi_scale)}")
        if not isinstance(self.is_high_dpi, bool):
            raise TypeError(f"Is high DPI must be boolean, got {type(self.is_high_dpi)}")
        if not isinstance(self.platform, str):
            raise TypeError(f"Platform must be string, got {type(self.platform)}")

        # Validate platform
        valid_platforms = ["Windows", "Linux", "Darwin", "Other"]
        if self.platform not in valid_platforms:
            raise ValueError(f"Platform must be one of {valid_platforms}, got {self.platform}")

    def get_resolution_category(self) -> str:
        """
        Categorize the display resolution.

        Returns:
            str: Resolution category (HD, FHD, QHD, 4K, 8K, or Custom)
        """
        total_pixels = self.screen_width * self.screen_height

        if total_pixels >= 7680 * 4320:  # 8K
            return "8K"
        elif total_pixels >= 3840 * 2160:  # 4K UHD
            return "4K"
        elif total_pixels >= 2560 * 1440:  # QHD
            return "QHD"
        elif total_pixels >= 1920 * 1080:  # Full HD
            return "FHD"
        elif total_pixels >= 1366 * 768:  # HD
            return "HD"
        else:
            return "Custom"

    def get_aspect_ratio(self) -> Tuple[int, int]:
        """
        Calculate the aspect ratio of the display.

        Returns:
            Tuple[int, int]: Simplified aspect ratio (width, height)
        """
        def gcd(a: int, b: int) -> int:
            """Calculate greatest common divisor."""
            while b:
                a, b = b, a % b
            return a

        common_divisor = gcd(self.screen_width, self.screen_height)
        return (self.screen_width // common_divisor, self.screen_height // common_divisor)

    def is_widescreen(self) -> bool:
        """
        Check if display is widescreen (aspect ratio >= 16:10).

        Returns:
            bool: True if widescreen
        """
        aspect_w, aspect_h = self.get_aspect_ratio()
        return aspect_w / aspect_h >= 1.6

    def get_recommended_window_size(self) -> Tuple[int, int]:
        """
        Get recommended default window size for this display.

        Returns:
            Tuple[int, int]: (width, height) for default window
        """
        # Base recommendations on resolution and DPI
        if self.get_resolution_category() in ["4K", "8K"] or self.is_high_dpi:
            # High resolution displays - use larger default window
            base_width = 1400
            base_height = 1000
        elif self.get_resolution_category() in ["QHD", "FHD"]:
            # Standard HD displays
            base_width = 1200
            base_height = 900
        elif self.get_resolution_category() == "HD":
            # Lower resolution displays
            base_width = 1024
            base_height = 768
        else:
            # Custom/unknown resolutions - conservative approach
            base_width = 800
            base_height = 600

        # Apply DPI scaling
        scaled_width = int(base_width * self.dpi_scale)
        scaled_height = int(base_height * self.dpi_scale)

        # Ensure window doesn't exceed 80% of screen size
        max_width = int(self.screen_width * 0.8)
        max_height = int(self.screen_height * 0.8)

        final_width = min(scaled_width, max_width)
        final_height = min(scaled_height, max_height)

        # Ensure minimum size
        final_width = max(final_width, 800)
        final_height = max(final_height, 600)

        return (final_width, final_height)

    def supports_minimum_size(self, min_width: int = 800, min_height: int = 600) -> bool:
        """
        Check if display can support minimum window size.

        Args:
            min_width: Minimum required width
            min_height: Minimum required height

        Returns:
            bool: True if display can support minimum size
        """
        return self.screen_width >= min_width and self.screen_height >= min_height

    def get_dpi_category(self) -> str:
        """
        Categorize the DPI scaling level.

        Returns:
            str: DPI category (Standard, High, Very High)
        """
        if self.dpi_scale >= 2.0:
            return "Very High"
        elif self.dpi_scale >= 1.5:
            return "High"
        else:
            return "Standard"

    def get_platform_specific_defaults(self) -> Dict[str, Any]:
        """
        Get platform-specific default settings.

        Returns:
            Dict[str, Any]: Platform-specific configuration
        """
        defaults = {
            "font_scale": 1.0,
            "icon_size": 16,
            "spacing": 6,
            "margin": 10
        }

        # Platform-specific adjustments
        if self.platform == "Windows":
            defaults.update({
                "font_scale": self.dpi_scale,
                "icon_size": int(16 * self.dpi_scale),
                "spacing": int(6 * self.dpi_scale),
                "margin": int(10 * self.dpi_scale)
            })
        elif self.platform == "Linux":
            # Linux often handles DPI scaling differently
            if self.is_high_dpi:
                defaults.update({
                    "font_scale": min(self.dpi_scale, 1.5),  # Cap at 1.5x
                    "icon_size": int(16 * min(self.dpi_scale, 1.5)),
                    "spacing": int(6 * min(self.dpi_scale, 1.5)),
                    "margin": int(10 * min(self.dpi_scale, 1.5))
                })

        return defaults

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "dpi_scale": self.dpi_scale,
            "is_high_dpi": self.is_high_dpi,
            "platform": self.platform
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisplayProfile':
        """Create DisplayProfile from dictionary."""
        return cls(
            screen_width=data["screen_width"],
            screen_height=data["screen_height"],
            dpi_scale=data["dpi_scale"],
            is_high_dpi=data["is_high_dpi"],
            platform=data["platform"]
        )

    @classmethod
    def detect_current(cls) -> 'DisplayProfile':
        """
        Detect current display profile (placeholder implementation).

        Note: Actual detection requires Qt application to be running.
        This provides fallback detection using system information.

        Returns:
            DisplayProfile: Detected or default profile
        """
        # Get platform
        system_platform = platform.system()
        platform_map = {
            "Windows": "Windows",
            "Linux": "Linux",
            "Darwin": "Darwin"
        }
        detected_platform = platform_map.get(system_platform, "Other")

        # Default values (will be replaced by Qt detection when available)
        default_width = 1920
        default_height = 1080
        default_dpi_scale = 1.0
        default_is_high_dpi = False

        # Try to detect some basic info on Linux
        if detected_platform == "Linux":
            try:
                import subprocess
                # Try to get screen resolution from xrandr
                result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if '*' in line and 'x' in line:
                            # Parse resolution from xrandr output
                            parts = line.strip().split()
                            for part in parts:
                                if 'x' in part and part.replace('x', '').replace('.', '').isdigit():
                                    width_str, height_str = part.split('x')
                                    default_width = int(float(width_str))
                                    default_height = int(float(height_str))
                                    break
                            break
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                # Fall back to defaults if xrandr fails
                pass

        # Estimate if high DPI based on resolution
        total_pixels = default_width * default_height
        if total_pixels >= 3840 * 2160:  # 4K or higher
            default_is_high_dpi = True
            default_dpi_scale = 1.5
        elif total_pixels >= 2560 * 1440:  # QHD
            default_is_high_dpi = True
            default_dpi_scale = 1.25

        return cls(
            screen_width=default_width,
            screen_height=default_height,
            dpi_scale=default_dpi_scale,
            is_high_dpi=default_is_high_dpi,
            platform=detected_platform
        )

    def __str__(self) -> str:
        """String representation of display profile."""
        return (f"DisplayProfile({self.screen_width}x{self.screen_height}, "
                f"DPI: {self.dpi_scale}x, {self.platform})")

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"DisplayProfile(screen_width={self.screen_width}, "
                f"screen_height={self.screen_height}, dpi_scale={self.dpi_scale}, "
                f"is_high_dpi={self.is_high_dpi}, platform='{self.platform}')")