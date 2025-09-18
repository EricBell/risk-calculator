# Risk Calculation Service Contract for Python Risk Calculator

## Class: RiskCalculationService

### Purpose
Provides risk calculation methods for different asset classes with support for three risk calculation approaches: percentage-based, fixed amount, and level-based position sizing. Designed specifically for Python with Decimal precision and cross-platform compatibility.

### Dependencies
```python
from decimal import Decimal, ROUND_DOWN
from typing import Optional
from models.equity_trade import EquityTrade
from models.option_trade import OptionTrade
from models.future_trade import FutureTrade
from models.calculation_result import CalculationResult
from models.risk_method import RiskMethod
```

## Method Contracts

### calculate_equity_position
```python
def calculate_equity_position(trade: EquityTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_method` in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]
- **For PERCENTAGE method**:
  - `trade.risk_percentage` >= 1.0 and <= 5.0
  - `trade.stop_loss_price` > 0
  - For LONG: `trade.stop_loss_price` < `trade.entry_price`
  - For SHORT: `trade.stop_loss_price` > `trade.entry_price`
- **For FIXED_AMOUNT method**:
  - `trade.fixed_risk_amount` >= 10 and <= 500
  - `trade.fixed_risk_amount` <= (`trade.account_size` * 0.05)
  - `trade.stop_loss_price` > 0 and proper direction validation
