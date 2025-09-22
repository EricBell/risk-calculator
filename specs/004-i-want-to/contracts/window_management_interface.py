"""
Window Management Interface Contract
Defines the interface for window configuration and responsive layout management.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
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


@dataclass
class DisplayProfile:
    """Display characteristics data structure"""
    screen_width: int
    screen_height: int
    dpi_scale: float
    is_high_dpi: bool
    platform: str


class WindowManagerInterface(ABC):
    """Interface for window configuration management"""

    @abstractmethod
    def save_window_configuration(self, config: WindowConfiguration) -> bool:
        """
        Save window configuration to persistent storage.

        Args:
            config: Window configuration to save

        Returns:
            bool: True if save successful, False otherwise
        """
        pass

    @abstractmethod
    def load_window_configuration(self) -> Optional[WindowConfiguration]:
        """
        Load window configuration from persistent storage.

        Returns:
            WindowConfiguration or None if no saved configuration
        """
        pass

    @abstractmethod
    def validate_window_bounds(self, config: WindowConfiguration) -> WindowConfiguration:
        """
        Validate window configuration against current screen bounds.

        Args:
            config: Window configuration to validate

        Returns:
            WindowConfiguration: Validated/adjusted configuration
        """
        pass

    @abstractmethod
    def get_default_window_size(self) -> Tuple[int, int]:
        """
        Get appropriate default window size for current display.

        Returns:
            Tuple[int, int]: (width, height) for default window
        """
        pass


class ResponsiveLayoutInterface(ABC):
    """Interface for responsive UI layout management"""

    @abstractmethod
    def calculate_scale_factors(self, base_size: Tuple[int, int],
                               current_size: Tuple[int, int]) -> Tuple[float, float]:
        """
        Calculate scaling factors for UI elements.

        Args:
            base_size: Original design size (width, height)
            current_size: Current window size (width, height)

        Returns:
            Tuple[float, float]: (x_scale, y_scale) factors
        """
        pass

    @abstractmethod
    def apply_responsive_scaling(self, scale_factors: Tuple[float, float]) -> None:
        """
        Apply scaling factors to UI elements.

        Args:
            scale_factors: (x_scale, y_scale) to apply
        """
        pass

    @abstractmethod
    def set_minimum_size(self, width: int, height: int) -> None:
        """
        Set minimum window size constraints.

        Args:
            width: Minimum window width
            height: Minimum window height
        """
        pass

    @abstractmethod
    def get_current_scale_factors(self) -> Tuple[float, float]:
        """
        Get current scaling factors.

        Returns:
            Tuple[float, float]: (x_scale, y_scale) factors
        """
        pass

    @abstractmethod
    def reset_scaling(self) -> None:
        """Reset scaling to default values."""
        pass

    @abstractmethod
    def is_scaling_active(self) -> bool:
        """
        Check if scaling is currently active.

        Returns:
            bool: True if scaling is active
        """
        pass


class DisplayProfileInterface(ABC):
    """Interface for display profile detection"""

    @abstractmethod
    def detect_display_profile(self) -> DisplayProfile:
        """
        Detect current display characteristics.

        Returns:
            DisplayProfile: Current display information
        """
        pass

    @abstractmethod
    def is_high_dpi_display(self) -> bool:
        """
        Check if current display is high-DPI.

        Returns:
            bool: True if high-DPI display
        """
        pass

    @abstractmethod
    def get_dpi_scale_factor(self) -> float:
        """
        Get DPI scaling factor for current display.

        Returns:
            float: DPI scale factor (1.0 = 100%, 2.0 = 200%)
        """
        pass

    @abstractmethod
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get screen dimensions (width, height).

        Returns:
            Tuple[int, int]: (width, height)
        """
        pass

    @abstractmethod
    def get_platform_info(self) -> str:
        """
        Get platform information.

        Returns:
            str: Platform name
        """
        pass

    @abstractmethod
    def calculate_optimal_window_size(self, base_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculate optimal window size based on DPI scaling.

        Args:
            base_size: Base window size (width, height)

        Returns:
            Tuple[int, int]: Optimal size (width, height)
        """
        pass

    @abstractmethod
    def supports_high_dpi_scaling(self) -> bool:
        """
        Check if platform supports high-DPI scaling.

        Returns:
            bool: True if high-DPI scaling is supported
        """
        pass