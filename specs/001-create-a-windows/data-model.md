# Data Model: Risk Calculator

## Core Entities

### Trade (Base Abstract Class)
**Purpose**: Base class for all trade types with common properties
**Properties**:
- `AccountSize` (decimal): Total trading capital in dollars
- `RiskPercentage` (decimal): Risk tolerance as percentage (1-5%)
- `CalculatedRiskAmount` (decimal, read-only): AccountSize × RiskPercentage / 100
- `PositionSize` (decimal, read-only): Calculated position size
- `EstimatedRisk` (decimal, read-only): Actual risk in dollars

**Validation Rules**:
- AccountSize > 0
- RiskPercentage >= 1.0 && RiskPercentage <= 5.0
- All monetary values use decimal precision for accuracy

**State Transitions**:
- New → InputComplete (all required fields filled)
- InputComplete → Calculated (position size computed)
- Calculated → New (inputs changed)

### EquityTrade : Trade
**Purpose**: Represents equity/stock trade with entry and stop loss prices
**Additional Properties**:
- `Symbol` (string): Stock ticker symbol
- `EntryPrice` (decimal): Price per share for entry
- `StopLossPrice` (decimal): Price per share for stop loss
- `CalculatedShares` (int, read-only): Number of shares to purchase

**Validation Rules**:
- Symbol is required and non-empty
- EntryPrice > 0
- StopLossPrice > 0
- StopLossPrice < EntryPrice (for long positions)
- CalculatedShares > 0

**Calculation Logic**:
```
RiskPerShare = EntryPrice - StopLossPrice
CalculatedShares = CalculatedRiskAmount / RiskPerShare
PositionSize = CalculatedShares
EstimatedRisk = CalculatedShares × RiskPerShare
```

### OptionTrade : Trade
**Purpose**: Represents options trade with premium and contract details
**Additional Properties**:
- `OptionSymbol` (string): Option contract symbol
- `Premium` (decimal): Cost per share of option
- `ContractMultiplier` (int): Shares per contract (default 100)
- `CalculatedContracts` (int, read-only): Number of contracts to purchase

**Validation Rules**:
- OptionSymbol is required and non-empty
- Premium > 0
- ContractMultiplier > 0 (typically 100)
- CalculatedContracts > 0

**Calculation Logic**:
```
CostPerContract = Premium × ContractMultiplier
CalculatedContracts = CalculatedRiskAmount / CostPerContract
PositionSize = CalculatedContracts
EstimatedRisk = CalculatedContracts × CostPerContract
```

### FutureTrade : Trade
**Purpose**: Represents futures trade with margin and tick value
**Additional Properties**:
- `ContractSymbol` (string): Futures contract symbol
- `EntryPrice` (decimal): Entry price for futures contract
- `StopLossPrice` (decimal): Stop loss price for futures contract
- `TickValue` (decimal): Dollar value per tick movement
- `TickSize` (decimal): Minimum price increment
- `MarginRequirement` (decimal): Initial margin per contract
- `CalculatedContracts` (int, read-only): Number of contracts to trade

**Validation Rules**:
- ContractSymbol is required and non-empty
- EntryPrice > 0
- StopLossPrice > 0
- StopLossPrice < EntryPrice (for long positions)
- TickValue > 0
- TickSize > 0
- MarginRequirement > 0
- CalculatedContracts > 0

**Calculation Logic**:
```
PriceRisk = EntryPrice - StopLossPrice
TicksAtRisk = PriceRisk / TickSize
RiskPerContract = TicksAtRisk × TickValue
CalculatedContracts = CalculatedRiskAmount / RiskPerContract
PositionSize = CalculatedContracts
EstimatedRisk = CalculatedContracts × RiskPerContract
```

## Supporting Models

### ValidationResult
**Purpose**: Encapsulates validation outcome for user feedback
**Properties**:
- `IsValid` (bool): Whether validation passed
- `ErrorMessages` (List<string>): Collection of validation error messages
- `WarningMessages` (List<string>): Collection of warning messages

### CalculationResult
**Purpose**: Encapsulates calculation outcome and results
**Properties**:
- `IsSuccess` (bool): Whether calculation completed successfully
- `PositionSize` (decimal): Calculated position size
- `EstimatedRisk` (decimal): Actual risk amount in dollars
- `ErrorMessage` (string): Error description if calculation failed

## View Models

### MainViewModel
**Purpose**: Coordinates the main application window and tab management
**Properties**:
- `SelectedTabIndex` (int): Currently active tab (0=Equities, 1=Options, 2=Futures)
- `EquityViewModel` (EquityViewModel): View model for equity tab
- `OptionViewModel` (OptionViewModel): View model for option tab
- `FutureViewModel` (FutureViewModel): View model for future tab

**Commands**:
- None (tab switching handled by TabControl binding)

### EquityViewModel : BaseViewModel
**Purpose**: Manages equity trade input and calculation
**Properties**:
- `Trade` (EquityTrade): Current equity trade data
- `ValidationResult` (ValidationResult): Current validation state
- `CalculationResult` (CalculationResult): Current calculation result

**Commands**:
- `CalculateCommand` (ICommand): Triggers position size calculation
- `ClearCommand` (ICommand): Resets all input fields

### OptionViewModel : BaseViewModel
**Purpose**: Manages option trade input and calculation
**Properties**:
- `Trade` (OptionTrade): Current option trade data
- `ValidationResult` (ValidationResult): Current validation state
- `CalculationResult` (CalculationResult): Current calculation result

**Commands**:
- `CalculateCommand` (ICommand): Triggers position size calculation
- `ClearCommand` (ICommand): Resets all input fields

### FutureViewModel : BaseViewModel
**Purpose**: Manages futures trade input and calculation
**Properties**:
- `Trade` (FutureTrade): Current futures trade data
- `ValidationResult` (ValidationResult): Current validation state
- `CalculationResult` (CalculationResult): Current calculation result

**Commands**:
- `CalculateCommand` (ICommand): Triggers position size calculation
- `ClearCommand` (ICommand): Resets all input fields

### BaseViewModel (Abstract)
**Purpose**: Common functionality for all view models
**Properties**:
- `IsBusy` (bool): Indicates if calculation is in progress
- `HasErrors` (bool): Indicates if validation errors exist

**Events**:
- `PropertyChanged` (INotifyPropertyChanged): Property change notifications

## Data Flow

### Input Validation Flow
1. User modifies input field
2. Property setter triggers validation
3. Validation results update UI error indicators
4. Calculate command enabled/disabled based on validation state

### Calculation Flow
1. User clicks Calculate button
2. Final validation check performed
3. Appropriate calculation service method called
4. Results displayed in UI
5. Error handling for edge cases

### Session Persistence
- Input values maintained during application session
- No permanent storage required
- Tab switching preserves individual tab states
- Application restart clears all data

## Error Handling

### Validation Errors
- Empty required fields
- Invalid numeric ranges
- Business rule violations (e.g., stop loss > entry price)

### Calculation Errors
- Division by zero scenarios
- Negative result values
- Insufficient account capital warnings

### User Experience
- Real-time validation feedback
- Clear error messages with suggested corrections
- Warnings for risky position sizes
- Calculation results prominently displayed