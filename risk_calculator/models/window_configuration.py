"""
WindowConfiguration model implementation.
Manages window size, position, and display state persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


@dataclass
class WindowConfiguration:
    """Window configuration data model with validation and state management."""

    width: int
    height: int
    x: int
    y: int
    maximized: bool
    last_updated: datetime

    # Class constants for validation
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    MAX_WIDTH = 7680  # Support up to 8K displays
    MAX_HEIGHT = 4320

    def validate(self) -> bool:
        """
        Validate window configuration values.

        Returns:
            bool: True if configuration is valid
        """
        try:
            # Check size constraints
            if self.width < self.MIN_WIDTH or self.width > self.MAX_WIDTH:
                return False
            if self.height < self.MIN_HEIGHT or self.height > self.MAX_HEIGHT:
                return False

            # Check data types
            if not isinstance(self.x, int) or not isinstance(self.y, int):
                return False
            if not isinstance(self.maximized, bool):
                return False
            if not isinstance(self.last_updated, datetime):
                return False

            return True

        except (TypeError, AttributeError):
            return False

    def is_within_screen_bounds(self, screen_width: int, screen_height: int) -> bool:
        """
        Check if window configuration fits within screen bounds.

        Args:
            screen_width: Available screen width
            screen_height: Available screen height

        Returns:
            bool: True if window fits on screen
        """
        # Check if window fits entirely on screen
        if (self.x >= 0 and self.y >= 0 and
            self.x + self.width <= screen_width and
            self.y + self.height <= screen_height):
            return True
        return False

    def adjust_to_screen(self, screen_width: int, screen_height: int) -> 'WindowConfiguration':
        """
        Adjust window configuration to fit within screen bounds.

        Args:
            screen_width: Available screen width
            screen_height: Available screen height

        Returns:
            WindowConfiguration: Adjusted configuration
        """
        new_width = self.width
        new_height = self.height
        new_x = self.x
        new_y = self.y

        # If window is larger than screen, resize to 80% of screen
        if self.width > screen_width or self.height > screen_height:
            new_width = int(screen_width * 0.8)
            new_height = int(screen_height * 0.8)

            # Ensure minimum constraints are still met
            new_width = max(new_width, self.MIN_WIDTH)
            new_height = max(new_height, self.MIN_HEIGHT)

        # Center the window if it doesn't fit or is off-screen
        if (new_x < 0 or new_y < 0 or
            new_x + new_width > screen_width or
            new_y + new_height > screen_height):
            new_x = max(0, (screen_width - new_width) // 2)
            new_y = max(0, (screen_height - new_height) // 2)

        return WindowConfiguration(
            width=new_width,
            height=new_height,
            x=new_x,
            y=new_y,
            maximized=self.maximized,
            last_updated=datetime.now()
        )

    def center_on_screen(self, screen_width: int, screen_height: int) -> 'WindowConfiguration':
        """
        Center window on screen.

        Args:
            screen_width: Available screen width
            screen_height: Available screen height

        Returns:
            WindowConfiguration: Centered configuration
        """
        centered_x = max(0, (screen_width - self.width) // 2)
        centered_y = max(0, (screen_height - self.height) // 2)

        return WindowConfiguration(
            width=self.width,
            height=self.height,
            x=centered_x,
            y=centered_y,
            maximized=self.maximized,
            last_updated=self.last_updated
        )

    def update_size(self, width: int, height: int) -> 'WindowConfiguration':
        """
        Update window size and timestamp.

        Args:
            width: New window width
            height: New window height

        Returns:
            WindowConfiguration: Updated configuration
        """
        return WindowConfiguration(
            width=width,
            height=height,
            x=self.x,
            y=self.y,
            maximized=self.maximized,
            last_updated=datetime.now()
        )

    def update_position(self, x: int, y: int) -> 'WindowConfiguration':
        """
        Update window position and timestamp.

        Args:
            x: New window x position
            y: New window y position

        Returns:
            WindowConfiguration: Updated configuration
        """
        return WindowConfiguration(
            width=self.width,
            height=self.height,
            x=x,
            y=y,
            maximized=self.maximized,
            last_updated=datetime.now()
        )

    def recover_to_defaults(self, screen_width: int, screen_height: int) -> 'WindowConfiguration':
        """
        Recover from invalid state to defaults.

        Args:
            screen_width: Available screen width
            screen_height: Available screen height

        Returns:
            WindowConfiguration: Valid default configuration
        """
        default_width = min(1024, int(screen_width * 0.8))
        default_height = min(768, int(screen_height * 0.8))

        # Ensure minimum constraints
        default_width = max(default_width, self.MIN_WIDTH)
        default_height = max(default_height, self.MIN_HEIGHT)

        return WindowConfiguration(
            width=default_width,
            height=default_height,
            x=(screen_width - default_width) // 2,
            y=(screen_height - default_height) // 2,
            maximized=False,
            last_updated=datetime.now()
        )

    def equals_window_properties(self, other: 'WindowConfiguration') -> bool:
        """
        Compare window properties (excluding timestamp).

        Args:
            other: Other configuration to compare

        Returns:
            bool: True if window properties are equal
        """
        return (self.width == other.width and
                self.height == other.height and
                self.x == other.x and
                self.y == other.y and
                self.maximized == other.maximized)

    def copy(self) -> 'WindowConfiguration':
        """
        Create a copy of the configuration.

        Returns:
            WindowConfiguration: Copy of this configuration
        """
        return WindowConfiguration(
            width=self.width,
            height=self.height,
            x=self.x,
            y=self.y,
            maximized=self.maximized,
            last_updated=self.last_updated
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize configuration to dictionary.

        Returns:
            Dict[str, Any]: Serialized configuration
        """
        return {
            'width': self.width,
            'height': self.height,
            'x': self.x,
            'y': self.y,
            'maximized': self.maximized,
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowConfiguration':
        """
        Deserialize configuration from dictionary.

        Args:
            data: Dictionary containing configuration data

        Returns:
            WindowConfiguration: Deserialized configuration
        """
        # Handle missing fields with defaults
        width = data.get('width', 1024)
        height = data.get('height', 768)
        x = data.get('x', 0)
        y = data.get('y', 0)
        maximized = data.get('maximized', False)

        # Handle timestamp
        last_updated_str = data.get('last_updated')
        if last_updated_str:
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                last_updated = datetime.now()
        else:
            last_updated = datetime.now()

        return cls(
            width=width,
            height=height,
            x=x,
            y=y,
            maximized=maximized,
            last_updated=last_updated
        )

    @classmethod
    def create_default(cls, screen_width: Optional[int] = None,
                      screen_height: Optional[int] = None) -> 'WindowConfiguration':
        """
        Create default window configuration.

        Args:
            screen_width: Optional screen width for centering
            screen_height: Optional screen height for centering

        Returns:
            WindowConfiguration: Default configuration
        """
        default_width = 1024
        default_height = 768

        # Calculate centered position if screen dimensions provided
        if screen_width and screen_height:
            x = max(0, (screen_width - default_width) // 2)
            y = max(0, (screen_height - default_height) // 2)
        else:
            x = 100
            y = 100

        return cls(
            width=default_width,
            height=default_height,
            x=x,
            y=y,
            maximized=False,
            last_updated=datetime.now()
        )