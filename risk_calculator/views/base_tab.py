"""Base trading tab abstract Tkinter frame with common UI functionality."""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..models.risk_method import RiskMethod


class BaseTradingTab(ttk.Frame, ABC):
    """Abstract base class for trading tabs with common UI elements and functionality."""

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.validation_labels: Dict[str, ttk.Label] = {}
        self.input_widgets: Dict[str, tk.Widget] = {}
        self.method_frames: Dict[RiskMethod, ttk.Frame] = {}
        self.current_method: RiskMethod = RiskMethod.PERCENTAGE

        # Aliases for test compatibility
        self.widgets = self.input_widgets
        self.error_labels = self.validation_labels
        self.method_radios = {}

        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Configure for proper window resizing
        self.grid_propagate(True)

        # Initialize UI components
        self._create_main_layout()
        self._create_common_widgets()
        self._create_method_specific_widgets()
        self._create_result_widgets()
        self._setup_bindings()
        self._create_test_aliases()

        # Register widgets for font scaling
        self._register_widgets_for_font_scaling()

    def _create_main_layout(self) -> None:
        """Create the main layout structure."""
        # Main container with padding
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Ensure the main frame resizes with the tab
        self.main_frame.grid_propagate(True)

        # Input section
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Trade Parameters", padding="10")
        self.input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Risk method selection
        self.method_frame = ttk.LabelFrame(self.main_frame, text="Risk Calculation Method", padding="10")
        self.method_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Method-specific inputs
        self.method_inputs_frame = ttk.LabelFrame(self.main_frame, text="Method Parameters", padding="10")
        self.method_inputs_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.method_inputs_frame.grid_columnconfigure(1, weight=1)

        # Action buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.button_frame.grid_columnconfigure(0, weight=1)

        # Results section
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Calculation Results", padding="10")
        self.result_frame.grid(row=4, column=0, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

    def _create_common_widgets(self) -> None:
        """Create common input widgets shared by all asset types."""
        row = 0

        # Account size
        ttk.Label(self.input_frame, text="Account Size ($):").grid(row=row, column=0, sticky="w", padx=(0, 10))
        account_entry = ttk.Entry(self.input_frame)
        account_entry.grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['account_size'] = account_entry
        self._add_validation_label('account_size', row)
        row += 1

        # Asset-specific fields will be added by subclasses
        self._create_asset_specific_widgets(row)

    def _create_method_specific_widgets(self) -> None:
        """Create risk method selection and method-specific input widgets."""
        # Risk method selection
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
            # Store radio button for test compatibility
            self.method_radios[method] = rb

        # Create frames for each method
        self._create_percentage_method_frame()
        self._create_fixed_amount_method_frame()
        if RiskMethod.LEVEL_BASED in methods:
            self._create_level_based_method_frame()

        # Show default method
        self.show_method_fields(RiskMethod.PERCENTAGE)

    def _create_percentage_method_frame(self) -> None:
        """Create percentage method input frame."""
        frame = ttk.Frame(self.method_inputs_frame)
        frame.grid_columnconfigure(1, weight=1)  # Allow entry to expand
        self.method_frames[RiskMethod.PERCENTAGE] = frame

        ttk.Label(frame, text="Risk Percentage (1-5%):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        risk_entry = ttk.Entry(frame)
        risk_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['risk_percentage'] = risk_entry
        self._add_method_validation_label('risk_percentage', frame, 0)

    def _create_fixed_amount_method_frame(self) -> None:
        """Create fixed amount method input frame."""
        frame = ttk.Frame(self.method_inputs_frame)
        frame.grid_columnconfigure(1, weight=1)  # Allow entry to expand
        self.method_frames[RiskMethod.FIXED_AMOUNT] = frame

        ttk.Label(frame, text="Fixed Risk Amount ($10-500):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        amount_entry = ttk.Entry(frame)
        amount_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['fixed_risk_amount'] = amount_entry
        self._add_method_validation_label('fixed_risk_amount', frame, 0)

    def _create_level_based_method_frame(self) -> None:
        """Create level-based method input frame."""
        frame = ttk.Frame(self.method_inputs_frame)
        frame.grid_columnconfigure(1, weight=1)  # Allow entry to expand
        self.method_frames[RiskMethod.LEVEL_BASED] = frame

        ttk.Label(frame, text="Support/Resistance Level ($):").grid(row=0, column=0, sticky="w", padx=(0, 10))
        level_entry = ttk.Entry(frame)
        level_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.input_widgets['support_resistance_level'] = level_entry
        self._add_method_validation_label('support_resistance_level', frame, 0)

    def _create_result_widgets(self) -> None:
        """Create result display widgets."""
        # Calculate button
        self.calculate_button = ttk.Button(
            self.button_frame,
            text="Calculate Position",
            command=self._on_calculate_clicked,
            state="disabled"
        )
        self.calculate_button.grid(row=0, column=0, pady=5)

        # Clear button
        clear_button = ttk.Button(
            self.button_frame,
            text="Clear All",
            command=self._on_clear_clicked
        )
        clear_button.grid(row=0, column=1, padx=(10, 0), pady=5)

        # Store buttons in widgets for test compatibility
        self.input_widgets['calculate_button'] = self.calculate_button
        self.input_widgets['clear_button'] = clear_button

        # Results display
        self.result_text = tk.Text(
            self.result_frame,
            height=8,
            state="disabled",
            wrap="word",
            font=("Consolas", 10)
        )
        self.result_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for results
        result_scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

    def _add_validation_label(self, field_name: str, row: int, column: int = 2) -> None:
        """Add validation label for a field."""
        label = ttk.Label(self.input_frame, text="", foreground="red", font=("TkDefaultFont", 8))
        label.grid(row=row, column=column, sticky="w", padx=(10, 0))
        self.validation_labels[field_name] = label

    def _add_method_validation_label(self, field_name: str, parent: tk.Widget, row: int, column: int = 2) -> None:
        """Add validation label for method-specific field."""
        label = ttk.Label(parent, text="", foreground="red", font=("TkDefaultFont", 8))
        label.grid(row=row, column=column, sticky="w", padx=(10, 0))
        self.validation_labels[field_name] = label

    def _setup_bindings(self) -> None:
        """Setup widget bindings and event handlers."""
        # Bind controller variables if controller is available
        if self.controller:
            for field_name, widget in self.input_widgets.items():
                if field_name in self.controller.tk_vars:
                    if isinstance(widget, (ttk.Entry, tk.Entry)):
                        widget.configure(textvariable=self.controller.tk_vars[field_name])
                    elif isinstance(widget, (tk.StringVar, tk.IntVar)):
                        # Variable is already controller's tk_var
                        pass

        # Enter key binding for calculate
        self.bind_all("<Return>", lambda e: self._on_calculate_clicked() if self.calculate_button['state'] != 'disabled' else None)

    def _register_widgets_for_font_scaling(self) -> None:
        """Register widgets with the main window's font manager for responsive scaling."""
        try:
            # Find the main window by walking up the widget hierarchy
            main_window = self._find_main_window()
            if not main_window or not hasattr(main_window, 'register_widget_for_font_scaling'):
                return

            # Register the result text widget for special font handling
            if hasattr(self, 'result_text'):
                main_window.register_widget_for_font_scaling(self.result_text, 'result')

            # Register validation label widgets
            for field_name, label in self.validation_labels.items():
                main_window.register_widget_for_font_scaling(label, 'error')

        except Exception:
            pass  # Ignore registration errors

    def _find_main_window(self):
        """Find the main window by walking up the widget hierarchy."""
        try:
            # First check if we have a direct reference
            if hasattr(self, 'main_window') and self.main_window:
                return self.main_window

            # Fallback: walk up the widget hierarchy
            widget = self.master  # Start with our parent (should be notebook)
            while widget:
                # Check if current widget has the font manager
                if hasattr(widget, 'register_widget_for_font_scaling'):
                    return widget
                # Move up the hierarchy
                widget = getattr(widget, 'master', None)
            return None
        except Exception:
            return None

    # Abstract methods that subclasses must implement
    @abstractmethod
    def _create_asset_specific_widgets(self, start_row: int) -> int:
        """Create widgets specific to the asset type. Return next available row."""
        pass

    @abstractmethod
    def _get_supported_methods(self) -> List[RiskMethod]:
        """Return list of risk methods supported by this asset type."""
        pass

    # Common interface methods
    def show_method_fields(self, method: RiskMethod) -> None:
        """Show/hide fields based on selected risk method."""
        # Hide all method frames
        for frame in self.method_frames.values():
            frame.grid_remove()

        # Show selected method frame
        if method in self.method_frames:
            frame = self.method_frames[method]
            frame.grid(row=0, column=0, sticky="ew")
            self.method_inputs_frame.grid_columnconfigure(0, weight=1)

        self.current_method = method

        # Don't call back to controller - this method is called BY the controller

    def show_validation_errors(self, errors: Dict[str, str]) -> None:
        """Display validation errors for fields."""
        # Clear all validation labels first
        for label in self.validation_labels.values():
            label.configure(text="")

        # Show new errors
        for field_name, error_message in errors.items():
            if field_name in self.validation_labels:
                self.validation_labels[field_name].configure(text=error_message)

    def clear_field_error(self, field_name: str) -> None:
        """Clear validation error for a specific field."""
        if field_name in self.validation_labels:
            self.validation_labels[field_name].configure(text="")

    def show_field_warning(self, field_name: str, warning: str) -> None:
        """Show warning message for a field."""
        if field_name in self.validation_labels:
            self.validation_labels[field_name].configure(text=warning, foreground="orange")

    def set_calculate_button_enabled(self, enabled: bool) -> None:
        """Enable or disable the calculate button."""
        state = "normal" if enabled else "disabled"
        self.calculate_button.configure(state=state)

    def set_busy_state(self, is_busy: bool) -> None:
        """Set busy state for the tab (disable/enable inputs)."""
        state = "disabled" if is_busy else "normal"

        # Disable all input widgets
        for widget in self.input_widgets.values():
            if isinstance(widget, (ttk.Entry, tk.Entry, ttk.Combobox)):
                widget.configure(state=state)

        # Update calculate button text
        if is_busy:
            self.calculate_button.configure(text="Calculating...", state="disabled")
        else:
            self.calculate_button.configure(text="Calculate Position")

    def show_calculation_result(self, result_data: Dict[str, Any]) -> None:
        """Display calculation results."""
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)

        # Format and display results
        result_text = self._format_calculation_result(result_data)
        self.result_text.insert(tk.END, result_text)
        self.result_text.configure(state="disabled")

    def show_calculation_error(self, error_message: str) -> None:
        """Display calculation error."""
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Error: {error_message}\n")
        self.result_text.configure(state="disabled")

    def show_warnings(self, warnings: List[str]) -> None:
        """Display warning messages."""
        if warnings:
            current_text = self.result_text.get(1.0, tk.END)
            self.result_text.configure(state="normal")
            for warning in warnings:
                self.result_text.insert(tk.END, f"⚠️  Warning: {warning}\n")
            self.result_text.configure(state="disabled")

    def clear_results(self) -> None:
        """Clear the results display."""
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.configure(state="disabled")

    def clear_all_inputs(self) -> None:
        """Clear all input fields except risk method."""
        for field_name, widget in self.input_widgets.items():
            if field_name != 'risk_method':
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    widget.delete(0, tk.END)

        # Clear validation errors
        self.show_validation_errors({})
        self.clear_results()

    @abstractmethod
    def _format_calculation_result(self, result_data: Dict[str, Any]) -> str:
        """Format calculation result for display. Must be implemented by subclasses."""
        pass

    def _on_calculate_clicked(self) -> None:
        """Handle calculate button click."""
        if self.controller:
            self.controller.calculate_position()

    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        if self.controller:
            self.controller.clear_inputs()

    def focus_first_input(self) -> None:
        """Set focus to the first input field."""
        if 'account_size' in self.input_widgets:
            self.input_widgets['account_size'].focus()

    def get_input_widget(self, field_name: str) -> Optional[tk.Widget]:
        """Get input widget by field name."""
        return self.input_widgets.get(field_name)

    def update_ui_theme(self, theme_config: Dict[str, Any]) -> None:
        """Update UI theme (for future theming support)."""
        # Placeholder for theme support
        pass

    def _create_test_aliases(self) -> None:
        """Create aliases for test compatibility."""
        # Add _entry suffix aliases for widgets
        entry_fields = ['symbol', 'account_size', 'entry_price', 'option_symbol', 'contract_symbol',
                       'premium', 'tick_value', 'tick_size', 'margin_requirement', 'fixed_risk_amount',
                       'risk_percentage', 'stop_loss_price', 'support_resistance_level']

        for field in entry_fields:
            if field in self.input_widgets:
                self.input_widgets[f'{field}_entry'] = self.input_widgets[field]

        # Add specific aliases for test compatibility
        if 'support_resistance_level' in self.input_widgets:
            self.input_widgets['level_entry'] = self.input_widgets['support_resistance_level']

        # Create method radio button aliases with expected naming
        radio_items = list(self.method_radios.items())  # Create copy to avoid iteration issues
        for method, radio_button in radio_items:
            key = f"method_{method.value}"
            self.method_radios[key] = radio_button