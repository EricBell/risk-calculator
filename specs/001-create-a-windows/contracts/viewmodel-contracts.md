# Controller Contracts

## Base Controller Contract

### Class: BaseController
```python
from abc import ABC, abstractmethod
from typing import Optional
from models.validation_result import ValidationResult

class BaseController(ABC):
    def __init__(self):
        self.is_busy: bool = False
        self.has_errors: bool = False
        self.validation_result: Optional[ValidationResult] = None
```

**Property Contracts**:
- `is_busy`: True during calculation operations, False otherwise
- `has_errors`: True when validation fails, False when all inputs valid
- `validation_result`: Current validation state with error messages

**Event Contracts**:
- Controllers notify views of state changes via callback functions
- Must provide specific property updates for UI refresh

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

**Method Contracts**:

#### calculate_position()
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid and controller not busy
- **Process**:
  1. Sets is_busy = True
  2. Validates trade inputs
  3. Calls risk calculation service
  4. Updates calculation_result
  5. Notifies view of changes
  6. Sets is_busy = False

#### clear_inputs()
```python
def clear_inputs(self) -> None:
```
- **Process**:
  1. Resets trade to default values
  2. Clears calculation_result
  3. Resets validation_result
  4. Notifies view of changes

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for individual field changes
- **Returns**: True if field is valid, False otherwise
- **Side Effects**: Updates validation_result with field-specific errors

## Option Controller Contract

### Class: OptionController(BaseController)
```python
from models.option_trade import OptionTrade

class OptionController(BaseController):
    def __init__(self, view, risk_service, validation_service):
        super().__init__()
        self.trade: OptionTrade = OptionTrade()
        self.calculation_result: Optional[CalculationResult] = None
```

**Property Contracts**:
- `trade`: Current option trade data with validation
- `calculation_result`: Result of last calculation attempt
- All changes to trade properties trigger validation

**Method Contracts**:

#### calculate_position()
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid and controller not busy
- **Process**: Same as EquityController but uses option-specific calculations

#### clear_inputs()
```python
def clear_inputs(self) -> None:
```
- **Process**: Same as EquityController but resets option-specific fields

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for option-specific fields
- **Returns**: True if field is valid, False otherwise

## Future Controller Contract

### Class: FutureController(BaseController)
```python
from models.future_trade import FutureTrade

class FutureController(BaseController):
    def __init__(self, view, risk_service, validation_service):
        super().__init__()
        self.trade: FutureTrade = FutureTrade()
        self.calculation_result: Optional[CalculationResult] = None
```

**Property Contracts**:
- `trade`: Current futures trade data with validation
- `calculation_result`: Result of last calculation attempt
- All changes to trade properties trigger validation

**Method Contracts**:

#### calculate_position()
```python
def calculate_position(self) -> None:
```
- **Preconditions**: Trade inputs are valid and controller not busy
- **Process**: Same as EquityController but uses futures-specific calculations

#### clear_inputs()
```python
def clear_inputs(self) -> None:
```
- **Process**: Same as EquityController but resets futures-specific fields

#### validate_input(field_name: str, value: any) -> bool
```python
def validate_input(self, field_name: str, value: any) -> bool:
```
- **Purpose**: Real-time validation for futures-specific fields
- **Returns**: True if field is valid, False otherwise

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
```

**Property Contracts**:
- `current_tab`: Currently active tab ("equity", "option", "future")
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
  4. Updates current_tab property

#### get_active_controller() -> BaseController
```python
def get_active_controller(self) -> BaseController:
```
- **Purpose**: Returns the controller for currently active tab
- **Returns**: EquityController, OptionController, or FutureController

## View Interface Contracts

### View Notification Methods
Each view must implement these methods for controller communication:

#### update_calculation_result(result: CalculationResult) -> None
```python
def update_calculation_result(self, result: CalculationResult) -> None:
```
- **Purpose**: Display calculation results in the UI
- **Process**: Updates result labels and handles error display

#### update_validation_errors(errors: ValidationResult) -> None
```python
def update_validation_errors(self, errors: ValidationResult) -> None:
```
- **Purpose**: Display validation errors in the UI
- **Process**: Shows field-specific error messages

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
- **Process**: Clears all entry fields and result displays

## Error Handling Contracts

### Exception Handling
All controllers must handle these exceptions:

1. **ValidationError**: Invalid input data
   - Display user-friendly error messages
   - Highlight problematic fields
   - Prevent calculation until resolved

2. **CalculationError**: Calculation service failures
   - Display error message to user
   - Log error for debugging
   - Reset calculation state

3. **SystemError**: Unexpected system errors
   - Display generic error message
   - Log detailed error information
   - Attempt graceful recovery

### Performance Contracts

1. **Response Time**: All operations must complete within 100ms
2. **Memory Usage**: Controllers should not retain large datasets
3. **UI Responsiveness**: Never block UI thread during operations
4. **Cross-Platform**: All functionality must work on Windows and Linux