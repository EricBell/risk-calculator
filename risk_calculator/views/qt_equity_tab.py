"""
Qt Equity Trading Tab
Equity-specific UI with all risk methods and responsive Qt widgets.
"""

from typing import Dict, List, Any, Optional, Callable

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                   QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
                                   QRadioButton, QButtonGroup, QComboBox, QGroupBox)
    from PySide6.QtCore import Signal
    HAS_QT = True
except ImportError:
    HAS_QT = False

from .qt_base_view import QtBaseView
from ..models.risk_method import RiskMethod


class QtEquityTab(QtBaseView):
    """Qt-based equity trading tab with responsive layout."""

    # Additional signals for equity-specific events
    risk_method_changed = Signal(str)  # risk_method
    direction_changed = Signal(str)    # trade_direction

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize Qt equity tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Risk method management
        self.current_method = RiskMethod.PERCENTAGE
        self.method_frames: Dict[RiskMethod, QGroupBox] = {}
        self.risk_method_combo: Optional[QComboBox] = None

        # Trade direction
        self.direction_group: Optional[QButtonGroup] = None
        self.long_radio: Optional[QRadioButton] = None
        self.short_radio: Optional[QRadioButton] = None

        # Result display
        self.result_display: Optional[QTextEdit] = None

    def setup_ui(self) -> None:
        """Setup the equity tab UI components."""
        main_layout = self.create_main_layout()

        # Create input sections
        input_section = self._create_input_section()
        main_layout.addWidget(input_section)

        # Create risk method selection
        risk_method_section = self._create_risk_method_section()
        main_layout.addWidget(risk_method_section)

        # Create method-specific frames (initially hidden)
        self._create_method_frames()
        for method, frame in self.method_frames.items():
            main_layout.addWidget(frame)
            if method != self.current_method:
                frame.hide()

        # Create result section
        result_section = self._create_result_section()
        main_layout.addWidget(result_section)

        # Create calculate button
        calculate_btn = self.create_calculate_button("Calculate Equity Position")
        main_layout.addWidget(calculate_btn)

        # Add stretch to push everything to top
        main_layout.addStretch()

    def _create_input_section(self) -> QGroupBox:
        """
        Create basic input section for equity trading.

        Returns:
            QGroupBox: Input section widget
        """
        group = QGroupBox("Trade Information")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Account size
        label, field = self.create_form_field("account_size", "Account Size ($)", "10000", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("account_size")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Stock symbol
        label, field = self.create_form_field("symbol", "Stock Symbol", "AAPL", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("symbol")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Entry price
        label, field = self.create_form_field("entry_price", "Entry Price ($)", "150.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("entry_price")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Trade direction
        direction_label = QLabel("Trade Direction *")
        self.layout_service.apply_responsive_font_scaling(direction_label, 10)
        layout.addWidget(direction_label, row, 0)

        direction_frame = QFrame()
        direction_layout = QHBoxLayout(direction_frame)
        direction_layout.setContentsMargins(0, 0, 0, 0)

        self.direction_group = QButtonGroup()
        self.long_radio = QRadioButton("Long")
        self.short_radio = QRadioButton("Short")

        self.long_radio.setChecked(True)  # Default to long
        self.direction_group.addButton(self.long_radio, 0)
        self.direction_group.addButton(self.short_radio, 1)

        # Apply responsive scaling
        self.layout_service.apply_responsive_font_scaling(self.long_radio, 10)
        self.layout_service.apply_responsive_font_scaling(self.short_radio, 10)

        direction_layout.addWidget(self.long_radio)
        direction_layout.addWidget(self.short_radio)
        direction_layout.addStretch()

        layout.addWidget(direction_frame, row, 1)

        # Connect direction change signal
        self.direction_group.buttonClicked.connect(self._on_direction_changed)

        return group

    def _create_risk_method_section(self) -> QGroupBox:
        """
        Create risk method selection section.

        Returns:
            QGroupBox: Risk method selection widget
        """
        group = QGroupBox("Risk Method")
        layout = QHBoxLayout(group)

        method_label = QLabel("Risk Calculation Method:")
        self.layout_service.apply_responsive_font_scaling(method_label, 10)
        layout.addWidget(method_label)

        self.risk_method_combo = QComboBox()
        self.risk_method_combo.addItems([
            "Percentage-based Risk",
            "Fixed Amount Risk",
            "Level-based Risk"
        ])
        self.layout_service.apply_responsive_font_scaling(self.risk_method_combo, 10)

        # Connect method change signal
        self.risk_method_combo.currentIndexChanged.connect(self._on_risk_method_changed)

        layout.addWidget(self.risk_method_combo)
        layout.addStretch()

        return group

    def _create_method_frames(self) -> None:
        """Create method-specific input frames."""
        # Percentage method frame
        self.method_frames[RiskMethod.PERCENTAGE] = self._create_percentage_frame()

        # Fixed amount method frame
        self.method_frames[RiskMethod.FIXED_AMOUNT] = self._create_fixed_amount_frame()

        # Level-based method frame
        self.method_frames[RiskMethod.LEVEL_BASED] = self._create_level_based_frame()

    def _create_percentage_frame(self) -> QGroupBox:
        """
        Create percentage-based risk method frame.

        Returns:
            QGroupBox: Percentage method frame
        """
        group = QGroupBox("Percentage-based Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Risk percentage
        label, field = self.create_form_field("risk_percentage", "Risk Percentage (%)", "2.0", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("risk_percentage")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Stop loss price
        label, field = self.create_form_field("stop_loss_price", "Stop Loss Price ($)", "140.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("stop_loss_price")
        layout.addWidget(error_label, row, 2)

        return group

    def _create_fixed_amount_frame(self) -> QGroupBox:
        """
        Create fixed amount risk method frame.

        Returns:
            QGroupBox: Fixed amount method frame
        """
        group = QGroupBox("Fixed Amount Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Fixed risk amount
        label, field = self.create_form_field("fixed_risk_amount", "Fixed Risk Amount ($)", "200.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("fixed_risk_amount")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Stop loss price (separate field for fixed amount method)
        label, field = self.create_form_field("stop_loss_price_fixed", "Stop Loss Price ($)", "140.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("stop_loss_price_fixed")
        layout.addWidget(error_label, row, 2)

        return group

    def _create_level_based_frame(self) -> QGroupBox:
        """
        Create level-based risk method frame.

        Returns:
            QGroupBox: Level-based method frame
        """
        group = QGroupBox("Level-based Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Support/resistance level
        label, field = self.create_form_field("support_resistance_level", "Support/Resistance Level ($)", "135.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("support_resistance_level")
        layout.addWidget(error_label, row, 2)

        return group

    def _create_result_section(self) -> QGroupBox:
        """
        Create result display section.

        Returns:
            QGroupBox: Result section widget
        """
        group = QGroupBox("Calculation Results")
        layout = QVBoxLayout(group)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlainText("Enter trade details and click Calculate to see results...")

        # Apply responsive scaling
        self.layout_service.set_minimum_size(self.result_display, 400, 200)
        self.layout_service.apply_responsive_font_scaling(self.result_display, 9)

        layout.addWidget(self.result_display)

        return group

    def setup_input_fields(self) -> None:
        """Setup input field connections and validation."""
        # Field connections are handled in QtBaseView
        pass

    def setup_result_display(self) -> None:
        """Setup result display formatting."""
        if self.result_display:
            # Set monospace font for better alignment
            font = self.result_display.font()
            font.setFamily("Consolas, Monaco, monospace")
            self.result_display.setFont(font)

    def setup_risk_method_selection(self) -> None:
        """Setup risk method selection handling."""
        # Method selection is handled in _on_risk_method_changed
        pass

    def update_required_fields(self, risk_method: str) -> None:
        """
        Update required fields based on risk method.

        Args:
            risk_method: Current risk method
        """
        # Hide all method frames
        for frame in self.method_frames.values():
            frame.hide()

        # Show current method frame
        method_enum = self._get_risk_method_enum(risk_method)
        if method_enum and method_enum in self.method_frames:
            self.method_frames[method_enum].show()
            self.current_method = method_enum

    def display_calculation_result(self, result: Dict[str, Any]) -> None:
        """
        Display calculation result in the result area.

        Args:
            result: Calculation result data
        """
        if not self.result_display:
            return

        formatted_result = self._format_calculation_result(result)
        self.result_display.setPlainText(formatted_result)

    def clear_results(self) -> None:
        """Clear the results display."""
        if self.result_display:
            self.result_display.setPlainText("Enter trade details and click Calculate to see results...")

    def get_form_data(self) -> Dict[str, str]:
        """
        Get current form data including method-specific fields.

        Returns:
            Dict[str, str]: Complete form data
        """
        form_data = super().get_form_data()

        # Add trade direction
        if self.direction_group:
            if self.long_radio and self.long_radio.isChecked():
                form_data["trade_direction"] = "LONG"
            elif self.short_radio and self.short_radio.isChecked():
                form_data["trade_direction"] = "SHORT"

        # Add current risk method
        form_data["risk_method"] = self.current_method.value

        return form_data

    def _format_calculation_result(self, result_data: Dict[str, Any]) -> str:
        """
        Format equity calculation result for display.

        Args:
            result_data: Result data from calculation

        Returns:
            str: Formatted result text
        """
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

        # Trade details
        form_data = self.get_form_data()
        result_text += "=== TRADE DETAILS ===\n"
        result_text += f"Symbol: {form_data.get('symbol', 'N/A')}\n"
        result_text += f"Entry Price: ${float(form_data.get('entry_price', 0)):.2f}\n"
        result_text += f"Direction: {form_data.get('trade_direction', 'N/A')}\n"

        # Method-specific details
        if risk_method == 'percentage':
            result_text += f"Risk Percentage: {form_data.get('risk_percentage', 0)}%\n"
            result_text += f"Stop Loss: ${float(form_data.get('stop_loss_price', 0)):.2f}\n"

            entry_price = float(form_data.get('entry_price', 0))
            stop_loss = float(form_data.get('stop_loss_price', 0))
            if entry_price and stop_loss:
                risk_per_share = abs(entry_price - stop_loss)
                result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

        elif risk_method == 'fixed_amount':
            result_text += f"Fixed Risk: ${form_data.get('fixed_risk_amount', 0)}\n"
            result_text += f"Stop Loss: ${float(form_data.get('stop_loss_price_fixed', 0)):.2f}\n"

            entry_price = float(form_data.get('entry_price', 0))
            stop_loss = float(form_data.get('stop_loss_price_fixed', 0))
            if entry_price and stop_loss:
                risk_per_share = abs(entry_price - stop_loss)
                result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

        elif risk_method == 'level_based':
            result_text += f"Support/Resistance: ${float(form_data.get('support_resistance_level', 0)):.2f}\n"

            entry_price = float(form_data.get('entry_price', 0))
            level = float(form_data.get('support_resistance_level', 0))
            if entry_price and level:
                risk_per_share = abs(entry_price - level)
                result_text += f"Risk per Share: ${risk_per_share:.2f}\n"

        result_text += f"\nAccount Size: ${float(form_data.get('account_size', 0)):.2f}\n"

        # Position guidelines
        result_text += "\n=== POSITION GUIDELINES ===\n"
        account_size = float(form_data.get('account_size', 0))
        if position_value > 0 and account_size > 0:
            position_percentage = (position_value / account_size) * 100
            result_text += f"Position as % of Account: {position_percentage:.1f}%\n"

            if position_percentage > 25:
                result_text += "⚠️  Position exceeds 25% of account\n"
            elif position_percentage > 10:
                result_text += "ℹ️  Large position (>10% of account)\n"
            else:
                result_text += "✅ Position size is reasonable\n"

        # Risk analysis
        result_text += "\n=== RISK ANALYSIS ===\n"
        if estimated_risk > 0 and account_size > 0:
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

        return result_text

    def _on_risk_method_changed(self, index: int) -> None:
        """
        Handle risk method selection change.

        Args:
            index: Selected combo box index
        """
        method_map = {
            0: RiskMethod.PERCENTAGE,
            1: RiskMethod.FIXED_AMOUNT,
            2: RiskMethod.LEVEL_BASED
        }

        if index in method_map:
            self.update_required_fields(method_map[index].value)
            self.risk_method_changed.emit(method_map[index].value)

    def _on_direction_changed(self) -> None:
        """Handle trade direction change."""
        if self.direction_group:
            if self.long_radio and self.long_radio.isChecked():
                self.direction_changed.emit("LONG")
            elif self.short_radio and self.short_radio.isChecked():
                self.direction_changed.emit("SHORT")

    def _get_risk_method_enum(self, risk_method: str) -> Optional[RiskMethod]:
        """
        Convert risk method string to enum.

        Args:
            risk_method: Risk method string

        Returns:
            RiskMethod or None: Risk method enum
        """
        method_map = {
            "percentage": RiskMethod.PERCENTAGE,
            "fixed_amount": RiskMethod.FIXED_AMOUNT,
            "level_based": RiskMethod.LEVEL_BASED
        }
        return method_map.get(risk_method)