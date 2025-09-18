# Python/Tkinter Controller and View Contracts

## Base Controller Contract

### Class: BaseController
```python
from abc import ABC, abstractmethod
from typing import Optional, Callable
from models.validation_result import ValidationResult
from models.risk_method import RiskMethod

class BaseController(ABC):
    def __init__(self, view):
        self.view = view
        self.is_busy: bool = False
        self.has_errors: bool = False
        self.validation_result: Optional[ValidationResult] = None
        self.current_risk_method: RiskMethod = RiskMethod.PERCENTAGE  # Default method
        self._setup_view_bindings()

    @abstractmethod
    def _setup_view_bindings(self) -> None:
        """Setup Tkinter variable bindings and event handlers"""
        pass
```

**Property Contracts**:
- `view`: Reference to Tkinter view/frame for this controller
- `is_busy`: True during calculation operations, False otherwise
- `has_errors`: True when validation fails, False when all inputs valid
- `validation_result`: Current validation state with error messages
- `current_risk_method`: Currently selected risk calculation method

**Tkinter Integration Contracts**:
- Controllers manage Tkinter StringVar/IntVar/DoubleVar variables
- Real-time validation through Tkinter variable trace callbacks
- Risk method changes trigger widget show/hide operations
- Error display through Tkinter Label widgets

## Equity Controller Contract

### Class: EquityController(BaseController)
```python
import tkinter as tk
from typing import Dict
from models.equity_trade import EquityTrade
from models.calculation_result import CalculationResult
from services.risk_calculator import RiskCalculationService
from services.validators import TradeValidationService

class EquityController(BaseController):
    def __init__(self, view, risk_service: RiskCalculationService, validation_service: TradeValidationService):
        self.trade: EquityTrade = EquityTrade()
        self.calculation_result: Optional[CalculationResult] = None
        self.risk_service = risk_service
        self.validation_service = validation_service

        # Tkinter variables for data binding
        self.tk_vars: Dict[str, tk.Variable] = {
            'symbol': tk.StringVar(value=''),
            'account_size': tk.StringVar(value=''),
            'entry_price': tk.StringVar(value=''),
            'risk_percentage': tk.StringVar(value='2.0'),
            'fixed_risk_amount': tk.StringVar(value=''),
            'stop_loss_price': tk.StringVar(value=''),
            'support_resistance_level': tk.StringVar(value=''),
            'risk_method': tk.StringVar(value=RiskMethod.PERCENTAGE.value)
        }

        super().__init__(view)
```

**Property Contracts**:
- `trade`: Current equity trade data with validation
- `calculation_result`: Result of last calculation attempt
- `tk_vars`: Dictionary of Tkinter variables for two-way data binding
- All Tkinter variable changes trigger real-time validation
- Risk method selection determines which widgets are visible

**Method Contracts**:

#### _setup_view_bindings() -> None
```python
def _setup_view_bindings(self) -> None:
```
- **Purpose**: Setup Tkinter variable trace callbacks for real-time validation
- **Process**:
  1. Add trace callbacks to all tk_vars for validation
  2. Setup risk method change handler
  3. Bind calculate and clear button commands
  4. Initialize widget visibility based on default risk method

#### set_risk_method(method: RiskMethod) -> None
```python
def set_risk_method(self, method: RiskMethod) -> None:
```
- **Purpose**: Changes the risk calculation method and updates Tkinter UI
- **Process**:
  1. Validates method is supported for equities (all three methods supported)
  2. Updates current_risk_method property and tk_vars['risk_method']
  3. Calls view.show_method_fields(method) to update widget visibility
  4. Clears calculation_result and updates result display
  5. Resets validation state and error labels

#### calculate_position() -> None
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid for selected method and controller not busy
- **Process**:
  1. Sets is_busy = True and disables calculate button
  2. Syncs tk_vars values to trade object
  3. Validates trade inputs based on current_risk_method
  4. Calls risk_service.calculate_equity_position(trade)
  5. Updates calculation_result and result text widget
  6. Sets is_busy = False and re-enables calculate button

