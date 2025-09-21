"""
Responsive layout management for Tkinter applications.
Provides utilities for creating layouts that adapt to window resizing.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum


class LayoutDirection(Enum):
    """Layout direction for responsive components."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"


class ResponsiveBreakpoint(Enum):
    """Responsive breakpoints based on window width."""
    SMALL = 800   # Minimum supported width
    MEDIUM = 1024  # Standard desktop
    LARGE = 1440   # Large desktop
    EXTRA_LARGE = 1920  # Full HD


@dataclass
class GridConfig:
    """Configuration for responsive grid layout."""
    columns: int = 2
    min_columns: int = 1
    max_columns: int = 4
    column_spacing: int = 10
    row_spacing: int = 5
    padding_x: int = 10
    padding_y: int = 10
    uniform_width: bool = True
    sticky: str = "ew"


@dataclass
class ResponsiveConfig:
    """Configuration for responsive behavior."""
    min_width: int = 800
    min_height: int = 600
    breakpoints: Dict[str, int] = None
    enable_adaptive_layout: bool = True
    resize_debounce_ms: int = 100
    animate_transitions: bool = False

    def __post_init__(self):
        if self.breakpoints is None:
            self.breakpoints = {
                "small": ResponsiveBreakpoint.SMALL.value,
                "medium": ResponsiveBreakpoint.MEDIUM.value,
                "large": ResponsiveBreakpoint.LARGE.value,
                "extra_large": ResponsiveBreakpoint.EXTRA_LARGE.value
            }


class ResponsiveGridManager:
    """Manages responsive grid layouts for Tkinter widgets."""

    def __init__(self, parent: tk.Widget, config: Optional[ResponsiveConfig] = None):
        """
        Initialize responsive grid manager.

        Args:
            parent: Parent widget to manage
            config: Responsive configuration
        """
        self.parent = parent
        self.config = config or ResponsiveConfig()
        self.grid_config = GridConfig()
        self.widgets: List[tk.Widget] = []
        self.current_columns = self.grid_config.columns
        self.current_width = 0
        self.current_height = 0
        self.resize_timer = None

        # Setup responsive behavior
        self._setup_responsive_bindings()

    def _setup_responsive_bindings(self):
        """Setup event bindings for responsive behavior."""
        if self.config.enable_adaptive_layout:
            self.parent.bind('<Configure>', self._on_configure)

    def _on_configure(self, event):
        """Handle window configuration changes."""
        if event.widget != self.parent:
            return

        # Debounce resize events
        if self.resize_timer:
            self.parent.after_cancel(self.resize_timer)

        self.resize_timer = self.parent.after(
            self.config.resize_debounce_ms,
            lambda: self._handle_resize(event.width, event.height)
        )

    def _handle_resize(self, width: int, height: int):
        """Handle debounced resize event."""
        self.current_width = width
        self.current_height = height

        # Calculate responsive columns
        new_columns = self._calculate_responsive_columns(width)

        if new_columns != self.current_columns:
            self.current_columns = new_columns
            self._relayout_widgets()

    def _calculate_responsive_columns(self, width: int) -> int:
        """Calculate number of columns based on window width."""
        if width < self.config.breakpoints["small"]:
            return self.grid_config.min_columns
        elif width < self.config.breakpoints["medium"]:
            return min(2, self.grid_config.columns)
        elif width < self.config.breakpoints["large"]:
            return min(3, self.grid_config.columns)
        else:
            return min(self.grid_config.max_columns, self.grid_config.columns)

    def _relayout_widgets(self):
        """Relayout widgets with current column configuration."""
        if not self.widgets:
            return

        # Clear existing grid configuration
        for widget in self.widgets:
            widget.grid_forget()

        # Relayout widgets
        for i, widget in enumerate(self.widgets):
            row = i // self.current_columns
            col = i % self.current_columns

            widget.grid(
                row=row,
                column=col,
                sticky=self.grid_config.sticky,
                padx=self.grid_config.column_spacing,
                pady=self.grid_config.row_spacing
            )

        # Configure column weights
        self._configure_column_weights()

    def _configure_column_weights(self):
        """Configure column weights for responsive behavior."""
        # Reset all column weights
        for i in range(self.grid_config.max_columns):
            self.parent.grid_columnconfigure(i, weight=0)

        # Set weights for active columns
        if self.grid_config.uniform_width:
            weight = 1
        else:
            weight = 1

        for i in range(self.current_columns):
            self.parent.grid_columnconfigure(i, weight=weight)

    def add_widget(self, widget: tk.Widget, **grid_options):
        """
        Add a widget to the responsive grid.

        Args:
            widget: Widget to add
            **grid_options: Additional grid options
        """
        self.widgets.append(widget)

        # Calculate position
        index = len(self.widgets) - 1
        row = index // self.current_columns
        col = index % self.current_columns

        # Apply grid options
        default_options = {
            'row': row,
            'column': col,
            'sticky': self.grid_config.sticky,
            'padx': self.grid_config.column_spacing,
            'pady': self.grid_config.row_spacing
        }
        default_options.update(grid_options)

        widget.grid(**default_options)
        self._configure_column_weights()

    def remove_widget(self, widget: tk.Widget):
        """
        Remove a widget from the responsive grid.

        Args:
            widget: Widget to remove
        """
        if widget in self.widgets:
            self.widgets.remove(widget)
            widget.grid_forget()
            self._relayout_widgets()

    def set_grid_config(self, config: GridConfig):
        """
        Update grid configuration.

        Args:
            config: New grid configuration
        """
        self.grid_config = config
        self.current_columns = self._calculate_responsive_columns(self.current_width)
        self._relayout_widgets()

    def get_current_breakpoint(self) -> str:
        """Get current responsive breakpoint."""
        width = self.current_width

        if width >= self.config.breakpoints["extra_large"]:
            return "extra_large"
        elif width >= self.config.breakpoints["large"]:
            return "large"
        elif width >= self.config.breakpoints["medium"]:
            return "medium"
        else:
            return "small"


