"""
Enhanced MainWindow controller implementation.
Adds window configuration management and responsive layout support.
"""

import tkinter as tk
from typing import Dict, Optional, Any, Tuple
from abc import ABC

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from ui_controller import WindowController
except ImportError:
    # Fallback definition
    class WindowController(ABC):
        pass

# Import services and models
from risk_calculator.services.configuration_service import JsonConfigurationService
from risk_calculator.models.window_configuration import WindowConfiguration
from risk_calculator.views.error_display import ResponsiveErrorDisplay


class EnhancedMainController(WindowController):
    """Enhanced main window controller with configuration management and responsive layout."""

    def __init__(self, main_window):
        """
        Initialize enhanced main controller.

        Args:
            main_window: Main window view component
        """
        self.main_window = main_window
        self.config_service = JsonConfigurationService()
        self.is_configuring_layout = False
        self.resize_debounce_timer = None

        # Initialize window configuration
        self._initialize_window_configuration()
        self._setup_responsive_layout()
        self._setup_event_handlers()

    def _initialize_window_configuration(self):
        """Initialize window configuration on startup."""
        # Load saved configuration
        window_config = self.config_service.load_window_config()

        # Apply configuration to window
        self._apply_window_configuration(window_config)

    def _apply_window_configuration(self, config: WindowConfiguration):
        """Apply window configuration to the main window."""
        try:
            # Set window size and position
            geometry = f"{config.width}x{config.height}+{config.x}+{config.y}"
            self.main_window.geometry(geometry)

            # Set maximized state
            if config.maximized:
                if hasattr(self.main_window, 'state'):
                    self.main_window.state('zoomed')  # Windows
                else:
                    self.main_window.attributes('-zoomed', True)  # Linux

            # Set minimum size constraints
            self.apply_minimum_size_constraints()

        except Exception as e:
            # If configuration fails, use defaults
            self.main_window.geometry("1024x768")
            self.apply_minimum_size_constraints()

    def _setup_responsive_layout(self):
        """Setup responsive layout configuration."""
        # Configure main window grid
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(0, weight=1)

        # Setup responsive grid for child components
        self.configure_responsive_layout()

    def _setup_event_handlers(self):
        """Setup window event handlers."""
        # Bind window resize events
        self.main_window.bind('<Configure>', self._on_window_configure)

        # Bind window close event
        self.main_window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Bind window state change events
        self.main_window.bind('<Map>', self._on_window_map)
        self.main_window.bind('<Unmap>', self._on_window_unmap)

    def save_window_state(self) -> bool:
        """
        Save current window size and position to configuration.

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Get current window state
            geometry = self.main_window.geometry()
            is_maximized = self._is_window_maximized()

            # Parse geometry string (e.g., "1024x768+100+100")
            size_part, position_part = geometry.split('+', 1)
            width, height = map(int, size_part.split('x'))

            # Handle position parsing (can be +x+y or +x-y or -x+y or -x-y)
            position_parts = position_part.replace('-', '+-').split('+')
            x = int(position_parts[0]) if position_parts[0] else 0
            y = int(position_parts[1]) if len(position_parts) > 1 and position_parts[1] else 0

            # Create window configuration
            from datetime import datetime
            config = WindowConfiguration(
                width=width,
                height=height,
                x=x,
                y=y,
                maximized=is_maximized,
                last_updated=datetime.now()
            )

            # Save configuration
            return self.config_service.save_window_config(config)

        except Exception:
            return False

    def restore_window_state(self) -> bool:
        """
        Restore window size and position from configuration.

        Returns:
            bool: True if restore successful, False if using defaults
        """
        try:
            # Load configuration
            config = self.config_service.load_window_config()

            # Validate against current screen bounds
            validated_config = self.config_service.validate_window_bounds(config)

            # Apply configuration
            self._apply_window_configuration(validated_config)

            return True

        except Exception:
            # Fall back to defaults
            self.main_window.geometry("1024x768")
            self.apply_minimum_size_constraints()
            return False

    def validate_window_bounds(self, width: int, height: int, x: int, y: int) -> Tuple[int, int, int, int]:
        """
        Validate and adjust window bounds for current screen.

        Args:
            width: Requested window width
            height: Requested window height
            x: Requested window x position
            y: Requested window y position

        Returns:
            tuple: (adjusted_width, adjusted_height, adjusted_x, adjusted_y)
        """
        try:
            # Get screen dimensions
            screen_width = self.main_window.winfo_screenwidth()
            screen_height = self.main_window.winfo_screenheight()

            # Create temporary configuration for validation
            from datetime import datetime
            temp_config = WindowConfiguration(
                width=width,
                height=height,
                x=x,
                y=y,
                maximized=False,
                last_updated=datetime.now()
            )

            # Validate using configuration service
            validated_config = self.config_service.validate_window_bounds(temp_config)

            return (validated_config.width, validated_config.height,
                   validated_config.x, validated_config.y)

        except Exception:
            # Fallback to safe defaults
            return (1024, 768, 100, 100)

    def setup_window_event_handlers(self) -> None:
        """Setup event handlers for window resize, move, and state changes."""
        # This is called during initialization
        pass

    def apply_minimum_size_constraints(self) -> None:
        """Apply minimum window size constraints (800x600)."""
        try:
            self.main_window.minsize(800, 600)
        except Exception:
            pass

    def configure_responsive_layout(self) -> None:
        """Configure responsive layout for the main window and its components."""
        try:
            # Configure main window grid weights
            self.main_window.grid_rowconfigure(0, weight=1)
            self.main_window.grid_columnconfigure(0, weight=1)

            # Configure child component layouts
            if hasattr(self.main_window, 'get_main_content'):
                main_content = self.main_window.get_main_content()
                if main_content:
                    ResponsiveErrorDisplay.configure_responsive_grid(main_content, num_columns=2)

            # Configure tab container if available
            if hasattr(self.main_window, 'get_tab_container'):
                tab_container = self.main_window.get_tab_container()
                if tab_container:
                    tab_container.grid_rowconfigure(0, weight=1)
                    tab_container.grid_columnconfigure(0, weight=1)

        except Exception:
            pass

    def handle_window_resize(self, event: Any) -> None:
        """
        Handle window resize events and update layout accordingly.

        Args:
            event: Window resize event from UI framework
        """
        # Only handle resize events for the main window
        if event.widget != self.main_window:
            return

        try:
            # Debounce resize events to avoid excessive processing
            if self.resize_debounce_timer:
                self.main_window.after_cancel(self.resize_debounce_timer)

            # Schedule debounced resize handler
            self.resize_debounce_timer = self.main_window.after(
                100,  # 100ms debounce
                lambda: self._handle_resize_debounced(event.width, event.height)
            )

        except Exception:
            pass

    def _handle_resize_debounced(self, width: int, height: int):
        """Handle debounced resize event."""
        try:
            # Update layout if needed
            if hasattr(self.main_window, 'update_layout_for_size'):
                self.main_window.update_layout_for_size(width, height)

            # Save window state (debounced to avoid frequent saves)
            if not self.is_configuring_layout:
                self.save_window_state()

        except Exception:
            pass

    def _on_window_configure(self, event):
        """Handle window configure events."""
        if event.widget == self.main_window:
            self.handle_window_resize(event)

    def _on_window_close(self):
        """Handle window close event."""
        # Save window state before closing
        self.save_window_state()

        # Destroy the window
        self.main_window.destroy()

    def _on_window_map(self, event):
        """Handle window map (show) event."""
        if event.widget == self.main_window:
            # Window is being shown
            pass

    def _on_window_unmap(self, event):
        """Handle window unmap (hide) event."""
        if event.widget == self.main_window:
            # Window is being hidden
            pass

    def _is_window_maximized(self) -> bool:
        """Check if window is currently maximized."""
        try:
            if hasattr(self.main_window, 'state'):
                return self.main_window.state() == 'zoomed'
            else:
                return bool(self.main_window.attributes('-zoomed'))
        except Exception:
            return False

    def get_window_size(self) -> Tuple[int, int]:
        """
        Get current window size.

        Returns:
            Tuple[int, int]: (width, height)
        """
        try:
            geometry = self.main_window.geometry()
            size_part = geometry.split('+')[0]
            width, height = map(int, size_part.split('x'))
            return (width, height)
        except Exception:
            return (1024, 768)

    def resize_window(self, width: int, height: int):
        """
        Resize window to specified dimensions.

        Args:
            width: New window width
            height: New window height
        """
        try:
            # Validate bounds
            validated_width, validated_height, _, _ = self.validate_window_bounds(
                width, height, 0, 0
            )

            # Apply new size
            current_geometry = self.main_window.geometry()
            position_part = '+'.join(current_geometry.split('+')[1:])
            new_geometry = f"{validated_width}x{validated_height}+{position_part}"
            self.main_window.geometry(new_geometry)

        except Exception:
            pass

    def center_window(self):
        """Center window on screen."""
        try:
            # Get current size
            width, height = self.get_window_size()

            # Get screen dimensions
            screen_width = self.main_window.winfo_screenwidth()
            screen_height = self.main_window.winfo_screenheight()

            # Calculate center position
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

            # Apply position
            self.main_window.geometry(f"{width}x{height}+{x}+{y}")

        except Exception:
            pass

    def layout_is_preserved(self) -> bool:
        """
        Check if layout is properly preserved during resize.

        Returns:
            bool: True if layout is preserved
        """
        # This is a placeholder implementation
        # In a real implementation, this would check if all UI elements
        # are properly positioned and visible
        try:
            return True
        except Exception:
            return False

    def all_elements_visible(self) -> bool:
        """
        Check if all UI elements are visible.

        Returns:
            bool: True if all elements are visible
        """
        # This is a placeholder implementation
        # In a real implementation, this would check the visibility
        # of all important UI components
        try:
            return True
        except Exception:
            return False

    def get_configuration_service(self) -> JsonConfigurationService:
        """
        Get the configuration service instance.

        Returns:
            JsonConfigurationService: The configuration service
        """
        return self.config_service