"""
Qt Futures Trading Tab
Futures-specific UI with all risk methods, margin requirements, and tick values.
"""

from typing import Dict, List, Any, Optional

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                   QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
                                   QRadioButton, QButtonGroup, QComboBox, QGroupBox)
    from PySide6.QtCore import Signal, QTimer
    HAS_QT = True
except ImportError:
    HAS_QT = False

from .qt_base_view import QtBaseView
from ..models.risk_method import RiskMethod
from ..services.enhanced_form_validation_service import EnhancedFormValidationService
from ..services.button_state_service import ButtonStateService


class QtFuturesTab(QtBaseView):
    """Qt-based futures trading tab with responsive layout."""

    # Additional signals for futures-specific events
    risk_method_changed = Signal(str)  # risk_method
    direction_changed = Signal(str)    # trade_direction

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize Qt futures tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Risk method management (all methods for futures)
        self.current_method = RiskMethod.PERCENTAGE
        self.method_frames: Dict[RiskMethod, QGroupBox] = {}
        self.risk_method_combo: Optional[QComboBox] = None

        # Trade direction
        self.direction_group: Optional[QButtonGroup] = None
        self.long_radio: Optional[QRadioButton] = None
        self.short_radio: Optional[QRadioButton] = None

        # Result display
        self.result_display: Optional[QTextEdit] = None

        # Real-time validation services
        self.validation_service = EnhancedFormValidationService()
        self.button_service = ButtonStateService()

        # Validation timer for debouncing
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._perform_validation)
        self.validation_delay_ms = 300  # 300ms debounce

        # Margin analysis display
        self.margin_display: Optional[QLabel] = None

    def setup_ui(self) -> None:
        """Setup the futures tab UI components."""
        main_layout = self.create_main_layout()

        # Create input sections
        input_section = self._create_input_section()
        main_layout.addWidget(input_section)

        # Create futures info panel
        info_section = self._create_info_section()
        main_layout.addWidget(info_section)

        # Create margin analysis section
        margin_section = self._create_margin_section()
        main_layout.addWidget(margin_section)

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
        calculate_btn = self.create_calculate_button("Calculate Futures Position")
        main_layout.addWidget(calculate_btn)

        # Add stretch to push everything to top
        main_layout.addStretch()

    def _create_input_section(self) -> QGroupBox:
        """
        Create basic input section for futures trading.

        Returns:
            QGroupBox: Input section widget
        """
        group = QGroupBox("Futures Contract Information")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Account size
        label, field = self.create_form_field("account_size", "Account Size ($)", "50000", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("account_size")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Contract symbol
        label, field = self.create_form_field("contract_symbol", "Contract Symbol", "ESH4", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("contract_symbol")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Entry price
        label, field = self.create_form_field("entry_price", "Entry Price", "4500.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("entry_price")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Tick value
        label, field = self.create_form_field("tick_value", "Tick Value ($)", "12.50", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)

        helper_label = QLabel("per tick")
        helper_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.layout_service.apply_responsive_font_scaling(helper_label, 8)
        layout.addWidget(helper_label, row, 2)

        error_label = self.create_error_label("tick_value")
        layout.addWidget(error_label, row, 3)
        row += 1

        # Tick size
        label, field = self.create_form_field("tick_size", "Tick Size", "0.25", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)

        helper_label = QLabel("minimum increment")
        helper_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.layout_service.apply_responsive_font_scaling(helper_label, 8)
        layout.addWidget(helper_label, row, 2)

        error_label = self.create_error_label("tick_size")
        layout.addWidget(error_label, row, 3)
        row += 1

        # Initial margin
        label, field = self.create_form_field("margin_requirement", "Initial Margin ($)", "6000", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)

        helper_label = QLabel("per contract")
        helper_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.layout_service.apply_responsive_font_scaling(helper_label, 8)
        layout.addWidget(helper_label, row, 2)

        error_label = self.create_error_label("margin_requirement")
        layout.addWidget(error_label, row, 3)
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

    def _create_info_section(self) -> QGroupBox:
        """
        Create informational section about futures trading.

        Returns:
            QGroupBox: Info section widget
        """
        group = QGroupBox("Futures Trading Information")
        layout = QVBoxLayout(group)

        info_text = (
            "• Tick Value: Dollar amount gained/lost per tick movement\n"
            "• Tick Size: Minimum price increment for the contract\n"
            "• Initial Margin: Required deposit per contract\n"
            "• Futures are leveraged instruments with margin requirements"
        )

        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666666; font-size: 9pt;")
        self.layout_service.apply_responsive_font_scaling(info_label, 8)

        layout.addWidget(info_label)

        return group

    def _create_margin_section(self) -> QGroupBox:
        """
        Create margin analysis section.

        Returns:
            QGroupBox: Margin section widget
        """
        group = QGroupBox("Margin Analysis")
        layout = QVBoxLayout(group)

        self.margin_display = QLabel("Enter contract details to see margin analysis...")
        self.margin_display.setStyleSheet("color: #333333; font-size: 10pt;")
        self.layout_service.apply_responsive_font_scaling(self.margin_display, 9)

        layout.addWidget(self.margin_display)

        return group

    def _create_risk_method_section(self) -> QGroupBox:
        """
        Create risk method selection section (all methods for futures).

        Returns:
            QGroupBox: Risk method selection widget
        """
        group = QGroupBox("Risk Method")
        layout = QHBoxLayout(group)

        method_label = QLabel("Risk Calculation Method:")
        self.layout_service.apply_responsive_font_scaling(method_label, 10)
        layout.addWidget(method_label)

        self.risk_method_combo = QComboBox()
        # All methods available for futures
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
        """Create method-specific input frames (all methods for futures)."""
        # Percentage method frame
        self.method_frames[RiskMethod.PERCENTAGE] = self._create_percentage_frame()

        # Fixed amount method frame
        self.method_frames[RiskMethod.FIXED_AMOUNT] = self._create_fixed_amount_frame()

        # Level-based method frame
        self.method_frames[RiskMethod.LEVEL_BASED] = self._create_level_based_frame()

    def _create_percentage_frame(self) -> QGroupBox:
        """
        Create percentage-based risk method frame for futures.

        Returns:
            QGroupBox: Percentage method frame
        """
        group = QGroupBox("Percentage-based Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Risk percentage
        label, field = self.create_form_field("risk_percentage", "Risk Percentage (%)", "1.0", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("risk_percentage")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Stop loss ticks
        label, field = self.create_form_field("stop_loss_ticks", "Stop Loss (ticks)", "8", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("stop_loss_ticks")
        layout.addWidget(error_label, row, 2)

        return group

    def _create_fixed_amount_frame(self) -> QGroupBox:
        """
        Create fixed amount risk method frame for futures.

        Returns:
            QGroupBox: Fixed amount method frame
        """
        group = QGroupBox("Fixed Amount Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Fixed risk amount
        label, field = self.create_form_field("fixed_risk_amount", "Fixed Risk Amount ($)", "500.00", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("fixed_risk_amount")
        layout.addWidget(error_label, row, 2)
        row += 1

        # Stop loss ticks
        label, field = self.create_form_field("stop_loss_ticks_fixed", "Stop Loss (ticks)", "8", True)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        error_label = self.create_error_label("stop_loss_ticks_fixed")
        layout.addWidget(error_label, row, 2)

        return group

    def _create_level_based_frame(self) -> QGroupBox:
        """
        Create level-based risk method frame for futures.

        Returns:
            QGroupBox: Level-based method frame
        """
        group = QGroupBox("Level-based Risk Calculation")
        layout = QGridLayout(group)
        layout.setSpacing(self.layout_service.get_scaled_spacing(8))

        row = 0

        # Support/resistance level
        label, field = self.create_form_field("support_resistance_level", "Support/Resistance Level", "4480.00", True)
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
        self.result_display.setPlainText("Enter futures contract details and click Calculate to see results...")

        # Apply responsive scaling
        self.layout_service.set_minimum_size(self.result_display, 400, 200)
        self.layout_service.apply_responsive_font_scaling(self.result_display, 9)

        layout.addWidget(self.result_display)

        return group

    def setup_input_fields(self) -> None:
        """Setup input field connections and validation."""
        # Connect all input fields to real-time validation
        for field_name, field_widget in self.input_fields.items():
            if isinstance(field_widget, QLineEdit):
                # Connect text change signal with debouncing
                field_widget.textChanged.connect(self._on_field_changed)
                # Also connect editing finished for immediate validation
                field_widget.editingFinished.connect(self._perform_validation)

        # Connect risk method change to validation
        if self.risk_method_combo:
            self.risk_method_combo.currentIndexChanged.connect(self._on_method_changed)

        # Connect direction change to validation
        if self.direction_group:
            self.direction_group.buttonClicked.connect(self._perform_validation)

        # Connect field changes to update margin analysis
        for field_name, field in self.input_fields.items():
            if field_name in ["margin_requirement", "account_size"]:
                field.textChanged.connect(self._update_margin_analysis)

        # Setup initial validation state
        self.validation_service.set_risk_method("futures")  # Futures use special method
        self._perform_validation()

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

        # Update margin analysis
        self._update_margin_analysis_with_result(result)

    def clear_results(self) -> None:
        """Clear the results display."""
        if self.result_display:
            self.result_display.setPlainText("Enter futures contract details and click Calculate to see results...")

        if self.margin_display:
            self.margin_display.setText("Enter contract details to see margin analysis...")

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
        Format futures calculation result for display.

        Args:
            result_data: Result data from calculation

        Returns:
            str: Formatted result text
        """
        result_text = "=== FUTURES POSITION CALCULATION ===\n\n"

        # Basic results
        position_size = result_data.get('position_size', 0)
        estimated_risk = result_data.get('estimated_risk', 0)
        risk_method = result_data.get('risk_method', 'Unknown')
        margin_required = result_data.get('margin_required', 0)

        result_text += f"Number of Contracts: {position_size:,}\n"
        result_text += f"Total Margin Required: ${margin_required:.2f}\n"
        result_text += f"Estimated Risk: ${estimated_risk:.2f}\n"
        result_text += f"Risk Method: {risk_method.replace('_', ' ').title()}\n\n"

        # Trade details
        form_data = self.get_form_data()
        result_text += "=== CONTRACT DETAILS ===\n"
        result_text += f"Contract Symbol: {form_data.get('contract_symbol', 'N/A')}\n"
        result_text += f"Entry Price: {float(form_data.get('entry_price', 0)):.2f}\n"
        result_text += f"Tick Value: ${float(form_data.get('tick_value', 0)):.2f}\n"
        result_text += f"Tick Size: {form_data.get('tick_size', '0')}\n"
        result_text += f"Direction: {form_data.get('trade_direction', 'N/A')}\n"

        # Method-specific details
        if risk_method == 'percentage':
            result_text += f"Risk Percentage: {form_data.get('risk_percentage', 0)}%\n"
            result_text += f"Stop Loss: {form_data.get('stop_loss_ticks', 0)} ticks\n"

        elif risk_method == 'fixed_amount':
            result_text += f"Fixed Risk: ${form_data.get('fixed_risk_amount', 0)}\n"
            result_text += f"Stop Loss: {form_data.get('stop_loss_ticks_fixed', 0)} ticks\n"

        elif risk_method == 'level_based':
            result_text += f"Support/Resistance: {form_data.get('support_resistance_level', 0)}\n"

        result_text += f"\nAccount Size: ${float(form_data.get('account_size', 0)):.2f}\n"

        # Leverage analysis
        result_text += "\n=== LEVERAGE ANALYSIS ===\n"
        account_size = float(form_data.get('account_size', 0))
        if margin_required > 0 and account_size > 0:
            margin_utilization = (margin_required / account_size) * 100
            result_text += f"Margin Utilization: {margin_utilization:.1f}%\n"

            if margin_utilization > 50:
                result_text += "⚠️  High margin utilization (>50%)\n"
            elif margin_utilization > 25:
                result_text += "ℹ️  Moderate margin utilization (>25%)\n"
            else:
                result_text += "✅ Conservative margin utilization\n"

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

        # Futures-specific notes
        result_text += "\n=== FUTURES TRADING NOTES ===\n"
        result_text += "• Monitor margin requirements and account equity\n"
        result_text += "• Futures have daily mark-to-market settlements\n"
        result_text += "• Consider rollover dates for continuous contracts\n"
        result_text += "• Leverage amplifies both profits and losses\n"

        return result_text

    def _update_margin_analysis(self) -> None:
        """Update margin analysis based on current inputs."""
        if not self.margin_display:
            return

        try:
            form_data = self.get_form_data()
            account_size = float(form_data.get('account_size', 0))
            margin_req = float(form_data.get('margin_requirement', 0))

            if account_size > 0 and margin_req > 0:
                max_contracts = int(account_size / margin_req)
                margin_text = f"Maximum contracts based on margin: {max_contracts}\n"
                margin_text += f"Margin requirement per contract: ${margin_req:.2f}"
                self.margin_display.setText(margin_text)
            else:
                self.margin_display.setText("Enter account size and margin requirement for analysis...")

        except (ValueError, TypeError):
            self.margin_display.setText("Enter valid numeric values for margin analysis...")

    def _update_margin_analysis_with_result(self, result: Dict[str, Any]) -> None:
        """
        Update margin analysis with calculation results.

        Args:
            result: Calculation result data
        """
        if not self.margin_display:
            return

        try:
            position_size = result.get('position_size', 0)
            margin_required = result.get('margin_required', 0)
            form_data = self.get_form_data()
            account_size = float(form_data.get('account_size', 0))

            if account_size > 0 and margin_required > 0:
                utilization = (margin_required / account_size) * 100
                margin_text = f"Position: {position_size} contracts\n"
                margin_text += f"Total margin required: ${margin_required:.2f}\n"
                margin_text += f"Margin utilization: {utilization:.1f}%"
                self.margin_display.setText(margin_text)

        except (ValueError, TypeError, KeyError):
            self.margin_display.setText("Margin analysis unavailable")

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

    def _on_field_changed(self) -> None:
        """Handle field text change with debouncing."""
        # Restart the validation timer to debounce rapid changes
        self.validation_timer.start(self.validation_delay_ms)

    def _on_method_changed(self) -> None:
        """Handle risk method change."""
        # Update validation service with futures method
        self.validation_service.set_risk_method("futures")
        # Perform immediate validation
        self._perform_validation()

    def _perform_validation(self) -> None:
        """Perform real-time form validation and update UI."""
        try:
            # Get current form data
            form_data = self.get_form_data()
            current_method = "futures"  # Futures always use futures method

            # Update validation service
            self.validation_service.set_risk_method(current_method)

            # Perform validation
            errors = self.validation_service.validate_form(form_data)

            # Update error displays
            self._update_error_displays(errors)

            # Update button state
            self._update_button_state(form_data, current_method)

            # Update field styling
            self._update_field_styling(errors)

        except Exception as e:
            # Silently handle validation errors to prevent UI crashes
            print(f"Validation error in futures tab: {e}")

    def _update_error_displays(self, errors: Dict[str, str]) -> None:
        """
        Update error label displays.

        Args:
            errors: Dictionary of field names to error messages
        """
        # Clear all error labels first
        for field_name in self.input_fields.keys():
            error_label = self.error_labels.get(field_name)
            if error_label:
                error_label.setText("")
                error_label.hide()

        # Show errors for fields with validation issues
        for field_name, error_message in errors.items():
            error_label = self.error_labels.get(field_name)
            if error_label:
                error_label.setText(error_message)
                error_label.show()
                # Apply error styling
                error_label.setStyleSheet("color: #d32f2f; font-size: 10px;")

    def _update_button_state(self, form_data: Dict[str, Any], risk_method: str) -> None:
        """
        Update calculate button state.

        Args:
            form_data: Current form data
            risk_method: Current risk method
        """
        button_id = "futures_calculate_button"

        # Update button model in button service
        self.button_service.update_button_model(button_id, form_data, risk_method)

        # Get button state
        should_enable = self.button_service.should_enable_button(form_data, risk_method)
        tooltip = self.button_service.get_button_tooltip(form_data, risk_method)

        # Update calculate button if it exists
        if hasattr(self, 'calculate_button') and self.calculate_button:
            self.calculate_button.setEnabled(should_enable)
            self.calculate_button.setToolTip(tooltip or "")

    def _update_field_styling(self, errors: Dict[str, str]) -> None:
        """
        Update field styling based on validation results.

        Args:
            errors: Dictionary of field names to error messages
        """
        for field_name, field_widget in self.input_fields.items():
            if isinstance(field_widget, QLineEdit):
                if field_name in errors:
                    # Apply error styling
                    field_widget.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #d32f2f;
                            border-radius: 4px;
                            padding: 4px;
                            background-color: #fff5f5;
                        }
                        QLineEdit:focus {
                            border: 2px solid #d32f2f;
                            background-color: #ffffff;
                        }
                    """)
                else:
                    # Apply normal styling
                    field_widget.setStyleSheet("""
                        QLineEdit {
                            border: 1px solid #cccccc;
                            border-radius: 4px;
                            padding: 4px;
                            background-color: #ffffff;
                        }
                        QLineEdit:focus {
                            border: 2px solid #1976d2;
                            background-color: #ffffff;
                        }
                    """)

    def get_validation_errors(self) -> Dict[str, str]:
        """
        Get current validation errors.

        Returns:
            Dictionary of field names to error messages
        """
        form_data = self.get_form_data()
        self.validation_service.set_risk_method("futures")
        return self.validation_service.validate_form(form_data)

    def is_form_valid(self) -> bool:
        """
        Check if the current form is valid.

        Returns:
            True if form is valid, False otherwise
        """
        form_data = self.get_form_data()
        self.validation_service.set_risk_method("futures")
        return self.validation_service.is_form_valid(form_data)

    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for futures trading.

        Returns:
            List of required field names
        """
        return self.validation_service.get_required_fields("futures")

    def validate_field(self, field_name: str, field_value: str) -> Optional[str]:
        """
        Validate a specific field.

        Args:
            field_name: Name of the field to validate
            field_value: Value to validate

        Returns:
            Error message if invalid, None if valid
        """
        return self.validation_service.validate_field(field_name, field_value)