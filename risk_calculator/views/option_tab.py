"""Options trading tab with level-based method disabled and option-specific UI."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any
from .base_tab import BaseTradingTab
from ..models.risk_method import RiskMethod


class OptionsTab(BaseTradingTab):
    """Options trading tab supporting only percentage and fixed amount risk methods."""

    def _create_asset_specific_widgets(self, start_row: int) -> int:
        """Create options-specific input widgets."""
        row = start_row

        # Option symbol
        ttk.Label(self.input_frame, text="Option Symbol:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        symbol_entry = ttk.Entry(self.input_frame)
        symbol_entry.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['option_symbol'] = symbol_entry
        self._add_validation_label('option_symbol', row)
        row += 1

        # Premium per share
        ttk.Label(self.input_frame, text="Premium per Share ($):").grid(row=row, column=0, sticky="w", padx=(0, 10))
        premium_entry = ttk.Entry(self.input_frame)
        premium_entry.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['premium'] = premium_entry
        self._add_validation_label('premium', row)
        row += 1

        # Contract multiplier
        ttk.Label(self.input_frame, text="Contract Multiplier:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        multiplier_frame = ttk.Frame(self.input_frame)
        multiplier_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        multiplier_frame.grid_columnconfigure(0, weight=1)

        multiplier_entry = ttk.Entry(multiplier_frame)
        multiplier_entry.grid(row=0, column=0, sticky="ew")
        multiplier_entry.insert(0, "100")  # Default value
        self.input_widgets['contract_multiplier'] = multiplier_entry

        ttk.Label(multiplier_frame, text="(typically 100)", font=("TkDefaultFont", 8)).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )
        self._add_validation_label('contract_multiplier', row)
        row += 1

        # Trade direction
        ttk.Label(self.input_frame, text="Direction:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        direction_frame = ttk.Frame(self.input_frame)
        direction_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))

        direction_var = tk.StringVar(value="LONG")
        self.input_widgets['trade_direction'] = direction_var

        long_rb = ttk.Radiobutton(direction_frame, text="Buy (Long)", variable=direction_var, value="LONG")
        long_rb.grid(row=0, column=0, sticky="w")
        short_rb = ttk.Radiobutton(direction_frame, text="Sell (Short)", variable=direction_var, value="SHORT")
        short_rb.grid(row=0, column=1, sticky="w", padx=(20, 0))
        row += 1

        # Add option-specific information panel
        self._create_option_info_panel(row)
        row += 1

        return row

    def _create_option_info_panel(self, row: int) -> None:
        """Create informational panel about options trading."""
        info_frame = ttk.LabelFrame(self.input_frame, text="Options Trading Info", padding="5")
        info_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        info_text = (
            "• Premium is the cost per share of the option\n"
            "• Total cost = Premium × Contract Multiplier × Number of Contracts\n"
            "• Risk is limited to premium paid for bought options\n"
            "• Level-based method not available for options"
        )

        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("TkDefaultFont", 8),
            foreground="gray",
            justify="left"
        )
        info_label.grid(row=0, column=0, sticky="w")

    def _get_supported_methods(self) -> List[RiskMethod]:
        """Return risk methods supported by options trading (no level-based)."""
        return [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]

    def _create_method_specific_widgets(self) -> None:
        """Override to exclude level-based method and customize for options."""
        # Risk method selection - only show supported methods
        method_var = tk.StringVar(value=RiskMethod.PERCENTAGE.value)
        self.input_widgets['risk_method'] = method_var

        methods = self._get_supported_methods()
        for i, method in enumerate(methods):
            rb = ttk.Radiobutton(
                self.method_frame,
                text=method.value.replace('_', ' ').title(),
                variable=method_var,
                value=method.value,
                command=lambda m=method: self.show_method_fields(m)
            )
            rb.grid(row=0, column=i, sticky="w", padx=(0, 20))

        # Add disabled level-based option with explanation
        level_rb = ttk.Radiobutton(
            self.method_frame,
            text="Level Based (N/A for Options)",
            variable=method_var,
            value=RiskMethod.LEVEL_BASED.value,
            state="disabled"
        )
        level_rb.grid(row=0, column=len(methods), sticky="w", padx=(0, 20))

        # Create frames for supported methods only
        self._create_percentage_method_frame()
        self._create_fixed_amount_method_frame()

        # Show default method
        self.show_method_fields(RiskMethod.PERCENTAGE)

    def _create_percentage_method_frame(self) -> None:
        """Create percentage method frame for options."""
        frame = ttk.Frame(self.method_inputs_frame)
        frame.grid_columnconfigure(1, weight=1)  # Allow entry to expand
        self.method_frames[RiskMethod.PERCENTAGE] = frame

        ttk.Label(frame, text="Risk Percentage (1-5%):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        risk_entry = ttk.Entry(frame)
        risk_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['risk_percentage'] = risk_entry
        self._add_method_validation_label('risk_percentage', frame, 0)

        # Add options-specific note
        note_label = ttk.Label(
            frame,
            text="Risk is calculated as % of account size",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        note_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

    def _create_fixed_amount_method_frame(self) -> None:
        """Create fixed amount method frame for options."""
        frame = ttk.Frame(self.method_inputs_frame)
        frame.grid_columnconfigure(1, weight=1)  # Allow entry to expand
        self.method_frames[RiskMethod.FIXED_AMOUNT] = frame

        ttk.Label(frame, text="Fixed Risk Amount ($10-500):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        amount_entry = ttk.Entry(frame)
        amount_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['fixed_risk_amount'] = amount_entry
        self._add_method_validation_label('fixed_risk_amount', frame, 0)

        # Add options-specific note
        note_label = ttk.Label(
            frame,
            text="Fixed dollar amount to risk on this trade",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        note_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

    def show_method_fields(self, method: RiskMethod) -> None:
        """Override to prevent level-based method selection."""
        if method == RiskMethod.LEVEL_BASED:
            # Show error message and revert to previous method
            self._show_level_based_error()
            # Revert to percentage method
            if 'risk_method' in self.input_widgets:
                self.input_widgets['risk_method'].set(RiskMethod.PERCENTAGE.value)
            method = RiskMethod.PERCENTAGE

        super().show_method_fields(method)

    def _show_level_based_error(self) -> None:
        """Show error message for level-based method attempt."""
        self.show_calculation_error(
            "Level-based risk method is not supported for options trading.\n"
            "Please use Percentage or Fixed Amount method."
        )

    def _format_calculation_result(self, result_data: Dict[str, Any]) -> str:
        """Format options calculation result for display."""
        result_text = "=== OPTIONS POSITION CALCULATION ===\n\n"

        # Basic results
        contracts = result_data.get('position_size', 0)
        estimated_risk = result_data.get('estimated_risk', 0)
        risk_method = result_data.get('risk_method', 'Unknown')
        total_premium_cost = result_data.get('total_premium_cost', 0)
        premium_per_share = result_data.get('premium_per_share', 0)
        contract_multiplier = result_data.get('contract_multiplier', 100)

        result_text += f"Number of Contracts: {contracts:,}\n"
        result_text += f"Premium per Share: ${premium_per_share:.2f}\n"
        result_text += f"Contract Multiplier: {contract_multiplier}\n"
        result_text += f"Total Premium Cost: ${total_premium_cost:.2f}\n"
        result_text += f"Estimated Risk: ${estimated_risk:.2f}\n"
        result_text += f"Risk Method: {risk_method.replace('_', ' ').title()}\n\n"

        # Contract details
        result_text += "=== CONTRACT DETAILS ===\n"
        if self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                result_text += f"Option Symbol: {trade_data.get('option_symbol', 'N/A')}\n"
                result_text += f"Direction: {trade_data.get('trade_direction', 'N/A')}\n"
                result_text += f"Account Size: ${trade_data.get('account_size', 0):.2f}\n"

                if risk_method == 'percentage':
                    result_text += f"Risk Percentage: {trade_data.get('risk_percentage', 0):.1f}%\n"
                elif risk_method == 'fixed_amount':
                    result_text += f"Fixed Risk Amount: ${trade_data.get('fixed_risk_amount', 0):.2f}\n"

            except Exception:
                result_text += "Trade details unavailable\n"

        # Cost analysis
        result_text += "\n=== COST ANALYSIS ===\n"
        if contracts > 0:
            cost_per_contract = total_premium_cost / contracts if contracts > 0 else 0
            result_text += f"Cost per Contract: ${cost_per_contract:.2f}\n"

            if self.controller:
                try:
                    trade_data = self.controller.get_current_trade_data()
                    account_size = trade_data.get('account_size', 0)
                    if account_size > 0:
                        cost_percentage = (total_premium_cost / account_size) * 100
                        result_text += f"Cost as % of Account: {cost_percentage:.2f}%\n"

                        if cost_percentage <= 2:
                            result_text += "✅ Conservative position size\n"
                        elif cost_percentage <= 5:
                            result_text += "✅ Moderate position size\n"
                        elif cost_percentage <= 10:
                            result_text += "⚠️  Larger position size\n"
                        else:
                            result_text += "🔴 High position size relative to account\n"

                except Exception:
                    pass

        # Risk analysis specific to options
        result_text += "\n=== OPTIONS RISK ANALYSIS ===\n"
        result_text += "• Maximum loss is limited to premium paid\n"
        result_text += "• Options can expire worthless\n"
        result_text += "• Time decay affects option value\n"

        if contracts > 0:
            # Calculate some basic metrics
            if premium_per_share > 0:
                breakeven_move_pct = (premium_per_share / 100) * 100  # Rough estimate
                result_text += f"• Estimated breakeven move needed: {breakeven_move_pct:.1f}%\n"

            # Position size warnings
            if contracts > 50:
                result_text += "⚠️  Large number of contracts - ensure adequate liquidity\n"
            elif contracts > 100:
                result_text += "🔴 Very large position - consider market impact\n"

        return result_text

    def get_option_greeks_display(self) -> str:
        """Get display text for option greeks (placeholder for future enhancement)."""
        return (
            "Option Greeks (Enhancement Opportunity):\n"
            "• Delta: Price sensitivity\n"
            "• Gamma: Delta sensitivity\n"
            "• Theta: Time decay\n"
            "• Vega: Volatility sensitivity\n"
            "• Rho: Interest rate sensitivity"
        )

    def show_premium_analysis(self, premium_data: Dict[str, Any]) -> None:
        """Show premium analysis information."""
        if not premium_data:
            return

        # Add premium analysis to result text
        current_text = self.result_text.get(1.0, tk.END)
        self.result_text.configure(state="normal")

        self.result_text.insert(tk.END, "\n=== PREMIUM ANALYSIS ===\n")

        # Show intrinsic vs extrinsic value if available
        if 'intrinsic_value' in premium_data:
            intrinsic = premium_data['intrinsic_value']
            extrinsic = premium_data.get('extrinsic_value', 0)
            result_text += f"Intrinsic Value: ${intrinsic:.2f}\n"
            result_text += f"Extrinsic Value: ${extrinsic:.2f}\n"

        # Show implied volatility if available
        if 'implied_volatility' in premium_data:
            iv = premium_data['implied_volatility']
            result_text += f"Implied Volatility: {iv:.1f}%\n"

        self.result_text.configure(state="disabled")

    def validate_option_inputs(self) -> List[str]:
        """Validate option-specific inputs."""
        warnings = []

        if not self.controller:
            return warnings

        try:
            trade_data = self.controller.get_current_trade_data()
            premium = trade_data.get('premium', 0)
            multiplier = trade_data.get('contract_multiplier', 100)
            account_size = trade_data.get('account_size', 0)

            # Check premium reasonableness
            if premium > 0:
                if premium < 0.01:
                    warnings.append("Very low premium - check for penny stocks")
                elif premium > 50:
                    warnings.append("Very high premium - verify option symbol")

            # Check contract multiplier
            if multiplier != 100:
                warnings.append("Non-standard contract multiplier detected")

            # Check account size vs premium
            if account_size > 0 and premium > 0:
                max_contracts = int(account_size / (premium * multiplier))
                if max_contracts < 1:
                    warnings.append("Premium cost exceeds account size")

        except Exception:
            pass

        return warnings

    def get_option_strategy_suggestions(self) -> List[str]:
        """Get option strategy suggestions based on current inputs."""
        suggestions = []

        if not self.controller:
            return suggestions

        try:
            trade_data = self.controller.get_current_trade_data()
            direction = trade_data.get('trade_direction', 'LONG')

            if direction == 'LONG':
                suggestions.extend([
                    "Consider call options for bullish outlook",
                    "Consider put options for bearish outlook or hedging",
                    "Review time to expiration for theta decay impact"
                ])
            else:  # SHORT
                suggestions.extend([
                    "Selling options requires margin account",
                    "Consider covered strategies to limit risk",
                    "Monitor assignment risk near expiration"
                ])

            suggestions.append("Always have an exit strategy planned")

        except Exception:
            pass

        return suggestions

    def show_expiration_warnings(self, days_to_expiration: int) -> None:
        """Show warnings based on days to expiration."""
        if days_to_expiration <= 0:
            self.show_warnings(["⚠️ Option has expired or expires today!"])
        elif days_to_expiration <= 7:
            self.show_warnings([f"⚠️ Option expires in {days_to_expiration} days - high theta decay"])
        elif days_to_expiration <= 30:
            self.show_warnings([f"ℹ️ Option expires in {days_to_expiration} days - monitor time decay"])

    def update_options_ui_state(self, state_data: Dict[str, Any]) -> None:
        """Update UI state based on options-specific data."""
        # Enable/disable widgets based on trade direction
        direction = state_data.get('trade_direction', 'LONG')

        # Update labels and hints based on direction
        if direction == 'LONG':
            # Buying options - risk is limited to premium
            pass
        else:
            # Selling options - may require different risk considerations
            pass

        # Update validation messages
        if state_data.get('show_margin_warning'):
            self.show_warnings(["Selling options may require margin account approval"])