class ResponsiveFormLayout:
    """Specialized responsive layout for form widgets."""

    def __init__(self, parent: tk.Widget, config: Optional[ResponsiveConfig] = None):
        """
        Initialize responsive form layout.

        Args:
            parent: Parent widget
            config: Responsive configuration
        """
        self.parent = parent
        self.config = config or ResponsiveConfig()
        self.form_fields: List[Dict[str, Any]] = []
        self.current_layout = LayoutDirection.HORIZONTAL
        self.grid_manager = ResponsiveGridManager(parent, config)

        # Setup form-specific configuration
        form_grid_config = GridConfig(
            columns=2,  # Label + Input
            min_columns=1,
            max_columns=2,
            column_spacing=5,
            row_spacing=8,
            sticky="ew"
        )
        self.grid_manager.set_grid_config(form_grid_config)

    def add_field(self, label_text: str, widget: tk.Widget,
                  error_widget: Optional[tk.Widget] = None,
                  required: bool = False, **options) -> Dict[str, Any]:
        """
        Add a form field with label and optional error display.

        Args:
            label_text: Text for the field label
            widget: Input widget
            error_widget: Optional error display widget
            required: Whether field is required
            **options: Additional layout options

        Returns:
            Dict containing field information
        """
        # Create label
        label = tk.Label(self.parent, text=label_text, anchor="w")
        if required:
            label.config(text=f"{label_text} *")

        # Calculate row for this field
        field_row = len(self.form_fields) * 2  # Allow space for error widgets

        # Position label and widget
        label.grid(row=field_row, column=0, sticky="w",
                  padx=(self.grid_manager.grid_config.padding_x, 5),
                  pady=self.grid_manager.grid_config.row_spacing)

        widget.grid(row=field_row, column=1, sticky="ew",
                   padx=(5, self.grid_manager.grid_config.padding_x),
                   pady=self.grid_manager.grid_config.row_spacing)

        # Position error widget if provided
        if error_widget:
            error_widget.grid(row=field_row + 1, column=1, sticky="w",
                            padx=(5, self.grid_manager.grid_config.padding_x))

        # Configure column weights
        self.parent.grid_columnconfigure(0, weight=0)  # Labels don't expand
        self.parent.grid_columnconfigure(1, weight=1)  # Inputs expand

        # Store field information
        field_info = {
            "label": label,
            "widget": widget,
            "error_widget": error_widget,
            "required": required,
            "row": field_row,
            "options": options
        }
        self.form_fields.append(field_info)

        return field_info

    def set_layout_direction(self, direction: LayoutDirection):
        """
        Set form layout direction.

        Args:
            direction: Layout direction
        """
        if direction != self.current_layout:
            self.current_layout = direction
            self._relayout_form()

    def _relayout_form(self):
        """Relayout form based on current configuration."""
        if self.current_layout == LayoutDirection.VERTICAL:
            # Stack labels above inputs
            for i, field in enumerate(self.form_fields):
                base_row = i * 3  # Label, widget, error (if any)

                field["label"].grid(row=base_row, column=0, columnspan=2,
                                  sticky="w")
                field["widget"].grid(row=base_row + 1, column=0, columnspan=2,
                                   sticky="ew")

                if field["error_widget"]:
                    field["error_widget"].grid(row=base_row + 2, column=0,
                                             columnspan=2, sticky="w")
        else:
            # Horizontal layout (default)
            for i, field in enumerate(self.form_fields):
                base_row = i * 2

                field["label"].grid(row=base_row, column=0, sticky="w")
                field["widget"].grid(row=base_row, column=1, sticky="ew")

                if field["error_widget"]:
                    field["error_widget"].grid(row=base_row + 1, column=1,
                                             sticky="w")

    def adapt_to_width(self, width: int):
        """
        Adapt form layout to window width.

        Args:
            width: Current window width
        """
        if width < self.config.breakpoints["medium"]:
            self.set_layout_direction(LayoutDirection.VERTICAL)
        else:
            self.set_layout_direction(LayoutDirection.HORIZONTAL)


