"""Main controller for tab management and application coordination."""

import tkinter as tk
from typing import Dict, Optional, Any
from .equity_controller import EquityController
from .option_controller import OptionController
from .future_controller import FutureController
from ..models.risk_method import RiskMethod


class MainController:
    """Main application controller that manages tabs and coordinates between controllers."""

    def __init__(self, main_view):
        self.main_view = main_view
        self.controllers: Dict[str, Any] = {}
        self.current_tab: Optional[str] = None
        self.session_data: Dict[str, Dict] = {}

        # Initialize tab controllers when views are available
        self._initialize_controllers()

    def _initialize_controllers(self) -> None:
        """Initialize individual tab controllers."""
        # Controllers will be initialized when their corresponding views are created
        pass

    def register_tab_controller(self, tab_name: str, controller) -> None:
        """Register a tab controller."""
        self.controllers[tab_name] = controller

        # Restore session data if available
        if tab_name in self.session_data:
            try:
                controller.load_trade_data(self.session_data[tab_name])
            except Exception:
                # If loading fails, start fresh
                pass

    def create_equity_controller(self, equity_view) -> EquityController:
        """Create and register equity controller."""
        controller = EquityController(equity_view)
        self.register_tab_controller('equity', controller)
        return controller

    def create_option_controller(self, option_view) -> OptionController:
        """Create and register option controller."""
        controller = OptionController(option_view)
        self.register_tab_controller('option', controller)
        return controller

    def create_future_controller(self, future_view) -> FutureController:
        """Create and register future controller."""
        controller = FutureController(future_view)
        self.register_tab_controller('future', controller)
        return controller

    def on_tab_changed(self, tab_name: str) -> None:
        """Handle tab change events."""
        # Save current tab data before switching
        if self.current_tab and self.current_tab in self.controllers:
            try:
                current_controller = self.controllers[self.current_tab]
                self.session_data[self.current_tab] = current_controller.get_current_trade_data()
            except Exception:
                # Skip saving if data is invalid
                pass

        # Update current tab
        old_tab = self.current_tab
        self.current_tab = tab_name

        # Notify views of tab change
        self._handle_tab_change_ui_updates(old_tab, tab_name)

    def _handle_tab_change_ui_updates(self, old_tab: Optional[str], new_tab: str) -> None:
        """Handle UI updates when tabs change."""
        # Update window title
        tab_titles = {
            'equity': 'Risk Calculator - Equity Trading',
            'option': 'Risk Calculator - Option Trading',
            'future': 'Risk Calculator - Futures Trading'
        }

        if hasattr(self.main_view, 'set_title'):
            title = tab_titles.get(new_tab, 'Risk Calculator')
            self.main_view.set_title(title)

        # Update any shared UI elements
        if hasattr(self.main_view, 'update_tab_specific_ui'):
            self.main_view.update_tab_specific_ui(new_tab)

    def set_global_risk_method(self, risk_method: RiskMethod) -> None:
        """Set risk method across all tabs (synchronized setting)."""
        for controller_name, controller in self.controllers.items():
            if controller_name == 'option' and risk_method == RiskMethod.LEVEL_BASED:
                # Skip setting level-based for options
                continue

            try:
                controller.set_risk_method(risk_method)
            except Exception:
                # Skip if controller doesn't support the method
                pass

    def clear_all_tabs(self) -> None:
        """Clear inputs in all tabs."""
        for controller in self.controllers.values():
            try:
                controller.clear_inputs()
            except Exception:
                pass

        # Clear session data
        self.session_data.clear()

    def clear_current_tab(self) -> None:
        """Clear inputs in the current tab only."""
        if self.current_tab and self.current_tab in self.controllers:
            try:
                self.controllers[self.current_tab].clear_inputs()
                # Remove from session data
                if self.current_tab in self.session_data:
                    del self.session_data[self.current_tab]
            except Exception:
                pass

    def get_current_controller(self):
        """Get the currently active tab controller."""
        if self.current_tab and self.current_tab in self.controllers:
            return self.controllers[self.current_tab]
        return None

    def calculate_current_tab(self) -> None:
        """Trigger calculation in the current tab."""
        current_controller = self.get_current_controller()
        if current_controller:
            try:
                current_controller.calculate_position()
            except Exception as e:
                if hasattr(self.main_view, 'show_error'):
                    self.main_view.show_error(f"Calculation failed: {str(e)}")

    def get_all_tab_data(self) -> Dict[str, Dict]:
        """Get data from all tabs for session persistence."""
        all_data = {}

        # Get data from active controllers
        for tab_name, controller in self.controllers.items():
            try:
                all_data[tab_name] = controller.get_current_trade_data()
            except Exception:
                # Skip tabs with invalid data
                pass

        # Include session data for inactive tabs
        for tab_name, data in self.session_data.items():
            if tab_name not in all_data:
                all_data[tab_name] = data

        return all_data

    def load_session_data(self, session_data: Dict[str, Dict]) -> None:
        """Load session data for all tabs."""
        self.session_data = session_data.copy()

        # Load data into active controllers
        for tab_name, data in session_data.items():
            if tab_name in self.controllers:
                try:
                    self.controllers[tab_name].load_trade_data(data)
                except Exception:
                    # Skip invalid data
                    pass

    def get_application_status(self) -> Dict[str, Any]:
        """Get overall application status and statistics."""
        status = {
            'current_tab': self.current_tab,
            'active_controllers': list(self.controllers.keys()),
            'session_data_tabs': list(self.session_data.keys()),
            'calculations_performed': 0,
            'validation_errors': 0
        }

        # Collect statistics from controllers
        for tab_name, controller in self.controllers.items():
            if hasattr(controller, 'has_errors'):
                if controller.has_errors:
                    status['validation_errors'] += 1

        return status

    def validate_all_tabs(self) -> Dict[str, bool]:
        """Validate all tabs and return validation status."""
        validation_status = {}

        for tab_name, controller in self.controllers.items():
            try:
                # Update controller with current data
                if hasattr(controller, '_sync_to_trade_object'):
                    controller._sync_to_trade_object()

                # Check if required fields are filled
                required_fields = controller.get_required_fields()
                all_filled = True

                for field_name in required_fields:
                    if field_name in controller.tk_vars:
                        value = controller.tk_vars[field_name].get().strip()
                        if not value:
                            all_filled = False
                            break

                validation_status[tab_name] = all_filled and not controller.has_errors

            except Exception:
                validation_status[tab_name] = False

        return validation_status

    def export_current_tab_data(self) -> Optional[Dict]:
        """Export current tab data for external use."""
        current_controller = self.get_current_controller()
        if current_controller:
            try:
                return current_controller.get_current_trade_data()
            except Exception:
                pass
        return None

    def import_tab_data(self, tab_name: str, data: Dict) -> bool:
        """Import data into a specific tab."""
        if tab_name in self.controllers:
            try:
                self.controllers[tab_name].load_trade_data(data)
                return True
            except Exception:
                pass
        elif tab_name in ['equity', 'option', 'future']:
            # Store data for when controller becomes available
            self.session_data[tab_name] = data
            return True

        return False

    def shutdown(self) -> None:
        """Cleanup when application is closing."""
        # Save current session data
        try:
            if self.current_tab and self.current_tab in self.controllers:
                current_controller = self.controllers[self.current_tab]
                self.session_data[self.current_tab] = current_controller.get_current_trade_data()
        except Exception:
            pass

        # Cleanup controllers
        for controller in self.controllers.values():
            if hasattr(controller, 'cleanup'):
                try:
                    controller.cleanup()
                except Exception:
                    pass

        # Clear references
        self.controllers.clear()
        self.session_data.clear()

    def handle_global_keyboard_shortcut(self, event) -> bool:
        """Handle application-wide keyboard shortcuts."""
        # Ctrl+1, Ctrl+2, Ctrl+3 for tab switching
        if event.state & 0x4:  # Control key
            if event.keysym == '1' and 'equity' in self.controllers:
                if hasattr(self.main_view, 'select_tab'):
                    self.main_view.select_tab('equity')
                return True
            elif event.keysym == '2' and 'option' in self.controllers:
                if hasattr(self.main_view, 'select_tab'):
                    self.main_view.select_tab('option')
                return True
            elif event.keysym == '3' and 'future' in self.controllers:
                if hasattr(self.main_view, 'select_tab'):
                    self.main_view.select_tab('future')
                return True
            elif event.keysym == 'Return':  # Ctrl+Enter for calculate
                self.calculate_current_tab()
                return True
            elif event.keysym == 'r':  # Ctrl+R for clear current tab
                self.clear_current_tab()
                return True

        return False

    def is_any_calculation_in_progress(self) -> bool:
        """Check if any tab has calculation in progress."""
        for controller in self.controllers.values():
            if hasattr(controller, 'is_busy') and controller.is_busy:
                return True
        return False