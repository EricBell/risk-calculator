"""
Error message display infrastructure for form validation.
Provides reusable components for showing field-specific error messages.
"""

import tkinter as tk
from typing import Dict, Optional


class ErrorLabel(tk.Label):
    """
    Specialized Label widget for displaying validation error messages.
    """

    def __init__(self, parent, **kwargs):
        # Set default styling for error messages
        default_config = {
            'text': '',
            'fg': '#d32f2f',  # Red color for errors
            'bg': parent.cget('bg') if hasattr(parent, 'cget') else 'white',
            'font': ('Arial', 8),
            'wraplength': 200,  # Wrap long error messages
            'justify': 'left',
            'anchor': 'w'
        }

        # Override defaults with any provided kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)

        # Start hidden
        self.grid_remove()

    def show_error(self, message: str):
        """
        Display an error message.

        Args:
            message: Error message to display
        """
        self.config(text=message)
        self.grid()

    def hide_error(self):
        """Hide the error message."""
        self.config(text='')
        self.grid_remove()

    def has_error(self) -> bool:
        """
        Check if an error message is currently displayed.

        Returns:
            bool: True if error message is shown
        """
        return self.cget('text') != '' and self.winfo_viewable()


class FieldErrorManager:
    """
    Manages error messages for multiple form fields.
    """

    def __init__(self):
        self.error_labels: Dict[str, ErrorLabel] = {}
        self.field_widgets: Dict[str, tk.Widget] = {}

    def register_field(self, field_name: str, field_widget: tk.Widget,
                      error_label: ErrorLabel):
        """
        Register a field and its associated error label.

        Args:
            field_name: Unique identifier for the field
            field_widget: The form field widget
            error_label: The error label widget
        """
        self.field_widgets[field_name] = field_widget
        self.error_labels[field_name] = error_label

    def show_error(self, field_name: str, message: str):
        """
        Show error message for a specific field.

        Args:
            field_name: Name of field with error
            message: Error message to display
        """
        if field_name in self.error_labels:
            self.error_labels[field_name].show_error(message)

    def hide_error(self, field_name: str):
        """
        Hide error message for a specific field.

        Args:
            field_name: Name of field to clear error for
        """
        if field_name in self.error_labels:
            self.error_labels[field_name].hide_error()

    def hide_all_errors(self):
        """Hide all error messages."""
        for error_label in self.error_labels.values():
            error_label.hide_error()

    def has_errors(self) -> bool:
        """
        Check if any field has an error message displayed.

        Returns:
            bool: True if any error messages are shown
        """
        return any(label.has_error() for label in self.error_labels.values())

    def get_error_fields(self) -> list:
        """
        Get list of field names that currently have errors.

        Returns:
            list: Names of fields with error messages
        """
        return [field_name for field_name, label in self.error_labels.items()
                if label.has_error()]

    def get_error_message(self, field_name: str) -> Optional[str]:
        """
        Get the current error message for a field.

        Args:
            field_name: Name of field

        Returns:
            Optional[str]: Error message or None if no error
        """
        if field_name in self.error_labels:
            label = self.error_labels[field_name]
            if label.has_error():
                return label.cget('text')
        return None


class ResponsiveErrorDisplay:
    """
    Helper class for creating responsive error display layouts.
    """

    @staticmethod
    def create_field_with_error(parent: tk.Widget, field_widget: tk.Widget,
                               row: int, column: int, **grid_kwargs) -> ErrorLabel:
        """
        Create a field with an associated error label in a responsive layout.

        Args:
            parent: Parent widget
            field_widget: The form field widget
            row: Grid row for the field
            column: Grid column for the field
            **grid_kwargs: Additional grid configuration

        Returns:
            ErrorLabel: The created error label
        """
        # Place the field widget
        field_widget.grid(row=row, column=column, **grid_kwargs)

        # Create and place error label directly below the field
        error_label = ErrorLabel(parent)
        error_label.grid(row=row + 1, column=column,
                        sticky='w', padx=grid_kwargs.get('padx', 0))

        return error_label

    @staticmethod
    def configure_responsive_grid(parent: tk.Widget, num_columns: int = 2):
        """
        Configure grid weights for responsive behavior.

        Args:
            parent: Parent widget to configure
            num_columns: Number of columns in the grid
        """
        # Configure column weights for responsive behavior
        for i in range(num_columns):
            parent.grid_columnconfigure(i, weight=1)

        # Configure some rows to expand with window
        # Note: Specific row configuration should be done by the calling code
        # based on the actual layout needs