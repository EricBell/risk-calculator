"""Main Flet view with tabbed navigation."""

import flet as ft
from .equity_view import EquityView
from .options_view import OptionsView
from .futures_view import FuturesView


class MainView(ft.UserControl):
    """Main application view with tabs for different trading instruments."""

    def __init__(self, main_controller=None):
        super().__init__()
        self.main_controller = main_controller

        # Create individual views
        self.equity_view = None
        self.options_view = None
        self.futures_view = None

        # Controllers will be set after initialization
        self.equity_controller = None
        self.options_controller = None
        self.futures_controller = None

        # Refs
        self.tabs_ref = ft.Ref[ft.Tabs]()
        self.status_text_ref = ft.Ref[ft.Text]()

    def build(self):
        """Build the main view structure."""
        # Create views
        self.equity_view = EquityView()
        self.options_view = OptionsView()
        self.futures_view = FuturesView()

        # Create and wire controllers if main_controller exists
        if self.main_controller:
            self.equity_controller = self.main_controller.create_equity_controller(self.equity_view)
            self.options_controller = self.main_controller.create_option_controller(self.options_view)
            self.futures_controller = self.main_controller.create_future_controller(self.futures_view)

            # Set controllers on views
            self.equity_view.controller = self.equity_controller
            self.options_view.controller = self.options_controller
            self.futures_view.controller = self.futures_controller

        return ft.Column(
            expand=True,
            controls=[
                # Title bar
                ft.Container(
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=ft.padding.all(15),
                    content=ft.Row([
                        ft.Icon(ft.icons.CALCULATE, size=24),
                        ft.Text(
                            "Risk Calculator - Daytrading Position Sizing",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                    ])
                ),
                # Tabs
                ft.Tabs(
                    ref=self.tabs_ref,
                    selected_index=0,
                    animation_duration=300,
                    expand=True,
                    tabs=[
                        ft.Tab(
                            text="Equity Trading",
                            icon=ft.icons.SHOW_CHART,
                            content=self.equity_view
                        ),
                        ft.Tab(
                            text="Options Trading",
                            icon=ft.icons.FUNCTIONS,
                            content=self.options_view
                        ),
                        ft.Tab(
                            text="Futures Trading",
                            icon=ft.icons.TRENDING_UP,
                            content=self.futures_view
                        ),
                    ],
                    on_change=self.on_tab_changed
                ),
                # Status bar
                ft.Container(
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    content=ft.Row([
                        ft.Icon(ft.icons.INFO_OUTLINE, size=16),
                        ft.Text(
                            "Ready",
                            ref=self.status_text_ref,
                            size=12
                        ),
                    ])
                )
            ]
        )

    def on_tab_changed(self, e: ft.ControlEvent):
        """Handle tab change."""
        tab_index = e.control.selected_index
        tab_names = ['equity', 'options', 'futures']

        if tab_index < len(tab_names):
            tab_name = tab_names[tab_index]

            # Notify main controller of tab change
            if self.main_controller:
                self.main_controller.on_tab_changed(tab_name)

            # Update status
            if self.status_text_ref.current:
                tab_labels = ['Equity Trading', 'Options Trading', 'Futures Trading']
                self.status_text_ref.current.value = f"{tab_labels[tab_index]} - Ready"
                self.update()

    def show_status(self, message: str):
        """Update status bar message."""
        if self.status_text_ref.current:
            self.status_text_ref.current.value = message
            self.update()

    def get_current_tab(self) -> str:
        """Get the name of the currently selected tab."""
        if self.tabs_ref.current:
            tab_index = self.tabs_ref.current.selected_index
            tab_names = ['equity', 'options', 'futures']
            return tab_names[tab_index] if tab_index < len(tab_names) else 'equity'
        return 'equity'

    def set_tab(self, tab_name: str):
        """Switch to a specific tab by name."""
        tab_map = {'equity': 0, 'options': 1, 'option': 1, 'futures': 2, 'future': 2}
        if self.tabs_ref.current and tab_name in tab_map:
            self.tabs_ref.current.selected_index = tab_map[tab_name]
            self.update()
