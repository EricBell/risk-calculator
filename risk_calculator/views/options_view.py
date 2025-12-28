"""Options trading view with Flet controls."""

import flet as ft
from typing import Dict
from .base_view import BaseTradingView
from ..models.risk_method import RiskMethod


class OptionsView(BaseTradingView):
    """Flet view for options trading (percentage and fixed amount methods only)."""

    def __init__(self, controller=None):
        super().__init__(controller)

        # Refs for options-specific fields
        self.account_size_ref = ft.Ref[ft.TextField]()
        self.option_symbol_ref = ft.Ref[ft.TextField]()
        self.premium_ref = ft.Ref[ft.TextField]()
        self.contract_multiplier_ref = ft.Ref[ft.TextField]()
        self.trade_direction_ref = ft.Ref[ft.RadioGroup]()

    def build_trade_parameters(self) -> ft.Control:
        """Build options-specific input fields."""
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
                        ref=self.option_symbol_ref,
                        label="Option Symbol",
                        hint_text="e.g., AAPL250117C00150000",
                        keyboard_type=ft.KeyboardType.TEXT,
                        on_change=lambda e: self.on_field_changed('option_symbol', e.control.value.upper())
                    ),
                    ft.TextField(
                        ref=self.premium_ref,
                        label="Premium per Share",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        prefix_text="$",
                        hint_text="Option price",
                        on_change=lambda e: self.on_field_changed('premium', e.control.value)
                    ),
                    ft.TextField(
                        ref=self.contract_multiplier_ref,
                        label="Contract Multiplier",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        value="100",
                        hint_text="Usually 100",
                        on_change=lambda e: self.on_field_changed('contract_multiplier', e.control.value)
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Column([
                            ft.Text("Trade Direction", size=12),
                            ft.RadioGroup(
                                ref=self.trade_direction_ref,
                                content=ft.Row([
                                    ft.Radio(value="LONG", label="Buy (Long)"),
                                    ft.Radio(value="SHORT", label="Sell (Short)"),
                                ]),
                                value="LONG",
                                on_change=lambda e: self.on_field_changed('trade_direction', e.control.value)
                            )
                        ])
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=10),
                        content=ft.Text(
                            "Note: Options risk is limited to the premium paid (for buyers)",
                            size=11,
                            italic=True,
                            color=ft.colors.PRIMARY
                        )
                    )
                ]
            )
        )

    def build_risk_method_selector(self) -> ft.Control:
        """Build risk method selector with level-based disabled."""
        return ft.Container(
            border=ft.border.all(1, ft.colors.OUTLINE),
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
                            ft.Radio(
                                value=RiskMethod.LEVEL_BASED.value,
                                label="Support/Resistance (N/A for Options)",
                                disabled=True
                            ),
                        ]),
                        value=RiskMethod.PERCENTAGE.value,
                        on_change=self.on_method_changed
                    ),
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Text(
                            "Level-based method not applicable to options trading",
                            size=11,
                            italic=True,
                            color=ft.colors.SECONDARY
                        )
                    )
                ]
            )
        )

    def build_method_fields(self) -> ft.Control:
        """Build method-specific input fields (only percentage and fixed amount)."""
        if self.current_method == RiskMethod.PERCENTAGE:
            return self.build_percentage_fields()
        elif self.current_method == RiskMethod.FIXED_AMOUNT:
            return self.build_fixed_amount_fields()
        # Level-based not supported for options
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
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Text(
                            "Contracts = (Account × Risk%) / (Premium × Multiplier)",
                            size=11,
                            italic=True,
                            color=ft.colors.SECONDARY
                        )
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
                    ft.Container(
                        padding=ft.padding.only(top=5),
                        content=ft.Text(
                            "Contracts = Fixed Risk / (Premium × Multiplier)",
                            size=11,
                            italic=True,
                            color=ft.colors.SECONDARY
                        )
                    )
                ]
            )
        )

    def format_calculation_result(self, result_data: Dict) -> str:
        """Format options calculation results for display."""
        lines = []
        lines.append("=" * 50)
        lines.append("OPTIONS POSITION CALCULATION RESULTS")
        lines.append("=" * 50)
        lines.append("")

        # Number of contracts
        if 'position_size' in result_data:
            lines.append(f"Number of Contracts: {int(result_data['position_size'])}")

        # Total cost
        if 'position_value' in result_data:
            lines.append(f"Total Premium Cost: ${result_data['position_value']:,.2f}")

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
        lines.append("Options Trading Notes:")
        lines.append("  • Risk limited to premium paid (for buyers)")
        lines.append("  • Each contract represents 100 shares")
        lines.append("  • Consider time decay (theta) in holding period")
        lines.append("  • Monitor implied volatility changes")

        return "\n".join(lines)

    def clear_all_inputs(self):
        """Clear all options input fields."""
        if self.account_size_ref.current:
            self.account_size_ref.current.value = ""
        if self.option_symbol_ref.current:
            self.option_symbol_ref.current.value = ""
        if self.premium_ref.current:
            self.premium_ref.current.value = ""
        if self.contract_multiplier_ref.current:
            self.contract_multiplier_ref.current.value = "100"
        if self.trade_direction_ref.current:
            self.trade_direction_ref.current.value = "LONG"

        self.clear_results()
        self.update()
