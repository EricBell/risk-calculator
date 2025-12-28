"""Base Flet view component for trading tabs."""

import flet as ft
from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..models.risk_method import RiskMethod


class BaseTradingView(ABC):
    """Base Flet view component for all trading tabs."""

    def __init__(self, controller=None):
        self.controller = controller
        self.validation_errors: Dict[str, str] = {}
        self.current_method = RiskMethod.PERCENTAGE
        self.page: Optional[ft.Page] = None

        # Refs for dynamic controls
        self.result_text_ref = ft.Ref[ft.TextField]()
        self.calculate_button_ref = ft.Ref[ft.ElevatedButton]()
        self.method_fields_ref = ft.Ref[ft.Container]()

        # Main container ref
        self.container_ref = ft.Ref[ft.Container]()

    def build(self):
        """Build the main view structure."""
        return ft.Container(
            ref=self.container_ref,
            padding=10,
            expand=True,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    self.build_trade_parameters(),
                    self.build_risk_method_selector(),
                    ft.Container(ref=self.method_fields_ref, content=self.build_method_fields()),
                    self.build_action_buttons(),
                    self.build_results_display()
                ]
            )
        )

    @abstractmethod
    def build_trade_parameters(self) -> ft.Control:
        """Build asset-specific input fields. Must be implemented by subclasses."""
        pass

    def build_risk_method_selector(self) -> ft.Control:
        """Build risk method radio button group."""
        return ft.Container(
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text("Risk Calculation Method", weight=ft.FontWeight.BOLD, size=14),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value=RiskMethod.PERCENTAGE.value, label="Percentage-Based Risk"),
                            ft.Radio(value=RiskMethod.FIXED_AMOUNT.value, label="Fixed Dollar Amount"),
                            ft.Radio(value=RiskMethod.LEVEL_BASED.value, label="Support/Resistance Level"),
                        ]),
                        value=RiskMethod.PERCENTAGE.value,
                        on_change=self.on_method_changed
                    )
                ]
            )
        )

    @abstractmethod
    def build_method_fields(self) -> ft.Control:
        """Build method-specific input fields. Must be implemented by subclasses."""
        pass

    def build_action_buttons(self) -> ft.Control:
        """Build Calculate and Clear buttons."""
        return ft.Container(
            margin=ft.margin.only(top=10, bottom=10),
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Calculate Position",
                        icon=ft.Icons.CALCULATE,
                        ref=self.calculate_button_ref,
                        on_click=self.on_calculate_clicked
                    ),
                    ft.OutlinedButton(
                        "Clear",
                        icon=ft.Icons.CLEAR,
                        on_click=self.on_clear_clicked
                    )
                ],
                spacing=10
            )
        )

    def build_results_display(self) -> ft.Control:
        """Build results display area."""
        return ft.Container(
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text("Calculation Results", weight=ft.FontWeight.BOLD, size=14),
                    ft.TextField(
                        ref=self.result_text_ref,
                        multiline=True,
                        read_only=True,
                        min_lines=8,
                        max_lines=20,
                        border=ft.InputBorder.NONE,
                        text_style=ft.TextStyle(font_family="Courier New"),
                        expand=True
                    )
                ]
            )
        )

    def create_text_field(
        self,
        label: str,
        field_name: str,
        keyboard_type=ft.KeyboardType.TEXT,
        suffix_text: Optional[str] = None,
        width: Optional[float] = None
    ) -> ft.TextField:
        """Helper to create a text field with validation."""
        return ft.TextField(
            label=label,
            keyboard_type=keyboard_type,
            suffix=suffix_text,
            width=width,
            on_change=lambda e: self.on_field_changed(field_name, e.control.value)
        )

    def on_field_changed(self, field_name: str, value: str):
        """Handle field value change."""
        if self.controller:
            self.controller.set_field_value(field_name, value)

    def on_method_changed(self, e: ft.ControlEvent):
        """Handle risk method change."""
        method_value = e.control.value
        method = RiskMethod(method_value)
        self.current_method = method

        if self.controller:
            self.controller.set_risk_method(method)

        # Update method-specific fields
        if self.method_fields_ref.current:
            self.method_fields_ref.current.content = self.build_method_fields()
            if self.page:
                self.page.update()

    def on_calculate_clicked(self, e: ft.ControlEvent):
        """Handle calculate button click."""
        if self.controller:
            self.controller.calculate_position()

    def on_clear_clicked(self, e: ft.ControlEvent):
        """Handle clear button click."""
        if self.controller:
            self.controller.clear_inputs()
        self.clear_results()

    def show_method_fields(self, method: RiskMethod):
        """Show fields appropriate for the selected risk method."""
        self.current_method = method
        if self.method_fields_ref.current:
            self.method_fields_ref.current.content = self.build_method_fields()
            if self.page:
                self.page.update()

    def show_validation_errors(self, errors: Dict[str, str]):
        """Display validation errors."""
        self.validation_errors = errors
        # Errors are displayed inline via TextField.error_text
        # This would be called by controller to update specific field errors
        if self.page:
            self.page.update()

    def clear_field_error(self, field_name: str):
        """Clear error for a specific field."""
        if field_name in self.validation_errors:
            del self.validation_errors[field_name]
        if self.page:
            self.page.update()

    def show_calculation_result(self, result_data: Dict):
        """Display calculation results."""
        if self.result_text_ref.current:
            formatted_result = self.format_calculation_result(result_data)
            self.result_text_ref.current.value = formatted_result
            if self.page:
                self.page.update()

    @abstractmethod
    def format_calculation_result(self, result_data: Dict) -> str:
        """Format calculation results for display. Must be implemented by subclasses."""
        pass

    def show_calculation_error(self, error_message: str):
        """Display calculation error."""
        if self.result_text_ref.current:
            self.result_text_ref.current.value = f"ERROR: {error_message}"
            if self.page:
                self.page.update()

    def show_warnings(self, warnings: list):
        """Display warnings."""
        if self.result_text_ref.current and warnings:
            current = self.result_text_ref.current.value or ""
            warning_text = "\n\nWARNINGS:\n" + "\n".join(f"⚠ {w}" for w in warnings)
            self.result_text_ref.current.value = current + warning_text
            if self.page:
                self.page.update()

    def clear_results(self):
        """Clear calculation results."""
        if self.result_text_ref.current:
            self.result_text_ref.current.value = ""
            if self.page:
                self.page.update()

    def set_busy_state(self, is_busy: bool):
        """Set busy state during calculations."""
        if self.calculate_button_ref.current:
            self.calculate_button_ref.current.disabled = is_busy
            self.calculate_button_ref.current.text = "Calculating..." if is_busy else "Calculate Position"
            if self.page:
                self.page.update()

    def set_calculate_button_enabled(self, enabled: bool):
        """Enable/disable calculate button."""
        if self.calculate_button_ref.current:
            self.calculate_button_ref.current.disabled = not enabled
            if self.page:
                self.page.update()

    def clear_all_inputs(self):
        """Clear all input fields (called by controller)."""
        # Subclasses can override to clear specific fields
        self.clear_results()
        if self.page:
            self.page.update()
