"""
Qt Application Bootstrap with High-DPI Scaling Support
Entry point for the Qt-based risk calculator application.
"""

import sys
import os
import signal
from typing import Optional

# Add parent directory to path for direct execution
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

try:
    from .services.application_lifecycle_service import ApplicationLifecycleService
except ImportError:
    # Handle direct execution
    from risk_calculator.services.application_lifecycle_service import ApplicationLifecycleService


class RiskCalculatorQtApp:
    """Main Qt application class with high-DPI scaling support."""

    def __init__(self):
        """Initialize Qt application with proper high-DPI scaling."""
        self.app: Optional[QApplication] = None
        self.main_window = None
        self.lifecycle_service = ApplicationLifecycleService()
        self._cleanup_timer = None

    def setup_high_dpi_scaling(self) -> None:
        """Configure high-DPI scaling before QApplication creation."""
        # Note: AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt 6.x
        # High-DPI scaling is now enabled by default, but we'll keep this for compatibility

        # Enable high-DPI scaling (deprecated but kept for Qt 5.x compatibility)
        try:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        except AttributeError:
            pass  # Not available in newer Qt versions

        # Use high-DPI pixmaps (deprecated but kept for Qt 5.x compatibility)
        try:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            pass  # Not available in newer Qt versions

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

            # Setup application lifecycle handlers
            self._setup_lifecycle_handlers()

        return self.app

    def _set_application_icon(self) -> None:
        """Set application icon if icon file exists."""
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

    def _setup_lifecycle_handlers(self) -> None:
        """Setup application lifecycle handlers for graceful shutdown."""
        # Register startup handlers
        self.lifecycle_service.register_startup_handler(self._on_application_startup)

        # Register shutdown handlers
        self.lifecycle_service.register_shutdown_handler(self._on_application_shutdown)

        # Setup signal handlers for graceful termination
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Connect Qt aboutToQuit signal
        self.app.aboutToQuit.connect(self._on_about_to_quit)

    def _on_application_startup(self) -> None:
        """Handle application startup tasks."""
        print("Risk Calculator application starting...")

    def _on_application_shutdown(self) -> None:
        """Handle application shutdown cleanup."""
        print("Risk Calculator application shutting down...")

        # Save any pending data
        if self.main_window and hasattr(self.main_window, 'save_window_state'):
            self.main_window.save_window_state()

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        print(f"Received signal {signum}, initiating graceful shutdown...")
        QTimer.singleShot(0, self.quit)

    def _on_about_to_quit(self):
        """Handle Qt aboutToQuit signal."""
        # Perform cleanup tasks
        self.lifecycle_service.shutdown_application()

    def create_main_window(self):
        """Create and configure the main window."""
        # Import here to avoid circular imports
        try:
            from .controllers.qt_main_controller import QtMainController
        except ImportError:
            from risk_calculator.controllers.qt_main_controller import QtMainController

        if self.main_window is None:
            # Create controller and let it create the main window
            self.controller = QtMainController()

            # Connect to error signal to see actual error
            def on_error(title, message):
                print(f"Controller Error - {title}: {message}")

            self.controller.error_occurred.connect(on_error)

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

            # Initialize lifecycle service
            self.lifecycle_service.initialize_application()

            # Create main window (controller handles showing it)
            main_window = self.create_main_window()

            # Center window on screen
            main_window.center_on_screen()

            # Run application event loop
            exit_code = app.exec()

            # Ensure cleanup happens
            self.quit()
            return exit_code

        except Exception as e:
            print(f"Error starting Qt application: {e}")
            # Ensure cleanup happens even on error
            self.quit()
            return 1

    def quit(self) -> None:
        """Quit the application gracefully."""
        try:
            # Trigger cleanup timer for delayed shutdown
            if not self._cleanup_timer:
                self._cleanup_timer = QTimer()
                self._cleanup_timer.setSingleShot(True)
                self._cleanup_timer.timeout.connect(self._force_quit)

            # Start cleanup timer (2 second timeout)
            self._cleanup_timer.start(2000)

            # Initiate graceful shutdown
            if self.app:
                # Close main window to trigger closeEvent
                if self.main_window:
                    self.main_window.close()

                # Quit Qt application
                self.app.quit()

        except Exception as e:
            print(f"Error during application shutdown: {e}")
            self._force_quit()

    def _force_quit(self) -> None:
        """Force application termination if graceful shutdown fails."""
        print("Forcing application termination...")
        try:
            if self.app:
                self.app.quit()
        except:
            pass

        # Force system exit as last resort
        import os
        os._exit(0)


def main() -> int:
    """Main entry point for Qt application."""
    qt_app = RiskCalculatorQtApp()
    return qt_app.run()


if __name__ == "__main__":
    sys.exit(main())