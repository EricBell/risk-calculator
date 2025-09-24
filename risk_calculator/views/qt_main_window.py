"""
Qt Main Window
Main application window with tabbed interface and responsive window management.
"""

from typing import Optional, Dict, Any

try:
    from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                                   QMenuBar, QMenu, QStatusBar, QApplication)
    from PySide6.QtCore import Signal, QTimer, QSettings
    from PySide6.QtGui import QAction, QResizeEvent, QCloseEvent
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..services.qt_window_manager import QtWindowManagerService
from ..services.qt_display_service import QtDisplayService
from ..services.qt_config_service import QtConfigurationService
from ..services.application_lifecycle_service import ApplicationLifecycleService
from ..models.window_configuration import WindowConfiguration
from .qt_base_view import QtBaseView


class QtMainWindow(QMainWindow):
    """Main application window with responsive window management."""

    # Signals
    window_resized = Signal(int, int)  # width, height
    tab_changed = Signal(int)  # tab_index
    menu_action_triggered = Signal(str)  # action_name

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize Qt main window.

        Args:
            parent: Parent widget
        """
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt main window not supported")

        super().__init__(parent)

        # Services
        self.window_manager = QtWindowManagerService()
        self.display_service = QtDisplayService()
        self.config_service = QtConfigurationService()
        self.lifecycle_service = ApplicationLifecycleService()

        # UI Components
        self.tab_widget: Optional[QTabWidget] = None
        self.menu_bar: Optional[QMenuBar] = None
        self.status_bar: Optional[QStatusBar] = None

        # Tab storage
        self.tabs: Dict[str, QWidget] = {}

        # Window state
        self.is_maximized_on_startup = False

        # Initialize UI
        self.setup_window_properties()
        self.setup_menu_bar()
        self.setup_tab_widget()
        self.setup_trading_tabs()
        self.setup_status_bar()
        self.restore_window_state()

        # Setup resize handling
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self._handle_resize_complete)
        self.resize_timer.setSingleShot(True)

        # Register cleanup handlers
        self.register_cleanup_handlers()

    def setup_window_properties(self) -> None:
        """Setup basic window properties."""
        self.setWindowTitle("Risk Calculator")
        self.setObjectName("MainWindow")

        # Set minimum size
        min_width, min_height = 800, 600
        self.setMinimumSize(min_width, min_height)

        # Get recommended size from display service
        try:
            recommended_width, recommended_height = self.display_service.get_recommended_window_size()
            self.resize(recommended_width, recommended_height)
        except Exception:
            # Fallback size
            self.resize(1024, 768)

    def setup_menu_bar(self) -> None:
        """Setup application menu bar."""
        self.menu_bar = self.menuBar()

        # File menu
        file_menu = self.menu_bar.addMenu("&File")

        # Export action
        export_action = QAction("&Export Configuration...", self)
        export_action.setStatusTip("Export configuration to file")
        export_action.triggered.connect(lambda: self.menu_action_triggered.emit("export_config"))
        file_menu.addAction(export_action)

        # Import action
        import_action = QAction("&Import Configuration...", self)
        import_action.setStatusTip("Import configuration from file")
        import_action.triggered.connect(lambda: self.menu_action_triggered.emit("import_config"))
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # Reset action
        reset_action = QAction("&Reset Settings", self)
        reset_action.setStatusTip("Reset all settings to defaults")
        reset_action.triggered.connect(lambda: self.menu_action_triggered.emit("reset_settings"))
        file_menu.addAction(reset_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = self.menu_bar.addMenu("&View")

        # Reset window size action
        reset_window_action = QAction("&Reset Window Size", self)
        reset_window_action.setStatusTip("Reset window to default size")
        reset_window_action.triggered.connect(lambda: self.menu_action_triggered.emit("reset_window_size"))
        view_menu.addAction(reset_window_action)

        # Help menu
        help_menu = self.menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Risk Calculator")
        about_action.triggered.connect(lambda: self.menu_action_triggered.emit("about"))
        help_menu.addAction(about_action)

    def setup_tab_widget(self) -> None:
        """Setup central tab widget."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("MainTabWidget")
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.tab_changed.emit)

        # Set as central widget
        self.setCentralWidget(self.tab_widget)

    def setup_trading_tabs(self) -> None:
        """Setup trading tabs - tabs will be added by the main controller."""
        # Note: Tabs are now created and managed by QtMainController
        # This method is kept for compatibility but doesn't create tabs anymore
        pass

    def setup_status_bar(self) -> None:
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready", 0)

    def add_trading_tab(self, tab_name: str, tab_widget: QWidget) -> None:
        """
        Add a trading tab to the tab widget.

        Args:
            tab_name: Display name for the tab
            tab_widget: Widget to add as tab content
        """
        if not self.tab_widget:
            return

        tab_index = self.tab_widget.addTab(tab_widget, tab_name)
        self.tabs[tab_name.lower()] = tab_widget

        # If this is the first tab, select it
        if self.tab_widget.count() == 1:
            self.tab_widget.setCurrentIndex(0)

    def show_status_message(self, message: str, timeout: int = 0) -> None:
        """
        Show message in status bar.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 = permanent)
        """
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)

    def get_current_tab(self) -> str:
        """
        Get the name of the currently active tab.

        Returns:
            str: Name of current tab
        """
        if not self.tab_widget:
            return ""

        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.tabText(current_index)

        return ""

    def get_current_tab_widget(self) -> Optional[QWidget]:
        """
        Get currently selected tab widget.

        Returns:
            QWidget or None: Current tab widget
        """
        if not self.tab_widget:
            return None

        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.widget(current_index)

        return None

    def get_tab_by_name(self, tab_name: str) -> Optional[QWidget]:
        """
        Get tab widget by name.

        Args:
            tab_name: Tab name to find

        Returns:
            QWidget or None: Tab widget
        """
        return self.tabs.get(tab_name.lower())

    def save_window_state(self) -> bool:
        """
        Save current window state to configuration.

        Returns:
            bool: True if saved successfully
        """
        try:
            # Create window configuration
            geometry = self.geometry()
            config = WindowConfiguration(
                width=geometry.width(),
                height=geometry.height(),
                x=geometry.x(),
                y=geometry.y(),
                maximized=self.isMaximized()
            )

            # Save using window manager
            success = self.window_manager.save_window_configuration(config)

            if success:
                self.show_status_message("Window state saved", 2000)
            else:
                self.show_status_message("Failed to save window state", 3000)

            return success

        except Exception:
            self.show_status_message("Error saving window state", 3000)
            return False

    def restore_window_state(self) -> bool:
        """
        Restore window state from configuration.

        Returns:
            bool: True if restored successfully
        """
        try:
            # Load configuration
            config = self.window_manager.load_window_configuration()

            if not config:
                # No saved configuration, use defaults
                self.show_status_message("Using default window size", 2000)
                return False

            # Validate bounds
            validated_config = self.window_manager.validate_window_bounds(config)

            # Apply configuration
            if validated_config.maximized:
                self.showMaximized()
                self.is_maximized_on_startup = True
            else:
                self.setGeometry(
                    validated_config.x,
                    validated_config.y,
                    validated_config.width,
                    validated_config.height
                )

            self.show_status_message("Window state restored", 2000)
            return True

        except Exception:
            self.show_status_message("Error restoring window state", 3000)
            return False

    def reset_to_default_size(self) -> None:
        """Reset window to default size for current display."""
        try:
            default_width, default_height = self.display_service.get_recommended_window_size()

            # Center on screen
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            x = (screen_geometry.width() - default_width) // 2
            y = (screen_geometry.height() - default_height) // 2

            self.setGeometry(x, y, default_width, default_height)
            self.show_status_message(f"Reset to default size: {default_width}x{default_height}", 3000)

        except Exception:
            # Fallback
            self.resize(1024, 768)
            self.show_status_message("Reset to fallback size: 1024x768", 3000)

    def get_display_info(self) -> Dict[str, Any]:
        """
        Get current display information.

        Returns:
            Dict[str, Any]: Display information
        """
        try:
            return self.display_service.get_display_summary()
        except Exception:
            return {"error": "Could not retrieve display information"}

    def export_all_configuration(self, file_path: str) -> bool:
        """
        Export all configuration to file.

        Args:
            file_path: Path to export file

        Returns:
            bool: True if exported successfully
        """
        try:
            # Save current window state first
            self.save_window_state()

            # Export using config service
            success = self.config_service.export_configuration(file_path)

            if success:
                self.show_status_message(f"Configuration exported to {file_path}", 3000)
            else:
                self.show_status_message("Failed to export configuration", 3000)

            return success

        except Exception:
            self.show_status_message("Error exporting configuration", 3000)
            return False

    def clear_all_configuration(self) -> bool:
        """
        Clear all saved configuration.

        Returns:
            bool: True if cleared successfully
        """
        try:
            success = self.config_service.clear_all_configuration()

            if success:
                self.show_status_message("All configuration cleared", 3000)
            else:
                self.show_status_message("Failed to clear configuration", 3000)

            return success

        except Exception:
            self.show_status_message("Error clearing configuration", 3000)
            return False

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handle window resize events.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        # Emit signal for responsive components
        new_size = event.size()
        self.window_resized.emit(new_size.width(), new_size.height())

        # Debounce resize handling to avoid excessive saves
        self.resize_timer.start(500)  # 500ms delay

    def register_cleanup_handlers(self) -> None:
        """Register cleanup handlers with the lifecycle service."""
        # Register main window cleanup
        self.lifecycle_service.register_cleanup_handler(self._cleanup_main_window)

        # Register tab cleanup
        self.lifecycle_service.register_cleanup_handler(self._cleanup_tabs)

        # Register window state cleanup
        self.lifecycle_service.register_cleanup_handler(self._cleanup_window_state)

    def _cleanup_main_window(self) -> None:
        """Cleanup main window resources."""
        try:
            # Stop any running timers
            if hasattr(self, 'resize_timer') and self.resize_timer:
                self.resize_timer.stop()

            # Close all dialogs
            for child in self.findChildren(QWidget):
                if child.isWindow() and child != self:
                    child.close()

        except Exception as e:
            print(f"Error during main window cleanup: {e}")

    def _cleanup_tabs(self) -> None:
        """Cleanup tab widgets and save form data."""
        try:
            # Save form data from all tabs
            for tab_name, tab_widget in self.tabs.items():
                if hasattr(tab_widget, 'get_form_data'):
                    form_data = tab_widget.get_form_data()
                    self.config_service.save_form_data(tab_name, form_data)

                # Clear validation timers in tabs
                if hasattr(tab_widget, 'validation_timer'):
                    tab_widget.validation_timer.stop()

        except Exception as e:
            print(f"Error during tabs cleanup: {e}")

    def _cleanup_window_state(self) -> None:
        """Cleanup and save window state."""
        try:
            self.save_window_state()
        except Exception as e:
            print(f"Error saving window state during cleanup: {e}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Args:
            event: Close event
        """
        try:
            # Trigger lifecycle cleanup
            self.lifecycle_service.force_cleanup()

            # Accept the close event
            event.accept()

        except Exception as e:
            print(f"Error during window close: {e}")
            # Force accept the event to ensure window closes
            event.accept()

    def _handle_resize_complete(self) -> None:
        """Handle completion of window resize (debounced)."""
        # Only save if not maximized and not during startup
        if not self.isMaximized() and not self.is_maximized_on_startup:
            self.save_window_state()

        # Clear startup flag after first resize
        self.is_maximized_on_startup = False

    def set_window_title(self, title: str) -> None:
        """
        Set the window title.

        Args:
            title: New window title
        """
        self.setWindowTitle(title)


    def set_current_tab(self, tab_name: str) -> None:
        """
        Set the currently active tab.

        Args:
            tab_name: Name of tab to activate
        """
        if not self.tab_widget:
            return

        # Find tab by name
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i).lower() == tab_name.lower():
                self.tab_widget.setCurrentIndex(i)
                break

    def enable_menu_items(self, items: Dict[str, bool]) -> None:
        """
        Enable/disable menu items.

        Args:
            items: Dict mapping menu item names to enabled state
        """
        if not self.menu_bar:
            return

        # Find and enable/disable menu actions
        for action in self.findChildren(QAction):
            action_name = action.text().replace("&", "").lower()
            if action_name in items:
                action.setEnabled(items[action_name])

    def show_about_dialog(self) -> None:
        """Show the about dialog"""
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.about(
                self,
                "About Risk Calculator",
                "Risk Calculator v1.0\n\nA professional risk calculation tool for day trading.\n\nBuilt with Qt6 and Python."
            )
        except Exception:
            self.show_status_message("Could not show about dialog", 3000)

    def close_application(self) -> None:
        """Close the application"""
        QApplication.quit()

    def setup_ui(self) -> None:
        """Setup UI components (already called in __init__)."""
        # This method exists for interface compatibility
        # Actual UI setup is done in __init__ via individual setup methods
        pass

    def center_on_screen(self) -> None:
        """Center the window on the screen."""
        try:
            from PySide6.QtGui import QScreen
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                window_geometry = self.geometry()

                # Calculate center position
                x = (screen_geometry.width() - window_geometry.width()) // 2
                y = (screen_geometry.height() - window_geometry.height()) // 2

                # Move window to center
                self.move(x, y)
        except Exception:
            # Fallback - move to a reasonable position
            self.move(100, 100)