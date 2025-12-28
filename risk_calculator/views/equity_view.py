"""Equity trading view with Flet controls."""

import flet as ft
from typing import Dict
from .base_view import BaseTradingView
from ..models.risk_method import RiskMethod


class EquityView(BaseTradingView):
    """Flet view for equity trading with all three risk methods."""

    def __init__(self, controller=None):
        super().__init__(controller)

        # Refs for equity-specific fields
        self.account_size_ref = ft.Ref[ft.TextField]()
        self.symbol_ref = ft.Ref[ft.TextField]()
        self.entry_price_ref = ft.Ref[ft.TextField]()
        self.trade_direction_ref = ft.Ref[ft.RadioGroup]()

    def build_trade_parameters(self) -> ft.Control:
        """Build equity-specific input fields."""
        return ft.Container(
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text("Trade Parameters", weight=ft.FontWeight.BOLD, size=14),
                    ft.TextField(
                        ref=self.account_size_ref,
                        label="Account Size ($)",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        on_change=lambda e: self.on_field_changed('account_size', e.control.value)
                    ),
                    ft.TextField(
                        ref=self.symbol_ref,
                        label="Stock Symbol",
                        hint_text="e.g., AAPL",
                        keyboard_type=ft.KeyboardType.TEXT,
                        on_change=lambda e: self.on_field_changed('symbol', e.control.value.upper())
                    ),
                    ft.TextField(
                        ref=self.entry_price_ref,
                        label="Entry Price",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        on_change=lambda e: self.on_field_changed('entry_price', e.control.value)
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Column([
                            ft.Text("Trade Direction", size=12),
                            ft.RadioGroup(
                                ref=self.trade_direction_ref,
                                content=ft.Row([
                                    ft.Radio(value="LONG", label="Long"),
                                    ft.Radio(value="SHORT", label="Short"),
                                ]),
                                value="LONG",
                                on_change=lambda e: self.on_field_changed('trade_direction', e.control.value)
                            )
                        ])
                    )
                ]
            )
        )

    def build_method_fields(self) -> ft.Control:
        """Build method-specific input fields based on current risk method."""
        if self.current_method == RiskMethod.PERCENTAGE:
            return self.build_percentage_fields()
        elif self.current_method == RiskMethod.FIXED_AMOUNT:
            return self.build_fixed_amount_fields()
        elif self.current_method == RiskMethod.LEVEL_BASED:
            return self.build_level_based_fields()
        return ft.Container()

    def build_percentage_fields(self) -> ft.Control:
        """Build fields for percentage-based risk method."""
        return ft.Container(
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text("Percentage Method Parameters", weight=ft.FontWeight.BOLD, size=14),
                    ft.TextField(
                        label="Risk Percentage",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        suffix_text="%",
                        hint_text="e.g., 2.0",
                        on_change=lambda e: self.on_field_changed('risk_percentage', e.control.value)
                    ),
                    ft.TextField(
                        label="Stop Loss Price",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        on_change=lambda e: self.on_field_changed('stop_loss_price', e.control.value)
                    )
                ]
            )
        )

    def build_fixed_amount_fields(self) -> ft.Control:
        """Build fields for fixed amount risk method."""
        return ft.Container(
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text("Fixed Amount Method Parameters", weight=ft.FontWeight.BOLD, size=14),
                    ft.TextField(
                        label="Fixed Risk Amount",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        hint_text="e.g., 200",
                        on_change=lambda e: self.on_field_changed('fixed_risk_amount', e.control.value)
                    ),
                    ft.TextField(
                        label="Stop Loss Price",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        on_change=lambda e: self.on_field_changed('stop_loss_price', e.control.value)
                    )
                ]
            )
        )

    def build_level_based_fields(self) -> ft.Control:
        """Build fields for level-based risk method."""
        return ft.Container(
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text("Level-Based Method Parameters", weight=ft.FontWeight.BOLD, size=14),
                    ft.TextField(
                        label="Support/Resistance Level",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        hint_text="Key price level",
                        on_change=lambda e: self.on_field_changed('support_resistance_level', e.control.value)
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Text(
                            "Position size calculated based on distance to support/resistance level",
                            size=11,
                            italic=True,
                            color=ft.colors.SECONDARY
                        )
                    )
                ]
            )
        )

    def format_calculation_result(self, result_data: Dict) -> str:
        """Format equity calculation results for display."""
        lines = []
        lines.append("=" * 50)
        lines.append("EQUITY POSITION CALCULATION RESULTS")
        lines.append("=" * 50)
        lines.append("")

        # Position size
        if 'position_size' in result_data:
            lines.append(f"Position Size: {int(result_data['position_size'])} shares")

        # Position value
        if 'position_value' in result_data:
            lines.append(f"Position Value: ${result_data['position_value']:,.2f}")

        # Risk amount
        if 'estimated_risk' in result_data:
            lines.append(f"Estimated Risk: ${result_data['estimated_risk']:,.2f}")

        # Risk method
        if 'risk_method' in result_data:
            method_name = result_data['risk_method'].replace('_', ' ').title()
            lines.append(f"Risk Method: {method_name}")

        lines.append("")
        lines.append("=" * 50)
        lines.append("")
        lines.append("Position Guidelines:")
        lines.append("  • Enter position at calculated size")
        lines.append("  • Set stop loss at specified price")
        lines.append("  • Monitor position for risk management")

        return "\n".join(lines)

    def clear_all_inputs(self):
        """Clear all equity input fields."""
        if self.account_size_ref.current:
            self.account_size_ref.current.value = ""
        if self.symbol_ref.current:
            self.symbol_ref.current.value = ""
        if self.entry_price_ref.current:
            self.entry_price_ref.current.value = ""
        if self.trade_direction_ref.current:
            self.trade_direction_ref.current.value = "LONG"

        self.clear_results()
        if self.page:
            self.page.update()
