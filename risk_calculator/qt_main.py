"""
Qt Application Bootstrap with High-DPI Scaling Support
Entry point for the Qt-based risk calculator application.
"""

import sys
import os
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class RiskCalculatorQtApp:
    """Main Qt application class with high-DPI scaling support."""

    def __init__(self):
        """Initialize Qt application with proper high-DPI scaling."""
        self.app: Optional[QApplication] = None
        self.main_window = None

    def setup_high_dpi_scaling(self) -> None:
        """Configure high-DPI scaling before QApplication creation."""
        # Enable high-DPI scaling
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

        # Use high-DPI pixmaps
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        # Set high-DPI scale factor rounding policy
        if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

    def create_application(self) -> QApplication:
        """Create and configure the Qt application."""
        if self.app is None:
            # Setup high-DPI scaling before creating QApplication
            self.setup_high_dpi_scaling()

            # Create QApplication
            self.app = QApplication(sys.argv)

            # Set application properties
            self.app.setApplicationName("Risk Calculator")
            self.app.setApplicationVersion("2.0.0")
            self.app.setOrganizationName("Risk Calculator")
            self.app.setOrganizationDomain("riskcalculator.local")

            # Set application icon if available
            self._set_application_icon()

        return self.app

    def _set_application_icon(self) -> None:
        """Set application icon if icon file exists."""
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

    def create_main_window(self):
        """Create and configure the main window."""
        # Import here to avoid circular imports
        from risk_calculator.controllers.qt_main_controller import QtMainController

        if self.main_window is None:
            # Create controller and let it create the main window
            self.controller = QtMainController()

            # Initialize the full application through the controller
            if self.controller.initialize_application():
                self.main_window = self.controller.main_window
            else:
                raise RuntimeError("Failed to initialize Qt application")

        return self.main_window

    def run(self) -> int:
        """Run the Qt application."""
        try:
            # Create application
            app = self.create_application()

            # Create main window (controller handles showing it)
            main_window = self.create_main_window()

            # Center window on screen
            main_window.center_on_screen()

            # Run application event loop
            return app.exec()

        except Exception as e:
            print(f"Error starting Qt application: {e}")
            return 1

    def quit(self) -> None:
        """Quit the application gracefully."""
        if self.app:
            self.app.quit()


def main() -> int:
    """Main entry point for Qt application."""
    qt_app = RiskCalculatorQtApp()
    return qt_app.run()


if __name__ == "__main__":
    sys.exit(main())