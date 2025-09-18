# Risk Calculation Service Contract

## Class: RiskCalculationService

### Purpose
Provides risk calculation methods for different asset classes with input validation and error handling.

## Method Contracts

### calculate_equity_position
```python
def calculate_equity_position(trade: EquityTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_percentage` >= 1.0 and <= 5.0
- `trade.entry_price` > 0
- `trade.stop_loss_price` > 0
- `trade.stop_loss_price` < `trade.entry_price`

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of shares (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- Position size calculated as: (account_size × risk_percentage / 100) / (entry_price - stop_loss_price)
- Shares rounded down to whole numbers using int() function
- Maximum position size limited by account capital
- Warning if position size would exceed 25% of account value
- Use decimal.Decimal for precise financial calculations

**Error Conditions**:
- Invalid input parameters → is_success = False, error_message describes issue
- Zero risk distance (entry_price = stop_loss_price) → "Risk distance cannot be zero"
- Calculated position exceeds account → Warning message included

### calculate_option_position
```python
def calculate_option_position(trade: OptionTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_percentage` >= 1.0 and <= 5.0
- `trade.premium` > 0
- `trade.contract_multiplier` > 0 (typically 100)

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of contracts (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- Position size calculated as: (account_size × risk_percentage / 100) / (premium × contract_multiplier)
- Contracts rounded down to whole numbers using int() function
- Risk equals total premium paid for contracts
- Warning if premium cost exceeds risk tolerance
- Use decimal.Decimal for precise financial calculations

**Error Conditions**:
- Invalid input parameters → is_success = False, error_message describes issue
- Premium too high for risk tolerance → Warning message about reducing contracts

### calculate_future_position
```python
def calculate_future_position(trade: FutureTrade) -> CalculationResult:
```

**Input Contract**:
- `trade.account_size` > 0
- `trade.risk_percentage` >= 1.0 and <= 5.0
- `trade.entry_price` > 0
- `trade.stop_loss_price` > 0
- `trade.stop_loss_price` < `trade.entry_price`
- `trade.tick_value` > 0
- `trade.tick_size` > 0
- `trade.margin_requirement` > 0

**Output Contract**:
- `CalculationResult.is_success` = True if calculation completed
- `CalculationResult.position_size` = calculated number of contracts (rounded down)
- `CalculationResult.estimated_risk` = actual risk amount in dollars
- `CalculationResult.error_message` = None if successful

**Business Rules**:
- Ticks at risk = (entry_price - stop_loss_price) / tick_size
- Risk per contract = ticks_at_risk × tick_value
- Position size = (account_size × risk_percentage / 100) / risk_per_contract
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

**Validation Rules**:
- symbol: Required, non-empty string
- account_size: > 0, reasonable maximum (e.g., $10M)
- risk_percentage: >= 1.0 and <= 5.0
- entry_price: > 0, reasonable range ($0.01 - $10,000)
- stop_loss_price: > 0, < entry_price

**Error Messages**:
- "Symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%"
- "Entry price must be greater than $0"
- "Stop loss must be below entry price for long positions"

### validate_option_trade
```python
def validate_option_trade(trade: OptionTrade) -> ValidationResult:
```

**Validation Rules**:
- option_symbol: Required, non-empty string
- account_size: > 0, reasonable maximum
- risk_percentage: >= 1.0 and <= 5.0
- premium: > 0, reasonable range ($0.01 - $1,000)
- contract_multiplier: > 0, typically 100

**Error Messages**:
- "Option symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%"
- "Premium must be greater than $0"
- "Contract multiplier must be greater than 0"

### validate_future_trade
```python
def validate_future_trade(trade: FutureTrade) -> ValidationResult:
```

**Validation Rules**:
- contract_symbol: Required, non-empty string
- account_size: > 0, reasonable maximum
- risk_percentage: >= 1.0 and <= 5.0
- entry_price: > 0, reasonable range
- stop_loss_price: > 0, < entry_price
- tick_value: > 0, reasonable range ($0.01 - $1,000)
- tick_size: > 0, reasonable range (0.0001 - 100)
- margin_requirement: > 0, reasonable range

**Error Messages**:
- "Contract symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%"
- "Entry price must be greater than $0"
- "Stop loss must be below entry price for long positions"
- "Tick value must be greater than $0"
- "Tick size must be greater than 0"
- "Margin requirement must be greater than $0"

## Test Contracts

### Unit Test Requirements

Each calculation method must have tests for:
1. **Valid input scenarios** - Verify correct calculations
2. **Boundary conditions** - Test edge cases (min/max values)
3. **Invalid input handling** - Verify error messages
4. **Rounding behavior** - Ensure proper fractional handling
5. **Business rule enforcement** - Verify warnings and limits
6. **Decimal precision** - Verify financial calculation accuracy

### Integration Test Scenarios

1. **End-to-end calculation flow**:
   - Input validation → Calculation → Result display
   - Error handling → User feedback → Correction flow

2. **Cross-asset class consistency**:
   - Same account/risk settings produce proportional results
   - Validation consistency across asset types

3. **Performance requirements**:
   - All calculations complete within 100ms
   - Memory usage remains under target limits
   - Cross-platform compatibility (Windows and Linux)