# Data Model: Risk Calculator

## Enumerations

### RiskMethod
**Purpose**: Defines the three available risk calculation approaches
**Values**:
- `PERCENTAGE`: Risk based on percentage of account size (1-5%)
- `FIXED_AMOUNT`: Risk based on fixed dollar amount ($10-$500)
- `LEVEL_BASED`: Risk based on technical support/resistance levels

## Core Entities

### Trade (Base Abstract Class)
**Purpose**: Base class for all trade types with common properties
**Properties**:
- `account_size` (Decimal): Total trading capital in dollars
- `risk_method` (RiskMethod): Selected risk calculation method
- `risk_percentage` (Decimal, optional): Risk tolerance as percentage (1-5%) - for PERCENTAGE method
- `fixed_risk_amount` (Decimal, optional): Fixed dollar risk amount ($10-$500) - for FIXED_AMOUNT method
- `calculated_risk_amount` (Decimal, read-only): Computed risk amount based on selected method
- `position_size` (Decimal, read-only): Calculated position size
- `estimated_risk` (Decimal, read-only): Actual risk in dollars

**Validation Rules**:
- account_size > 0
- For PERCENTAGE method: risk_percentage >= 1.0 and <= 5.0
- For FIXED_AMOUNT method: fixed_risk_amount >= 10 and <= 500 and <= (account_size * 0.05)
- All monetary values use Decimal precision for accuracy

**State Transitions**:
- New → InputComplete (all required fields for selected method filled)
- InputComplete → Calculated (position size computed)
- Calculated → New (inputs changed)

**Calculation Logic**:
```python
# Risk amount calculation based on method
if risk_method == RiskMethod.PERCENTAGE:
    calculated_risk_amount = account_size * risk_percentage / 100
elif risk_method == RiskMethod.FIXED_AMOUNT:
    calculated_risk_amount = fixed_risk_amount
elif risk_method == RiskMethod.LEVEL_BASED:
    calculated_risk_amount = account_size * 0.02  # Default 2% if not specified
```

### EquityTrade : Trade
**Purpose**: Represents equity/stock trade with entry and stop/level prices
**Additional Properties**:
- `symbol` (str): Stock ticker symbol
- `entry_price` (Decimal): Price per share for entry
- `stop_loss_price` (Decimal, optional): Price per share for stop loss - PERCENTAGE/FIXED_AMOUNT methods
- `support_resistance_level` (Decimal, optional): Technical level price - LEVEL_BASED method
- `trade_direction` (str): "LONG" or "SHORT" - determines which levels are valid
- `calculated_shares` (int, read-only): Number of shares to purchase

**Validation Rules**:
- symbol is required and non-empty
- entry_price > 0
- For PERCENTAGE/FIXED_AMOUNT methods: stop_loss_price > 0
- For LONG trades: stop_loss_price < entry_price OR support_resistance_level < entry_price
- For SHORT trades: stop_loss_price > entry_price OR support_resistance_level > entry_price
- calculated_shares > 0

**Calculation Logic**:
```python
# Determine risk per share based on method
if risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
    risk_per_share = abs(entry_price - stop_loss_price)
elif risk_method == RiskMethod.LEVEL_BASED:
    risk_per_share = abs(entry_price - support_resistance_level)

calculated_shares = int(calculated_risk_amount / risk_per_share)
position_size = calculated_shares
estimated_risk = calculated_shares * risk_per_share
```

### OptionTrade : Trade
**Purpose**: Represents options trade with premium and contract details
**Additional Properties**:
- `option_symbol` (str): Option contract symbol
- `premium` (Decimal): Cost per share of option
- `contract_multiplier` (int): Shares per contract (default 100)
- `calculated_contracts` (int, read-only): Number of contracts to purchase

**Validation Rules**:
- option_symbol is required and non-empty
- premium > 0
- contract_multiplier > 0 (typically 100)
- calculated_contracts > 0
- Level-based method not supported for options (risk is premium paid)

**Calculation Logic**:
```python
# Options risk is always the premium paid (no stop loss)
cost_per_contract = premium * contract_multiplier

if risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
    calculated_contracts = int(calculated_risk_amount / cost_per_contract)
elif risk_method == RiskMethod.LEVEL_BASED:
    # Level-based not applicable - disable this option in UI
    calculated_contracts = 0

position_size = calculated_contracts
estimated_risk = calculated_contracts * cost_per_contract
```

### FutureTrade : Trade
**Purpose**: Represents futures trade with margin and tick value
**Additional Properties**:
- `contract_symbol` (str): Futures contract symbol
- `entry_price` (Decimal): Entry price for futures contract
- `stop_loss_price` (Decimal, optional): Stop loss price - PERCENTAGE/FIXED_AMOUNT methods
- `support_resistance_level` (Decimal, optional): Technical level price - LEVEL_BASED method
- `tick_value` (Decimal): Dollar value per tick movement
- `tick_size` (Decimal): Minimum price increment
- `margin_requirement` (Decimal): Initial margin per contract
- `trade_direction` (str): "LONG" or "SHORT"
- `calculated_contracts` (int, read-only): Number of contracts to trade

