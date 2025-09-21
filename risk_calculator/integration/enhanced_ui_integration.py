"""
Complete UI integration for enhanced risk calculator features.
Coordinates enhanced services, controllers, views, and validation.
"""

import tkinter as tk
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass

# Import existing components
from risk_calculator.models.risk_method import RiskMethod

# Import enhanced services
from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
from risk_calculator.services.configuration_service import JsonConfigurationService

# Import enhanced controllers
from risk_calculator.controllers.enhanced_base_controller import EnhancedBaseController
from risk_calculator.controllers.enhanced_main_controller import EnhancedMainController
from risk_calculator.controllers.enhanced_menu_controller import EnhancedMenuController
from risk_calculator.controllers.enhanced_controller_adapter import EnhancedControllerAdapter

# Import enhanced views
from risk_calculator.views.error_display import FieldErrorManager, ErrorDisplayConfig
from risk_calculator.views.responsive_layout import ResponsiveGridManager, ResponsiveConfig
from risk_calculator.views.window_event_handlers import WindowEventManager
from risk_calculator.views.enhanced_view_integration import EnhancedViewIntegrator

# Import contract interfaces
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    spec_contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'specs', '003-there-are-several', 'contracts')
    sys.path.insert(0, spec_contracts_path)
    from validation_service import TradeType
except ImportError:
    # Fallback definition
    from enum import Enum
    class TradeType(Enum):
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"


@dataclass
class IntegrationConfig:
    """Configuration for complete UI integration."""
    enable_enhanced_validation: bool = True
    enable_enhanced_errors: bool = True
    enable_responsive_layout: bool = True
    enable_window_management: bool = True
    enable_menu_integration: bool = True
    auto_save_window_state: bool = True
    error_display_config: Optional[ErrorDisplayConfig] = None
    responsive_config: Optional[ResponsiveConfig] = None


