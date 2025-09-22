"""
UI Layout State Model
Tracks current scaling ratios and element positioning for proportional resizing.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple, List, Optional


@dataclass
class UILayoutState:
    """UI layout state for responsive scaling and element positioning."""

    base_width: int
    base_height: int
    current_width: int
    current_height: int
    scale_factor_x: float
    scale_factor_y: float
    font_base_size: int

    def __post_init__(self):
        """Validate layout state values after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate UI layout state values."""
        # Validate dimensions
        if self.base_width <= 0 or self.base_height <= 0:
            raise ValueError("Base dimensions must be positive")
        if self.current_width <= 0 or self.current_height <= 0:
            raise ValueError("Current dimensions must be positive")

        # Validate scale factors
        if not (0.1 <= self.scale_factor_x <= 10.0):
            raise ValueError(f"X scale factor must be between 0.1 and 10.0, got {self.scale_factor_x}")
        if not (0.1 <= self.scale_factor_y <= 10.0):
            raise ValueError(f"Y scale factor must be between 0.1 and 10.0, got {self.scale_factor_y}")

        # Validate font size
        if not (8 <= self.font_base_size <= 72):
            raise ValueError(f"Font base size must be between 8 and 72, got {self.font_base_size}")

        # Validate types
        if not isinstance(self.base_width, int):
            raise TypeError(f"Base width must be integer, got {type(self.base_width)}")
        if not isinstance(self.base_height, int):
            raise TypeError(f"Base height must be integer, got {type(self.base_height)}")
        if not isinstance(self.current_width, int):
            raise TypeError(f"Current width must be integer, got {type(self.current_width)}")
        if not isinstance(self.current_height, int):
            raise TypeError(f"Current height must be integer, got {type(self.current_height)}")
        if not isinstance(self.scale_factor_x, (int, float)):
            raise TypeError(f"X scale factor must be numeric, got {type(self.scale_factor_x)}")
        if not isinstance(self.scale_factor_y, (int, float)):
            raise TypeError(f"Y scale factor must be numeric, got {type(self.scale_factor_y)}")
        if not isinstance(self.font_base_size, int):
            raise TypeError(f"Font base size must be integer, got {type(self.font_base_size)}")

    def update_size(self, new_width: int, new_height: int) -> 'UILayoutState':
        """
        Update layout state with new dimensions and recalculate scale factors.

        Args:
            new_width: New window width
            new_height: New window height

        Returns:
            UILayoutState: Updated layout state
        """
        new_scale_x = new_width / self.base_width
        new_scale_y = new_height / self.base_height

        return UILayoutState(
            base_width=self.base_width,
            base_height=self.base_height,
            current_width=new_width,
            current_height=new_height,
            scale_factor_x=new_scale_x,
            scale_factor_y=new_scale_y,
            font_base_size=self.font_base_size
        )

    def get_scaled_font_size(self, base_font_size: Optional[int] = None) -> int:
        """
        Calculate scaled font size based on current scale factors.

        Args:
            base_font_size: Base font size to scale (uses layout's base if None)

        Returns:
            int: Scaled font size
        """
        if base_font_size is None:
            base_font_size = self.font_base_size

        # Use smaller of the two scale factors to maintain readability
        scale_factor = min(self.scale_factor_x, self.scale_factor_y)

        # Apply reasonable limits to font scaling
        scale_factor = max(0.8, min(scale_factor, 2.0))

        scaled_size = int(base_font_size * scale_factor)

        # Ensure font size stays within reasonable bounds
        return max(8, min(scaled_size, 72))

    def get_scaled_dimensions(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """
        Calculate scaled dimensions for a UI element.

        Args:
            base_width: Base width of element
            base_height: Base height of element

        Returns:
            Tuple[int, int]: (scaled_width, scaled_height)
        """
        scaled_width = int(base_width * self.scale_factor_x)
        scaled_height = int(base_height * self.scale_factor_y)

        # Ensure minimum sizes
        scaled_width = max(1, scaled_width)
        scaled_height = max(1, scaled_height)

        return (scaled_width, scaled_height)

    def get_scaled_position(self, base_x: int, base_y: int) -> Tuple[int, int]:
        """
        Calculate scaled position for a UI element.

        Args:
            base_x: Base x position
            base_y: Base y position

        Returns:
            Tuple[int, int]: (scaled_x, scaled_y)
        """
        scaled_x = int(base_x * self.scale_factor_x)
        scaled_y = int(base_y * self.scale_factor_y)

        return (scaled_x, scaled_y)

    def get_scaled_spacing(self, base_spacing: int) -> int:
        """
        Calculate scaled spacing value.

        Args:
            base_spacing: Base spacing value

        Returns:
            int: Scaled spacing
        """
        # Use average of scale factors for spacing
        avg_scale = (self.scale_factor_x + self.scale_factor_y) / 2
        scaled_spacing = int(base_spacing * avg_scale)

        # Ensure minimum spacing
        return max(1, scaled_spacing)

    def get_scale_category(self) -> str:
        """
        Categorize the current scaling level.

        Returns:
            str: Scale category (Small, Normal, Large, Very Large)
        """
        avg_scale = (self.scale_factor_x + self.scale_factor_y) / 2

        if avg_scale < 0.8:
            return "Small"
        elif avg_scale < 1.2:
            return "Normal"
        elif avg_scale < 1.8:
            return "Large"
        else:
            return "Very Large"

    def is_proportional_scaling(self, tolerance: float = 0.1) -> bool:
        """
        Check if scaling is proportional (similar X and Y scale factors).

        Args:
            tolerance: Allowed difference between scale factors

        Returns:
            bool: True if scaling is proportional
        """
        return abs(self.scale_factor_x - self.scale_factor_y) <= tolerance

    def get_aspect_ratio(self) -> float:
        """
        Get current window aspect ratio.

        Returns:
            float: Aspect ratio (width/height)
        """
        return self.current_width / self.current_height

    def get_base_aspect_ratio(self) -> float:
        """
        Get base design aspect ratio.

        Returns:
            float: Base aspect ratio (width/height)
        """
        return self.base_width / self.base_height

    def aspect_ratio_changed(self, tolerance: float = 0.05) -> bool:
        """
        Check if aspect ratio has changed significantly from base.

        Args:
            tolerance: Allowed aspect ratio difference

        Returns:
            bool: True if aspect ratio changed significantly
        """
        current_ratio = self.get_aspect_ratio()
        base_ratio = self.get_base_aspect_ratio()

        return abs(current_ratio - base_ratio) > tolerance

    def get_layout_hints(self) -> Dict[str, Any]:
        """
        Get layout hints for UI components.

        Returns:
            Dict[str, Any]: Layout hints and recommendations
        """
        return {
            "scale_category": self.get_scale_category(),
            "proportional_scaling": self.is_proportional_scaling(),
            "aspect_ratio_changed": self.aspect_ratio_changed(),
            "recommended_font_size": self.get_scaled_font_size(),
            "spacing_scale": self.get_scaled_spacing(6),
            "margin_scale": self.get_scaled_spacing(10),
            "needs_layout_adjustment": self.aspect_ratio_changed() or not self.is_proportional_scaling()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "base_width": self.base_width,
            "base_height": self.base_height,
            "current_width": self.current_width,
            "current_height": self.current_height,
            "scale_factor_x": self.scale_factor_x,
            "scale_factor_y": self.scale_factor_y,
            "font_base_size": self.font_base_size
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UILayoutState':
        """Create UILayoutState from dictionary."""
        return cls(
            base_width=data["base_width"],
            base_height=data["base_height"],
            current_width=data["current_width"],
            current_height=data["current_height"],
            scale_factor_x=data["scale_factor_x"],
            scale_factor_y=data["scale_factor_y"],
            font_base_size=data["font_base_size"]
        )

    @classmethod
    def create_initial(cls, base_width: int, base_height: int, font_size: int = 10) -> 'UILayoutState':
        """
        Create initial layout state (1:1 scaling).

        Args:
            base_width: Base design width
            base_height: Base design height
            font_size: Base font size

        Returns:
            UILayoutState: Initial layout state
        """
        return cls(
            base_width=base_width,
            base_height=base_height,
            current_width=base_width,
            current_height=base_height,
            scale_factor_x=1.0,
            scale_factor_y=1.0,
            font_base_size=font_size
        )

    @classmethod
    def create_from_window(cls, base_width: int, base_height: int,
                          window_width: int, window_height: int,
                          font_size: int = 10) -> 'UILayoutState':
        """
        Create layout state from current window dimensions.

        Args:
            base_width: Base design width
            base_height: Base design height
            window_width: Current window width
            window_height: Current window height
            font_size: Base font size

        Returns:
            UILayoutState: Layout state for current window
        """
        scale_x = window_width / base_width
        scale_y = window_height / base_height

        return cls(
            base_width=base_width,
            base_height=base_height,
            current_width=window_width,
            current_height=window_height,
            scale_factor_x=scale_x,
            scale_factor_y=scale_y,
            font_base_size=font_size
        )

    def __str__(self) -> str:
        """String representation of layout state."""
        return (f"UILayoutState({self.current_width}x{self.current_height}, "
                f"scale: {self.scale_factor_x:.2f}x{self.scale_factor_y:.2f})")

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"UILayoutState(base={self.base_width}x{self.base_height}, "
                f"current={self.current_width}x{self.current_height}, "
                f"scale_x={self.scale_factor_x:.2f}, scale_y={self.scale_factor_y:.2f}, "
                f"font_base={self.font_base_size})")