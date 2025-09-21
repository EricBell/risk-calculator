"""
Enhanced error display components for form validation.
Provides visual feedback for field-level and form-level validation errors.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, List, Any
from dataclasses import dataclass


@dataclass
class ErrorDisplayConfig:
    """Configuration for error display appearance."""
    error_color: str = "#DC3545"  # Bootstrap danger red
    warning_color: str = "#FFC107"  # Bootstrap warning yellow
    success_color: str = "#28A745"  # Bootstrap success green
    font_family: str = "Arial"
    font_size: int = 9
    max_width: int = 400
    padding_x: int = 5
    padding_y: int = 2


class ErrorLabel(tk.Label):
    """Enhanced label widget for displaying field validation errors."""

    def __init__(self, parent, config: Optional[ErrorDisplayConfig] = None, **kwargs):
        """
        Initialize error label.

        Args:
            parent: Parent widget
            config: Error display configuration
            **kwargs: Additional label options
        """
        self.config_obj = config or ErrorDisplayConfig()
        self._has_error = False
        self._error_message = ""

        # Set default label options
        default_options = {
            "text": "",
            "fg": self.config_obj.error_color,
            "font": (self.config_obj.font_family, self.config_obj.font_size),
            "wraplength": self.config_obj.max_width,
            "justify": "left",
            "anchor": "w"
        }
        default_options.update(kwargs)

        super().__init__(parent, **default_options)

        # Initially hide the label
        self.hide()

    def show_error(self, message: str, error_type: str = "error"):
        """
        Show error message with appropriate styling.

        Args:
            message: Error message to display
            error_type: Type of error (error, warning, success)
        """
        self._has_error = True
        self._error_message = message

        # Set color based on error type
        color_map = {
            "error": self.config_obj.error_color,
            "warning": self.config_obj.warning_color,
            "success": self.config_obj.success_color
        }
        color = color_map.get(error_type, self.config_obj.error_color)

        # Update label
        self.config(text=message, fg=color)
        try:
            self.pack(anchor="w", padx=self.config_obj.padding_x, pady=self.config_obj.padding_y)
        except:
            # Fallback to grid if pack fails
            self.grid(sticky="w", padx=self.config_obj.padding_x, pady=self.config_obj.padding_y)

    def show_warning(self, message: str):
        """Show warning message."""
        self.show_error(message, "warning")

    def show_success(self, message: str):
        """Show success message."""
        self.show_error(message, "success")

    def hide(self):
        """Hide error label and clear error state."""
        self._has_error = False
        self._error_message = ""
        try:
            self.pack_forget()
        except:
            try:
                self.grid_remove()
            except:
                pass

    def hide_error(self):
        """Alias for hide method (backward compatibility)."""
        self.hide()

    def clear(self):
        """Alias for hide method."""
        self.hide()

    def has_error(self) -> bool:
        """Check if error label is currently showing an error."""
        return self._has_error

    def get_error_message(self) -> str:
        """Get current error message."""
        return self._error_message

    def set_max_width(self, width: int):
        """Update maximum width for text wrapping."""
        self.config_obj.max_width = width
        self.config(wraplength=width)


class FieldErrorManager:
    """Manager for coordinating error display across multiple form fields."""

    def __init__(self, config: Optional[ErrorDisplayConfig] = None):
        """
        Initialize field error manager.

        Args:
            config: Error display configuration
        """
        self.config = config or ErrorDisplayConfig()
        self.error_labels: Dict[str, ErrorLabel] = {}
        self.field_widgets: Dict[str, tk.Widget] = {}

    def register_field(self, field_name: str, field_widget: tk.Widget, error_label: ErrorLabel):
        """
        Register a field with its error label.

        Args:
            field_name: Name of the field
            field_widget: Input widget for the field
            error_label: Error label widget for the field
        """
        self.field_widgets[field_name] = field_widget
        self.error_labels[field_name] = error_label

    def create_error_label(self, parent: tk.Widget, field_name: str) -> ErrorLabel:
        """
        Create and register an error label for a field.

        Args:
            parent: Parent widget for the error label
            field_name: Name of the field

        Returns:
            ErrorLabel: Created error label
        """
        error_label = ErrorLabel(parent, self.config)
        if field_name in self.field_widgets:
            self.error_labels[field_name] = error_label
        return error_label

    def show_error(self, field_name: str, message: str, error_type: str = "error"):
        """
        Show error for specific field.

        Args:
            field_name: Name of field with error
            message: Error message
            error_type: Type of error (error, warning, success)
        """
        if field_name in self.error_labels:
            self.error_labels[field_name].show_error(message, error_type)

    def show_warning(self, field_name: str, message: str):
        """Show warning for specific field."""
        self.show_error(field_name, message, "warning")

    def show_success(self, field_name: str, message: str):
        """Show success message for specific field."""
        self.show_error(field_name, message, "success")

    def hide_error(self, field_name: str):
        """
        Hide error for specific field.

        Args:
            field_name: Name of field to clear error for
        """
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()

    def hide_all_errors(self):
        """Hide all error messages."""
        for error_label in self.error_labels.values():
            error_label.hide()

    def has_errors(self) -> bool:
        """Check if any field has visible errors."""
        return any(label.has_error() for label in self.error_labels.values())

    def get_error_fields(self) -> List[str]:
        """Get list of field names that currently have errors."""
        return [
            field_name for field_name, label in self.error_labels.items()
            if label.has_error()
        ]

    def get_all_error_messages(self) -> Dict[str, str]:
        """Get all current error messages."""
        return {
            field_name: label.get_error_message()
            for field_name, label in self.error_labels.items()
            if label.has_error()
        }

    def get_error_message(self, field_name: str) -> Optional[str]:
        """
        Get the current error message for a field (backward compatibility).

        Args:
            field_name: Name of field

        Returns:
            Optional[str]: Error message or None if no error
        """
        if field_name in self.error_labels:
            label = self.error_labels[field_name]
            if label.has_error():
                return label.get_error_message()
        return None

    def update_field_styling(self, field_name: str, has_error: bool):
        """
        Update field widget styling to indicate error state.

        Args:
            field_name: Name of field to update
            has_error: Whether field has an error
        """
        if field_name not in self.field_widgets:
            return

        widget = self.field_widgets[field_name]

        try:
            if has_error:
                # Add error styling
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    if isinstance(widget, tk.Entry):
                        widget.config(highlightbackground=self.config.error_color, highlightthickness=1)
                    # For ttk.Entry, we would need to configure styles
                elif isinstance(widget, (tk.Text, tk.Listbox)):
                    widget.config(highlightbackground=self.config.error_color, highlightthickness=1)
            else:
                # Remove error styling
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    if isinstance(widget, tk.Entry):
                        widget.config(highlightbackground="SystemWindowFrame", highlightthickness=0)
                elif isinstance(widget, (tk.Text, tk.Listbox)):
                    widget.config(highlightbackground="SystemWindowFrame", highlightthickness=0)

        except Exception:
            # Widget styling is not critical, continue silently
            pass


class ResponsiveErrorDisplay:
    """Utility class for creating responsive error display layouts."""

    @staticmethod
    def configure_responsive_grid(parent: tk.Widget, num_columns: int = 2):
        """
        Configure responsive grid layout for parent widget.

        Args:
            parent: Parent widget to configure
            num_columns: Number of columns in grid
        """
        try:
            # Configure column weights for responsive layout
            for col in range(num_columns):
                parent.grid_columnconfigure(col, weight=1)

            # Configure row weights (will be set as rows are added)
            # This is typically done dynamically as widgets are added

        except Exception:
            # Grid configuration is not critical
            pass

    @staticmethod
    def create_field_with_error(parent: tk.Widget, field_name: str, label_text: str,
                               row: int, column: int = 0, field_type: str = "entry",
                               config: Optional[ErrorDisplayConfig] = None) -> tuple:
        """
        Create a complete field with label, input, and error display.

        Args:
            parent: Parent widget
            field_name: Name of the field
            label_text: Text for the field label
            row: Grid row for placement
            column: Grid column for placement
            field_type: Type of input field (entry, text, combobox)
            config: Error display configuration

        Returns:
            tuple: (label_widget, input_widget, error_label)
        """
        config = config or ErrorDisplayConfig()

        try:
            # Create label
            label = tk.Label(parent, text=label_text, anchor="w")
            label.grid(row=row, column=column, sticky="w", padx=5, pady=2)

            # Create input field
            if field_type == "entry":
                field_widget = tk.Entry(parent)
            elif field_type == "text":
                field_widget = tk.Text(parent, height=3)
            elif field_type == "combobox":
                field_widget = ttk.Combobox(parent)
            else:
                field_widget = tk.Entry(parent)  # Default

            field_widget.grid(row=row, column=column + 1, sticky="ew", padx=5, pady=2)

            # Create error label
            error_label = ErrorLabel(parent, config)
            error_label.grid(row=row + 1, column=column + 1, sticky="w", padx=5)

            # Configure column weight for responsive layout
            parent.grid_columnconfigure(column + 1, weight=1)

            return label, field_widget, error_label

        except Exception:
            # Return minimal widgets if creation fails
            label = tk.Label(parent, text=label_text)
            field_widget = tk.Entry(parent)
            error_label = ErrorLabel(parent, config)
            return label, field_widget, error_label

    @staticmethod
    def create_form_error_summary(parent: tk.Widget, config: Optional[ErrorDisplayConfig] = None) -> tk.Frame:
        """
        Create a summary panel for displaying form-level errors.

        Args:
            parent: Parent widget
            config: Error display configuration

        Returns:
            tk.Frame: Error summary frame
        """
        config = config or ErrorDisplayConfig()

        # Create frame for error summary
        error_frame = tk.Frame(parent, relief="solid", borderwidth=1)
        error_frame.pack(fill="x", padx=10, pady=5)

        # Create header label
        header_label = tk.Label(
            error_frame,
            text="Please correct the following errors:",
            font=(config.font_family, config.font_size + 1, "bold"),
            fg=config.error_color
        )
        header_label.pack(anchor="w", padx=config.padding_x, pady=config.padding_y)

        # Create text widget for error list
        error_text = tk.Text(
            error_frame,
            height=4,
            wrap="word",
            font=(config.font_family, config.font_size),
            fg=config.error_color,
            relief="flat",
            state="disabled"
        )
        error_text.pack(fill="both", expand=True, padx=config.padding_x, pady=config.padding_y)

        # Initially hide the frame
        error_frame.pack_forget()

        return error_frame

    @staticmethod
    def update_error_summary(error_frame: tk.Frame, error_messages: List[str]):
        """
        Update error summary with current error messages.

        Args:
            error_frame: Error summary frame
            error_messages: List of error messages to display
        """
        try:
            # Find the text widget in the frame
            error_text = None
            for child in error_frame.winfo_children():
                if isinstance(child, tk.Text):
                    error_text = child
                    break

            if not error_text:
                return

            # Update text content
            error_text.config(state="normal")
            error_text.delete(1.0, "end")

            if error_messages:
                # Show frame and update content
                for i, message in enumerate(error_messages, 1):
                    error_text.insert("end", f"{i}. {message}\n")
                error_frame.pack(fill="x", padx=10, pady=5)
            else:
                # Hide frame if no errors
                error_frame.pack_forget()

            error_text.config(state="disabled")

        except Exception:
            # Error summary update is not critical
            pass