class EnhancedUIIntegration:
    """Complete integration of enhanced UI components."""

    def __init__(self, main_window: tk.Tk, config: Optional[IntegrationConfig] = None):
        """
        Initialize complete UI integration.

        Args:
            main_window: Main application window
            config: Integration configuration
        """
        self.main_window = main_window
        self.config = config or IntegrationConfig()

        # Enhanced services
        self.validation_service: Optional[EnhancedValidationService] = None
        self.configuration_service: Optional[JsonConfigurationService] = None

        # Enhanced controllers
        self.main_controller: Optional[EnhancedMainController] = None
        self.menu_controller: Optional[EnhancedMenuController] = None
        self.tab_adapters: Dict[str, EnhancedControllerAdapter] = {}

        # Enhanced views
        self.view_integrators: Dict[str, EnhancedViewIntegrator] = {}
        self.window_event_manager: Optional[WindowEventManager] = None

        # Integration state
        self.is_integrated = False
        self.integration_errors: List[str] = []

        # Initialize integration
        self._initialize_integration()

    def _initialize_integration(self):
        """Initialize the complete integration."""
        try:
            # Initialize enhanced services
            if self.config.enable_enhanced_validation:
                self._initialize_enhanced_services()

            # Initialize enhanced controllers
            self._initialize_enhanced_controllers()

            # Initialize enhanced views
            if self.config.enable_enhanced_errors or self.config.enable_responsive_layout:
                self._initialize_enhanced_views()

            # Setup window management
            if self.config.enable_window_management:
                self._setup_window_management()

            # Setup menu integration
            if self.config.enable_menu_integration:
                self._setup_menu_integration()

            self.is_integrated = True

        except Exception as e:
            self.integration_errors.append(f"Integration initialization failed: {str(e)}")

    def _initialize_enhanced_services(self):
        """Initialize enhanced services."""
        try:
            self.validation_service = EnhancedValidationService()
            self.configuration_service = JsonConfigurationService()
        except Exception as e:
            self.integration_errors.append(f"Service initialization failed: {str(e)}")

    def _initialize_enhanced_controllers(self):
        """Initialize enhanced controllers."""
        try:
            # Main window controller
            if hasattr(self.main_window, 'main_controller'):
                # Replace or enhance existing main controller
                self.main_controller = EnhancedMainController(self.main_window)
            else:
                self.main_controller = EnhancedMainController(self.main_window)

            # Menu controller
            self.menu_controller = EnhancedMenuController(self.main_window)

        except Exception as e:
            self.integration_errors.append(f"Controller initialization failed: {str(e)}")

    def _initialize_enhanced_views(self):
        """Initialize enhanced view integrations."""
        try:
            # Create view integrators for existing tabs
            if hasattr(self.main_window, 'tabs'):
                for tab_name, tab_view in self.main_window.tabs.items():
                    view_integrator = EnhancedViewIntegrator(tab_view)
                    self.view_integrators[tab_name] = view_integrator

        except Exception as e:
            self.integration_errors.append(f"View integration failed: {str(e)}")

    def _setup_window_management(self):
        """Setup enhanced window management."""
        try:
            if not self.window_event_manager:
                self.window_event_manager = WindowEventManager(self.main_window)

            # Setup window state persistence
            if self.config.auto_save_window_state and self.main_controller:
                from risk_calculator.views.window_event_handlers import WindowEvent

                # Save window state on close
                self.window_event_manager.add_handler(
                    WindowEvent.CLOSE,
                    lambda: self.main_controller.save_window_state()
                )

                # Restore window state on startup
                self.main_controller.restore_window_state()

        except Exception as e:
            self.integration_errors.append(f"Window management setup failed: {str(e)}")

    def _setup_menu_integration(self):
        """Setup enhanced menu integration."""
        try:
            if self.menu_controller and hasattr(self.main_window, 'menubar'):
                # Integrate menu with validation system
                self.menu_controller.set_main_window(self.main_window)

                # Setup tab change handlers
                if hasattr(self.main_window, 'notebook'):
                    self.main_window.notebook.bind(
                        '<<NotebookTabChanged>>',
                        self.menu_controller.handle_tab_change
                    )

        except Exception as e:
            self.integration_errors.append(f"Menu integration failed: {str(e)}")

    def integrate_existing_tab(self, tab_name: str, tab_view, tab_controller) -> bool:
        """
        Integrate enhanced features with an existing tab.

        Args:
            tab_name: Name/identifier for the tab
            tab_view: Tab view instance
            tab_controller: Tab controller instance

        Returns:
            bool: True if integration successful
        """
        try:
            # Create controller adapter
            adapter = EnhancedControllerAdapter(tab_controller, tab_view)
            self.tab_adapters[tab_name] = adapter

            # Create view integrator
            view_integrator = EnhancedViewIntegrator(tab_view)
            self.view_integrators[tab_name] = view_integrator

            # Connect adapter with view integrator error manager
            if view_integrator.error_manager:
                adapter.error_manager = view_integrator.error_manager

            return True

        except Exception as e:
            self.integration_errors.append(f"Tab integration failed for {tab_name}: {str(e)}")
            return False

    def update_tab_validation(self, tab_name: str, form_data: Dict[str, str]) -> bool:
        """
        Update validation for a specific tab.

        Args:
            tab_name: Name of tab to update
            form_data: Current form data

        Returns:
            bool: True if validation successful
        """
        try:
            if tab_name in self.tab_adapters:
                adapter = self.tab_adapters[tab_name]
                adapter._update_form_validation()
                return True

            return False

        except Exception as e:
            self.integration_errors.append(f"Validation update failed for {tab_name}: {str(e)}")
            return False

    def show_tab_error(self, tab_name: str, field_name: str, error_message: str):
        """
        Show error for specific field in a tab.

        Args:
            tab_name: Name of tab
            field_name: Name of field with error
            error_message: Error message to display
        """
        try:
            if tab_name in self.view_integrators:
                integrator = self.view_integrators[tab_name]
                integrator.show_field_error(field_name, error_message)

        except Exception as e:
            self.integration_errors.append(f"Error display failed for {tab_name}.{field_name}: {str(e)}")

    def clear_tab_errors(self, tab_name: str):
        """
        Clear all errors for a specific tab.

        Args:
            tab_name: Name of tab to clear errors for
        """
        try:
            if tab_name in self.view_integrators:
                integrator = self.view_integrators[tab_name]
                integrator.clear_all_errors()

        except Exception as e:
            self.integration_errors.append(f"Error clearing failed for {tab_name}: {str(e)}")

    def get_tab_validation_state(self, tab_name: str) -> Dict[str, Any]:
        """
        Get validation state for a specific tab.

        Args:
            tab_name: Name of tab

        Returns:
            Dict containing validation state
        """
        try:
            if tab_name in self.tab_adapters:
                adapter = self.tab_adapters[tab_name]
                return adapter.get_validation_state()

            return {"has_errors": False, "error_count": 0}

        except Exception:
            return {"has_errors": False, "error_count": 0}

    def handle_risk_method_change(self, tab_name: str, risk_method: str):
        """
        Handle risk method change for a tab.

        Args:
            tab_name: Name of tab
            risk_method: New risk method
        """
        try:
            if tab_name in self.tab_adapters:
                adapter = self.tab_adapters[tab_name]
                adapter.set_risk_method(risk_method)

        except Exception as e:
            self.integration_errors.append(f"Risk method change failed for {tab_name}: {str(e)}")

    def save_window_configuration(self) -> bool:
        """
        Save current window configuration.

        Returns:
            bool: True if save successful
        """
        try:
            if self.main_controller:
                return self.main_controller.save_window_state()
            return False

        except Exception:
            return False

    def restore_window_configuration(self) -> bool:
        """
        Restore window configuration.

        Returns:
            bool: True if restore successful
        """
        try:
            if self.main_controller:
                return self.main_controller.restore_window_state()
            return False

        except Exception:
            return False

    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get integration status and health information.

        Returns:
            Dict containing integration status
        """
        return {
            "is_integrated": self.is_integrated,
            "services_initialized": bool(self.validation_service and self.configuration_service),
            "controllers_initialized": bool(self.main_controller and self.menu_controller),
            "window_management_enabled": bool(self.window_event_manager),
            "tab_integrations": len(self.tab_adapters),
            "view_integrations": len(self.view_integrators),
            "integration_errors": self.integration_errors.copy(),
            "error_count": len(self.integration_errors)
        }

    def get_validation_service(self) -> Optional[EnhancedValidationService]:
        """Get the enhanced validation service."""
        return self.validation_service

    def get_configuration_service(self) -> Optional[JsonConfigurationService]:
        """Get the configuration service."""
        return self.configuration_service

    def get_main_controller(self) -> Optional[EnhancedMainController]:
        """Get the enhanced main controller."""
        return self.main_controller

    def get_menu_controller(self) -> Optional[EnhancedMenuController]:
        """Get the enhanced menu controller."""
        return self.menu_controller

    def get_tab_adapter(self, tab_name: str) -> Optional[EnhancedControllerAdapter]:
        """Get the controller adapter for a specific tab."""
        return self.tab_adapters.get(tab_name)

    def get_view_integrator(self, tab_name: str) -> Optional[EnhancedViewIntegrator]:
        """Get the view integrator for a specific tab."""
        return self.view_integrators.get(tab_name)


def create_enhanced_ui(main_window: tk.Tk,
                      enable_all_features: bool = True) -> EnhancedUIIntegration:
    """
    Create enhanced UI integration with all features.

    Args:
        main_window: Main application window
        enable_all_features: Whether to enable all enhancement features

    Returns:
        EnhancedUIIntegration: Configured integration
    """
    config = IntegrationConfig(
        enable_enhanced_validation=enable_all_features,
        enable_enhanced_errors=enable_all_features,
        enable_responsive_layout=enable_all_features,
        enable_window_management=enable_all_features,
        enable_menu_integration=enable_all_features,
        auto_save_window_state=enable_all_features
    )

    return EnhancedUIIntegration(main_window, config)


def integrate_with_existing_app(main_window: tk.Tk,
                               existing_tabs: Optional[Dict[str, Tuple[Any, Any]]] = None) -> EnhancedUIIntegration:
    """
    Integrate enhanced features with an existing application.

    Args:
        main_window: Main application window
        existing_tabs: Dictionary of tab_name -> (view, controller) pairs

    Returns:
        EnhancedUIIntegration: Configured integration
    """
    integration = create_enhanced_ui(main_window)

    # Integrate existing tabs if provided
    if existing_tabs:
        for tab_name, (tab_view, tab_controller) in existing_tabs.items():
            integration.integrate_existing_tab(tab_name, tab_view, tab_controller)

    return integration