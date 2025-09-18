# Controller Contracts

## Base Controller Contract

### Class: BaseController
```python
from abc import ABC, abstractmethod
from typing import Optional
from models.validation_result import ValidationResult
from models.risk_method import RiskMethod

class BaseController(ABC):
    def __init__(self):
        self.is_busy: bool = False
        self.has_errors: bool = False
        self.validation_result: Optional[ValidationResult] = None
        self.current_risk_method: RiskMethod = RiskMethod.PERCENTAGE  # Default method
```

**Property Contracts**:
- `is_busy`: True during calculation operations, False otherwise
- `has_errors`: True when validation fails, False when all inputs valid
- `validation_result`: Current validation state with error messages
- `current_risk_method`: Currently selected risk calculation method

**Event Contracts**:
- Controllers notify views of state changes via callback functions
- Must provide specific property updates for UI refresh
- Risk method changes trigger UI layout updates

## Equity Controller Contract

### Class: EquityController(BaseController)
```python
from models.equity_trade import EquityTrade
from models.calculation_result import CalculationResult

class EquityController(BaseController):
    def __init__(self, view, risk_service, validation_service):
        super().__init__()
        self.trade: EquityTrade = EquityTrade()
        self.calculation_result: Optional[CalculationResult] = None
        self.view = view
        self.risk_service = risk_service
        self.validation_service = validation_service
```

**Property Contracts**:
- `trade`: Current equity trade data with validation
- `calculation_result`: Result of last calculation attempt
- All changes to trade properties trigger validation
- Risk method selection determines which fields are required

**Method Contracts**:

#### set_risk_method(method: RiskMethod) -> None
```python
def set_risk_method(self, method: RiskMethod) -> None:
```
- **Purpose**: Changes the risk calculation method and updates UI
- **Process**:
  1. Validates method is supported for equities (all three methods supported)
  2. Updates current_risk_method property
  3. Clears calculation_result
  4. Triggers UI field visibility changes
  5. Resets validation state
  6. Notifies view of method change

#### calculate_position() -> None
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid for selected method and controller not busy
- **Process**:
  1. Sets is_busy = True
  2. Validates trade inputs based on current_risk_method
  3. Calls risk_service.calculate_equity_position(trade)
  4. Updates calculation_result with method indicator
  5. Notifies view of changes
  6. Sets is_busy = False

#### clear_inputs() -> None
```python
def clear_inputs(self) -> None:
```
- **Process**:
  1. Resets trade to default values (preserves risk_method)
  2. Clears calculation_result
  3. Resets validation_result
  4. Maintains current risk method selection
  5. Notifies view of changes

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for individual field changes
- **Method-aware validation**: Different validation rules based on current_risk_method
- **Returns**: True if field is valid, False otherwise
- **Side Effects**: Updates validation_result with field-specific errors

#### get_required_fields() -> List[str]
```python
def get_required_fields(self) -> List[str]:
```
- **Purpose**: Returns list of required fields based on current risk method
- **PERCENTAGE method**: ['symbol', 'account_size', 'risk_percentage', 'entry_price', 'stop_loss_price']
- **FIXED_AMOUNT method**: ['symbol', 'account_size', 'fixed_risk_amount', 'entry_price', 'stop_loss_price']
- **LEVEL_BASED method**: ['symbol', 'account_size', 'entry_price', 'support_resistance_level', 'trade_direction']

## Option Controller Contract

### Class: OptionController(BaseController)
```python
from models.option_trade import OptionTrade

class OptionController(BaseController):
    def __init__(self, view, risk_service, validation_service):
        super().__init__()
        self.trade: OptionTrade = OptionTrade()
        self.calculation_result: Optional[CalculationResult] = None
        self.supported_methods = [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]  # Level-based not supported
```

**Property Contracts**:
- `trade`: Current option trade data with validation
- `calculation_result`: Result of last calculation attempt
- `supported_methods`: Only PERCENTAGE and FIXED_AMOUNT methods available
- All changes to trade properties trigger validation

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

## View Interface Contracts

### View Notification Methods
Each view must implement these methods for controller communication:

#### update_calculation_result(result: CalculationResult) -> None
```python
def update_calculation_result(self, result: CalculationResult) -> None:
```
- **Purpose**: Display calculation results in the UI
- **Process**: Updates result labels and shows which risk method was used

#### update_validation_errors(errors: ValidationResult) -> None
```python
def update_validation_errors(self, errors: ValidationResult) -> None:
```
- **Purpose**: Display validation errors in the UI
- **Process**: Shows field-specific error messages with method context

#### set_busy_state(is_busy: bool) -> None
```python
def set_busy_state(self, is_busy: bool) -> None:
```
- **Purpose**: Show/hide loading indicators during calculations
- **Process**: Disables inputs and shows progress indicator when busy

#### clear_all_inputs() -> None
```python
def clear_all_inputs(self) -> None:
```
- **Purpose**: Reset all form inputs to default values
- **Process**: Clears all entry fields but preserves risk method selection

#### update_risk_method_ui(method: RiskMethod, supported_methods: List[RiskMethod]) -> None
```python
def update_risk_method_ui(self, method: RiskMethod, supported_methods: List[RiskMethod]) -> None:
```
- **Purpose**: Update UI to reflect risk method selection
- **Process**:
  1. Enable/disable risk method radio buttons based on supported_methods
  2. Show/hide relevant input fields based on selected method
  3. Update field labels and help text
  4. Clear fields not relevant to selected method

#### show_method_fields(method: RiskMethod) -> None
```python
def show_method_fields(self, method: RiskMethod) -> None:
```
- **Purpose**: Show/hide input fields based on selected risk method
- **PERCENTAGE method**: Show risk_percentage field, stop_loss fields
- **FIXED_AMOUNT method**: Show fixed_risk_amount field, stop_loss fields
- **LEVEL_BASED method**: Show support_resistance_level field, trade_direction selector

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

## Error Handling Contracts

### Method-Specific Exception Handling
All controllers must handle these method-specific exceptions:

1. **UnsupportedRiskMethodError**: Method not available for asset class
   - Display asset-specific error message
   - Revert to previous method selection
   - Show available methods for current asset

2. **ValidationError**: Invalid input data for selected method
   - Display method-specific error messages
   - Highlight problematic fields
   - Show method requirements

3. **CalculationError**: Calculation service failures
   - Display error message with method context
   - Log error for debugging
   - Reset calculation state

4. **SystemError**: Unexpected system errors
   - Display generic error message
   - Log detailed error information
   - Attempt graceful recovery

### Performance Contracts

1. **Response Time**: All operations must complete within 100ms regardless of method
2. **Memory Usage**: Controllers should not retain large datasets
3. **UI Responsiveness**: Method switching must be instantaneous
4. **Cross-Platform**: All functionality must work on Windows and Linux
5. **Method Persistence**: Risk method selection preserved during session