"""
Enhanced view integration for error display and responsive layout.
Integrates enhanced error display components with existing views.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, List, Any, Callable
from dataclasses import dataclass

# Import enhanced components
from risk_calculator.views.error_display import (
    ErrorLabel, FieldErrorManager, ErrorDisplayConfig, ResponsiveErrorDisplay
)
from risk_calculator.views.responsive_layout import (
    ResponsiveGridManager, ResponsiveFormLayout, ResponsiveConfig
)
from risk_calculator.views.window_event_handlers import (
    WindowEventManager, ResponsiveWindowEventHandler
)


@dataclass
class ViewIntegrationConfig:
    """Configuration for view integration."""
    enable_enhanced_errors: bool = True
    enable_responsive_layout: bool = True
    enable_window_events: bool = True
    error_display_config: Optional[ErrorDisplayConfig] = None
    responsive_config: Optional[ResponsiveConfig] = None


class EnhancedViewIntegrator:
    """Integrates enhanced components with existing views."""

    def __init__(self, view, config: Optional[ViewIntegrationConfig] = None):
        """
        Initialize view integrator.

        Args:
            view: Existing view to enhance
            config: Integration configuration
        """
        self.view = view
        self.config = config or ViewIntegrationConfig()

        # Initialize enhanced components
        self.error_manager: Optional[FieldErrorManager] = None
        self.responsive_manager: Optional[ResponsiveGridManager] = None
        self.window_event_manager: Optional[WindowEventManager] = None

        # Integration state
        self.error_labels_created = False
        self.responsive_layout_setup = False
        self.event_handlers_setup = False

        # Setup integration
        self._setup_integration()

    def _setup_integration(self):
        """Setup integration with existing view."""
        if self.config.enable_enhanced_errors:
            self._setup_error_display_integration()

        if self.config.enable_responsive_layout:
            self._setup_responsive_layout_integration()

        if self.config.enable_window_events:
            self._setup_window_event_integration()

    def _setup_error_display_integration(self):
        """Setup enhanced error display integration."""
        try:
            error_config = self.config.error_display_config or ErrorDisplayConfig()
            self.error_manager = FieldErrorManager(error_config)

            # Create error labels for existing input widgets
            self._create_enhanced_error_labels()

            self.error_labels_created = True

        except Exception:
            # Error display integration is not critical
            pass

    def _create_enhanced_error_labels(self):
        """Create enhanced error labels for existing input widgets."""
        if not self.error_manager:
            return

        # Find input widgets in the view
        input_widgets = self._find_input_widgets()

        for field_name, widget in input_widgets.items():
            try:
                # Create error label
                error_label = self._create_error_label_for_widget(widget, field_name)

                # Register with error manager
                self.error_manager.register_field(field_name, widget, error_label)

            except Exception:
                # Continue with other widgets if one fails
                continue

    def _find_input_widgets(self) -> Dict[str, tk.Widget]:
        """Find input widgets in the view."""
        input_widgets = {}

        # Check for common input widget patterns
        widget_patterns = [
            'account_size_entry', 'account_entry',
            'risk_percentage_entry', 'percentage_entry',
            'fixed_risk_amount_entry', 'fixed_amount_entry', 'fixed_risk_entry',
            'entry_price_entry', 'entry_entry',
            'stop_loss_entry', 'stop_entry',
            'premium_entry',
            'tick_value_entry', 'tick_entry',
            'support_resistance_entry', 'level_entry'
        ]

        for pattern in widget_patterns:
            if hasattr(self.view, pattern):
                widget = getattr(self.view, pattern)
                # Extract field name from pattern
                field_name = self._extract_field_name_from_pattern(pattern)
                input_widgets[field_name] = widget

        # Check input_widgets dictionary if available
        if hasattr(self.view, 'input_widgets'):
            input_widgets.update(self.view.input_widgets)

        # Check widgets dictionary if available (test compatibility)
        if hasattr(self.view, 'widgets'):
            input_widgets.update(self.view.widgets)

        return input_widgets

    def _extract_field_name_from_pattern(self, pattern: str) -> str:
        """Extract field name from widget pattern."""
        # Remove common suffixes
        field_name = pattern.replace('_entry', '').replace('_widget', '')

        # Handle special cases
        field_mappings = {
            'account': 'account_size',
            'percentage': 'risk_percentage',
            'fixed_amount': 'fixed_risk_amount',
            'fixed_risk': 'fixed_risk_amount',
            'entry': 'entry_price',
            'stop': 'stop_loss_price',
            'tick': 'tick_value',
            'level': 'support_resistance_level',
            'support_resistance': 'support_resistance_level'
        }

        return field_mappings.get(field_name, field_name)

    def _create_error_label_for_widget(self, widget: tk.Widget, field_name: str) -> ErrorLabel:
        """Create error label positioned near a widget."""
        # Get parent widget
        parent = widget.master if hasattr(widget, 'master') else widget.winfo_parent()

        # Create error label
        error_config = self.config.error_display_config or ErrorDisplayConfig()
        error_label = ErrorLabel(parent, error_config)

        # Position error label
        try:
            self._position_error_label(error_label, widget)
        except Exception:
            # Fallback positioning
            error_label.pack(anchor='w', padx=5)

        return error_label

    def _position_error_label(self, error_label: ErrorLabel, widget: tk.Widget):
        """Position error label relative to input widget."""
        # Try to get grid information
        try:
            grid_info = widget.grid_info()
            if grid_info:
                row = int(grid_info.get('row', 0))
                column = int(grid_info.get('column', 0))

                # Position error label below the widget
                error_label.grid(row=row + 1, column=column, sticky='w', padx=5)
                return
        except Exception:
            pass

        # Try to get pack information
        try:
            pack_info = widget.pack_info()
            if pack_info:
                error_label.pack(anchor='w', padx=5)
                return
        except Exception:
            pass

        # Fallback positioning
        error_label.pack(anchor='w', padx=5)

    def _setup_responsive_layout_integration(self):
        """Setup responsive layout integration."""
        try:
            responsive_config = self.config.responsive_config or ResponsiveConfig()

            # Create responsive manager for the view
            if hasattr(self.view, 'master'):
                parent = self.view.master
            else:
                parent = self.view

            self.responsive_manager = ResponsiveGridManager(parent, responsive_config)

            # Configure existing widgets for responsive behavior
            self._configure_responsive_widgets()

            self.responsive_layout_setup = True

        except Exception:
            # Responsive layout integration is not critical
            pass

    def _configure_responsive_widgets(self):
        """Configure existing widgets for responsive behavior."""
        if not self.responsive_manager:
            return

        # Configure main container weights
        try:
            if hasattr(self.view, 'grid_columnconfigure'):
                self.view.grid_columnconfigure(0, weight=1)

            if hasattr(self.view, 'grid_rowconfigure'):
                self.view.grid_rowconfigure(0, weight=1)

            # Configure input frames if available
            frames_to_configure = ['input_frame', 'main_frame', 'result_frame']
            for frame_name in frames_to_configure:
                if hasattr(self.view, frame_name):
                    frame = getattr(self.view, frame_name)
                    if hasattr(frame, 'grid_columnconfigure'):
                        frame.grid_columnconfigure(1, weight=1)  # Input columns expand

        except Exception:
            pass

    def _setup_window_event_integration(self):
        """Setup window event integration."""
        try:
            # Find root window
            root_window = self._find_root_window()
            if not root_window:
                return

            # Create window event manager
            self.window_event_manager = WindowEventManager(root_window)

            # Setup responsive event handlers
            responsive_components = [self]
            if self.responsive_manager:
                responsive_components.append(self.responsive_manager)

            self.responsive_event_handler = ResponsiveWindowEventHandler(
                root_window, responsive_components
            )

            self.event_handlers_setup = True

        except Exception:
            # Window event integration is not critical
            pass

    def _find_root_window(self) -> Optional[tk.Tk]:
        """Find the root window."""
        try:
            widget = self.view
            while widget:
                if isinstance(widget, tk.Tk):
                    return widget
                if hasattr(widget, 'master'):
                    widget = widget.master
                else:
                    widget = widget.winfo_parent()
                    if widget:
                        widget = widget.nametowidget(widget)
                    else:
                        break
            return None
        except Exception:
            return None

    def show_field_error(self, field_name: str, error_message: str):
        """Show error for specific field using enhanced error display."""
        if self.error_manager:
            self.error_manager.show_error(field_name, error_message)

    def hide_field_error(self, field_name: str):
        """Hide error for specific field."""
        if self.error_manager:
            self.error_manager.hide_error(field_name)

    def clear_all_errors(self):
        """Clear all error messages."""
        if self.error_manager:
            self.error_manager.hide_all_errors()

    def handle_window_resize(self, event):
        """Handle window resize events for responsive behavior."""
        try:
            if self.responsive_manager:
                self.responsive_manager._handle_resize(event.width, event.height)
        except Exception:
            pass

    def adapt_to_size(self, width: int, height: int):
        """Adapt view layout to window size."""
        # This can be implemented based on specific view requirements
        pass

    def get_error_manager(self) -> Optional[FieldErrorManager]:
        """Get the error manager instance."""
        return self.error_manager

    def get_responsive_manager(self) -> Optional[ResponsiveGridManager]:
        """Get the responsive manager instance."""
        return self.responsive_manager

    def get_window_event_manager(self) -> Optional[WindowEventManager]:
        """Get the window event manager instance."""
        return self.window_event_manager

    def is_enhanced_errors_enabled(self) -> bool:
        """Check if enhanced error display is enabled."""
        return self.error_labels_created

    def is_responsive_layout_enabled(self) -> bool:
        """Check if responsive layout is enabled."""
        return self.responsive_layout_setup

    def is_window_events_enabled(self) -> bool:
        """Check if window events are enabled."""
        return self.event_handlers_setup


class ViewIntegrationFactory:
    """Factory for creating view integrations."""

    @staticmethod
    def create_enhanced_view(view, enable_all: bool = True) -> EnhancedViewIntegrator:
        """
        Create enhanced view with all features enabled.

        Args:
            view: Existing view to enhance
            enable_all: Whether to enable all enhancement features

        Returns:
            EnhancedViewIntegrator: Configured integrator
        """
        config = ViewIntegrationConfig(
            enable_enhanced_errors=enable_all,
            enable_responsive_layout=enable_all,
            enable_window_events=enable_all
        )

        return EnhancedViewIntegrator(view, config)

    @staticmethod
    def create_error_only_view(view) -> EnhancedViewIntegrator:
        """
        Create view with only enhanced error display.

        Args:
            view: Existing view to enhance

        Returns:
            EnhancedViewIntegrator: Configured integrator
        """
        config = ViewIntegrationConfig(
            enable_enhanced_errors=True,
            enable_responsive_layout=False,
            enable_window_events=False
        )

        return EnhancedViewIntegrator(view, config)

    @staticmethod
    def create_responsive_only_view(view) -> EnhancedViewIntegrator:
        """
        Create view with only responsive layout.

        Args:
            view: Existing view to enhance

        Returns:
            EnhancedViewIntegrator: Configured integrator
        """
        config = ViewIntegrationConfig(
            enable_enhanced_errors=False,
            enable_responsive_layout=True,
            enable_window_events=True
        )

        return EnhancedViewIntegrator(view, config)


def enhance_existing_view(view,
                         enable_errors: bool = True,
                         enable_responsive: bool = True,
                         enable_events: bool = True) -> EnhancedViewIntegrator:
    """
    Enhance an existing view with enhanced components.

    Args:
        view: Existing view to enhance
        enable_errors: Whether to enable enhanced error display
        enable_responsive: Whether to enable responsive layout
        enable_events: Whether to enable window events

    Returns:
        EnhancedViewIntegrator: Configured integrator
    """
    config = ViewIntegrationConfig(
        enable_enhanced_errors=enable_errors,
        enable_responsive_layout=enable_responsive,
        enable_window_events=enable_events
    )

    return EnhancedViewIntegrator(view, config)