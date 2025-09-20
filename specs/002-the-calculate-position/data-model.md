# Data Model: Calculate Position Button Fix

**Date**: 2025-09-20  
**Purpose**: Define the data entities and validation rules for button enablement logic

## Core Entities

### 1. ButtonValidationState
**Purpose**: Tracks the overall enablement state of the Calculate Position button

**Attributes**:
- `has_errors: bool` - Whether any validation errors exist
- `required_fields_filled: bool` - Whether all required fields contain values  
- `is_enabled: bool` - Computed property: `not has_errors and required_fields_filled`
- `validation_errors: Dict[str, str]` - Field-specific error messages
- `last_updated: datetime` - When state was last computed

**State Transitions**:
- `DISABLED` → `ENABLED`: When `has_errors=False` AND `required_fields_filled=True`
- `ENABLED` → `DISABLED`: When `has_errors=True` OR `required_fields_filled=False`
- `BUSY` → `DISABLED`: During calculation, temporarily disabled regardless of validation

**Validation Rules**:
- Button must start in disabled state
- State updates must be triggered by field changes
- State must persist across method switches within same tab
- State must be independent between tabs

### 2. FieldValidationResult
**Purpose**: Represents the validation status of a single form field

**Attributes**:
- `field_name: str` - Identifier for the form field
- `value: str` - Current field value
- `is_valid: bool` - Whether field passes validation
- `error_message: Optional[str]` - Specific error if invalid
- `is_required: bool` - Whether field is required for current method
- `is_filled: bool` - Whether field contains non-empty value

**Validation Rules**:
- Empty values are valid during typing (not required to show errors)
- Required fields must have non-empty values for button enablement
- Invalid values must display specific error messages
- Validation must be consistent with existing service patterns

### 3. MethodFieldRequirements  
**Purpose**: Defines which fields are required for each risk calculation method

**Attributes**:
- `method: RiskMethod` - The risk calculation method (PERCENTAGE, FIXED_AMOUNT, LEVEL_BASED)
- `required_fields: List[str]` - Field names required for this method
- `tab_type: TabType` - Which tab this applies to (EQUITY, OPTIONS, FUTURES)
- `is_supported: bool` - Whether method is supported on this tab

**Relationships**:
- Each tab has different method support (Options excludes LEVEL_BASED)
- Each method has different field requirements
- Base fields + method-specific fields = total required fields

**Validation Rules**:
- Method must be supported on current tab
- Required fields list must be complete for calculation
- Field requirements must match existing controller logic

### 4. RealTimeValidationEvent
**Purpose**: Represents a field change event that triggers validation

**Attributes**:
- `field_name: str` - Which field changed
- `old_value: str` - Previous field value
- `new_value: str` - Current field value  
- `trigger_type: str` - How change was triggered (USER_INPUT, METHOD_SWITCH, CLEAR)
- `timestamp: datetime` - When event occurred

**State Transitions**:
- Field change → Validate single field → Update validation state → Update button state
- Method switch → Clear validation state → Validate all fields → Update button state
- Form clear → Reset validation state → Update button state

## Entity Relationships

```
ButtonValidationState
├── has_errors (computed from FieldValidationResult.is_valid)
├── required_fields_filled (computed from MethodFieldRequirements + FieldValidationResult.is_filled)
└── validation_errors (aggregated from FieldValidationResult.error_message)

MethodFieldRequirements
├── determines which FieldValidationResult entries are required
└── varies by current method selection

RealTimeValidationEvent
├── triggers FieldValidationResult updates
└── triggers ButtonValidationState recalculation
```

## Validation State Machine

```
[FORM LOAD] → ButtonValidationState(has_errors=False, required_fields_filled=False)
                                   ↓
[USER TYPES] → RealTimeValidationEvent → FieldValidationResult update
                                       ↓
[VALIDATION] → ButtonValidationState recalculation
                                   ↓
[BUTTON UPDATE] → UI reflects new enabled/disabled state
```

## Critical Validation Rules

### Field-Level Validation
- **Empty fields**: Valid during typing, invalid for required field completion
- **Numeric fields**: Must parse to valid Decimal, range checking per field type
- **Price relationships**: Stop loss must be directionally correct vs entry price
- **Method compatibility**: Level-based not allowed for options

### Button Enablement Logic
```python
def calculate_button_enabled() -> bool:
    return (
        not has_validation_errors() and 
        all_required_fields_filled() and
        current_method_supported()
    )
```

### Error State Persistence
- Field errors persist until field value becomes valid
- Method switch clears irrelevant field errors
- Global error state recomputed on every field change

## Integration with Existing Models

This data model extends the existing architecture:

- **TradeModel entities**: Provide data for validation (EquityTrade, OptionTrade, FutureTrade)
- **ValidationService**: Implements field validation rules
- **Controller state**: Manages ButtonValidationState and FieldValidationResult instances
- **View components**: Display validation errors and button state

## Performance Considerations

- **State computation**: O(n) where n = number of required fields
- **Error tracking**: O(1) field error updates  
- **Memory usage**: Minimal overhead for validation state objects
- **Real-time updates**: <100ms validation response maintained