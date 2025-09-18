"""Equity trading tab with all three risk method fields and equity-specific UI."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional
from .base_tab import BaseTradingTab
from ..models.risk_method import RiskMethod


class EquityTab(BaseTradingTab):
    """Equity trading tab supporting percentage, fixed amount, and level-based risk methods."""

    def _create_asset_specific_widgets(self, start_row: int) -> int:
        """Create equity-specific input widgets."""
        row = start_row

        # Stock symbol
        ttk.Label(self.input_frame, text="Stock Symbol:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        symbol_entry = ttk.Entry(self.input_frame, width=10)
        symbol_entry.grid(row=row, column=1, sticky="w", padx=(0, 10))
        self.input_widgets['symbol'] = symbol_entry
        self._add_validation_label('symbol', row)
        row += 1

        # Entry price
        ttk.Label(self.input_frame, text="Entry Price ($):").grid(row=row, column=0, sticky="w", padx=(0, 10))
        entry_price = ttk.Entry(self.input_frame, width=15)
        entry_price.grid(row=row, column=1, sticky="w", padx=(0, 10))
        self.input_widgets['entry_price'] = entry_price
        self._add_validation_label('entry_price', row)
        row += 1

        # Trade direction
        ttk.Label(self.input_frame, text="Direction:").grid(row=row, column=0, sticky="w", padx=(0, 10))
        direction_frame = ttk.Frame(self.input_frame)
        direction_frame.grid(row=row, column=1, sticky="w", padx=(0, 10))

        direction_var = tk.StringVar(value="LONG")
        self.input_widgets['trade_direction'] = direction_var

        long_rb = ttk.Radiobutton(direction_frame, text="Long", variable=direction_var, value="LONG")
        long_rb.grid(row=0, column=0, sticky="w")
        short_rb = ttk.Radiobutton(direction_frame, text="Short", variable=direction_var, value="SHORT")
        short_rb.grid(row=0, column=1, sticky="w", padx=(20, 0))
        row += 1

        return row

    def _get_supported_methods(self) -> List[RiskMethod]:
        """Return all risk methods supported by equity trading."""
        return [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]

    def _create_percentage_method_frame(self) -> None:
        """Create percentage method frame with stop loss field."""
        super()._create_percentage_method_frame()
        frame = self.method_frames[RiskMethod.PERCENTAGE]

        # Add stop loss field
        ttk.Label(frame, text="Stop Loss Price ($):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        stop_loss_entry = ttk.Entry(frame, width=15)
        stop_loss_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
        self.input_widgets['stop_loss_price'] = stop_loss_entry
        self._add_method_validation_label('stop_loss_price', frame, 1)

    def _create_fixed_amount_method_frame(self) -> None:
        """Create fixed amount method frame with stop loss field."""
        super()._create_fixed_amount_method_frame()
        frame = self.method_frames[RiskMethod.FIXED_AMOUNT]

        # Add stop loss field
        ttk.Label(frame, text="Stop Loss Price ($):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        stop_loss_entry = ttk.Entry(frame, width=15)
        stop_loss_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(10, 0))

        # Note: We need different widget reference for different methods
        # This is handled in show_method_fields by updating the reference
        if 'stop_loss_price' not in self.input_widgets:
            self.input_widgets['stop_loss_price'] = stop_loss_entry

        self._add_method_validation_label('stop_loss_price_fixed', frame, 1)

    def show_method_fields(self, method: RiskMethod) -> None:
        """Override to handle stop loss field references properly."""
        super().show_method_fields(method)

        # Update stop loss field reference based on current method
        if method == RiskMethod.PERCENTAGE:
            frame = self.method_frames[RiskMethod.PERCENTAGE]
            # Find stop loss entry in percentage frame
            for child in frame.winfo_children():
                if isinstance(child, ttk.Entry) and child.grid_info().get('row') == 1:
                    self.input_widgets['stop_loss_price'] = child
                    break
        elif method == RiskMethod.FIXED_AMOUNT:
            frame = self.method_frames[RiskMethod.FIXED_AMOUNT]
            # Find stop loss entry in fixed amount frame
            for child in frame.winfo_children():
                if isinstance(child, ttk.Entry) and child.grid_info().get('row') == 1:
                    self.input_widgets['stop_loss_price'] = child
                    break

        # Re-bind controller variables if controller is available
        if self.controller and hasattr(self.controller, 'tk_vars'):
            if 'stop_loss_price' in self.controller.tk_vars and 'stop_loss_price' in self.input_widgets:
                widget = self.input_widgets['stop_loss_price']
                if isinstance(widget, ttk.Entry):
                    widget.configure(textvariable=self.controller.tk_vars['stop_loss_price'])

    def _format_calculation_result(self, result_data: Dict[str, Any]) -> str:
        """Format equity calculation result for display."""
        result_text = "=== EQUITY POSITION CALCULATION ===\n\n"

        # Basic results
        position_size = result_data.get('position_size', 0)
        estimated_risk = result_data.get('estimated_risk', 0)
        risk_method = result_data.get('risk_method', 'Unknown')
        position_value = result_data.get('position_value', 0)

        result_text += f"Position Size: {position_size:,} shares\n"
        result_text += f"Estimated Risk: ${estimated_risk:.2f}\n"
        result_text += f"Position Value: ${position_value:.2f}\n"
        result_text += f"Risk Method: {risk_method.replace('_', ' ').title()}\n\n"

        # Method-specific details
        if self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                result_text += "=== TRADE DETAILS ===\n"
                result_text += f"Symbol: {trade_data.get('symbol', 'N/A')}\n"
                result_text += f"Entry Price: ${trade_data.get('entry_price', 0):.2f}\n"
                result_text += f"Direction: {trade_data.get('trade_direction', 'N/A')}\n"

                if risk_method == 'percentage':
                    result_text += f"Risk Percentage: {trade_data.get('risk_percentage', 0):.1f}%\n"
                    result_text += f"Stop Loss: ${trade_data.get('stop_loss_price', 0):.2f}\n"
                    if trade_data.get('entry_price') and trade_data.get('stop_loss_price'):
                        risk_per_share = abs(trade_data['entry_price'] - trade_data['stop_loss_price'])
                        result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

                elif risk_method == 'fixed_amount':
                    result_text += f"Fixed Risk: ${trade_data.get('fixed_risk_amount', 0):.2f}\n"
                    result_text += f"Stop Loss: ${trade_data.get('stop_loss_price', 0):.2f}\n"
                    if trade_data.get('entry_price') and trade_data.get('stop_loss_price'):
                        risk_per_share = abs(trade_data['entry_price'] - trade_data['stop_loss_price'])
                        result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

                elif risk_method == 'level_based':
                    result_text += f"Support/Resistance: ${trade_data.get('support_resistance_level', 0):.2f}\n"
                    if trade_data.get('entry_price') and trade_data.get('support_resistance_level'):
                        risk_per_share = abs(trade_data['entry_price'] - trade_data['support_resistance_level'])
                        result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

                result_text += f"\nAccount Size: ${trade_data.get('account_size', 0):.2f}\n"

            except Exception:
                result_text += "Trade details unavailable\n"

        # Position sizing guidelines
        result_text += "\n=== POSITION GUIDELINES ===\n"
        if position_value > 0 and self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                account_size = trade_data.get('account_size', 0)
                if account_size > 0:
                    position_percentage = (position_value / account_size) * 100
                    result_text += f"Position as % of Account: {position_percentage:.1f}%\n"

                    if position_percentage > 25:
                        result_text += "⚠️  Position exceeds 25% of account\n"
                    elif position_percentage > 10:
                        result_text += "ℹ️  Large position (>10% of account)\n"
                    else:
                        result_text += "✅ Position size is reasonable\n"

            except Exception:
                pass

        result_text += "\n=== RISK ANALYSIS ===\n"
        if estimated_risk > 0 and self.controller:
            try:
                trade_data = self.controller.get_current_trade_data()
                account_size = trade_data.get('account_size', 0)
                if account_size > 0:
                    risk_percentage = (estimated_risk / account_size) * 100
                    result_text += f"Risk as % of Account: {risk_percentage:.2f}%\n"

                    if risk_percentage <= 1:
                        result_text += "✅ Conservative risk level\n"
                    elif risk_percentage <= 2:
                        result_text += "✅ Moderate risk level\n"
                    elif risk_percentage <= 3:
                        result_text += "⚠️  Higher risk level\n"
                    else:
                        result_text += "🔴 High risk level\n"

            except Exception:
                pass

        return result_text

    def get_equity_specific_info(self) -> Dict[str, Any]:
        """Get equity-specific information for advanced features."""
        if not self.controller:
            return {}

        try:
            trade_data = self.controller.get_current_trade_data()
            info = {
                'symbol': trade_data.get('symbol', ''),
                'entry_price': trade_data.get('entry_price', 0),
                'stop_loss_price': trade_data.get('stop_loss_price', 0),
                'support_resistance_level': trade_data.get('support_resistance_level', 0),
                'trade_direction': trade_data.get('trade_direction', 'LONG'),
                'current_method': self.current_method.value
            }

            # Calculate additional metrics
            if info['entry_price'] and info['stop_loss_price']:
                info['risk_per_share'] = abs(info['entry_price'] - info['stop_loss_price'])
                info['risk_reward_ratio'] = self._calculate_risk_reward_ratio(trade_data)

            return info

        except Exception:
            return {}

    def _calculate_risk_reward_ratio(self, trade_data: Dict) -> Optional[float]:
        """Calculate risk-reward ratio for equity trade."""
        try:
            entry_price = trade_data.get('entry_price', 0)
            stop_loss = trade_data.get('stop_loss_price', 0)
            direction = trade_data.get('trade_direction', 'LONG')

            if not entry_price or not stop_loss:
                return None

            risk_per_share = abs(entry_price - stop_loss)

            # For calculation purposes, assume 2:1 risk-reward target
            if direction == 'LONG':
                target_price = entry_price + (2 * risk_per_share)
                reward_per_share = target_price - entry_price
            else:  # SHORT
                target_price = entry_price - (2 * risk_per_share)
                reward_per_share = entry_price - target_price

            if risk_per_share > 0:
                return reward_per_share / risk_per_share

        except Exception:
            pass

        return None

    def show_price_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """Show price-based alerts or notifications."""
        if not alerts:
            return

        # Add alerts to result text
        current_text = self.result_text.get(1.0, tk.END)
        self.result_text.configure(state="normal")

        self.result_text.insert(tk.END, "\n=== PRICE ALERTS ===\n")
        for alert in alerts:
            alert_text = f"📊 {alert.get('message', 'Alert')}\n"
            self.result_text.insert(tk.END, alert_text)

        self.result_text.configure(state="disabled")

    def validate_price_relationships(self) -> List[str]:
        """Validate price relationships for equity trades."""
        warnings = []

        if not self.controller:
            return warnings

        try:
            trade_data = self.controller.get_current_trade_data()
            entry_price = trade_data.get('entry_price', 0)
            stop_loss = trade_data.get('stop_loss_price', 0)
            support_resistance = trade_data.get('support_resistance_level', 0)
            direction = trade_data.get('trade_direction', 'LONG')

            # Check stop loss relationship
            if entry_price and stop_loss:
                if direction == 'LONG' and stop_loss >= entry_price:
                    warnings.append("Stop loss should be below entry price for long positions")
                elif direction == 'SHORT' and stop_loss <= entry_price:
                    warnings.append("Stop loss should be above entry price for short positions")

                # Check risk distance
                risk_distance = abs(entry_price - stop_loss)
                risk_percentage = (risk_distance / entry_price) * 100

                if risk_percentage < 0.5:
                    warnings.append("Stop loss very close to entry (< 0.5%)")
                elif risk_percentage > 10:
                    warnings.append("Stop loss very far from entry (> 10%)")

            # Check support/resistance relationship
            if entry_price and support_resistance:
                if direction == 'LONG' and support_resistance >= entry_price:
                    warnings.append("Support level should be below entry for long positions")
                elif direction == 'SHORT' and support_resistance <= entry_price:
                    warnings.append("Resistance level should be above entry for short positions")

        except Exception:
            pass

        return warnings