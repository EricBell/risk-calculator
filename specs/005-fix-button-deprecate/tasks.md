# Tasks: Qt Application Refinement and Tkinter Deprecation

**Input**: Design documents from `/specs/005-fix-button-deprecate/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: Tkinter deprecation, dependency verification
   → Tests: contract tests, integration tests
   → Core: validation models, button state management
   → Integration: Qt signal/slot connections, process lifecycle
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All quickstart scenarios implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `risk_calculator/`, `tests/` at repository root
- Existing MVC structure: `models/`, `views/`, `controllers/`, `services/`
- New validation-specific components integrate with existing structure

## Phase 3.1: Tkinter Deprecation Setup
- [ ] T001 Rename risk_calculator/main.py to risk_calculator/main_tkinter_deprecated.py
- [ ] T002 Create deprecation warning in risk_calculator/main_tkinter_deprecated.py with clear Qt redirection message
- [ ] T003 [P] Update setup.py entry points to use qt_main.py as default application launcher
- [ ] T004 [P] Create clear Qt installation and usage instructions in README.md

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T005 [P] Contract test FormValidationInterface in tests/contract/test_form_validation_interface.py
- [ ] T006 [P] Contract test ButtonStateInterface in tests/contract/test_button_state_interface.py
- [ ] T007 [P] Contract test ApplicationLifecycleInterface in tests/contract/test_application_lifecycle_interface.py
- [ ] T008 [P] Contract test TkinterDeprecationInterface in tests/contract/test_tkinter_deprecation_interface.py
- [ ] T009 [P] Integration test Tkinter deprecation verification in tests/integration/test_tkinter_deprecation.py
- [ ] T010 [P] Integration test calculate button enablement complete form in tests/integration/test_button_enablement_complete.py
- [ ] T011 [P] Integration test calculate button disabled with clear errors in tests/integration/test_button_disabled_errors.py
- [ ] T012 [P] Integration test risk method switching validation in tests/integration/test_risk_method_switching.py
- [ ] T013 [P] Integration test cross-tab validation consistency in tests/integration/test_cross_tab_validation.py
- [ ] T014 [P] Integration test application exit process cleanup in tests/integration/test_application_exit_cleanup.py
- [ ] T015 [P] Integration test rapid field changes performance in tests/integration/test_rapid_field_changes.py

## Phase 3.3: Core Models (ONLY after tests are failing)
- [ ] T016 [P] FormValidationState model in risk_calculator/models/form_validation_state.py
- [ ] T017 [P] ButtonState model in risk_calculator/models/button_state.py
- [ ] T018 [P] FieldValidationState model in risk_calculator/models/field_validation_state.py
- [ ] T019 [P] ApplicationProcessState model in risk_calculator/models/application_process_state.py

## Phase 3.4: Validation Services
- [ ] T020 [P] Enhanced form validation service in risk_calculator/services/enhanced_form_validation_service.py
- [ ] T021 [P] Button state management service in risk_calculator/services/button_state_service.py
- [ ] T022 [P] Application lifecycle management service in risk_calculator/services/application_lifecycle_service.py
- [ ] T023 Tkinter deprecation service in risk_calculator/services/tkinter_deprecation_service.py

## Phase 3.5: Qt UI Integration
- [ ] T024 Implement real-time validation in risk_calculator/views/qt_equity_tab.py with Qt signals
- [ ] T025 Implement real-time validation in risk_calculator/views/qt_options_tab.py with Qt signals
- [ ] T026 Implement real-time validation in risk_calculator/views/qt_futures_tab.py with Qt signals
- [ ] T027 Add button state management to risk_calculator/controllers/qt_equity_controller.py
- [ ] T028 Add button state management to risk_calculator/controllers/qt_options_controller.py
- [ ] T029 Add button state management to risk_calculator/controllers/qt_futures_controller.py

## Phase 3.6: Signal/Slot Connections
- [ ] T030 Connect field change signals to validation in risk_calculator/views/qt_equity_tab.py
- [ ] T031 Connect field change signals to validation in risk_calculator/views/qt_options_tab.py
- [ ] T032 Connect field change signals to validation in risk_calculator/views/qt_futures_tab.py
- [ ] T033 Implement risk method change signal handling across all Qt trading tabs

## Phase 3.7: Application Lifecycle Integration
- [ ] T034 Integrate application lifecycle management in risk_calculator/qt_main.py
- [ ] T035 Add cleanup handlers registration in risk_calculator/views/qt_main_window.py
- [ ] T036 Implement graceful exit with process cleanup in risk_calculator/qt_main.py

## Phase 3.8: Error Display Enhancement
- [ ] T037 [P] Implement field-specific error tooltips in risk_calculator/views/qt_equity_tab.py
- [ ] T038 [P] Implement field-specific error tooltips in risk_calculator/views/qt_options_tab.py
- [ ] T039 [P] Implement field-specific error tooltips in risk_calculator/views/qt_futures_tab.py
- [ ] T040 Add button tooltip error messaging across all Qt trading tabs

## Phase 3.9: Performance Optimization
- [ ] T041 [P] Add validation debouncing to prevent excessive validation calls
- [ ] T042 [P] Optimize signal/slot connections for responsive UI updates
- [ ] T043 [P] Implement efficient button state caching mechanism

## Phase 3.10: Polish and Validation
- [ ] T044 [P] Unit tests for FormValidationState in tests/unit/test_form_validation_state.py
- [ ] T045 [P] Unit tests for ButtonState in tests/unit/test_button_state.py
- [ ] T046 [P] Unit tests for FieldValidationState in tests/unit/test_field_validation_state.py
- [ ] T047 [P] Unit tests for ApplicationProcessState in tests/unit/test_application_process_state.py
- [ ] T048 Performance tests for validation response time (<50ms) in tests/performance/test_validation_performance.py
- [ ] T049 Performance tests for application exit time (<2s) in tests/performance/test_exit_performance.py
- [ ] T050 Cross-platform validation on Windows and Linux following quickstart.md scenarios

## Dependencies
- Tkinter deprecation (T001-T004) can run independently
- Tests (T005-T015) before implementation (T016-T043)
- Models (T016-T019) before services (T020-T023)
- Services before UI integration (T024-T029)
- UI integration before signal/slot connections (T030-T033)
- Signal connections before lifecycle integration (T034-T036)
- Core functionality before error display (T037-T040)
- Implementation before performance optimization (T041-T043)
- Everything before polish (T044-T050)

## Parallel Example for Phase 3.2 (TDD Tests)
```bash
# Launch T005-T008 together (Contract tests):
Task: "Contract test FormValidationInterface in tests/contract/test_form_validation_interface.py"
Task: "Contract test ButtonStateInterface in tests/contract/test_button_state_interface.py"
Task: "Contract test ApplicationLifecycleInterface in tests/contract/test_application_lifecycle_interface.py"
Task: "Contract test TkinterDeprecationInterface in tests/contract/test_tkinter_deprecation_interface.py"

