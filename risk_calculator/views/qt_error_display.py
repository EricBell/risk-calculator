"""
Qt Error Display Components
Provides consistent error display widgets and utilities for Qt views.
"""

from typing import Optional, Dict, List, Any
from enum import Enum

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame, QScrollArea, QDialog)
    from PySide6.QtCore import Signal, Qt, QTimer
    from PySide6.QtGui import QPixmap, QIcon
    HAS_QT = True
except ImportError:
    HAS_QT = False


class ErrorSeverity(Enum):
    """Error severity levels for display styling."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QtErrorLabel(QLabel):
    """Enhanced error label with severity styling and auto-hide functionality."""

    def __init__(self, field_name: str = "", parent: Optional[QWidget] = None):
        """
        Initialize Qt error label.

        Args:
            field_name: Associated field name
            parent: Parent widget
        """
        super().__init__(parent)

        self.field_name = field_name
        self.severity = ErrorSeverity.ERROR
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self.hide)
        self.auto_hide_timer.setSingleShot(True)

        self._setup_styling()

    def _setup_styling(self) -> None:
        """Setup default error label styling."""
        self.setWordWrap(True)
        self.hide()  # Initially hidden
        self._update_style()

    def _update_style(self) -> None:
        """Update styling based on severity level."""
        styles = {
            ErrorSeverity.INFO: "color: #2196F3; font-size: 9pt; font-weight: normal;",
            ErrorSeverity.WARNING: "color: #FF9800; font-size: 9pt; font-weight: bold;",
            ErrorSeverity.ERROR: "color: #F44336; font-size: 9pt; font-weight: bold;",
            ErrorSeverity.CRITICAL: "color: #D32F2F; font-size: 9pt; font-weight: bold; background-color: #FFEBEE; padding: 2px;"
        }

        self.setStyleSheet(styles.get(self.severity, styles[ErrorSeverity.ERROR]))

    def show_error(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
                   auto_hide_ms: int = 0) -> None:
        """
        Show error message with specified severity.

        Args:
            message: Error message to display
            severity: Error severity level
            auto_hide_ms: Auto-hide timeout in milliseconds (0 = no auto-hide)
        """
        self.severity = severity
        self._update_style()

        # Add severity prefix if not INFO
        if severity != ErrorSeverity.INFO:
            prefix_map = {
                ErrorSeverity.WARNING: "⚠️ ",
                ErrorSeverity.ERROR: "❌ ",
                ErrorSeverity.CRITICAL: "🔴 "
            }
            message = prefix_map.get(severity, "") + message
        else:
            message = "ℹ️ " + message

        self.setText(message)
        self.show()

        # Setup auto-hide if specified
        if auto_hide_ms > 0:
            self.auto_hide_timer.start(auto_hide_ms)

    def hide_error(self) -> None:
        """Hide the error message."""
        self.auto_hide_timer.stop()
        self.hide()


class QtErrorPanel(QFrame):
    """Collapsible error panel for displaying multiple errors."""

    errors_cleared = Signal()

    def __init__(self, title: str = "Errors", parent: Optional[QWidget] = None):
        """
        Initialize Qt error panel.

        Args:
            title: Panel title
            parent: Parent widget
        """
        super().__init__(parent)

        self.title = title
        self.errors: Dict[str, Dict[str, Any]] = {}

        self._setup_ui()
        self._setup_styling()

    def _setup_ui(self) -> None:
        """Setup error panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Header with title and clear button
        header_layout = QHBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setStyleSheet("font-size: 9pt; padding: 2px 8px;")
        self.clear_button.clicked.connect(self.clear_all_errors)
        header_layout.addWidget(self.clear_button)

        layout.addLayout(header_layout)

        # Scrollable error content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(3)

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

        # Initially hidden
        self.hide()

    def _setup_styling(self) -> None:
        """Setup panel styling."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #F44336;
                background-color: #FFEBEE;
                border-radius: 4px;
                padding: 5px;
            }
        """)

    def add_error(self, error_id: str, message: str,
                  severity: ErrorSeverity = ErrorSeverity.ERROR,
                  field_name: str = "") -> None:
        """
        Add or update an error in the panel.

        Args:
            error_id: Unique identifier for the error
            message: Error message
            severity: Error severity level
            field_name: Associated field name
        """
        # Remove existing error if present
        if error_id in self.errors:
            self.remove_error(error_id)

        # Create error display widget
        error_widget = QWidget()
        error_layout = QHBoxLayout(error_widget)
        error_layout.setContentsMargins(5, 2, 5, 2)

        # Error message label
        error_label = QLabel(message)
        error_label.setWordWrap(True)

        # Style based on severity
        styles = {
            ErrorSeverity.INFO: "color: #2196F3;",
            ErrorSeverity.WARNING: "color: #FF9800; font-weight: bold;",
            ErrorSeverity.ERROR: "color: #F44336; font-weight: bold;",
            ErrorSeverity.CRITICAL: "color: #D32F2F; font-weight: bold;"
        }
        error_label.setStyleSheet(f"font-size: 10pt; {styles.get(severity, styles[ErrorSeverity.ERROR])}")

        error_layout.addWidget(error_label)

        # Individual remove button
        remove_button = QPushButton("×")
        remove_button.setFixedSize(20, 20)
        remove_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #999;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                color: #F44336;
                background-color: #FFEBEE;
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_error(error_id))
        error_layout.addWidget(remove_button)

        # Add to layout
        self.content_layout.addWidget(error_widget)

        # Store error info
        self.errors[error_id] = {
            "widget": error_widget,
            "message": message,
            "severity": severity,
            "field_name": field_name
        }

        # Update panel visibility and title
        self._update_panel()

    def remove_error(self, error_id: str) -> None:
        """
        Remove an error from the panel.

        Args:
            error_id: Error identifier to remove
        """
        if error_id in self.errors:
            error_info = self.errors[error_id]
            widget = error_info["widget"]

            # Remove widget from layout and delete it
            self.content_layout.removeWidget(widget)
            widget.deleteLater()

            # Remove from errors dict
            del self.errors[error_id]

            # Update panel
            self._update_panel()

    def clear_all_errors(self) -> None:
        """Clear all errors from the panel."""
        error_ids = list(self.errors.keys())
        for error_id in error_ids:
            self.remove_error(error_id)

        self.errors_cleared.emit()

    def has_errors(self) -> bool:
        """
        Check if panel has any errors.

        Returns:
            bool: True if panel has errors
        """
        return len(self.errors) > 0

    def get_error_count(self) -> int:
        """
        Get number of errors in panel.

        Returns:
            int: Error count
        """
        return len(self.errors)

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Dict[str, Any]]:
        """
        Get errors filtered by severity.

        Args:
            severity: Severity level to filter by

        Returns:
            List[Dict[str, Any]]: Matching errors
        """
        return [error for error in self.errors.values()
                if error["severity"] == severity]

    def _update_panel(self) -> None:
        """Update panel visibility and title based on error count."""
        error_count = self.get_error_count()

        if error_count == 0:
            self.hide()
        else:
            # Update title with count
            self.title_label.setText(f"{self.title} ({error_count})")
            self.show()


