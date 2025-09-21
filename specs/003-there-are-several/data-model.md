# Data Model: UI Bug Fixes and Window Responsiveness

**Feature**: UI Bug Fixes and Window Responsiveness
**Branch**: `003-there-are-several`
**Date**: 2025-09-20

## Entity Overview

This feature introduces new data models to support window configuration persistence and enhanced validation state management.

## Core Entities

### 1. WindowConfiguration
**Purpose**: Manages window size, position, and display state persistence

**Attributes**:
- `width: int` - Window width in pixels (minimum: 800)
- `height: int` - Window height in pixels (minimum: 600)
- `x: int` - Window x-position on screen
- `y: int` - Window y-position on screen
- `maximized: bool` - Whether window is maximized
- `last_updated: datetime` - Timestamp of last configuration change

**Validation Rules**:
- Width must be >= 800 pixels (minimum usability constraint)
- Height must be >= 600 pixels (minimum usability constraint)
- X/Y coordinates must be within available screen bounds
- If coordinates exceed screen bounds, auto-adjust to 80% of screen size, centered

**State Transitions**:
- Created → Set default values (1024x768, centered)
- Modified → Update timestamp and persist to file
- Invalid → Reset to defaults and regenerate config file

### 2. FieldValidationState
**Purpose**: Tracks validation status for individual form fields

**Attributes**:
- `field_name: str` - Unique identifier for form field
- `value: str` - Current field value
- `is_valid: bool` - Whether field passes validation
- `error_message: str` - Human-readable error description (empty if valid)
- `is_required: bool` - Whether field is required for form completion

**Validation Rules**:
- field_name must be non-empty and unique within form
- is_valid derived from field-specific validation rules
- error_message required when is_valid is False
- Required fields with empty values are automatically invalid

**State Transitions**:
- Created → Set initial validation state based on field type
- Value Changed → Re-validate and update error message
- Form Submitted → Final validation check before enabling action

### 3. FormValidationState
**Purpose**: Aggregates validation state across all form fields

**Attributes**:
- `form_id: str` - Unique identifier for form (e.g., 'equity_tab', 'options_tab')
- `field_states: Dict[str, FieldValidationState]` - Map of field validation states
- `has_errors: bool` - Whether any field has validation errors
- `all_required_filled: bool` - Whether all required fields have values
- `is_submittable: bool` - Whether form can be submitted (no errors + all required filled)

**Validation Rules**:
- has_errors is True if any field_state.is_valid is False
- all_required_filled is True if all required fields have non-empty values
- is_submittable is True only when has_errors is False AND all_required_filled is True

**State Transitions**:
- Field Added → Update field_states map
- Field Changed → Re-evaluate aggregated validation state
- Method Changed → Re-validate all fields for new requirements

## Entity Relationships

### WindowConfiguration ↔ ConfigurationService
- WindowConfiguration is persisted and loaded by ConfigurationService
- One-to-one relationship (single window configuration per application instance)

### FieldValidationState ↔ FormValidationState
- FormValidationState contains multiple FieldValidationState instances
- One-to-many relationship (form has multiple fields)

### FormValidationState ↔ BaseController
- BaseController manages FormValidationState for its view
- One-to-one relationship (controller manages one form)

## Data Persistence

### WindowConfiguration Storage
**Location**: `~/.risk_calculator/window_config.json`
**Format**: JSON with the following structure:
```json
{
  "window": {
    "width": 1024,
    "height": 768,
    "x": 100,
    "y": 100,
    "maximized": false,
    "last_updated": "2025-09-20T10:30:00Z"
  }
}
```

**Backup Strategy**:
- Create `.bak` file before writing new configuration
- If write fails, restore from backup
- If both files corrupted, regenerate with defaults

### FieldValidationState Storage
**Location**: In-memory only (no persistence required)
**Rationale**: Validation state is ephemeral and recalculated on each form interaction

## Integration with Existing Models

### Enhancement to Existing Entities
- **No breaking changes** to existing trade models (EquityTrade, OptionTrade, FutureTrade)
- **No modifications** to existing calculation services
- **Additive only** - new models supplement existing architecture

### Service Layer Integration
- **ConfigurationService** (new) - manages WindowConfiguration persistence
- **ValidationService** (enhanced) - extended to support FieldValidationState
- **Existing services** - no changes required

### Controller Layer Integration
- **BaseController** (enhanced) - manages FormValidationState
- **MainController** (enhanced) - manages WindowConfiguration
- **Tab controllers** - inherit enhanced validation from BaseController

## Migration Strategy

### New Installation
- WindowConfiguration created with default values on first startup
- FormValidationState initialized for each tab controller
- No migration required

### Existing Installation
- Detect missing window_config.json and create with defaults
- Existing form functionality continues unchanged
- Enhanced validation gradually replaces basic validation

## Performance Considerations

### Memory Usage
- WindowConfiguration: ~200 bytes per instance
- FieldValidationState: ~100 bytes per field (estimated 15 fields total = 1.5KB)
- FormValidationState: ~500 bytes per form (3 forms = 1.5KB)
- **Total additional memory**: <5KB (negligible impact)

### I/O Performance
- WindowConfiguration persistence: <10ms for JSON read/write
- Validation state updates: In-memory only, <1ms per field
- Configuration loading: Once on startup, minimal impact

### Validation Performance
- Field validation: <5ms per field (real-time acceptable)
- Form validation: <10ms for all fields (button state update)
- Overall impact: <100ms for complete form re-validation

## Testing Requirements

### Unit Tests Required
- WindowConfiguration validation and serialization
- FieldValidationState state transitions
- FormValidationState aggregation logic
- Configuration file I/O with error handling

### Integration Tests Required
- Window configuration persistence across app restarts
- Form validation state integration with UI updates
- Button enablement based on validation state changes
- Error message display coordination with validation state

### Edge Case Testing
- Corrupted configuration file recovery
- Invalid window dimensions handling
- Screen resolution change scenarios
- Rapid field value changes (stress testing)

## Success Criteria

### Functional Criteria
- WindowConfiguration correctly persists and restores window state
- FieldValidationState accurately tracks field validation status
- FormValidationState correctly determines form submission eligibility
- Integration maintains existing functionality while adding new capabilities

### Performance Criteria
- Configuration load/save operations complete within 10ms
- Validation state updates maintain UI responsiveness (<100ms)
- Memory usage increase remains under 5MB
- No impact on application startup time

### Quality Criteria
- All new entities have comprehensive unit test coverage
- Integration tests verify end-to-end functionality
- No regression in existing model behavior
- Cross-platform compatibility maintained