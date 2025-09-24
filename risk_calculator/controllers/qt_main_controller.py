"""Qt Main Controller integration - orchestrates the entire Qt application."""

from typing import Dict, Any, Optional

try:
    from PySide6.QtCore import QObject, Signal, Slot
    from PySide6.QtWidgets import QMessageBox, QFileDialog
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..views.qt_main_window import QtMainWindow
from ..views.qt_equity_tab import QtEquityTab
from ..views.qt_options_tab import QtOptionsTab
from ..views.qt_futures_tab import QtFuturesTab

from .qt_equity_controller import QtEquityController
from .qt_options_controller import QtOptionsController
from .qt_futures_controller import QtFuturesController

from ..services.qt_window_manager import QtWindowManagerService
from ..services.qt_display_service import QtDisplayService
from ..services.qt_config_service import QtConfigurationService
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService


class QtMainController(QObject):
    """Main Qt controller that orchestrates the entire application."""

    # Application-level signals
    application_closing = Signal()
    error_occurred = Signal(str, str)  # title, message
    status_message = Signal(str, int)  # message, timeout

    def __init__(self):
        """Initialize Qt main controller."""
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt main controller not supported")

        super().__init__()

        # Initialize services
        self.window_manager = QtWindowManagerService()
        self.display_service = QtDisplayService()
        self.config_service = QtConfigurationService()
        self.risk_calculator = RiskCalculationService()
        self.trade_validator = TradeValidationService()

        # Initialize UI components
        self.main_window: Optional[QtMainWindow] = None
        self.tab_controllers: Dict[str, Any] = {}

        # Application state
        self.current_tab = "equity"
        self.is_initialized = False

    def initialize_application(self) -> bool:
        """
        Initialize the Qt application components.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Create main window
            self.main_window = QtMainWindow()

            # Setup main window connections
            self._setup_main_window_connections()

            # Create and setup tabs
            self._create_trading_tabs()

            # Setup application-level connections
            self._setup_application_connections()

            # Show main window
            self.main_window.show()

            # Emit status message
            self.status_message.emit("Risk Calculator Qt initialized successfully", 3000)

            self.is_initialized = True
            return True

        except Exception as e:
            self.error_occurred.emit("Initialization Error",
                                   f"Failed to initialize Qt application: {str(e)}")
            return False

    def _setup_main_window_connections(self) -> None:
        """Setup main window signal connections."""
        if not self.main_window:
            return

        # Connect window signals to controller methods
        self.main_window.window_resized.connect(self._on_window_resized)
        self.main_window.tab_changed.connect(self._on_tab_changed)
        self.main_window.menu_action_triggered.connect(self._on_menu_action)

        # Connect status messages
        self.status_message.connect(self.main_window.show_status_message)

        # Connect error handling
        self.error_occurred.connect(self._show_error_dialog)

    def _create_trading_tabs(self) -> None:
        """Create and setup all trading tabs with their controllers."""
        if not self.main_window:
            return

        # Create Equity tab
        equity_view = QtEquityTab()
        equity_controller = QtEquityController(
            equity_view,
            self.risk_calculator,
            self.trade_validator
        )
        self._setup_tab_controller_connections(equity_controller, "equity")

        self.main_window.add_trading_tab("Equity", equity_view)
        self.tab_controllers["equity"] = equity_controller

        # Create Options tab
        options_view = QtOptionsTab()
        options_controller = QtOptionsController(
            options_view,
            self.risk_calculator,
            self.trade_validator
        )
        self._setup_tab_controller_connections(options_controller, "options")

        self.main_window.add_trading_tab("Options", options_view)
        self.tab_controllers["options"] = options_controller

        # Create Futures tab
        futures_view = QtFuturesTab()
        futures_controller = QtFuturesController(
            futures_view,
            self.risk_calculator,
            self.trade_validator
        )
        self._setup_tab_controller_connections(futures_controller, "futures")

        self.main_window.add_trading_tab("Futures", futures_view)
        self.tab_controllers["futures"] = futures_controller

        # Load saved form data
        self._restore_form_data()

    def _setup_tab_controller_connections(self, controller: Any, tab_name: str) -> None:
        """
        Setup connections for a tab controller.

        Args:
            controller: Tab controller instance
            tab_name: Name of the tab
        """
        # Connect controller signals
        controller.validation_changed.connect(
            lambda has_errors, name=tab_name: self._on_validation_changed(name, has_errors)
        )

        controller.calculation_completed.connect(
            lambda result, name=tab_name: self._on_calculation_completed(name, result)
        )

        controller.error_occurred.connect(
            lambda error, name=tab_name: self._on_controller_error(name, error)
        )

        controller.busy_state_changed.connect(
            lambda busy, name=tab_name: self._on_busy_state_changed(name, busy)
        )

    def _setup_application_connections(self) -> None:
        """Setup application-level signal connections."""
        # Connect application closing signal
        if self.main_window:
            # Qt's closeEvent is handled in the main window itself
            pass

    @Slot(int, int)
    def _on_window_resized(self, width: int, height: int) -> None:
        """
        Handle window resize events.

        Args:
            width: New window width
            height: New window height
        """
        # Apply responsive scaling to all tabs
        for controller in self.tab_controllers.values():
            if hasattr(controller.view, 'apply_responsive_scaling'):
                # Use standard design base size and let the view handle current size
                controller.view.apply_responsive_scaling(1024, 768)

    @Slot(int)
    def _on_tab_changed(self, tab_index: int) -> None:
        """
        Handle tab change events.

        Args:
            tab_index: New tab index
        """
        tab_names = list(self.tab_controllers.keys())
        if 0 <= tab_index < len(tab_names):
            self.current_tab = tab_names[tab_index]
            self.status_message.emit(f"Switched to {self.current_tab.title()} trading", 2000)

    @Slot(str)
    def _on_menu_action(self, action_name: str) -> None:
        """
        Handle menu action events.

        Args:
            action_name: Name of triggered action
        """
        if action_name == "export_config":
            self._export_configuration()
        elif action_name == "import_config":
            self._import_configuration()
        elif action_name == "reset_settings":
            self._reset_settings()
        elif action_name == "reset_window_size":
            self._reset_window_size()
        elif action_name == "resize_compact":
            self._resize_to_compact()
        elif action_name == "resize_large":
            self._resize_to_large()
        elif action_name == "maximize_window":
            self._maximize_window()
        elif action_name == "about":
            self._show_about_dialog()

    def _on_validation_changed(self, tab_name: str, has_errors: bool) -> None:
        """
        Handle validation change events from tab controllers.

        Args:
            tab_name: Name of the tab
            has_errors: Whether tab has validation errors
        """
        if has_errors:
            self.status_message.emit(f"{tab_name.title()} tab has validation errors", 0)
        else:
            self.status_message.emit(f"{tab_name.title()} tab validation passed", 2000)

    def _on_calculation_completed(self, tab_name: str, result: Dict[str, Any]) -> None:
        """
        Handle calculation completion events.

        Args:
            tab_name: Name of the tab
            result: Calculation result
        """
        position_size = result.get('position_size', 0)
        estimated_risk = result.get('estimated_risk', 0)

        message = f"{tab_name.title()}: {position_size} units, ${estimated_risk:.2f} risk"
        self.status_message.emit(message, 5000)

    def _on_controller_error(self, tab_name: str, error_message: str) -> None:
        """
        Handle errors from tab controllers.

        Args:
            tab_name: Name of the tab
            error_message: Error message
        """
        self.error_occurred.emit(f"{tab_name.title()} Error", error_message)

    def _on_busy_state_changed(self, tab_name: str, is_busy: bool) -> None:
        """
        Handle busy state changes from tab controllers.

        Args:
            tab_name: Name of the tab
            is_busy: Whether controller is busy
        """
        if is_busy:
            self.status_message.emit(f"Calculating {tab_name} position...", 0)
        else:
            self.status_message.emit("Ready", 0)

    def _export_configuration(self) -> None:
        """Export application configuration to file."""
        try:
            # Open file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Configuration",
                "risk_calculator_config.json",
                "JSON Files (*.json)"
            )

            if file_path:
                # Save current form data first
                self._save_form_data()

                # Export configuration
                success = self.main_window.export_all_configuration(file_path)

                if success:
                    self.status_message.emit(f"Configuration exported to {file_path}", 3000)
                else:
                    self.error_occurred.emit("Export Error", "Failed to export configuration")

        except Exception as e:
            self.error_occurred.emit("Export Error", f"Export failed: {str(e)}")

    def _import_configuration(self) -> None:
        """Import application configuration from file."""
        try:
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Configuration",
                "",
                "JSON Files (*.json)"
            )

            if file_path:
                # Note: Import functionality would need to be implemented in config service
                self.status_message.emit("Import functionality not yet implemented", 3000)

        except Exception as e:
            self.error_occurred.emit("Import Error", f"Import failed: {str(e)}")

    def _reset_settings(self) -> None:
        """Reset all application settings."""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self.main_window,
                "Reset Settings",
                "Are you sure you want to reset all settings to defaults?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.main_window.clear_all_configuration()

                if success:
                    self.status_message.emit("Settings reset to defaults", 3000)
                    # Recommend restart
                    QMessageBox.information(
                        self.main_window,
                        "Settings Reset",
                        "Settings have been reset. Please restart the application for changes to take full effect."
                    )

        except Exception as e:
            self.error_occurred.emit("Reset Error", f"Reset failed: {str(e)}")

    def _reset_window_size(self) -> None:
        """Reset window to default size."""
        if self.main_window:
            self.main_window.reset_to_default_size()

    def _resize_to_compact(self) -> None:
        """Resize window to compact size (WSLg workaround)."""
        if self.main_window:
            self.main_window.resize(900, 650)
            self.status_message.emit("Window resized to compact size (900x650)", 2000)

    def _resize_to_large(self) -> None:
        """Resize window to large size (WSLg workaround)."""
        if self.main_window:
            self.main_window.resize(1200, 800)
            self.status_message.emit("Window resized to large size (1200x800)", 2000)

    def _maximize_window(self) -> None:
        """Maximize window (WSLg workaround)."""
        if self.main_window:
            if self.main_window.isMaximized():
                self.main_window.showNormal()
                self.status_message.emit("Window restored to normal size", 2000)
            else:
                self.main_window.showMaximized()
                self.status_message.emit("Window maximized", 2000)

    def _show_about_dialog(self) -> None:
        """Show about dialog."""
        about_text = """
        <h2>Risk Calculator Qt</h2>
        <p>Professional risk management tool for day trading</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Equity, Options, and Futures position sizing</li>
        <li>Multiple risk calculation methods</li>
        <li>Responsive UI with high-DPI support</li>
        <li>Cross-platform compatibility</li>
        </ul>
        <p><b>Version:</b> 2.0 (Qt Migration)</p>
        <p><b>Framework:</b> PySide6</p>
        <p><b>Note:</b> On WSL environments, use View menu resize options if manual window resizing doesn't work.</p>
        """

        QMessageBox.about(self.main_window, "About Risk Calculator", about_text)

    def _save_form_data(self) -> None:
        """Save current form data for all tabs."""
        for tab_name, controller in self.tab_controllers.items():
            try:
                form_data = controller.view.get_form_data()
                self.config_service.save_form_data(tab_name, form_data)
            except Exception:
                # Ignore errors during form data saving
                pass

    def _restore_form_data(self) -> None:
        """Restore saved form data for all tabs."""
        for tab_name, controller in self.tab_controllers.items():
            try:
                form_data = self.config_service.load_form_data(tab_name)

                # Restore form data to view
                for field_name, value in form_data.items():
                    controller.view.set_field_value(field_name, value)

            except Exception:
                # Ignore errors during form data restoration
                pass

    @Slot(str, str)
    def _show_error_dialog(self, title: str, message: str) -> None:
        """
        Show error dialog.

        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self.main_window, title, message)

    def get_application_status(self) -> Dict[str, Any]:
        """
        Get comprehensive application status.

        Returns:
            Dict[str, Any]: Application status information
        """
        status = {
            "initialized": self.is_initialized,
            "current_tab": self.current_tab,
            "window_info": {},
            "tabs": {}
        }

        if self.main_window:
            status["window_info"] = self.main_window.get_display_info()

        # Get tab status
        for tab_name, controller in self.tab_controllers.items():
            status["tabs"][tab_name] = {
                "has_errors": controller.has_errors,
                "is_busy": controller.is_busy,
                "last_calculation": controller.calculation_result is not None
            }

        return status

    def shutdown_application(self) -> None:
        """Shutdown application gracefully."""
        try:
            # Save current form data
            self._save_form_data()

            # Save window state
            if self.main_window:
                self.main_window.save_window_state()

            # Emit closing signal
            self.application_closing.emit()

            self.status_message.emit("Application shutting down...", 1000)

        except Exception as e:
            # Log error but continue shutdown
            print(f"Error during shutdown: {e}")

    def get_current_tab_controller(self) -> Optional[Any]:
        """
        Get the currently active tab controller.

        Returns:
            Tab controller or None
        """
        return self.tab_controllers.get(self.current_tab)

    def switch_to_tab(self, tab_name: str) -> bool:
        """
        Programmatically switch to a specific tab.

        Args:
            tab_name: Name of tab to switch to

        Returns:
            bool: True if switch successful
        """
        if tab_name in self.tab_controllers and self.main_window:
            tab_names = list(self.tab_controllers.keys())
            try:
                tab_index = tab_names.index(tab_name)
                self.main_window.tab_widget.setCurrentIndex(tab_index)
                return True
            except ValueError:
                pass

        return False