**Validation Rules**:
- contract_symbol is required and non-empty
- entry_price > 0
- For PERCENTAGE/FIXED_AMOUNT methods: stop_loss_price > 0
- For LONG trades: stop_loss_price < entry_price OR support_resistance_level < entry_price
- For SHORT trades: stop_loss_price > entry_price OR support_resistance_level > entry_price
- tick_value > 0
- tick_size > 0
- margin_requirement > 0
- calculated_contracts > 0

**Calculation Logic**:
```python
# Determine price risk based on method
if risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
    price_risk = abs(entry_price - stop_loss_price)
elif risk_method == RiskMethod.LEVEL_BASED:
    price_risk = abs(entry_price - support_resistance_level)

ticks_at_risk = price_risk / tick_size
risk_per_contract = ticks_at_risk * tick_value
calculated_contracts = int(calculated_risk_amount / risk_per_contract)
position_size = calculated_contracts
estimated_risk = calculated_contracts * risk_per_contract
```

## Supporting Models

### ValidationResult
**Purpose**: Encapsulates validation outcome for user feedback
**Properties**:
- `is_valid` (bool): Whether validation passed
- `error_messages` (List[str]): Collection of validation error messages
- `warning_messages` (List[str]): Collection of warning messages
- `field_errors` (Dict[str, str]): Field-specific error messages

### CalculationResult
**Purpose**: Encapsulates calculation outcome and results
**Properties**:
- `is_success` (bool): Whether calculation completed successfully
- `position_size` (Decimal): Calculated position size
- `estimated_risk` (Decimal): Actual risk amount in dollars
- `risk_method_used` (RiskMethod): Which method was used for calculation
- `warning_message` (str, optional): Warning about position size, margin, etc.
- `error_message` (str, optional): Error description if calculation failed

## Controller Models

### MainController
**Purpose**: Coordinates the main application window and tab management
**Properties**:
- `selected_tab_index` (int): Currently active tab (0=Equities, 1=Options, 2=Futures)
- `equity_controller` (EquityController): Controller for equity tab
- `option_controller` (OptionController): Controller for option tab
- `future_controller` (FutureController): Controller for future tab

### EquityController : BaseController
**Purpose**: Manages equity trade input and calculation
**Properties**:
- `trade` (EquityTrade): Current equity trade data
- `validation_result` (ValidationResult): Current validation state
- `calculation_result` (CalculationResult): Current calculation result

**Methods**:
- `calculate_position()`: Triggers position size calculation
- `clear_inputs()`: Resets all input fields
- `validate_input(field_name, value)`: Real-time field validation
- `update_risk_method(method)`: Changes risk calculation method

### OptionController : BaseController
**Purpose**: Manages option trade input and calculation
**Properties**:
- `trade` (OptionTrade): Current option trade data
- `validation_result` (ValidationResult): Current validation state
- `calculation_result` (CalculationResult): Current calculation result

**Methods**:
- `calculate_position()`: Triggers position size calculation
- `clear_inputs()`: Resets all input fields
- `validate_input(field_name, value)`: Real-time field validation
- `update_risk_method(method)`: Changes risk calculation method (level-based disabled)

### FutureController : BaseController
**Purpose**: Manages futures trade input and calculation
**Properties**:
- `trade` (FutureTrade): Current futures trade data
- `validation_result` (ValidationResult): Current validation state
- `calculation_result` (CalculationResult): Current calculation result

**Methods**:
- `calculate_position()`: Triggers position size calculation
- `clear_inputs()`: Resets all input fields
- `validate_input(field_name, value)`: Real-time field validation
- `update_risk_method(method)`: Changes risk calculation method

### BaseController (Abstract)
**Purpose**: Common functionality for all controllers
**Properties**:
- `is_busy` (bool): Indicates if calculation is in progress
- `has_errors` (bool): Indicates if validation errors exist

## Data Flow

### Risk Method Selection Flow
1. User selects risk calculation method (radio buttons)
2. UI shows/hides relevant input fields
3. Validation rules updated based on selected method
4. Previous calculations cleared
5. Input focus moved to appropriate fields

### Input Validation Flow
1. User modifies input field
2. Real-time validation triggered
3. Field-specific errors displayed immediately
4. Calculate button enabled/disabled based on overall validation state
5. Method-specific validation rules applied

### Calculation Flow
1. User clicks Calculate button
2. Final validation check performed for selected method
3. Appropriate calculation service method called with method parameter
4. Results displayed with method indicator
5. Error handling for edge cases and method-specific issues

### Session Persistence
- Input values maintained during application session
- Risk method selection preserved per tab
- No permanent storage required
- Tab switching preserves individual tab states and method selections
- Application restart clears all data

## Error Handling

### Method-Specific Validation Errors
- **PERCENTAGE method**: Risk percentage outside 1-5% range
- **FIXED_AMOUNT method**: Amount outside $10-$500 range, amount > 5% of account
- **LEVEL_BASED method**: Support/resistance level same as entry price
- **All methods**: Empty required fields, invalid numeric ranges

### Calculation Errors
- Division by zero scenarios (zero risk distance)
- Negative result values
- Insufficient account capital warnings
- Method-specific edge cases (e.g., level too close to entry)

### User Experience
- Real-time validation feedback with method context
- Clear error messages with suggested corrections
- Method-specific warnings (e.g., "Level-based not available for options")
- Calculation results show which method was used
- Visual indicators for active risk method