- **For LEVEL_BASED method**:
  - `trade.support_resistance_level` > 0
  - For LONG: `trade.support_resistance_level` < `trade.entry_price`
  - For SHORT: `trade.support_resistance_level` > `trade.entry_price`

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of shares (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.risk_method_used` = method used for calculation
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- **PERCENTAGE**: Position size = (account_size × risk_percentage / 100) / (entry_price - stop_loss_price)
- **FIXED_AMOUNT**: Position size = fixed_risk_amount / (entry_price - stop_loss_price)
- **LEVEL_BASED**: Position size = (account_size × 0.02) / (entry_price - support_resistance_level)
- Shares rounded down to whole numbers using Decimal.quantize(Decimal('1'), rounding=ROUND_DOWN)
- Maximum position size limited by account capital divided by entry price
- Warning if position size would exceed 25% of account value
- All calculations use decimal.Decimal for precise financial arithmetic
- Cross-platform decimal precision: getcontext().prec = 28 for consistency

**Error Conditions**:
- Invalid input parameters → is_success = False, error_message describes issue
- Zero risk distance (prices equal) → "Risk distance cannot be zero"
- Calculated position exceeds account → Warning message included
- Method-specific validation failures → Descriptive error message

### calculate_option_position
```python
def calculate_option_position(trade: OptionTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_method` in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT] (LEVEL_BASED not supported)
- `trade.premium` > 0
- `trade.contract_multiplier` > 0 (typically 100)
- **For PERCENTAGE method**: `trade.risk_percentage` >= 1.0 and <= 5.0
- **For FIXED_AMOUNT method**: `trade.fixed_risk_amount` >= 10 and <= 500

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of contracts (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.risk_method_used` = method used for calculation
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- **PERCENTAGE**: Contracts = (account_size × risk_percentage / 100) / (premium × contract_multiplier)
- **FIXED_AMOUNT**: Contracts = fixed_risk_amount / (premium × contract_multiplier)
- **LEVEL_BASED**: Return error "Level-based method not applicable for options"
- Contracts rounded down to whole numbers using int() function
- Risk equals total premium paid for contracts
- Warning if premium cost exceeds risk tolerance
- Use decimal.Decimal for precise financial calculations

**Error Conditions**:
- Invalid input parameters → is_success = False, error_message describes issue
- Level-based method selected → "Level-based method not supported for options"
- Premium too high for risk tolerance → Warning message about reducing contracts

### calculate_future_position
```python
def calculate_future_position(trade: FutureTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_method` in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]
- `trade.entry_price` > 0
- `trade.tick_value` > 0
- `trade.tick_size` > 0
- `trade.margin_requirement` > 0
- **For PERCENTAGE method**:
  - `trade.risk_percentage` >= 1.0 and <= 5.0
  - `trade.stop_loss_price` > 0 with proper direction validation
- **For FIXED_AMOUNT method**:
  - `trade.fixed_risk_amount` >= 10 and <= 500
  - `trade.stop_loss_price` > 0 with proper direction validation
- **For LEVEL_BASED method**:
  - `trade.support_resistance_level` > 0 with proper direction validation

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of contracts (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.risk_method_used` = method used for calculation
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- **PERCENTAGE**: Contracts = (account_size × risk_percentage / 100) / (tick_value × ticks_at_risk)
- **FIXED_AMOUNT**: Contracts = fixed_risk_amount / (tick_value × ticks_at_risk)
- **LEVEL_BASED**: Contracts = (account_size × 0.02) / (tick_value × ticks_to_level)
- Ticks at risk = price_difference / tick_size
- Contracts rounded down to whole numbers using int() function
- Margin requirement checked for position feasibility
- Use decimal.Decimal for precise financial calculations

**Error Conditions**:
- Invalid input parameters → is_success = False, error_message describes issue
- Insufficient margin for calculated position → Warning about margin requirements
- Zero tick risk distance → "Price difference must be at least one tick"

## Validation Service Contract

### Class: TradeValidationService

### validate_equity_trade
```python
def validate_equity_trade(trade: EquityTrade) -> ValidationResult:
```

**Method-Specific Validation Rules**:
- **Common to all methods**:
  - symbol: Required, non-empty string
  - account_size: > 0, reasonable maximum (e.g., $10M)
  - entry_price: > 0, reasonable range ($0.01 - $10,000)
  - risk_method: Must be valid RiskMethod enum value

- **PERCENTAGE method**:
  - risk_percentage: >= 1.0 and <= 5.0
  - stop_loss_price: > 0, proper direction relative to entry_price

- **FIXED_AMOUNT method**:
  - fixed_risk_amount: >= 10 and <= 500 and <= (account_size × 0.05)
  - stop_loss_price: > 0, proper direction relative to entry_price

- **LEVEL_BASED method**:
  - support_resistance_level: > 0, proper direction relative to entry_price
  - risk_percentage: Optional, defaults to 2% if not specified

**Error Messages**:
- "Symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%" (PERCENTAGE method)
- "Fixed risk amount must be between $10 and $500" (FIXED_AMOUNT method)
- "Fixed risk amount cannot exceed 5% of account size" (FIXED_AMOUNT method)
- "Entry price must be greater than $0"
- "Stop loss must be below entry price for long positions" (PERCENTAGE/FIXED_AMOUNT methods)
- "Support level must be below entry price for long positions" (LEVEL_BASED method)
- "Resistance level must be above entry price for short positions" (LEVEL_BASED method)

### validate_option_trade
```python
def validate_option_trade(trade: OptionTrade) -> ValidationResult:
```

**Method-Specific Validation Rules**:
- **Common to all methods**:
  - option_symbol: Required, non-empty string
  - account_size: > 0, reasonable maximum
  - premium: > 0, reasonable range ($0.01 - $1,000)
  - contract_multiplier: > 0, typically 100

- **PERCENTAGE method**: risk_percentage: >= 1.0 and <= 5.0
- **FIXED_AMOUNT method**: fixed_risk_amount: >= 10 and <= 500 and <= (account_size × 0.05)
- **LEVEL_BASED method**: Not supported - validation should return error

**Error Messages**:
- "Option symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%" (PERCENTAGE method)
- "Fixed risk amount must be between $10 and $500" (FIXED_AMOUNT method)
- "Premium must be greater than $0"
- "Contract multiplier must be greater than 0"
- "Level-based method not supported for options trading" (LEVEL_BASED method)

### validate_future_trade
```python
def validate_future_trade(trade: FutureTrade) -> ValidationResult:
```

**Method-Specific Validation Rules**:
- **Common to all methods**:
  - contract_symbol: Required, non-empty string
  - account_size: > 0, reasonable maximum
  - entry_price: > 0, reasonable range
  - tick_value: > 0, reasonable range ($0.01 - $1,000)
  - tick_size: > 0, reasonable range (0.0001 - 100)
  - margin_requirement: > 0, reasonable range

- **PERCENTAGE method**:
  - risk_percentage: >= 1.0 and <= 5.0
  - stop_loss_price: > 0, proper direction relative to entry_price

- **FIXED_AMOUNT method**:
  - fixed_risk_amount: >= 10 and <= 500 and <= (account_size × 0.05)
  - stop_loss_price: > 0, proper direction relative to entry_price

- **LEVEL_BASED method**:
  - support_resistance_level: > 0, proper direction relative to entry_price
  - risk_percentage: Optional, defaults to 2% if not specified

**Error Messages**:
- "Contract symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%" (PERCENTAGE method)
- "Fixed risk amount must be between $10 and $500" (FIXED_AMOUNT method)
- "Entry price must be greater than $0"
- "Stop loss must be below entry price for long positions" (PERCENTAGE/FIXED_AMOUNT methods)
- "Support level must be below entry price for long positions" (LEVEL_BASED method)
- "Tick value must be greater than $0"
- "Tick size must be greater than 0"
- "Margin requirement must be greater than $0"

## Risk Method Helper Contract

### Class: RiskAmountCalculator

### calculate_risk_amount
```python
def calculate_risk_amount(account_size: Decimal, risk_method: RiskMethod,
                         risk_percentage: Decimal = None,
                         fixed_risk_amount: Decimal = None) -> Decimal:
```

**Purpose**: Centralized calculation of risk amount based on selected method

**Business Rules**:
- **PERCENTAGE**: Returns account_size × risk_percentage / 100
- **FIXED_AMOUNT**: Returns fixed_risk_amount
- **LEVEL_BASED**: Returns account_size × 0.02 (default 2%)

**Validation**:
- Ensures required parameters are provided for each method
- Validates parameter ranges before calculation

## Python Implementation Examples

### Decimal Precision Setup
```python
from decimal import Decimal, getcontext, ROUND_DOWN

class RiskCalculationService:
    def __init__(self):
        # Set consistent precision for cross-platform compatibility
        getcontext().prec = 28
        self.DEFAULT_LEVEL_RISK_PERCENTAGE = Decimal('0.02')  # 2% for level-based

    def _round_position_size(self, position_size: Decimal) -> int:
        """Round position size down to whole number"""
        return int(position_size.quantize(Decimal('1'), rounding=ROUND_DOWN))

    def _calculate_risk_amount(self, trade) -> Decimal:
        """Calculate risk amount based on method"""
        if trade.risk_method == RiskMethod.PERCENTAGE:
            return trade.account_size * trade.risk_percentage / Decimal('100')
        elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
            return trade.fixed_risk_amount
        elif trade.risk_method == RiskMethod.LEVEL_BASED:
            return trade.account_size * self.DEFAULT_LEVEL_RISK_PERCENTAGE
        else:
            raise ValueError(f"Unsupported risk method: {trade.risk_method}")
```

### Performance Contracts

#### Response Time Requirements
- All calculations MUST complete within 100ms on target hardware
- Decimal operations optimized for financial precision over speed
- No network calls or I/O operations in calculation methods
- Memory usage per calculation < 1MB

#### Cross-Platform Consistency
- Identical results on Windows and Linux Python 3.12+
- Consistent decimal precision across different architectures
- Unicode symbol handling for international markets
- Timezone-independent calculations (no datetime dependencies)

## Test Contracts

### Unit Test Requirements

Each calculation method must have tests for:
1. **Valid input scenarios** - Verify correct calculations for all three methods
2. **Method switching** - Verify proper handling when risk method changes
3. **Boundary conditions** - Test edge cases (min/max values) for each method
4. **Invalid input handling** - Verify error messages for each method
5. **Rounding behavior** - Ensure proper fractional handling across methods
6. **Business rule enforcement** - Verify warnings and limits for each method
7. **Decimal precision** - Verify financial calculation accuracy to 2 decimal places
8. **Method-specific validation** - Test validation rules unique to each method
9. **Cross-platform consistency** - Same results on Windows and Linux
10. **Performance requirements** - All calculations under 100ms

### Integration Test Scenarios

1. **End-to-end calculation flow**:
   - Risk method selection → Input validation → Calculation → Result display
   - Error handling → User feedback → Correction flow
   - Method switching during session → State preservation

2. **Cross-method consistency**:
   - Same account size produces expected results across methods
   - Validation consistency maintains user experience
   - Method availability varies correctly by asset class

3. **Performance requirements**:
   - All calculations complete within 100ms regardless of method
   - Memory usage remains under target limits
   - Cross-platform compatibility (Windows and Linux)
   - Method switching is instantaneous in UI