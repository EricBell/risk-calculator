# Tasks: Fix Calculate Position Button Always Disabled

**Input**: Design documents from `/specs/002-the-calculate-position/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → ✅ Implementation plan loaded: Python/Tkinter desktop app bug fix
   → Extract: Tkinter, pytest, decimal validation, real-time UI updates
2. Load optional design documents:
   → ✅ data-model.md: ButtonValidationState, FieldValidationResult entities
   → ✅ contracts/: IButtonValidationService, field validation rules
   → ✅ research.md: Existing architecture analysis and root cause areas
3. Generate tasks by category:
   → Debugging: Investigate existing button logic
   → Tests: Contract tests for validation service, quickstart scenarios
   → Core: Fix button enablement logic, validation state management
   → Integration: Event binding, real-time validation
   → Polish: Performance verification, regression tests
4. Apply task rules:
   → Investigation tasks can run in parallel [P]
   → Implementation tasks are sequential (shared files)
   → Tests before fixes (TDD approach)
5. Number tasks sequentially (T001, T002...)
6. Focus: Bug fix, not new feature - minimal code changes
7. SUCCESS: 17 targeted debugging and fix tasks ready
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions
- Focus: Debug and fix existing logic, not build new features

## Phase 3.1: Investigation & Setup
- [ ] T001 [P] Investigate current button state logic in `risk_calculator/controllers/base_controller.py` lines 137-156
- [ ] T002 [P] Investigate field validation setup in `risk_calculator/services/realtime_validator.py`
- [ ] T003 [P] Investigate event binding patterns in all three controllers (`equity_controller.py`, `option_controller.py`, `future_controller.py`)
- [ ] T004 Create test environment for button validation debugging

## Phase 3.2: Contract Tests (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation fixes**
- [ ] T005 [P] Contract test for IButtonValidationService in `tests/contract/test_button_validation_service.py`
- [ ] T006 [P] Contract test for field validation rules in `tests/contract/test_field_validation_rules.py`
- [ ] T007 [P] Integration test for basic button enablement (Equity tab) in `tests/integration/test_button_enablement_equity.py`
- [ ] T008 [P] Integration test for real-time validation (Options tab) in `tests/integration/test_button_enablement_options.py`
- [ ] T009 [P] Integration test for method switching (Futures tab) in `tests/integration/test_button_enablement_futures.py`

## Phase 3.3: Debug & Fix Implementation (ONLY after tests are failing)
- [ ] T010 Debug and fix `_update_calculate_button_state()` method in `risk_calculator/controllers/base_controller.py`
- [ ] T011 Debug and fix `_are_required_fields_filled()` method in `risk_calculator/controllers/base_controller.py`
- [ ] T012 Debug and fix field change event handling in `_on_field_change()` method in `risk_calculator/controllers/base_controller.py`
- [ ] T013 Verify and fix StringVar trace binding setup in controller `_setup_view_bindings()` methods
- [ ] T014 Debug and fix validation error state management in `risk_calculator/controllers/base_controller.py`

## Phase 3.4: Integration & Event Binding
- [ ] T015 Verify real-time validation service integration in `risk_calculator/services/realtime_validator.py`
- [ ] T016 Test and fix method switching validation updates across all tabs
- [ ] T017 Verify button state persistence during tab switches

## Phase 3.5: Validation & Polish
- [ ] T018 [P] Run quickstart test scenarios from `specs/002-the-calculate-position/quickstart.md`
- [ ] T019 [P] Performance validation: verify <100ms validation response time
- [ ] T020 [P] Regression testing: ensure existing functionality still works
- [ ] T021 Update CLAUDE.md with fix details and resolution

## Dependencies
- Investigation (T001-T003) can run in parallel
- Contract tests (T005-T009) before implementation (T010-T017)
- T010 (button state) blocks T011 (required fields) blocks T012 (field changes)
- T013 (event binding) blocks T015 (validation service)
- All implementation before validation (T018-T021)

## Root Cause Focus Areas
Based on research.md analysis, prioritize these investigation areas:

1. **Button State Logic**: `_update_calculate_button_state()` may have logic bugs
2. **Field Detection**: `_are_required_fields_filled()` may not detect complete forms
3. **Event Binding**: StringVar trace callbacks may not be firing
4. **Error State**: `has_errors` flag may not be clearing properly
5. **Method Switching**: Required field updates during method changes

## Parallel Investigation Example
```
# Launch T001-T003 together for comprehensive analysis:
Task: "Investigate button state logic in base_controller.py lines 137-156"
Task: "Investigate field validation in realtime_validator.py" 
Task: "Investigate event binding in all three controller files"
```

## Contract Test Example
```
# Launch T005-T009 together for comprehensive test coverage:
Task: "Contract test IButtonValidationService interface compliance"
Task: "Contract test field validation rules for all tabs and methods"
Task: "Integration test basic button enablement flow on Equity tab"
Task: "Integration test real-time validation on Options tab"
Task: "Integration test method switching on Futures tab"
```

## Expected Outcomes
- Button enables correctly when all required fields are valid and filled
- Button disables immediately when required fields are cleared or become invalid
- Real-time validation response time <100ms
- All three tabs (Equity, Options, Futures) work correctly
- All three methods work correctly where supported
- No regression in existing functionality

## Debug Strategy
1. **Systematic Investigation**: Use T001-T003 to map current logic flow
2. **Test-Driven Fixes**: Write failing tests (T005-T009) that demonstrate expected behavior
3. **Minimal Code Changes**: Focus on fixing bugs, not rebuilding architecture
4. **Validation First**: Fix validation state before button logic
5. **Performance Verification**: Ensure fixes maintain <100ms response time

## Notes
- This is a bug fix, not a new feature - preserve existing architecture
- Focus on debugging existing logic rather than adding new code
- Test each fix thoroughly to prevent regression
- Maintain cross-platform compatibility (Windows/Linux)
- Follow existing code patterns and conventions

## Task Generation Rules Applied
1. **From Contracts**: Each contract interface → contract test task [P]
2. **From Research**: Each potential failure point → investigation task [P]  
3. **From Quickstart**: Each test scenario → integration test [P]
4. **Bug Fix Focus**: Debug tasks before fix tasks, minimal changes
5. **Ordering**: Investigation → Tests → Fixes → Validation → Polish

## Validation Checklist
- [x] All contract interfaces have corresponding tests
- [x] All quickstart scenarios have integration tests  
- [x] All investigation tasks come before implementation
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] Focus on debugging existing code, not new features