#### clear_inputs() -> None
```python
def clear_inputs(self) -> None:
```
- **Process**:
  1. Resets all tk_vars to default values (preserves risk_method)
  2. Clears trade object to default state
  3. Clears calculation_result and result text widget
  4. Resets validation_result and error labels
  5. Maintains current risk method selection and widget visibility

#### _on_field_change(self, var_name: str, *args) -> None
```python
def _on_field_change(self, var_name: str, *args) -> None:
```
- **Purpose**: Tkinter variable trace callback for real-time validation
- **Process**:
  1. Get current value from tk_vars[var_name]
  2. Validate field value based on current_risk_method
  3. Update error label widget for the field
  4. Update has_errors property and calculate button state

#### _sync_to_trade_object() -> None
```python
def _sync_to_trade_object(self) -> None:
```
- **Purpose**: Sync Tkinter variable values to trade data object
- **Process**:
  1. Convert string values to appropriate types (Decimal, etc.)
  2. Set trade object properties from tk_vars
  3. Handle method-specific field assignments
  4. Apply trade direction and other enums

## Option Controller Contract

### Class: OptionController(BaseController)
```python
import tkinter as tk
from models.option_trade import OptionTrade

class OptionController(BaseController):
    def __init__(self, view, risk_service: RiskCalculationService, validation_service: TradeValidationService):
        self.trade: OptionTrade = OptionTrade()
        self.calculation_result: Optional[CalculationResult] = None
        self.risk_service = risk_service
        self.validation_service = validation_service
        self.supported_methods = [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]  # Level-based not supported

        # Tkinter variables for options-specific fields
        self.tk_vars: Dict[str, tk.Variable] = {
            'option_symbol': tk.StringVar(value=''),
            'account_size': tk.StringVar(value=''),
            'premium': tk.StringVar(value=''),
            'contract_multiplier': tk.StringVar(value='100'),
            'risk_percentage': tk.StringVar(value='2.0'),
            'fixed_risk_amount': tk.StringVar(value=''),
            'risk_method': tk.StringVar(value=RiskMethod.PERCENTAGE.value)
        }

        super().__init__(view)
```

**Property Contracts**:
- `trade`: Current option trade data with validation
- `calculation_result`: Result of last calculation attempt
- `supported_methods`: Only PERCENTAGE and FIXED_AMOUNT methods available
- `tk_vars`: Tkinter variables for options-specific fields (no stop loss or levels)
- Level-based method disabled in UI (radio button disabled and shows tooltip)

**Method Contracts**:

#### set_risk_method(method: RiskMethod) -> None
```python
def set_risk_method(self, method: RiskMethod) -> None:
```
- **Purpose**: Changes the risk calculation method with options-specific validation
- **Process**:
  1. Validates method is in supported_methods (rejects LEVEL_BASED)
  2. If LEVEL_BASED selected, shows error and maintains current method
  3. Updates current_risk_method property
  4. Clears calculation_result
  5. Triggers UI field visibility changes
  6. Notifies view of method change

#### calculate_position() -> None
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid for selected method and controller not busy
- **Process**: Same as EquityController but uses option-specific calculations
- **Note**: Level-based method will return error if somehow selected

#### clear_inputs() -> None
```python
def clear_inputs(self) -> None:
```
- **Process**: Same as EquityController but resets option-specific fields

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for option-specific fields
- **Method-aware**: Different validation rules based on current_risk_method
- **Returns**: True if field is valid, False otherwise

#### get_required_fields() -> List[str]
```python
def get_required_fields(self) -> List[str]:
```
- **Purpose**: Returns list of required fields based on current risk method
- **PERCENTAGE method**: ['option_symbol', 'account_size', 'risk_percentage', 'premium', 'contract_multiplier']
- **FIXED_AMOUNT method**: ['option_symbol', 'account_size', 'fixed_risk_amount', 'premium', 'contract_multiplier']
- **LEVEL_BASED method**: Not supported - returns empty list

## Future Controller Contract

### Class: FutureController(BaseController)
```python
from models.future_trade import FutureTrade

class FutureController(BaseController):
    def __init__(self, view, risk_service, validation_service):
        super().__init__()
        self.trade: FutureTrade = FutureTrade()
        self.calculation_result: Optional[CalculationResult] = None
        self.supported_methods = [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]  # All methods supported
```