class ResponsiveTabLayout:
    """Responsive layout manager for tabbed interfaces."""

    def __init__(self, notebook: ttk.Notebook, config: Optional[ResponsiveConfig] = None):
        """
        Initialize responsive tab layout.

        Args:
            notebook: Notebook widget to manage
            config: Responsive configuration
        """
        self.notebook = notebook
        self.config = config or ResponsiveConfig()
        self.tab_managers: Dict[str, ResponsiveGridManager] = {}

        # Setup responsive behavior for notebook
        self.notebook.bind('<Configure>', self._on_notebook_configure)

    def _on_notebook_configure(self, event):
        """Handle notebook configuration changes."""
        if event.widget == self.notebook:
            width = event.width
            height = event.height

            # Update all tab managers
            for manager in self.tab_managers.values():
                manager._handle_resize(width, height)

    def add_tab_manager(self, tab_id: str, tab_frame: tk.Widget) -> ResponsiveGridManager:
        """
        Add responsive manager for a tab.

        Args:
            tab_id: Unique identifier for the tab
            tab_frame: Tab frame widget

        Returns:
            ResponsiveGridManager: Manager for the tab
        """
        manager = ResponsiveGridManager(tab_frame, self.config)
        self.tab_managers[tab_id] = manager
        return manager

    def get_tab_manager(self, tab_id: str) -> Optional[ResponsiveGridManager]:
        """
        Get responsive manager for a tab.

        Args:
            tab_id: Tab identifier

        Returns:
            ResponsiveGridManager or None
        """
        return self.tab_managers.get(tab_id)

    def configure_tab_responsive_layout(self, tab_id: str, grid_config: GridConfig):
        """
        Configure responsive layout for a specific tab.

        Args:
            tab_id: Tab identifier
            grid_config: Grid configuration
        """
        manager = self.tab_managers.get(tab_id)
        if manager:
            manager.set_grid_config(grid_config)


def create_responsive_window(root: tk.Tk, config: Optional[ResponsiveConfig] = None) -> ResponsiveGridManager:
    """
    Create a responsive window with grid management.

    Args:
        root: Root window
        config: Responsive configuration

    Returns:
        ResponsiveGridManager: Manager for the window
    """
    config = config or ResponsiveConfig()

    # Set minimum window size
    root.minsize(config.min_width, config.min_height)

    # Create and return grid manager
    return ResponsiveGridManager(root, config)


def configure_responsive_widget(widget: tk.Widget,
                               expand_horizontal: bool = True,
                               expand_vertical: bool = False,
                               min_width: Optional[int] = None,
                               min_height: Optional[int] = None):
    """
    Configure a widget for responsive behavior.

    Args:
        widget: Widget to configure
        expand_horizontal: Whether widget should expand horizontally
        expand_vertical: Whether widget should expand vertically
        min_width: Minimum width constraint
        min_height: Minimum height constraint
    """
    # Configure grid weights
    parent = widget.winfo_parent()
    if parent:
        parent_widget = widget.nametowidget(parent)

        # Get widget grid info
        grid_info = widget.grid_info()
        if grid_info:
            row = grid_info.get('row', 0)
            column = grid_info.get('column', 0)

            if expand_horizontal:
                parent_widget.grid_columnconfigure(column, weight=1)
            if expand_vertical:
                parent_widget.grid_rowconfigure(row, weight=1)

    # Set minimum size if specified
    if min_width or min_height:
        widget.update_idletasks()
        current_width = widget.winfo_reqwidth()
        current_height = widget.winfo_reqheight()

        new_width = max(current_width, min_width or 0)
        new_height = max(current_height, min_height or 0)

        widget.config(width=new_width, height=new_height)