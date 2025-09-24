"""
Qt Equity Trading Tab
Equity-specific UI with all risk methods and responsive Qt widgets.
"""

from typing import Dict, List, Any, Optional, Callable

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
        # Initialize attributes BEFORE calling super().__init__
        # because setup_ui() is called in parent constructor

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

        # Input fields reference (will be set up after parent init)
        self.input_fields: Dict[str, QLineEdit] = {}

        # Real-time validation services
        self.validation_service = EnhancedFormValidationService()
        self.button_service = ButtonStateService()

        # Button state caching for performance
        self._cached_button_enabled = None
        self._cached_button_tooltip = None
        self._cached_form_hash = None

        # Call parent constructor (which calls setup_ui())
        super().__init__(parent)

        # Set up input_fields reference to form_fields from base class
        # This must be done after super().__init__() when form_fields is populated
        self.input_fields = self.form_fields

        # Validation timer for debouncing (requires Qt app to be initialized)
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._perform_validation)
        self.validation_delay_ms = 300  # 300ms debounce

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

        # Create convenient field references for tests and controllers
        self._setup_field_references()

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

    def _setup_field_references(self) -> None:
        """Setup convenient field references for tests and controllers."""
        # Create direct references to form fields for easier access
        self.account_size_entry = self.form_fields.get('account_size')
        self.symbol_entry = self.form_fields.get('symbol')
        self.entry_price_entry = self.form_fields.get('entry_price')
        self.risk_percentage_entry = self.form_fields.get('risk_percentage')
        self.stop_loss_price_entry = self.form_fields.get('stop_loss_price')
        self.fixed_risk_amount_entry = self.form_fields.get('fixed_risk_amount')
        self.stop_loss_price_fixed_entry = self.form_fields.get('stop_loss_price_fixed')
        self.support_resistance_level_entry = self.form_fields.get('support_resistance_level')

        # Field references are now set up for test and controller access

    def trigger_validation(self) -> None:
        """Manually trigger validation - useful for tests and debugging."""
        # Force update the validation state
        self._perform_validation()

        # Also emit textChanged signals for all fields to trigger controller updates
        for field_name, field_widget in self.form_fields.items():
            if hasattr(field_widget, 'textChanged') and hasattr(field_widget, 'text'):
                # Emit the textChanged signal manually
                field_widget.textChanged.emit(field_widget.text())

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

        # Setup initial validation state
        self.validation_service.set_risk_method(self.current_method.value)
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

    def _on_field_changed(self) -> None:
        """Handle field text change with debouncing."""
        # Restart the validation timer to debounce rapid changes
        self.validation_timer.start(self.validation_delay_ms)

    def _on_method_changed(self) -> None:
        """Handle risk method change."""
        # Update validation service with new method
        self.validation_service.set_risk_method(self.current_method.value)
        # Perform immediate validation
        self._perform_validation()

    def _perform_validation(self) -> None:
        """Perform real-time form validation and update UI."""
        try:
            # Get current form data
            form_data = self.get_form_data()
            current_method = self.current_method.value

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
            print(f"Validation error in equity tab: {e}")

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
        Update calculate button state with caching for performance.

        Args:
            form_data: Current form data
            risk_method: Current risk method
        """
        # Create form hash for caching
        form_hash = hash((
            frozenset(form_data.items()) if form_data else frozenset(),
            risk_method
        ))

        # Check cache to avoid unnecessary updates
        if (form_hash == self._cached_form_hash and
            self._cached_button_enabled is not None and
            self._cached_button_tooltip is not None):
            return

        button_id = "equity_calculate_button"

        # Update button model in button service
        self.button_service.update_button_model(button_id, form_data, risk_method)

        # Get button state
        should_enable = self.button_service.should_enable_button(form_data, risk_method)
        tooltip = self.button_service.get_button_tooltip(form_data, risk_method)

        # Update cache
        self._cached_form_hash = form_hash
        self._cached_button_enabled = should_enable
        self._cached_button_tooltip = tooltip

        # Update UI only if state changed
        if hasattr(self, 'calculate_button') and self.calculate_button:
            if self.calculate_button.isEnabled() != should_enable:
                self.calculate_button.setEnabled(should_enable)

            current_tooltip = self.calculate_button.toolTip()
            new_tooltip = tooltip or ""
            if current_tooltip != new_tooltip:
                self.calculate_button.setToolTip(new_tooltip)

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
                    # Set error tooltip
                    field_widget.setToolTip(f"Error: {errors[field_name]}")
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
                    # Clear error tooltip
                    field_widget.setToolTip("")

    def get_validation_errors(self) -> Dict[str, str]:
        """
        Get current validation errors.

        Returns:
            Dictionary of field names to error messages
        """
        form_data = self.get_form_data()
        self.validation_service.set_risk_method(self.current_method.value)
        return self.validation_service.validate_form(form_data)

    def is_form_valid(self) -> bool:
        """
        Check if the current form is valid.

        Returns:
            True if form is valid, False otherwise
        """
        form_data = self.get_form_data()
        self.validation_service.set_risk_method(self.current_method.value)
        return self.validation_service.is_form_valid(form_data)

    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for current risk method.

        Returns:
            List of required field names
        """
        return self.validation_service.get_required_fields(self.current_method.value)

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