**Property Contracts**:
- `trade`: Current futures trade data with validation
- `calculation_result`: Result of last calculation attempt
- `supported_methods`: All three risk methods available
- All changes to trade properties trigger validation

**Method Contracts**:

#### set_risk_method(method: RiskMethod) -> None
```python
def set_risk_method(self, method: RiskMethod) -> None:
```
- **Purpose**: Changes the risk calculation method (all methods supported)
- **Process**: Same as EquityController but for futures-specific validation

#### calculate_position() -> None
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid for selected method and controller not busy
- **Process**: Same as EquityController but uses futures-specific calculations

#### clear_inputs() -> None
```python
def clear_inputs(self) -> None:
```
- **Process**: Same as EquityController but resets futures-specific fields

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for futures-specific fields
- **Method-aware**: Different validation rules based on current_risk_method
- **Returns**: True if field is valid, False otherwise

#### get_required_fields() -> List[str]
```python
def get_required_fields(self) -> List[str]:
```
- **Purpose**: Returns list of required fields based on current risk method
- **PERCENTAGE method**: ['contract_symbol', 'account_size', 'risk_percentage', 'entry_price', 'stop_loss_price', 'tick_value', 'tick_size', 'margin_requirement']
- **FIXED_AMOUNT method**: ['contract_symbol', 'account_size', 'fixed_risk_amount', 'entry_price', 'stop_loss_price', 'tick_value', 'tick_size', 'margin_requirement']
- **LEVEL_BASED method**: ['contract_symbol', 'account_size', 'entry_price', 'support_resistance_level', 'trade_direction', 'tick_value', 'tick_size', 'margin_requirement']

## Main Application Controller Contract

### Class: MainController
```python
class MainController:
    def __init__(self, main_view):
        self.main_view = main_view
        self.equity_controller = EquityController(...)
        self.option_controller = OptionController(...)
        self.future_controller = FutureController(...)
        self.current_tab: str = "equity"
        self.global_risk_method: RiskMethod = RiskMethod.PERCENTAGE  # Default for new tabs
```

**Property Contracts**:
- `current_tab`: Currently active tab ("equity", "option", "future")
- `global_risk_method`: Default risk method for new tab activations
- References to all tab-specific controllers

**Method Contracts**:

#### switch_tab(tab_name: str) -> None
```python
def switch_tab(self, tab_name: str) -> None:
```
- **Purpose**: Handle tab switching and maintain session state
- **Process**:
  1. Saves current tab state
  2. Switches to new tab
  3. Restores previous inputs for new tab
  4. Applies global_risk_method if tab hasn't been used before
  5. Updates current_tab property

#### set_global_risk_method(method: RiskMethod) -> None
```python
def set_global_risk_method(self, method: RiskMethod) -> None:
```
- **Purpose**: Sets default risk method for all tabs (user preference)
- **Process**:
  1. Updates global_risk_method
  2. Optionally applies to all tabs or just new activations
  3. Checks method compatibility with each asset class

#### get_active_controller() -> BaseController
```python
def get_active_controller(self) -> BaseController:
```
- **Purpose**: Returns the controller for currently active tab
- **Returns**: EquityController, OptionController, or FutureController

#### sync_common_fields() -> None
```python
def sync_common_fields(self) -> None:
```
- **Purpose**: Optional feature to sync account_size across tabs
- **Process**:
  1. Takes account_size from current tab
  2. Updates account_size in other tabs
  3. Maintains risk method selection per tab

## Tkinter View Interface Contracts

### Base View Contract

### Class: BaseTradingTab(ttk.Frame)
```python
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, List

class BaseTradingTab(ttk.Frame, ABC):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.widgets: Dict[str, tk.Widget] = {}
        self.error_labels: Dict[str, tk.Label] = {}
        self._create_widgets()
        self._layout_widgets()

    @abstractmethod
    def _create_widgets(self) -> None:
        """Create all Tkinter widgets for this tab"""
        pass

    @abstractmethod
    def _layout_widgets(self) -> None:
        """Layout widgets using grid/pack"""
        pass
```

### Tkinter Widget Management Methods

