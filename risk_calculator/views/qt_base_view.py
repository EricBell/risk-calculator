"""
Base Qt View Component
Provides common functionality for all Qt-based views in the application.
"""

from typing import Dict, Any, Optional, Callable
from abc import ABCMeta, abstractmethod

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                   QLabel, QLineEdit, QPushButton, QFrame)
    from PySide6.QtCore import Signal, QObject
    from PySide6.QtGui import QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..services.qt_layout_service import QtResponsiveLayoutService
from ..models.ui_layout_state import UILayoutState


class QtBaseViewMeta(type(QWidget), ABCMeta):
    """Metaclass that combines Qt's metaclass with ABCMeta to resolve conflicts."""
    pass


class QtBaseView(QWidget, metaclass=QtBaseViewMeta):
    """Base class for all Qt views with responsive layout support."""

    # Signals for field changes and form events
    field_changed = Signal(str, str)  # field_name, new_value
    calculate_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize base Qt view.

        Args:
            parent: Parent widget
        """
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt views not supported")

        super().__init__(parent)

        # Services
        self.layout_service = QtResponsiveLayoutService()

        # Form state
        self.form_fields: Dict[str, QLineEdit] = {}
        self.error_labels: Dict[str, QLabel] = {}
        self.field_change_callback: Optional[Callable[[str, str], None]] = None
        self.calculate_callback: Optional[Callable[[], None]] = None

        # Layout
        self.main_layout: Optional[QVBoxLayout] = None
        self.calculate_button: Optional[QPushButton] = None

        # Initialize UI
        self.setup_ui()
        self.connect_signals()

    @abstractmethod
    def setup_ui(self) -> None:
        """Setup the UI components. Must be implemented by subclasses."""
        pass

    def connect_signals(self) -> None:
        """Connect Qt signals to appropriate handlers."""
        # Connect field change signal to callback
        self.field_changed.connect(self._on_field_changed)
        self.calculate_requested.connect(self._on_calculate_requested)

    def create_main_layout(self) -> QVBoxLayout:
        """
        Create and set main layout for the widget.

        Returns:
            QVBoxLayout: Main layout
        """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(self.layout_service.get_scaled_spacing(10))
        self.main_layout.setContentsMargins(
            self.layout_service.get_scaled_spacing(15),
            self.layout_service.get_scaled_spacing(15),
            self.layout_service.get_scaled_spacing(15),
            self.layout_service.get_scaled_spacing(15)
        )
        return self.main_layout

    def create_form_field(self, field_name: str, label_text: str,
                         placeholder: str = "", required: bool = False) -> tuple[QLabel, QLineEdit]:
        """
        Create a form field with label and input.

        Args:
            field_name: Internal field name
            label_text: Display label text
            placeholder: Placeholder text
            required: Whether field is required

        Returns:
            tuple[QLabel, QLineEdit]: Label and input widgets
        """
        # Create label
        label = QLabel(label_text)
        if required:
            label.setText(f"{label_text} *")

        # Apply responsive font scaling
        self.layout_service.apply_responsive_font_scaling(label, 10)

        # Create input field
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setObjectName(field_name)

        # Apply responsive scaling
        self.layout_service.set_minimum_size(input_field, 120, 25)
        self.layout_service.apply_responsive_font_scaling(input_field, 10)

        # Connect text changed signal
        input_field.textChanged.connect(
            lambda text, name=field_name: self.field_changed.emit(name, text)
        )

        # Store reference
        self.form_fields[field_name] = input_field

        return label, input_field

    def create_error_label(self, field_name: str) -> QLabel:
        """
        Create error label for a form field.

        Args:
            field_name: Associated field name

        Returns:
            QLabel: Error label widget
        """
        error_label = QLabel("")
        error_label.setObjectName(f"{field_name}_error")
        error_label.setStyleSheet("color: red; font-size: 9pt;")
        error_label.hide()  # Initially hidden

        # Apply responsive font scaling
        self.layout_service.apply_responsive_font_scaling(error_label, 9)

        # Store reference
        self.error_labels[field_name] = error_label

        return error_label

    def create_calculate_button(self, text: str = "Calculate Position") -> QPushButton:
        """
        Create calculate button with responsive styling.

        Args:
            text: Button text

        Returns:
            QPushButton: Calculate button
        """
        button = QPushButton(text)
        button.setObjectName("calculate_button")
        button.setEnabled(False)  # Initially disabled

        # Apply responsive sizing
        self.layout_service.set_minimum_size(button, 150, 35)
        self.layout_service.apply_responsive_font_scaling(button, 11)

        # Connect click signal
        button.clicked.connect(lambda: self.calculate_requested.emit())

        self.calculate_button = button
        return button

    def create_section_frame(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """
        Create a section frame with title and layout.

        Args:
            title: Section title

        Returns:
            tuple[QFrame, QVBoxLayout]: Frame and its layout
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setLineWidth(1)

        layout = QVBoxLayout(frame)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        # Add title label
        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.layout_service.apply_responsive_font_scaling(title_label, 12)

        layout.addWidget(title_label)

        return frame, layout

    def get_form_data(self) -> Dict[str, str]:
        """
        Get current form data.

        Returns:
            Dict[str, str]: Field names to values
        """
        return {name: field.text() for name, field in self.form_fields.items()}

    def set_field_value(self, field_name: str, value: str) -> None:
        """
        Set value for a specific field.

        Args:
            field_name: Field to update
            value: New value
        """
        if field_name in self.form_fields:
            field = self.form_fields[field_name]
            # Temporarily block signals to avoid triggering change events
            field.blockSignals(True)
            field.setText(value)
            field.blockSignals(False)

    def show_field_error(self, field_name: str, error_message: str) -> None:
        """
        Show error message for a field.

        Args:
            field_name: Field with error
            error_message: Error message to display
        """
        if field_name in self.error_labels:
            error_label = self.error_labels[field_name]
            error_label.setText(error_message)
            error_label.show()

        # Also style the input field
        if field_name in self.form_fields:
            field = self.form_fields[field_name]
            field.setStyleSheet("border: 1px solid red;")

    def hide_field_error(self, field_name: str) -> None:
        """
        Hide error message for a field.

        Args:
            field_name: Field to clear error
        """
        if field_name in self.error_labels:
            error_label = self.error_labels[field_name]
            error_label.hide()

        # Reset input field styling
        if field_name in self.form_fields:
            field = self.form_fields[field_name]
            field.setStyleSheet("")

    def set_calculate_button_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the calculate button.

        Args:
            enabled: Whether button should be enabled
        """
        if self.calculate_button:
            self.calculate_button.setEnabled(enabled)

    def register_field_change_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Register callback for field changes.

        Args:
            callback: Callback function (field_name, new_value) -> None
        """
        self.field_change_callback = callback

    def register_calculate_callback(self, callback: Callable[[], None]) -> None:
        """
        Register callback for calculate button clicks.

        Args:
            callback: Callback function () -> None
        """
        self.calculate_callback = callback

    def apply_responsive_scaling(self, base_width: int = 1024, base_height: int = 768) -> None:
        """
        Apply responsive scaling to the entire view.

        Args:
            base_width: Base design width
            base_height: Base design height
        """
        current_size = self.size()
        self.layout_service.initialize_layout_state(
            base_width=base_width,
            base_height=base_height,
            current_width=current_size.width(),
            current_height=current_size.height()
        )

        # Apply scaling to all widgets recursively
        self._apply_scaling_recursive(self)

    def _apply_scaling_recursive(self, widget: QWidget) -> None:
        """
        Recursively apply scaling to widget and its children.

        Args:
            widget: Widget to scale
        """
        # Apply font scaling
        self.layout_service.apply_responsive_font_scaling(widget)

        # Apply to child widgets
        for child in widget.findChildren(QWidget):
            if child.parent() == widget:  # Direct children only
                self._apply_scaling_recursive(child)

    def _on_field_changed(self, field_name: str, new_value: str) -> None:
        """
        Handle field change signal.

        Args:
            field_name: Changed field name
            new_value: New field value
        """
        if self.field_change_callback:
            self.field_change_callback(field_name, new_value)

    def _on_calculate_requested(self) -> None:
        """Handle calculate button clicked signal."""
        if self.calculate_callback:
            self.calculate_callback()

    def resizeEvent(self, event) -> None:
        """Handle widget resize events for responsive scaling."""
        super().resizeEvent(event)

        # Update layout state with new size
        new_size = event.size()
        if hasattr(self.layout_service, '_layout_state') and self.layout_service._layout_state:
            self.layout_service.update_layout_state(new_size.width(), new_size.height())

            # Reapply scaling
            self._apply_scaling_recursive(self)