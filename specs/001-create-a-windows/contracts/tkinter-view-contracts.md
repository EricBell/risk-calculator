# Tkinter View Contracts for Python Risk Calculator

## Main Window Contract

### Class: MainWindow(tk.Tk)
```python
import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Risk Calculator")
        self.geometry("800x600")
        self.resizable(True, True)

        # Create main controller
        self.controller = MainController(self)

        # Create main UI
        self._create_menu()
        self._create_notebook()
        self._create_status_bar()
```

**Responsibilities**:
- Application window management and configuration
- Menu bar creation (File, Edit, Help)
- Tab container (ttk.Notebook) management
- Status bar for application messages
- Window-level keyboard shortcuts and events

### Cross-Platform UI Contracts

#### _configure_styles() -> None
```python
def _configure_styles(self) -> None:
```
- **Purpose**: Configure ttk styles for consistent cross-platform appearance
- **Process**:
  1. Create custom styles for error states (red borders)
  2. Configure button styles for different states
  3. Set up theme-appropriate colors and fonts
  4. Ensure Windows and Linux compatibility

#### _setup_keyboard_shortcuts() -> None
```python
def _setup_keyboard_shortcuts(self) -> None:
```
- **Purpose**: Setup keyboard navigation and shortcuts
- **Process**:
  1. Ctrl+Tab for tab switching
  2. F5 for calculate (across all tabs)
  3. Ctrl+R for clear/reset
  4. Escape for cancel operations

## Trading Tab Base Contract

### Class: BaseTradingTab(ttk.Frame)
```python
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, Optional
from models.risk_method import RiskMethod

class BaseTradingTab(ttk.Frame, ABC):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Widget containers
        self.method_frame: Optional[ttk.LabelFrame] = None
        self.input_frame: Optional[ttk.LabelFrame] = None
        self.button_frame: Optional[ttk.Frame] = None
        self.result_frame: Optional[ttk.LabelFrame] = None

        # Widget dictionaries for easy access
        self.entry_widgets: Dict[str, ttk.Entry] = {}
        self.label_widgets: Dict[str, ttk.Label] = {}
        self.error_labels: Dict[str, ttk.Label] = {}
        self.method_radios: Dict[str, ttk.Radiobutton] = {}

        self._build_ui()

    @abstractmethod
    def _create_method_selection(self) -> None:
        """Create risk method radio buttons"""
        pass

    @abstractmethod
    def _create_input_fields(self) -> None:
        """Create asset-specific input fields"""
        pass

    @abstractmethod
    def get_supported_methods(self) -> List[RiskMethod]:
        """Return list of supported risk methods for this asset class"""
        pass
```

## Risk Method UI Management

### Method Selection Contracts

#### create_method_radio_buttons(supported_methods: List[RiskMethod]) -> None
```python
def create_method_radio_buttons(self, supported_methods: List[RiskMethod]) -> None:
```
- **Purpose**: Create radio buttons for available risk methods
- **Process**:
  1. Create ttk.Radiobutton for each supported method
  2. Disable unsupported methods with tooltip explanation
  3. Set default selection to PERCENTAGE method
  4. Bind selection change to controller callback

#### update_field_visibility(method: RiskMethod) -> None
```python
def update_field_visibility(self, method: RiskMethod) -> None:
```
- **Purpose**: Show/hide input fields based on selected risk method
- **Widget Management**:
  - **PERCENTAGE method**: Show risk_percentage Entry, stop_loss Entry
  - **FIXED_AMOUNT method**: Show fixed_risk_amount Entry, stop_loss Entry
  - **LEVEL_BASED method**: Show support_resistance_level Entry, trade_direction Frame
- **Implementation**: Use grid_remove()/grid() for smooth transitions

## Input Field Contracts

### Common Field Creation

#### create_common_fields() -> None
```python
def create_common_fields(self) -> None:
```
- **Purpose**: Create fields common to all risk methods
- **Fields Created**:
  - Symbol/Contract Symbol (Entry with validation)
  - Account Size (Entry with currency formatting)
  - Entry Price (Entry with price validation)
- **Validation**: Real-time validation with error label display

#### create_method_specific_fields() -> None
```python
def create_method_specific_fields(self) -> None:
```
- **Purpose**: Create fields specific to each risk method
- **PERCENTAGE Fields**:
  - Risk Percentage (Entry with 1-5% range validation)
  - Percentage slider (Scale widget, optional)
- **FIXED_AMOUNT Fields**:
  - Fixed Risk Amount (Entry with $10-$500 validation)
  - Account percentage display (read-only Label)
- **LEVEL_BASED Fields**:
  - Support/Resistance Level (Entry with price validation)
  - Trade Direction (Radiobutton Frame: Long/Short)

### Field Validation Display

#### show_field_error(field_name: str, error_message: str) -> None
```python
def show_field_error(self, field_name: str, error_message: str) -> None:
```
- **Purpose**: Display validation error for specific field
- **Visual Feedback**:
  1. Show error label with red text below field
  2. Change Entry border color to red (custom style)
  3. Add error icon (optional) next to field
  4. Update tooltip with error details

#### clear_field_error(field_name: str) -> None
```python
def clear_field_error(self, field_name: str) -> None:
```
- **Purpose**: Clear validation error display
- **Process**:
  1. Hide error label for field
  2. Reset Entry border color to normal
  3. Remove error icon and tooltip
  4. Update field status to valid state

