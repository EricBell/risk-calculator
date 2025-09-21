"""Futures trading tab with tick value inputs and margin requirements."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional
from decimal import Decimal
from .base_tab import BaseTradingTab
from ..models.risk_method import RiskMethod


class FuturesTab(BaseTradingTab):
    """Futures trading tab supporting all three risk methods with futures-specific inputs."""

    def _create_asset_specific_widgets(self, start_row: int) -> int:
        """Create futures-specific input widgets."""
        row = start_row

        # Contract symbol
        ttk.Label(self.input_frame, text="Contract Symbol:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        symbol_entry = ttk.Entry(self.input_frame)
        symbol_entry.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['contract_symbol'] = symbol_entry
        self._add_validation_label('contract_symbol', row)
        row += 1

        # Entry price
        ttk.Label(self.input_frame, text="Entry Price:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        entry_price = ttk.Entry(self.input_frame)
        entry_price.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['entry_price'] = entry_price
        self._add_validation_label('entry_price', row)
        row += 1

        # Tick value
        ttk.Label(self.input_frame, text="Tick Value ($):").grid(row=row, column=0, sticky="w", padx=(0, 10))
        tick_value_frame = ttk.Frame(self.input_frame)
        tick_value_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        tick_value_frame.grid_columnconfigure(0, weight=1)

        tick_value_entry = ttk.Entry(tick_value_frame)
        tick_value_entry.grid(row=0, column=0, sticky="ew")
        self.input_widgets['tick_value'] = tick_value_entry

        ttk.Label(tick_value_frame, text="per tick", font=("TkDefaultFont", 8)).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )
        self._add_validation_label('tick_value', row)
        row += 1

        # Tick size
        ttk.Label(self.input_frame, text="Tick Size:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        tick_size_frame = ttk.Frame(self.input_frame)
        tick_size_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        tick_size_frame.grid_columnconfigure(0, weight=1)

        tick_size_entry = ttk.Entry(tick_size_frame)
        tick_size_entry.grid(row=0, column=0, sticky="ew")
        self.input_widgets['tick_size'] = tick_size_entry

        ttk.Label(tick_size_frame, text="minimum price increment", font=("TkDefaultFont", 8)).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )
        self._add_validation_label('tick_size', row)
        row += 1

        # Margin requirement
        ttk.Label(self.input_frame, text="Initial Margin ($):").grid(row=row, column=0, sticky="w", padx=(0, 10))
        margin_frame = ttk.Frame(self.input_frame)
        margin_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        margin_frame.grid_columnconfigure(0, weight=1)

        margin_entry = ttk.Entry(margin_frame)
        margin_entry.grid(row=0, column=0, sticky="ew")
        self.input_widgets['margin_requirement'] = margin_entry

        ttk.Label(margin_frame, text="per contract", font=("TkDefaultFont", 8)).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )
        self._add_validation_label('margin_requirement', row)
        row += 1

        # Trade direction
        ttk.Label(self.input_frame, text="Direction:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        direction_frame = ttk.Frame(self.input_frame)
        direction_frame.grid(row=row, column=1, sticky="ew", padx=(0, 10))

        direction_var = tk.StringVar(value="LONG")
        self.input_widgets['trade_direction'] = direction_var

        long_rb = ttk.Radiobutton(direction_frame, text="Long", variable=direction_var, value="LONG")
        long_rb.grid(row=0, column=0, sticky="w")
        short_rb = ttk.Radiobutton(direction_frame, text="Short", variable=direction_var, value="SHORT")
        short_rb.grid(row=0, column=1, sticky="w", padx=(20, 0))
        row += 1

        # Add futures-specific information panel
        self._create_futures_info_panel(row)
        row += 1

        # Add margin utilization display
        self._create_margin_display(row)
        row += 1

        return row

    def _create_futures_info_panel(self, row: int) -> None:
        """Create informational panel about futures trading."""
        info_frame = ttk.LabelFrame(self.input_frame, text="Futures Trading Info", padding="5")
        info_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        info_text = (
            "• Tick Value: Dollar amount gained/lost per tick movement\n"
            "• Tick Size: Minimum price increment for the contract\n"
            "• Initial Margin: Required deposit per contract\n"
            "• Futures are leveraged instruments with margin requirements"
        )

        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("TkDefaultFont", 8),
            foreground="gray",
            justify="left"
        )
        info_label.grid(row=0, column=0, sticky="w")

    def _create_margin_display(self, row: int) -> None:
        """Create margin utilization display."""
        self.margin_frame = ttk.LabelFrame(self.input_frame, text="Margin Analysis", padding="5")
        self.margin_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Margin utilization labels
        self.margin_labels = {
            'utilization': ttk.Label(self.margin_frame, text="Margin Utilization: N/A"),
            'available': ttk.Label(self.margin_frame, text="Available Margin: N/A"),
            'total_required': ttk.Label(self.margin_frame, text="Total Margin Required: N/A")
        }

        for i, (key, label) in enumerate(self.margin_labels.items()):
            label.grid(row=i, column=0, sticky="w", pady=2)

    def _get_supported_methods(self) -> List[RiskMethod]:
        """Return all risk methods supported by futures trading."""
        return [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]

    def _create_percentage_method_frame(self) -> None:
        """Create percentage method frame with stop loss field."""
        super()._create_percentage_method_frame()
        frame = self.method_frames[RiskMethod.PERCENTAGE]

        # Add stop loss field
        ttk.Label(frame, text="Stop Loss Price:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        stop_loss_entry = ttk.Entry(frame)
        stop_loss_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(10, 0))
        self.input_widgets['stop_loss_price'] = stop_loss_entry
        self._add_method_validation_label('stop_loss_price', frame, 1)

    def _create_fixed_amount_method_frame(self) -> None:
        """Create fixed amount method frame with stop loss field."""
        super()._create_fixed_amount_method_frame()
        frame = self.method_frames[RiskMethod.FIXED_AMOUNT]

        # Add stop loss field
        ttk.Label(frame, text="Stop Loss Price:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        stop_loss_entry = ttk.Entry(frame)
        stop_loss_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(10, 0))

        # Handle multiple stop loss entries like in equity tab
        if 'stop_loss_price' not in self.input_widgets:
            self.input_widgets['stop_loss_price'] = stop_loss_entry

        self._add_method_validation_label('stop_loss_price_fixed', frame, 1)

    def show_method_fields(self, method: RiskMethod) -> None:
        """Override to handle stop loss field references properly."""
        super().show_method_fields(method)

        # Update stop loss field reference based on current method
        if method == RiskMethod.PERCENTAGE:
            frame = self.method_frames[RiskMethod.PERCENTAGE]
            for child in frame.winfo_children():
                if isinstance(child, ttk.Entry) and child.grid_info().get('row') == 1:
                    self.input_widgets['stop_loss_price'] = child
                    break
        elif method == RiskMethod.FIXED_AMOUNT:
            frame = self.method_frames[RiskMethod.FIXED_AMOUNT]
            for child in frame.winfo_children():
                if isinstance(child, ttk.Entry) and child.grid_info().get('row') == 1:
                    self.input_widgets['stop_loss_price'] = child
                    break

        # Re-bind controller variables
        if self.controller and hasattr(self.controller, 'tk_vars'):
            if 'stop_loss_price' in self.controller.tk_vars and 'stop_loss_price' in self.input_widgets:
                widget = self.input_widgets['stop_loss_price']
                if isinstance(widget, ttk.Entry):
                    widget.configure(textvariable=self.controller.tk_vars['stop_loss_price'])

        # Update margin display
        self.update_margin_display()

    def update_margin_display(self) -> None:
        """Update margin utilization display."""
        if not self.controller:
            return

        try:
            margin_info = self.controller.get_margin_utilization()

            utilization = margin_info.get('utilization_percentage', 0)
            available = margin_info.get('available_margin', 0)
            total_required = margin_info.get('total_margin_required', 0)

            self.margin_labels['utilization'].configure(text=f"Margin Utilization: {utilization:.1f}%")
            self.margin_labels['available'].configure(text=f"Available Margin: ${available:.2f}")
            self.margin_labels['total_required'].configure(text=f"Total Margin Required: ${total_required:.2f}")

            # Color code utilization
            if utilization > 80:
                color = "red"
            elif utilization > 60:
                color = "orange"
            else:
                color = "green"

            self.margin_labels['utilization'].configure(foreground=color)

        except Exception:
            # Reset to N/A if calculation fails
            for label in self.margin_labels.values():
                label.configure(text=label.cget('text').split(':')[0] + ": N/A", foreground="black")

    def _format_calculation_result(self, result_data: Dict[str, Any]) -> str:
        """Format futures calculation result for display."""
        result_text = "=== FUTURES POSITION CALCULATION ===\n\n"

        # Basic results
        contracts = result_data.get('position_size', 0)
        estimated_risk = result_data.get('estimated_risk', 0)
        risk_method = result_data.get('risk_method', 'Unknown')
        ticks_at_risk = result_data.get('ticks_at_risk', 0)
        tick_value = result_data.get('tick_value', 0)
        tick_size = result_data.get('tick_size', 0)
        margin_per_contract = result_data.get('margin_per_contract', 0)
        total_margin = result_data.get('total_margin_required', 0)
        available_margin = result_data.get('available_margin', 0)

        result_text += f"Number of Contracts: {contracts:,}\n"
        result_text += f"Estimated Risk: ${estimated_risk:.2f}\n"
        result_text += f"Risk Method: {risk_method.replace('_', ' ').title()}\n"
        result_text += f"Ticks at Risk: {ticks_at_risk}\n"
        result_text += f"Tick Value: ${tick_value:.2f}\n"
        result_text += f"Tick Size: {tick_size}\n\n"

        # Margin analysis
        result_text += "=== MARGIN ANALYSIS ===\n"
        result_text += f"Margin per Contract: ${margin_per_contract:.2f}\n"
        result_text += f"Total Margin Required: ${total_margin:.2f}\n"
        result_text += f"Available Margin: ${available_margin:.2f}\n"

        if total_margin > 0 and self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                account_size = trade_data.get('account_size', 0)
                if account_size > 0:
                    utilization = (total_margin / account_size) * 100
                    result_text += f"Margin Utilization: {utilization:.1f}%\n"

                    if utilization <= 25:
                        result_text += "✅ Conservative margin usage\n"
                    elif utilization <= 50:
                        result_text += "✅ Moderate margin usage\n"
                    elif utilization <= 75:
                        result_text += "⚠️  Higher margin usage\n"
                    else:
                        result_text += "🔴 High margin usage - monitor carefully\n"
            except Exception:
                pass

        result_text += "\n=== CONTRACT DETAILS ===\n"
        if self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                result_text += f"Contract Symbol: {trade_data.get('contract_symbol', 'N/A')}\n"
                result_text += f"Entry Price: {trade_data.get('entry_price', 0)}\n"
                result_text += f"Direction: {trade_data.get('trade_direction', 'N/A')}\n"

                if risk_method == 'percentage':
                    result_text += f"Risk Percentage: {trade_data.get('risk_percentage', 0):.1f}%\n"
                    result_text += f"Stop Loss: {trade_data.get('stop_loss_price', 0)}\n"
                elif risk_method == 'fixed_amount':
                    result_text += f"Fixed Risk Amount: ${trade_data.get('fixed_risk_amount', 0):.2f}\n"
                    result_text += f"Stop Loss: {trade_data.get('stop_loss_price', 0)}\n"
                elif risk_method == 'level_based':
                    result_text += f"Support/Resistance: {trade_data.get('support_resistance_level', 0)}\n"

                result_text += f"Account Size: ${trade_data.get('account_size', 0):.2f}\n"

            except Exception:
                result_text += "Trade details unavailable\n"

        # Risk analysis specific to futures
        result_text += "\n=== FUTURES RISK ANALYSIS ===\n"
        if contracts > 0:
            # Calculate risk per tick
            risk_per_tick = tick_value * contracts if tick_value > 0 else 0
            result_text += f"Risk per Tick Movement: ${risk_per_tick:.2f}\n"

            # Daily limit considerations
            if ticks_at_risk > 0:
                result_text += f"Price Movement Needed: {ticks_at_risk} ticks\n"

            # Leverage analysis
            if total_margin > 0 and estimated_risk > 0:
                leverage_ratio = estimated_risk / total_margin
                result_text += f"Effective Leverage Ratio: {leverage_ratio:.1f}:1\n"

        result_text += "\n=== FUTURES TRADING REMINDERS ===\n"
        result_text += "• Futures are highly leveraged instruments\n"
        result_text += "• Monitor margin requirements daily\n"
        result_text += "• Be aware of daily price limits\n"
        result_text += "• Consider rollover dates for expiring contracts\n"

        if available_margin < total_margin * 0.5:  # Less than 50% buffer
            result_text += "⚠️  Low margin buffer - consider position size\n"

        return result_text

    def show_tick_analysis(self, tick_data: Dict[str, Any]) -> None:
        """Show tick movement analysis."""
        if not tick_data:
            return

        current_text = self.result_text.get(1.0, tk.END)
        self.result_text.configure(state="normal")

        self.result_text.insert(tk.END, "\n=== TICK ANALYSIS ===\n")

        daily_range = tick_data.get('daily_tick_range', 0)
        avg_range = tick_data.get('average_tick_range', 0)

        if daily_range > 0:
            self.result_text.insert(tk.END, f"Daily Tick Range: {daily_range} ticks\n")

        if avg_range > 0:
            self.result_text.insert(tk.END, f"Average Daily Range: {avg_range} ticks\n")

        self.result_text.configure(state="disabled")

    def validate_futures_inputs(self) -> List[str]:
        """Validate futures-specific inputs."""
        warnings = []

        if not self.controller:
            return warnings

        try:
            trade_data = self.controller.get_current_trade_data()
            tick_value = trade_data.get('tick_value', 0)
            tick_size = trade_data.get('tick_size', 0)
            margin = trade_data.get('margin_requirement', 0)
            entry_price = trade_data.get('entry_price', 0)

            # Validate tick relationships
            if tick_value > 0 and tick_size > 0:
                # Check for reasonable tick value to size ratio
                value_per_point = tick_value / tick_size if tick_size > 0 else 0
                if value_per_point > 1000:
                    warnings.append("Very high tick value relative to tick size")

            # Validate margin vs entry price
            if margin > 0 and entry_price > 0:
                if margin > entry_price:
                    warnings.append("Margin requirement exceeds entry price - verify values")

            # Check for common contract specifications
            common_specs = self._get_common_contract_specs()
            symbol = trade_data.get('contract_symbol', '').upper()

            if symbol and symbol in common_specs:
                spec = common_specs[symbol]
                if tick_value > 0 and abs(tick_value - spec['tick_value']) > 0.01:
                    warnings.append(f"Tick value differs from standard {symbol} specification")

        except Exception:
            pass

        return warnings

    def _get_common_contract_specs(self) -> Dict[str, Dict]:
        """Get common futures contract specifications."""
        return {
            'ES': {'tick_value': 12.50, 'tick_size': 0.25, 'name': 'E-mini S&P 500'},
            'NQ': {'tick_value': 5.00, 'tick_size': 0.25, 'name': 'E-mini NASDAQ'},
            'YM': {'tick_value': 5.00, 'tick_size': 1.00, 'name': 'E-mini Dow'},
            'CL': {'tick_value': 10.00, 'tick_size': 0.01, 'name': 'Crude Oil'},
            'GC': {'tick_value': 10.00, 'tick_size': 0.10, 'name': 'Gold'},
            'SI': {'tick_value': 25.00, 'tick_size': 0.005, 'name': 'Silver'},
            'ZB': {'tick_value': 31.25, 'tick_size': 0.03125, 'name': '30-Year Treasury Bond'},
            'ZN': {'tick_value': 15.625, 'tick_size': 0.015625, 'name': '10-Year Treasury Note'}
        }

    def show_contract_specifications(self, symbol: str) -> None:
        """Show contract specifications for common futures."""
        specs = self._get_common_contract_specs()

        if symbol.upper() in specs:
            spec = specs[symbol.upper()]

            # Auto-fill common values
            if hasattr(self, 'input_widgets'):
                if 'tick_value' in self.input_widgets:
                    self.input_widgets['tick_value'].delete(0, tk.END)
                    self.input_widgets['tick_value'].insert(0, str(spec['tick_value']))

                if 'tick_size' in self.input_widgets:
                    self.input_widgets['tick_size'].delete(0, tk.END)
                    self.input_widgets['tick_size'].insert(0, str(spec['tick_size']))

            # Show specification info
            self.show_warnings([f"Auto-filled specs for {spec['name']} ({symbol.upper()})"])

    def get_margin_alerts(self) -> List[str]:
        """Get margin-related alerts."""
        alerts = []

        if not self.controller:
            return alerts

        try:
            margin_info = self.controller.get_margin_utilization()
            utilization = margin_info.get('utilization_percentage', 0)
            available = margin_info.get('available_margin', 0)

            if utilization > 90:
                alerts.append("🔴 Margin utilization very high - risk of margin call")
            elif utilization > 75:
                alerts.append("⚠️  High margin utilization - monitor closely")

            if available < 1000:  # Less than $1000 available
                alerts.append("⚠️  Low available margin - consider reducing position")

        except Exception:
            pass

        return alerts

    def _on_calculate_clicked(self) -> None:
        """Override to update margin display after calculation."""
        super()._on_calculate_clicked()
        self.after_idle(self.update_margin_display)

    def show_leverage_warning(self, leverage_ratio: float) -> None:
        """Show leverage warning based on calculated ratio."""
        if leverage_ratio > 10:
            self.show_warnings([
                f"⚠️  High leverage ratio: {leverage_ratio:.1f}:1",
                "Consider reducing position size for better risk management"
            ])
        elif leverage_ratio > 20:
            self.show_warnings([
                f"🔴 Very high leverage: {leverage_ratio:.1f}:1",
                "Extreme risk - strongly consider reducing position"
            ])