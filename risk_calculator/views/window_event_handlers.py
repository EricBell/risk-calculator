"""
Window event handlers for responsive UI behavior.
Manages window resize, state changes, and cross-platform event handling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass
from enum import Enum
import time


class WindowEvent(Enum):
    """Types of window events."""
    RESIZE = "resize"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    FOCUS_IN = "focus_in"
    FOCUS_OUT = "focus_out"
    CLOSE = "close"
    MOVE = "move"


@dataclass
class EventHandlerConfig:
    """Configuration for window event handling."""
    debounce_ms: int = 100
    enable_resize_debounce: bool = True
    track_window_state: bool = True
    log_events: bool = False
    min_resize_interval: int = 50  # Minimum ms between resize events


class WindowEventManager:
    """Manages window events and responsive behavior."""

    def __init__(self, window: tk.Tk, config: Optional[EventHandlerConfig] = None):
        """
        Initialize window event manager.

        Args:
            window: Main window to manage
            config: Event handler configuration
        """
        self.window = window
        self.config = config or EventHandlerConfig()
        self.event_handlers: Dict[WindowEvent, List[Callable]] = {
            event: [] for event in WindowEvent
        }

        # State tracking
        self.last_resize_time = 0
        self.resize_debounce_timer = None
        self.current_state = "normal"
        self.last_geometry = ""
        self.is_minimized = False
        self.has_focus = True

        # Bind window events
        self._setup_event_bindings()

    def _setup_event_bindings(self):
        """Setup event bindings for the window."""
        # Resize and move events
        self.window.bind('<Configure>', self._on_configure)

        # Window state events
        self.window.bind('<Map>', self._on_map)
        self.window.bind('<Unmap>', self._on_unmap)

        # Focus events
        self.window.bind('<FocusIn>', self._on_focus_in)
        self.window.bind('<FocusOut>', self._on_focus_out)

        # Window close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Window state change tracking (platform-specific)
        try:
            self.window.bind('<Visibility>', self._on_visibility_change)
        except Exception:
            pass  # Not all platforms support this event

    def _on_configure(self, event):
        """Handle window configure events (resize/move)."""
        if event.widget != self.window:
            return

        current_time = time.time() * 1000  # Convert to milliseconds
        geometry = self.window.geometry()

        # Check if this is a resize or move event
        if geometry != self.last_geometry:
            if self._is_resize_event(event):
                self._handle_resize_event(event, current_time)
            else:
                self._handle_move_event(event)

            self.last_geometry = geometry

    def _is_resize_event(self, event) -> bool:
        """Determine if configure event is a resize."""
        try:
            current_size = f"{event.width}x{event.height}"
            last_size = self.last_geometry.split('+')[0] if self.last_geometry else ""
            return current_size != last_size
        except (AttributeError, IndexError):
            return True  # Assume resize if we can't determine

    def _handle_resize_event(self, event, current_time: float):
        """Handle window resize with debouncing."""
        if self.config.enable_resize_debounce:
            # Cancel previous timer
            if self.resize_debounce_timer:
                self.window.after_cancel(self.resize_debounce_timer)

            # Check minimum interval
            if current_time - self.last_resize_time < self.config.min_resize_interval:
                return

            # Schedule debounced handler
            self.resize_debounce_timer = self.window.after(
                self.config.debounce_ms,
                lambda: self._execute_resize_handlers(event)
            )
        else:
            self._execute_resize_handlers(event)

        self.last_resize_time = current_time

    def _execute_resize_handlers(self, event):
        """Execute all registered resize handlers."""
        self._log_event(WindowEvent.RESIZE, f"Size: {event.width}x{event.height}")
        self._call_handlers(WindowEvent.RESIZE, event)

    def _handle_move_event(self, event):
        """Handle window move events."""
        self._log_event(WindowEvent.MOVE, f"Position: {self.window.winfo_x()},{self.window.winfo_y()}")
        self._call_handlers(WindowEvent.MOVE, event)

    def _on_map(self, event):
        """Handle window map (show) events."""
        if event.widget != self.window:
            return

        if self.is_minimized:
            self.is_minimized = False
            self._log_event(WindowEvent.RESTORE, "Window restored")
            self._call_handlers(WindowEvent.RESTORE, event)
        else:
            self._log_event(WindowEvent.MAXIMIZE, "Window mapped")

    def _on_unmap(self, event):
        """Handle window unmap (hide) events."""
        if event.widget != self.window:
            return

        self.is_minimized = True
        self._log_event(WindowEvent.MINIMIZE, "Window minimized")
        self._call_handlers(WindowEvent.MINIMIZE, event)

    def _on_focus_in(self, event):
        """Handle window focus in events."""
        if not self.has_focus:
            self.has_focus = True
            self._log_event(WindowEvent.FOCUS_IN, "Window gained focus")
            self._call_handlers(WindowEvent.FOCUS_IN, event)

    def _on_focus_out(self, event):
        """Handle window focus out events."""
        if self.has_focus:
            self.has_focus = False
            self._log_event(WindowEvent.FOCUS_OUT, "Window lost focus")
            self._call_handlers(WindowEvent.FOCUS_OUT, event)

    def _on_close(self):
        """Handle window close events."""
        self._log_event(WindowEvent.CLOSE, "Window closing")
        self._call_handlers(WindowEvent.CLOSE, None)

    def _on_visibility_change(self, event):
        """Handle visibility change events (platform-specific)."""
        try:
            state = event.state
            if state == "VisibilityUnobscured":
                self._call_handlers(WindowEvent.RESTORE, event)
            elif state == "VisibilityFullyObscured":
                self._call_handlers(WindowEvent.MINIMIZE, event)
        except AttributeError:
            pass

    def _call_handlers(self, event_type: WindowEvent, event):
        """Call all registered handlers for an event type."""
        for handler in self.event_handlers[event_type]:
            try:
                if event:
                    handler(event)
                else:
                    handler()
            except Exception as e:
                if self.config.log_events:
                    print(f"Error in {event_type.value} handler: {e}")

    def _log_event(self, event_type: WindowEvent, details: str):
        """Log event if logging is enabled."""
        if self.config.log_events:
            print(f"Window Event [{event_type.value}]: {details}")

    def add_handler(self, event_type: WindowEvent, handler: Callable):
        """
        Add event handler for specific window event.

        Args:
            event_type: Type of window event
            handler: Handler function to call
        """
        self.event_handlers[event_type].append(handler)

    def remove_handler(self, event_type: WindowEvent, handler: Callable):
        """
        Remove event handler for specific window event.

        Args:
            event_type: Type of window event
            handler: Handler function to remove
        """
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)

    def clear_handlers(self, event_type: Optional[WindowEvent] = None):
        """
        Clear event handlers.

        Args:
            event_type: Specific event type to clear, or None for all
        """
        if event_type:
            self.event_handlers[event_type].clear()
        else:
            for handlers in self.event_handlers.values():
                handlers.clear()

    def get_window_state(self) -> Dict[str, Any]:
        """
        Get current window state information.

        Returns:
            Dict containing window state details
        """
        try:
            return {
                "geometry": self.window.geometry(),
                "state": self.window.state(),
                "width": self.window.winfo_width(),
                "height": self.window.winfo_height(),
                "x": self.window.winfo_x(),
                "y": self.window.winfo_y(),
                "minimized": self.is_minimized,
                "has_focus": self.has_focus,
                "screen_width": self.window.winfo_screenwidth(),
                "screen_height": self.window.winfo_screenheight()
            }
        except Exception:
            return {}

    def is_window_maximized(self) -> bool:
        """Check if window is currently maximized."""
        try:
            return self.window.state() == 'zoomed'
        except Exception:
            try:
                return bool(self.window.attributes('-zoomed'))
            except Exception:
                return False

    def set_window_state_tracking(self, enabled: bool):
        """
        Enable or disable window state tracking.

        Args:
            enabled: Whether to track window state
        """
        self.config.track_window_state = enabled


class ResponsiveWindowEventHandler:
    """Specialized event handler for responsive UI behavior."""

    def __init__(self, window: tk.Tk, responsive_components: Optional[List] = None):
        """
        Initialize responsive window event handler.

        Args:
            window: Main window
            responsive_components: List of components to notify on events
        """
        self.window = window
        self.responsive_components = responsive_components or []
        self.event_manager = WindowEventManager(window)

        # Setup responsive event handlers
        self._setup_responsive_handlers()

    def _setup_responsive_handlers(self):
        """Setup event handlers for responsive behavior."""
        self.event_manager.add_handler(WindowEvent.RESIZE, self._on_responsive_resize)
        self.event_manager.add_handler(WindowEvent.MINIMIZE, self._on_responsive_minimize)
        self.event_manager.add_handler(WindowEvent.RESTORE, self._on_responsive_restore)

    def _on_responsive_resize(self, event):
        """Handle resize events for responsive components."""
        width = event.width
        height = event.height

        # Notify all responsive components
        for component in self.responsive_components:
            if hasattr(component, 'handle_window_resize'):
                try:
                    component.handle_window_resize(event)
                except Exception:
                    pass  # Continue with other components

            if hasattr(component, 'adapt_to_size'):
                try:
                    component.adapt_to_size(width, height)
                except Exception:
                    pass

    def _on_responsive_minimize(self, event):
        """Handle minimize events for responsive components."""
        for component in self.responsive_components:
            if hasattr(component, 'on_window_minimize'):
                try:
                    component.on_window_minimize()
                except Exception:
                    pass

    def _on_responsive_restore(self, event):
        """Handle restore events for responsive components."""
        for component in self.responsive_components:
            if hasattr(component, 'on_window_restore'):
                try:
                    component.on_window_restore()
                except Exception:
                    pass

    def add_responsive_component(self, component):
        """
        Add a component to receive responsive events.

        Args:
            component: Component with responsive event methods
        """
        if component not in self.responsive_components:
            self.responsive_components.append(component)

    def remove_responsive_component(self, component):
        """
        Remove a component from responsive events.

        Args:
            component: Component to remove
        """
        if component in self.responsive_components:
            self.responsive_components.remove(component)


class CrossPlatformWindowHandler:
    """Cross-platform window event handling utilities."""

    @staticmethod
    def setup_window_for_platform(window: tk.Tk):
        """
        Setup window for cross-platform compatibility.

        Args:
            window: Window to configure
        """
        # Platform-specific window configuration
        import platform
        system = platform.system()

        if system == "Windows":
            # Windows-specific setup
            try:
                window.state('zoomed')  # Start maximized on Windows
            except Exception:
                pass

        elif system == "Darwin":  # macOS
            # macOS-specific setup
            try:
                window.lift()
                window.attributes('-topmost', True)
                window.attributes('-topmost', False)
            except Exception:
                pass

        elif system == "Linux":
            # Linux-specific setup
            try:
                window.attributes('-zoomed', True)
            except Exception:
                pass

    @staticmethod
    def get_platform_specific_geometry(window: tk.Tk) -> Dict[str, Any]:
        """
        Get platform-specific geometry information.

        Args:
            window: Window to analyze

        Returns:
            Dict containing platform-specific geometry details
        """
        import platform
        system = platform.system()

        try:
            base_info = {
                "geometry": window.geometry(),
                "width": window.winfo_width(),
                "height": window.winfo_height(),
                "x": window.winfo_x(),
                "y": window.winfo_y(),
                "platform": system
            }

            if system == "Windows":
                # Windows-specific geometry
                try:
                    base_info["state"] = window.state()
                except Exception:
                    base_info["state"] = "normal"

            elif system == "Darwin":
                # macOS-specific geometry
                try:
                    base_info["topmost"] = window.attributes('-topmost')
                except Exception:
                    base_info["topmost"] = False

            elif system == "Linux":
                # Linux-specific geometry
                try:
                    base_info["zoomed"] = window.attributes('-zoomed')
                except Exception:
                    base_info["zoomed"] = False

            return base_info

        except Exception:
            return {"platform": system, "error": "Could not get geometry"}

    @staticmethod
    def set_platform_specific_state(window: tk.Tk, maximized: bool):
        """
        Set window maximized state in platform-specific way.

        Args:
            window: Window to configure
            maximized: Whether window should be maximized
        """
        import platform
        system = platform.system()

        try:
            if system == "Windows":
                if maximized:
                    window.state('zoomed')
                else:
                    window.state('normal')

            elif system == "Darwin":
                # macOS doesn't have direct maximization control
                if maximized:
                    window.lift()

            elif system == "Linux":
                window.attributes('-zoomed', maximized)

        except Exception:
            # Fallback to geometry manipulation
            if maximized:
                try:
                    screen_width = window.winfo_screenwidth()
                    screen_height = window.winfo_screenheight()
                    window.geometry(f"{screen_width}x{screen_height}+0+0")
                except Exception:
                    pass