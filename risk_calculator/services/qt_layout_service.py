"""
Qt Responsive Layout Service
Handles responsive scaling and layout management for Qt widgets.
"""

from typing import Tuple, Dict, Any, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import QSize, QRect
    from PySide6.QtGui import QFont

try:
    from PySide6.QtWidgets import QWidget, QApplication
    from PySide6.QtCore import QSize, QRect
    from PySide6.QtGui import QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False
    # Create dummy classes for type hints when Qt not available
    class QWidget:
        pass
    class QSize:
        pass
    class QRect:
        pass
    class QFont:
        pass

from ..models.ui_layout_state import UILayoutState
from ..models.display_profile import DisplayProfile


class QtResponsiveLayoutService:
    """Qt-based responsive layout and scaling service."""

    def __init__(self):
        """Initialize Qt responsive layout service."""
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt layout service not supported")

        self._layout_state: Optional[UILayoutState] = None
        self._base_font_size = 10

    def initialize_layout_state(self, base_width: int, base_height: int,
                              current_width: int, current_height: int,
                              base_font_size: int = 10) -> UILayoutState:
        """
        Initialize layout state for responsive scaling.

        Args:
            base_width: Base design width
            base_height: Base design height
            current_width: Current window width
            current_height: Current window height
            base_font_size: Base font size

        Returns:
            UILayoutState: Initialized layout state
        """
        self._base_font_size = base_font_size
        self._layout_state = UILayoutState.create_from_window(
            base_width=base_width,
            base_height=base_height,
            window_width=current_width,
            window_height=current_height,
            font_size=base_font_size
        )
        return self._layout_state

    def update_layout_state(self, new_width: int, new_height: int) -> UILayoutState:
        """
        Update layout state with new window dimensions.

        Args:
            new_width: New window width
            new_height: New window height

        Returns:
            UILayoutState: Updated layout state
        """
        if not self._layout_state:
            # Initialize with default base size if not set
            return self.initialize_layout_state(1024, 768, new_width, new_height)

        self._layout_state = self._layout_state.update_size(new_width, new_height)
        return self._layout_state

    def calculate_scale_factors(self, base_size: Tuple[int, int],
                              current_size: Tuple[int, int]) -> Tuple[float, float]:
        """
        Calculate scale factors for responsive layout.

        Args:
            base_size: (base_width, base_height)
            current_size: (current_width, current_height)

        Returns:
            Tuple[float, float]: (x_scale, y_scale)
        """
        base_width, base_height = base_size
        current_width, current_height = current_size

        x_scale = current_width / base_width if base_width > 0 else 1.0
        y_scale = current_height / base_height if base_height > 0 else 1.0

        return (x_scale, y_scale)

    def apply_responsive_scaling(self, widget: QWidget,
                               scale_factors: Optional[Tuple[float, float]] = None) -> None:
        """
        Apply responsive scaling to a Qt widget.

        Args:
            widget: Qt widget to scale
            scale_factors: Optional (x_scale, y_scale) factors
        """
        if not self._layout_state:
            return

        # Use provided scale factors or get from layout state
        if scale_factors:
            scale_x, scale_y = scale_factors
        else:
            scale_x = self._layout_state.scale_factor_x
            scale_y = self._layout_state.scale_factor_y

        # Scale widget geometry
        current_geometry = widget.geometry()

        # Calculate new size
        new_width = int(current_geometry.width() * scale_x)
        new_height = int(current_geometry.height() * scale_y)

        # Ensure minimum size
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)

        widget.resize(new_width, new_height)

        # Scale font if applicable
        self._scale_widget_font(widget, min(scale_x, scale_y))

    def apply_responsive_font_scaling(self, widget: QWidget,
                                    base_font_size: Optional[int] = None) -> None:
        """
        Apply responsive font scaling to a Qt widget.

        Args:
            widget: Qt widget to scale font
            base_font_size: Base font size (uses layout default if None)
        """
        if not self._layout_state:
            return

        if base_font_size is None:
            base_font_size = self._base_font_size

        scaled_font_size = self._layout_state.get_scaled_font_size(base_font_size)

        current_font = widget.font()
        current_font.setPointSize(scaled_font_size)
        widget.setFont(current_font)

    def get_scaled_dimensions(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """
        Get scaled dimensions for UI elements.

        Args:
            base_width: Base width
            base_height: Base height

        Returns:
            Tuple[int, int]: (scaled_width, scaled_height)
        """
        if not self._layout_state:
            return (base_width, base_height)

        return self._layout_state.get_scaled_dimensions(base_width, base_height)

    def get_scaled_spacing(self, base_spacing: int) -> int:
        """
        Get scaled spacing value.

        Args:
            base_spacing: Base spacing value

        Returns:
            int: Scaled spacing
        """
        if not self._layout_state:
            return base_spacing

        return self._layout_state.get_scaled_spacing(base_spacing)

    def get_scaled_font_size(self, base_font_size: Optional[int] = None) -> int:
        """
        Get scaled font size.

        Args:
            base_font_size: Base font size (uses layout default if None)

        Returns:
            int: Scaled font size
        """
        if not self._layout_state:
            return base_font_size or self._base_font_size

        return self._layout_state.get_scaled_font_size(base_font_size)

    def set_minimum_size(self, widget: QWidget, min_width: int, min_height: int) -> None:
        """
        Set minimum size for a Qt widget with scaling.

        Args:
            widget: Qt widget
            min_width: Minimum width
            min_height: Minimum height
        """
        if self._layout_state:
            scaled_width, scaled_height = self._layout_state.get_scaled_dimensions(
                min_width, min_height
            )
            widget.setMinimumSize(QSize(scaled_width, scaled_height))
        else:
            widget.setMinimumSize(QSize(min_width, min_height))

    def get_layout_hints(self) -> Dict[str, Any]:
        """
        Get layout hints for responsive design.

        Returns:
            Dict[str, Any]: Layout hints and recommendations
        """
        if not self._layout_state:
            return {
                "scale_category": "Normal",
                "proportional_scaling": True,
                "aspect_ratio_changed": False,
                "recommended_font_size": self._base_font_size,
                "spacing_scale": 6,
                "margin_scale": 10,
                "needs_layout_adjustment": False
            }

        return self._layout_state.get_layout_hints()

    def is_high_scaling_mode(self, threshold: float = 1.5) -> bool:
        """
        Check if current scaling is considered high scaling.

        Args:
            threshold: Scale factor threshold

        Returns:
            bool: True if in high scaling mode
        """
        if not self._layout_state:
            return False

        avg_scale = (self._layout_state.scale_factor_x + self._layout_state.scale_factor_y) / 2
        return avg_scale >= threshold

    def create_responsive_geometry(self, x: int, y: int, width: int, height: int) -> QRect:
        """
        Create responsive geometry based on current scaling.

        Args:
            x: Base x position
            y: Base y position
            width: Base width
            height: Base height

        Returns:
            QRect: Scaled geometry
        """
        if not self._layout_state:
            return QRect(x, y, width, height)

        scaled_x, scaled_y = self._layout_state.get_scaled_position(x, y)
        scaled_width, scaled_height = self._layout_state.get_scaled_dimensions(width, height)

        return QRect(scaled_x, scaled_y, scaled_width, scaled_height)

    def auto_detect_base_size(self) -> Tuple[int, int]:
        """
        Auto-detect appropriate base size based on current display.

        Returns:
            Tuple[int, int]: (base_width, base_height)
        """
        try:
            from .qt_display_service import QtDisplayService
            display_service = QtDisplayService()
            profile = display_service.detect_display_profile()

            # Use display-aware base sizing
            if profile.get_resolution_category() in ["4K", "8K"]:
                return (1400, 1000)
            elif profile.get_resolution_category() in ["QHD", "FHD"]:
                return (1200, 900)
            elif profile.get_resolution_category() == "HD":
                return (1024, 768)
            else:
                return (800, 600)

        except Exception:
            # Fallback to standard base size
            return (1024, 768)

    def _scale_widget_font(self, widget: QWidget, scale_factor: float) -> None:
        """
        Internal method to scale widget font.

        Args:
            widget: Qt widget
            scale_factor: Scale factor to apply
        """
        current_font = widget.font()
        current_size = current_font.pointSize()

        if current_size > 0:
            # Scale existing font size
            new_size = max(8, min(int(current_size * scale_factor), 72))
            current_font.setPointSize(new_size)
            widget.setFont(current_font)

    def get_current_state(self) -> Optional[UILayoutState]:
        """
        Get current layout state.

        Returns:
            UILayoutState or None if not initialized
        """
        return self._layout_state

    def reset_layout_state(self) -> None:
        """Reset layout state to None."""
        self._layout_state = None