class QtErrorDialog(QDialog):
    """Modal dialog for displaying detailed error information."""

    def __init__(self, title: str = "Error Details", parent: Optional[QWidget] = None):
        """
        Initialize Qt error dialog.

        Args:
            title: Dialog title
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 400)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup error dialog UI."""
        layout = QVBoxLayout(self)

        # Error content area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.content_area.setWidget(self.content_widget)
        layout.addWidget(self.content_area)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def show_error_details(self, errors: List[Dict[str, Any]]) -> None:
        """
        Show detailed error information.

        Args:
            errors: List of error dictionaries
        """
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        # Add error details
        for i, error in enumerate(errors):
            error_frame = QFrame()
            error_frame.setFrameStyle(QFrame.Shape.Box)
            error_frame.setStyleSheet("padding: 10px; margin: 5px; background-color: #F5F5F5;")

            error_layout = QVBoxLayout(error_frame)

            # Error title
            title_label = QLabel(f"Error {i+1}: {error.get('field_name', 'General')}")
            title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            error_layout.addWidget(title_label)

            # Error message
            message_label = QLabel(error.get('message', 'No message'))
            message_label.setWordWrap(True)
            message_label.setStyleSheet("font-size: 11pt; margin: 5px 0px;")
            error_layout.addWidget(message_label)

            # Severity info
            severity = error.get('severity', ErrorSeverity.ERROR)
            severity_label = QLabel(f"Severity: {severity.value.upper()}")
            severity_styles = {
                ErrorSeverity.INFO: "color: #2196F3;",
                ErrorSeverity.WARNING: "color: #FF9800;",
                ErrorSeverity.ERROR: "color: #F44336;",
                ErrorSeverity.CRITICAL: "color: #D32F2F; font-weight: bold;"
            }
            severity_label.setStyleSheet(f"font-size: 10pt; {severity_styles.get(severity, '')}")
            error_layout.addWidget(severity_label)

            self.content_layout.addWidget(error_frame)

        # Add stretch to push content to top
        self.content_layout.addStretch()

    @staticmethod
    def show_errors(errors: List[Dict[str, Any]],
                   title: str = "Error Details",
                   parent: Optional[QWidget] = None) -> None:
        """
        Static method to show errors in a dialog.

        Args:
            errors: List of error dictionaries
            title: Dialog title
            parent: Parent widget
        """
        if not HAS_QT:
            return

        dialog = QtErrorDialog(title, parent)
        dialog.show_error_details(errors)
        dialog.exec()


class QtStatusIndicator(QLabel):
    """Status indicator widget for showing current validation state."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize Qt status indicator.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setFixedSize(16, 16)
        self._set_status("unknown")

    def _set_status(self, status: str) -> None:
        """
        Set status indicator appearance.

        Args:
            status: Status type ("valid", "invalid", "unknown", "pending")
        """
        status_styles = {
            "valid": "background-color: #4CAF50; border-radius: 8px;",
            "invalid": "background-color: #F44336; border-radius: 8px;",
            "unknown": "background-color: #9E9E9E; border-radius: 8px;",
            "pending": "background-color: #FF9800; border-radius: 8px;"
        }

        self.setStyleSheet(status_styles.get(status, status_styles["unknown"]))

        # Set tooltip
        tooltip_map = {
            "valid": "Field is valid",
            "invalid": "Field has errors",
            "unknown": "Field not validated",
            "pending": "Validation in progress"
        }
        self.setToolTip(tooltip_map.get(status, "Unknown status"))

    def set_valid(self) -> None:
        """Set indicator to valid state."""
        self._set_status("valid")

    def set_invalid(self) -> None:
        """Set indicator to invalid state."""
        self._set_status("invalid")

    def set_unknown(self) -> None:
        """Set indicator to unknown state."""
        self._set_status("unknown")

    def set_pending(self) -> None:
        """Set indicator to pending state."""
        self._set_status("pending")