## Results Display Contracts

### Calculation Results

#### create_results_display() -> None
```python
def create_results_display(self) -> None:
```
- **Purpose**: Create widgets for displaying calculation results
- **Widgets Created**:
  - Result Text widget (read-only, formatted output)
  - Method indicator Label (shows which method was used)
  - Copy button for results (optional)
  - Clear results button

#### update_results(result: CalculationResult) -> None
```python
def update_results(self, result: CalculationResult) -> None:
```
- **Purpose**: Display calculation results with formatting
- **Content Format**:
  ```
  Risk Method: [Percentage/Fixed Amount/Level Based]
  Position Size: [X shares/contracts]
  Estimated Risk: $[X.XX]
  Risk Amount: $[X.XX]
  ```
- **Color Coding**: Green for success, red for errors, yellow for warnings

## Asset-Specific Tab Contracts

### Equity Tab Contract

#### Class: EquityTab(BaseTradingTab)
```python
def _create_input_fields(self) -> None:
```
- **Equity-Specific Fields**:
  - Stock Symbol (Entry with symbol validation)
  - Share Price fields (Entry/Stop Loss/Support-Resistance)
  - Trade Direction selection (for level-based method)
- **Supported Methods**: All three risk methods available

### Options Tab Contract

#### Class: OptionsTab(BaseTradingTab)
```python
def _create_input_fields(self) -> None:
```
- **Options-Specific Fields**:
  - Option Symbol (Entry with options symbol format)
  - Premium (Entry with price validation)
  - Contract Multiplier (Entry, default 100)
  - Expiration Date (optional, for display only)
- **Supported Methods**: PERCENTAGE and FIXED_AMOUNT only
- **UI Behavior**: Level-based radio button disabled with tooltip

### Futures Tab Contract

#### Class: FuturesTab(BaseTradingTab)
```python
def _create_input_fields(self) -> None:
```
- **Futures-Specific Fields**:
  - Contract Symbol (Entry with futures symbol format)
  - Tick Value (Entry with currency validation)
  - Tick Size (Entry with decimal validation)
  - Margin Requirement (Entry with currency validation)
  - Contract specifications display (read-only)
- **Supported Methods**: All three risk methods available

## Event Handling Contracts

### User Interaction Events

#### on_calculate_clicked() -> None
```python
def on_calculate_clicked(self) -> None:
```
- **Purpose**: Handle calculate button click
- **Process**:
  1. Disable calculate button and show busy state
  2. Call controller.calculate_position()
  3. Handle results or errors
  4. Re-enable calculate button

#### on_clear_clicked() -> None
```python
def on_clear_clicked(self) -> None:
```
- **Purpose**: Handle clear button click
- **Process**:
  1. Show confirmation dialog (optional)
  2. Call controller.clear_inputs()
  3. Reset UI to default state
  4. Preserve risk method selection

#### on_method_changed() -> None
```python
def on_method_changed(self) -> None:
```
- **Purpose**: Handle risk method radio button change
- **Process**:
  1. Get selected method from radio button variable
  2. Call update_field_visibility() for UI changes
  3. Clear previous calculation results
  4. Call controller.set_risk_method()

## Accessibility and Usability Contracts

### Keyboard Navigation

#### setup_tab_order() -> None
```python
def setup_tab_order(self) -> None:
```
- **Purpose**: Configure logical tab order for keyboard navigation
- **Tab Order**:
  1. Risk method radio buttons
  2. Common fields (symbol, account size, entry price)
  3. Method-specific fields
  4. Calculate button
  5. Clear button

### Screen Reader Support

#### configure_accessibility() -> None
```python
def configure_accessibility(self) -> None:
```
- **Purpose**: Configure accessibility features
- **Features**:
  1. Set accessible names for all widgets
  2. Configure accessible descriptions for complex fields
  3. Associate labels with their input fields
  4. Provide keyboard alternatives for all mouse actions

### Cross-Platform Compatibility

#### handle_platform_differences() -> None
```python
def handle_platform_differences(self) -> None:
```
- **Purpose**: Handle Windows/Linux UI differences
- **Adjustments**:
  1. Font size scaling for different DPI settings
  2. Widget spacing adjustments for different themes
  3. Keyboard shortcut variations (Ctrl vs Cmd considerations)
  4. File dialog and message box styling

## Performance Contracts

### UI Responsiveness

#### throttle_validation(delay_ms: int = 300) -> None
```python
def throttle_validation(self, delay_ms: int = 300) -> None:
```
- **Purpose**: Prevent excessive validation calls during rapid typing
- **Implementation**: Use Tkinter's after() method to debounce validation

#### lazy_load_widgets() -> None
```python
def lazy_load_widgets(self) -> None:
```
- **Purpose**: Create widgets only when tab is first accessed
- **Process**: Initialize widgets on first tab selection to improve startup time

## Error Handling Contracts

### Exception Display

#### show_calculation_error(error: Exception) -> None
```python
def show_calculation_error(self, error: Exception) -> None:
```
- **Purpose**: Display calculation errors to user
- **Process**:
  1. Show error message in results area
  2. Log error details for debugging
  3. Provide user-friendly error descriptions
  4. Suggest corrective actions when possible

#### show_validation_summary(errors: List[str]) -> None
```python
def show_validation_summary(self, errors: List[str]) -> None:
```
- **Purpose**: Display multiple validation errors in summary
- **Implementation**: Use message box or status bar for multiple errors