#### show_method_fields(method: RiskMethod) -> None
```python
def show_method_fields(self, method: RiskMethod) -> None:
```
- **Purpose**: Show/hide Tkinter widgets based on selected risk method
- **Process**:
  1. Use widget.grid_remove() to hide irrelevant fields
  2. Use widget.grid() to show relevant fields for selected method
  3. Update labels and tooltips for method-specific context
- **PERCENTAGE method**: Show risk_percentage Entry, stop_loss Entry
- **FIXED_AMOUNT method**: Show fixed_risk_amount Entry, stop_loss Entry
- **LEVEL_BASED method**: Show support_resistance_level Entry, trade_direction Radiobuttons

#### update_calculation_result(result: CalculationResult) -> None
```python
def update_calculation_result(self, result: CalculationResult) -> None:
```
- **Purpose**: Display calculation results in Tkinter Text or Label widgets
- **Process**:
  1. Update result text widget with formatted output
  2. Show which risk method was used in calculation
  3. Display position size, estimated risk, and risk amount
  4. Use color coding for success/error states

#### show_validation_errors(field_errors: Dict[str, str]) -> None
```python
def show_validation_errors(self, field_errors: Dict[str, str]) -> None:
```
- **Purpose**: Display field-specific validation errors
- **Process**:
  1. Update error_labels[field_name] with error text
  2. Show/hide error labels based on validation state
  3. Use red text color for error messages
  4. Clear error when field becomes valid

#### set_busy_state(is_busy: bool) -> None
```python
def set_busy_state(self, is_busy: bool) -> None:
```
- **Purpose**: Disable/enable UI during calculations
- **Process**:
  1. Set state='disabled'/'normal' on all Entry widgets
  2. Disable/enable calculate Button
  3. Show/hide progress indicator (optional)
  4. Change cursor to waiting/default

#### bind_to_controller_vars(tk_vars: Dict[str, tk.Variable]) -> None
```python
def bind_to_controller_vars(self, tk_vars: Dict[str, tk.Variable]) -> None:
```
- **Purpose**: Connect Tkinter Entry widgets to controller variables
- **Process**:
  1. Set textvariable property of Entry widgets to tk_vars
  2. Set variable property of Radiobutton widgets to tk_vars
  3. Ensure two-way data binding between view and controller
  4. Setup trace callbacks for real-time validation

## Risk Method UI Behavior

### Field Visibility Rules
1. **Common fields always visible**: symbol/account_size/entry_price
2. **Method-specific fields**:
   - PERCENTAGE: risk_percentage slider/input, stop_loss_price
   - FIXED_AMOUNT: fixed_risk_amount input, stop_loss_price
   - LEVEL_BASED: support_resistance_level, trade_direction radio buttons
3. **Asset-specific fields**: Always visible (premium for options, tick data for futures)

### Method Selection UI
- Radio buttons for risk method selection
- Method availability varies by asset class (options disable level-based)
- Visual indicators show active method
- Method switching clears previous calculations
- Help text explains each method

## Python Exception Handling Contracts

### Tkinter-Specific Exception Handling
All controllers must handle these Python/Tkinter-specific exceptions:

1. **tkinter.TclError**: Widget operation failures
   - Handle widget destruction during callbacks
   - Graceful degradation when widgets unavailable
   - Log widget errors for debugging

2. **decimal.InvalidOperation**: Invalid decimal conversions
   - Display user-friendly number format errors
   - Highlight problematic input fields
   - Suggest correct number formats

3. **ValueError**: Invalid risk method or calculation inputs
   - Display method-specific validation messages
   - Reset fields to last valid state
   - Show method requirements and constraints

4. **AttributeError**: Missing trade object properties
   - Handle incomplete trade data gracefully
   - Initialize missing properties with defaults
   - Validate trade object completeness

### Cross-Platform Performance Contracts

1. **Response Time**: All operations must complete within 100ms on both Windows and Linux
2. **Memory Usage**: Controllers should release Tkinter variables properly to prevent leaks
3. **UI Responsiveness**: Tkinter widget updates must be non-blocking
4. **Decimal Precision**: Consistent financial calculations across platforms
5. **Method Persistence**: Risk method selection preserved during application session
6. **Widget Cleanup**: Proper disposal of Tkinter trace callbacks and event bindings