# Launch T009-T015 together (Integration tests):
Task: "Integration test Tkinter deprecation verification in tests/integration/test_tkinter_deprecation.py"
Task: "Integration test calculate button enablement complete form in tests/integration/test_button_enablement_complete.py"
Task: "Integration test calculate button disabled with clear errors in tests/integration/test_button_disabled_errors.py"
Task: "Integration test risk method switching validation in tests/integration/test_risk_method_switching.py"
```

## Parallel Example for Phase 3.3 (Model Creation)
```bash
# Launch T016-T019 together (Models):
Task: "FormValidationState model in risk_calculator/models/form_validation_state.py"
Task: "ButtonState model in risk_calculator/models/button_state.py"
Task: "FieldValidationState model in risk_calculator/models/field_validation_state.py"
Task: "ApplicationProcessState model in risk_calculator/models/application_process_state.py"
```

## Parallel Example for Phase 3.4 (Services)
```bash
# Launch T020-T022 together (Services):
Task: "Enhanced form validation service in risk_calculator/services/enhanced_form_validation_service.py"
Task: "Button state management service in risk_calculator/services/button_state_service.py"
Task: "Application lifecycle management service in risk_calculator/services/application_lifecycle_service.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify contract tests fail before implementing interfaces
- Preserve existing business logic during Qt enhancement
- Test on both Windows and Linux throughout development
- Maintain existing calculation accuracy exactly
- Commit after each task completion

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - button_validation_interface.py → T005-T008 (FormValidation, ButtonState, ApplicationLifecycle, TkinterDeprecation)

2. **From Data Model**:
   - Form Validation State → T016 (model creation)
   - Button State → T017 (model creation)
   - Field Validation State → T018 (model creation)
   - Application Process State → T019 (model creation)

3. **From Quickstart Scenarios**:
   - Scenario 1 → T009 (Tkinter deprecation verification)
   - Scenario 2 → T010 (button enablement complete form)
   - Scenario 3 → T011 (button disabled with errors)
   - Scenario 4 → T012 (risk method switching)
   - Scenario 5 → T013 (cross-tab consistency)
   - Scenario 6 → T014 (application exit cleanup)
   - Scenario 7 → T015 (rapid field changes performance)

4. **Ordering**:
   - Setup → Tests → Models → Services → UI Integration → Signal/Slot → Lifecycle → Polish
   - Qt-specific dependencies: Models before services, services before UI, UI before signals

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T005-T008)
- [x] All entities have model tasks (T016-T019)
- [x] All tests come before implementation (T005-T015 before T016+)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Qt-specific requirements addressed (signals, validation, lifecycle)
- [x] Existing functionality preservation validated (business logic unchanged)
- [x] Cross-platform compatibility ensured (Windows + Linux)

## Critical Success Criteria
- **Tkinter Completely Deprecated**: No user can access Tkinter version (T001-T004, T009)
- **Real-time Button Validation**: Button enables immediately when form complete (T010, T024-T029)
- **Clear Error Messages**: User knows exactly why button disabled (T011, T037-T040)
- **Process Cleanup**: Complete termination on exit (T014, T034-T036)
- **Cross-Platform Consistency**: Identical behavior on Windows and Linux (T050)
- **Performance Standards**: <50ms validation, <2s exit time (T048-T049)

## File Impact Summary
**Modified Files**: 12+ Qt view and controller files
**New Files**: 19+ model, service, and test files
**Deprecated Files**: 1 main Tkinter entry point
**Risk Level**: Medium (button enablement logic is critical UX)
**Test Coverage**: 100% of button enablement and deprecation scenarios