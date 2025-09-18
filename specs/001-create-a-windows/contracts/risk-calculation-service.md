# Risk Calculation Service Contract

## Interface: IRiskCalculationService

### Purpose
Provides risk calculation methods for different asset classes with input validation and error handling.

## Method Contracts

### CalculateEquityPosition
```csharp
CalculationResult CalculateEquityPosition(EquityTrade trade)
```

**Input Contract**:
- `trade.AccountSize` > 0
- `trade.RiskPercentage` >= 1.0 && <= 5.0
- `trade.EntryPrice` > 0
- `trade.StopLossPrice` > 0
- `trade.StopLossPrice` < `trade.EntryPrice`

**Output Contract**:
- `CalculationResult.IsSuccess` = true if calculation completed
- `CalculationResult.PositionSize` = calculated number of shares (rounded down)
- `CalculationResult.EstimatedRisk` = actual risk amount in dollars
- `CalculationResult.ErrorMessage` = null if successful

**Business Rules**:
- Position size calculated as: (AccountSize × RiskPercentage / 100) / (EntryPrice - StopLossPrice)
- Shares rounded down to whole numbers
- Maximum position size limited by account capital
- Warning if position size would exceed 25% of account value

**Error Conditions**:
- Invalid input parameters → IsSuccess = false, ErrorMessage describes issue
- Zero risk distance (EntryPrice = StopLossPrice) → "Risk distance cannot be zero"
- Calculated position exceeds account → Warning message included

### CalculateOptionPosition
```csharp
CalculationResult CalculateOptionPosition(OptionTrade trade)
```

**Input Contract**:
- `trade.AccountSize` > 0
- `trade.RiskPercentage` >= 1.0 && <= 5.0
- `trade.Premium` > 0
- `trade.ContractMultiplier` > 0 (typically 100)

**Output Contract**:
- `CalculationResult.IsSuccess` = true if calculation completed
- `CalculationResult.PositionSize` = calculated number of contracts (rounded down)
- `CalculationResult.EstimatedRisk` = actual risk amount in dollars
- `CalculationResult.ErrorMessage` = null if successful

**Business Rules**:
- Position size calculated as: (AccountSize × RiskPercentage / 100) / (Premium × ContractMultiplier)
- Contracts rounded down to whole numbers
- Risk equals total premium paid for contracts
- Warning if premium cost exceeds risk tolerance

**Error Conditions**:
- Invalid input parameters → IsSuccess = false, ErrorMessage describes issue
- Premium too high for risk tolerance → Warning message about reducing contracts

### CalculateFuturePosition
```csharp
CalculationResult CalculateFuturePosition(FutureTrade trade)
```

**Input Contract**:
- `trade.AccountSize` > 0
- `trade.RiskPercentage` >= 1.0 && <= 5.0
- `trade.EntryPrice` > 0
- `trade.StopLossPrice` > 0
- `trade.StopLossPrice` < `trade.EntryPrice`
- `trade.TickValue` > 0
- `trade.TickSize` > 0
- `trade.MarginRequirement` > 0

**Output Contract**:
- `CalculationResult.IsSuccess` = true if calculation completed
- `CalculationResult.PositionSize` = calculated number of contracts (rounded down)
- `CalculationResult.EstimatedRisk` = actual risk amount in dollars
- `CalculationResult.ErrorMessage` = null if successful

**Business Rules**:
- Ticks at risk = (EntryPrice - StopLossPrice) / TickSize
- Risk per contract = TicksAtRisk × TickValue
- Position size = (AccountSize × RiskPercentage / 100) / RiskPerContract
- Contracts rounded down to whole numbers
- Margin requirement checked for position feasibility

**Error Conditions**:
- Invalid input parameters → IsSuccess = false, ErrorMessage describes issue
- Insufficient margin for calculated position → Warning about margin requirements
- Zero tick risk distance → "Price difference must be at least one tick"

## Validation Service Contract

### Interface: ITradeValidationService

### ValidateEquityTrade
```csharp
ValidationResult ValidateEquityTrade(EquityTrade trade)
```

**Validation Rules**:
- Symbol: Required, non-empty string
- AccountSize: > 0, reasonable maximum (e.g., $10M)
- RiskPercentage: >= 1.0 && <= 5.0
- EntryPrice: > 0, reasonable range ($0.01 - $10,000)
- StopLossPrice: > 0, < EntryPrice

**Error Messages**:
- "Symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%"
- "Entry price must be greater than $0"
- "Stop loss must be below entry price for long positions"

### ValidateOptionTrade
```csharp
ValidationResult ValidateOptionTrade(OptionTrade trade)
```

**Validation Rules**:
- OptionSymbol: Required, non-empty string
- AccountSize: > 0, reasonable maximum
- RiskPercentage: >= 1.0 && <= 5.0
- Premium: > 0, reasonable range ($0.01 - $1,000)
- ContractMultiplier: > 0, typically 100

**Error Messages**:
- "Option symbol is required"
- "Account size must be greater than $0"
- "Risk percentage must be between 1% and 5%"
- "Premium must be greater than $0"
- "Contract multiplier must be greater than 0"

### ValidateFutureTrade
```csharp
ValidationResult ValidateFutureTrade(FutureTrade trade)
```

**Validation Rules**:
- ContractSymbol: Required, non-empty string
- AccountSize: > 0, reasonable maximum
- RiskPercentage: >= 1.0 && <= 5.0
- EntryPrice: > 0, reasonable range
- StopLossPrice: > 0, < EntryPrice
- TickValue: > 0, reasonable range ($0.01 - $1,000)
- TickSize: > 0, reasonable range (0.0001 - 100)
- MarginRequirement: > 0, reasonable range

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