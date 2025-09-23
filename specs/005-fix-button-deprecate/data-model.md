# Data Model: Qt Application Refinement and Tkinter Deprecation

## Core Entities

### Form Validation State
**Purpose**: Tracks the current validation status of all input fields for real-time button enablement
**Fields**:
- `field_states: Dict[str, FieldValidationState]` - Individual field validation results
- `overall_valid: bool` - Whether all required fields pass validation
- `error_messages: Dict[str, str]` - Field-specific error messages for display
- `required_fields: List[str]` - Fields required for current risk method
- `risk_method: str` - Currently selected risk calculation method
- `last_updated: datetime` - Timestamp of last validation update

**Validation Rules**:
- All required fields must be present and valid
- Error messages must be non-empty strings when validation fails
- Risk method must be one of: percentage, fixed_amount, level_based
- Field states must exist for all form fields

**State Transitions**:
- Invalid → Valid (when field passes validation)
- Valid → Invalid (when field fails validation)
- Partial → Complete (when all required fields filled)
- Complete → Partial (when required field cleared)

### Button State
**Purpose**: Represents the enabled/disabled status of the Calculate Position button and associated messaging
**Fields**:
- `enabled: bool` - Whether the Calculate Position button is enabled
- `tooltip_message: str` - Explanatory message for disabled state
- `error_count: int` - Number of validation errors preventing enablement
- `missing_fields: List[str]` - Specific fields that need completion
- `invalid_fields: List[str]` - Specific fields that have validation errors

**Validation Rules**:
- Button enabled only when error_count is zero
- Tooltip message must explain why button is disabled
- Missing and invalid field lists must be mutually exclusive
- All field references must correspond to actual form fields

**State Transitions**:
- Disabled → Enabled (when all validation passes)
- Enabled → Disabled (when validation fails)
- Error → Warning (when partial validation passes)

### Field Validation State
**Purpose**: Detailed validation information for individual form fields
**Fields**:
- `field_name: str` - Unique identifier for the form field
- `value: str` - Current field value
- `is_valid: bool` - Whether field passes validation
- `is_required: bool` - Whether field is required for current risk method
- `error_message: str` - Specific validation error message
- `validation_type: str` - Type of validation applied (numeric, required, range)

**Validation Rules**:
- Field name must be unique within form
- Required fields cannot be empty
- Numeric fields must contain valid numbers
- Error message must be empty when is_valid is True

**Relationships**:
- Many-to-one with Form Validation State
- One-to-one with Button State contributions

### Application Process State
**Purpose**: Tracks application lifecycle and process management for proper cleanup
**Fields**:
- `process_id: int` - System process identifier
- `qt_application: QApplication` - Qt application instance reference
- `main_window: QMainWindow` - Main window instance reference
- `cleanup_handlers: List[Callable]` - Registered cleanup functions
- `exit_requested: bool` - Whether application exit has been requested

**Validation Rules**:
- Process ID must be valid system process
- Qt application instance must be properly initialized
- Cleanup handlers must be callable functions
- Exit sequence must complete all cleanup tasks

**State Transitions**:
- Starting → Running (when application fully initialized)
- Running → Exiting (when user requests exit)
- Exiting → Terminated (when all cleanup complete)

## Data Flow

### Real-time Validation Flow
```
Field Change → Field Validation → Form Validation State Update → Button State Update → UI Refresh
```

### Button Enablement Flow
```
Form Validation State → Required Fields Check → Error Count Calculation → Button Enable/Disable → Tooltip Update
```

### Application Exit Flow
```
Exit Request → Cleanup Handler Execution → Qt Application Shutdown → Process Termination
```

## Storage Schema

### In-Memory State Management
```
form_validation_cache: FormValidationState
button_state_cache: ButtonState
field_states_cache: Dict[str, FieldValidationState]
```

### No Persistent Storage Required
- All validation state is ephemeral and recalculated on application start
- Form data is not persisted between sessions
- Process state is managed by operating system

## Migration Considerations

### Existing Data Preservation
- All existing trading calculation models remain unchanged
- Risk calculation services maintain current interfaces
- Window configuration persistence continues through existing QSettings

### New Validation-Specific Models
- Form validation state models are new additions for button enablement
- Button state tracking enhances user experience
- Application process management ensures proper cleanup
- Field validation state provides granular error reporting

## Integration Points

### With Existing Services
- Form Validation State integrates with existing ValidationService
- Button State coordinates with existing controllers
- Application Process State leverages existing Qt window management

### With Qt Framework
- Field Validation State connects to Qt signal/slot system
- Button State updates Qt widget enabled property
- Application Process State uses QApplication lifecycle methods