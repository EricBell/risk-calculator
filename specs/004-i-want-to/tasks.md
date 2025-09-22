# Tasks: Qt Migration with Responsive Window Management

**Input**: Design documents from `/specs/004-i-want-to/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Overall Progress: 🎉 100% Complete (50/50 tasks) 🎉
- ✅ **Phase 3.1**: Environment Setup (3/3 tasks)
- ✅ **Phase 3.2**: Tests First (11/11 tasks)
- ✅ **Phase 3.3**: Core Models (3/3 tasks)
- ✅ **Phase 3.4**: Qt Services (4/4 tasks)
- ✅ **Phase 3.5**: Qt View Components (6/6 tasks)
- ✅ **Phase 3.6**: Controller Integration (5/5 tasks)
- ✅ **Phase 3.7**: Application Integration (5/5 tasks)
- ✅ **Phase 3.8**: Configuration & Persistence (4/4 tasks)
- ✅ **Phase 3.9**: Polish & Performance (9/9 tasks)

**🎉 MIGRATION STATUS: COMPLETE ✅**
*Production-ready Qt application with enhanced capabilities and comprehensive testing*

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
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, Qt views
   → Integration: window management, configuration
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
   → All Qt views implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `risk_calculator/`, `tests/` at repository root
- Existing MVC structure: `models/`, `views/`, `controllers/`, `services/`
- New Qt-specific components integrate with existing structure

## Phase 3.1: Environment Setup ✅ COMPLETED
- [x] T001 Install PySide6 dependency in requirements.txt and verify Qt installation
- [x] T002 Create Qt application bootstrap in risk_calculator/qt_main.py with high-DPI scaling
- [x] T003 [P] Configure linting rules for Qt-specific code patterns and imports

## Phase 3.2: Tests First (TDD) ✅ COMPLETED
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test WindowManagerInterface in tests/contract/test_window_manager_interface.py
- [x] T005 [P] Contract test ResponsiveLayoutInterface in tests/contract/test_responsive_layout_interface.py
- [x] T006 [P] Contract test DisplayProfileInterface in tests/contract/test_display_profile_interface.py
- [x] T007 [P] Contract test QtViewInterface in tests/contract/test_qt_view_interface.py
- [x] T008 [P] Contract test QtMainWindowInterface in tests/contract/test_qt_main_window_interface.py
- [x] T009 [P] Contract test QtTradingTabInterface in tests/contract/test_qt_trading_tab_interface.py
- [x] T010 [P] Integration test high-DPI display adaptation in tests/integration/test_high_dpi_display.py
- [x] T011 [P] Integration test window resize and persistence in tests/integration/test_window_persistence.py
- [x] T012 [P] Integration test risk calculation preservation in tests/integration/test_calculation_preservation.py
- [x] T013 [P] Integration test cross-platform configuration in tests/integration/test_cross_platform_config.py
- [x] T014 [P] Integration test edge case handling in tests/integration/test_edge_cases.py

## Phase 3.3: Core Models ✅ COMPLETED
- [x] T015 [P] Window Configuration model in risk_calculator/models/window_configuration.py
- [x] T016 [P] Display Profile model in risk_calculator/models/display_profile.py
- [x] T017 [P] UI Layout State model in risk_calculator/models/ui_layout_state.py

## Phase 3.4: Qt Services ✅ COMPLETED
- [x] T018 [P] Window Manager service in risk_calculator/services/qt_window_manager.py
- [x] T019 [P] Display Profile service in risk_calculator/services/qt_display_service.py
- [x] T020 [P] Responsive Layout service in risk_calculator/services/qt_layout_service.py
- [x] T021 Configuration persistence service using QSettings in risk_calculator/services/qt_config_service.py

## Phase 3.5: Qt View Components ✅ COMPLETED
- [x] T022 [P] Base Qt View component in risk_calculator/views/qt_base_view.py
- [x] T023 [P] Qt Main Window in risk_calculator/views/qt_main_window.py
- [x] T024 [P] Qt Equity Tab in risk_calculator/views/qt_equity_tab.py
- [x] T025 [P] Qt Options Tab in risk_calculator/views/qt_options_tab.py
- [x] T026 [P] Qt Futures Tab in risk_calculator/views/qt_futures_tab.py
- [x] T027 Error display components for Qt in risk_calculator/views/qt_error_display.py

## Phase 3.6: Controller Integration ✅ COMPLETED
- [x] T028 Qt-compatible base controller in risk_calculator/controllers/qt_base_controller.py
- [x] T029 Equity controller Qt adapter in risk_calculator/controllers/qt_equity_controller.py
- [x] T030 Options controller Qt adapter in risk_calculator/controllers/qt_options_controller.py
- [x] T031 Futures controller Qt adapter in risk_calculator/controllers/qt_futures_controller.py
- [x] T032 Main window controller integration in risk_calculator/controllers/qt_main_controller.py

## Phase 3.7: Application Integration ✅ COMPLETED
- [x] T033 Qt application entry point with window management in risk_calculator/qt_main.py
- [x] T034 Menu system migration from Tkinter to Qt in qt_main_window.py
- [x] T035 Tab widget setup and management integration
- [x] T036 Signal/slot connections for real-time validation
- [x] T037 High-DPI scaling and font management setup

## Phase 3.8: Configuration & Persistence ✅ COMPLETED
- [x] T038 QSettings integration for cross-platform storage
- [x] T039 Window state save/restore functionality
- [x] T040 Configuration validation and fallback mechanisms
- [x] T041 Multi-monitor support and bounds checking

## Phase 3.9: Polish & Performance ✅ COMPLETED
- [x] T042 [P] Unit tests for Window Configuration model in tests/unit/test_window_configuration.py
- [x] T043 [P] Unit tests for Display Profile detection in tests/unit/test_display_profile.py
- [x] T044 [P] Unit tests for responsive scaling in tests/unit/test_responsive_scaling.py
- [x] T045 Performance tests for startup time (<3 seconds) in tests/performance/test_startup.py
- [x] T046 Performance tests for UI responsiveness (<100ms) in tests/performance/test_ui_response.py
- [x] T047 Memory usage validation (<100MB) in tests/performance/test_memory.py
- [x] T048 [P] Update existing documentation for Qt migration
- [x] T049 Cross-platform validation on Windows and Linux
- [x] T050 Remove Tkinter dependencies and cleanup legacy code

## Dependencies
- Environment setup (T001-T003) before all other tasks
- Tests (T004-T014) before implementation (T015-T041)
- Models (T015-T017) before services (T018-T021)
- Services before views (T022-T027)
- Views before controllers (T028-T032)
- Controllers before application integration (T033-T037)
- Core functionality before configuration (T038-T041)
- Implementation before polish (T042-T050)

## Parallel Example
```
# Launch contract tests together (T004-T009):
Task: "Contract test WindowManagerInterface in tests/contract/test_window_manager_interface.py"
Task: "Contract test ResponsiveLayoutInterface in tests/contract/test_responsive_layout_interface.py"
Task: "Contract test DisplayProfileInterface in tests/contract/test_display_profile_interface.py"
Task: "Contract test QtViewInterface in tests/contract/test_qt_view_interface.py"

# Launch model creation together (T015-T017):
Task: "Window Configuration model in risk_calculator/models/window_configuration.py"
Task: "Display Profile model in risk_calculator/models/display_profile.py"
Task: "UI Layout State model in risk_calculator/models/ui_layout_state.py"

# Launch Qt view components together (T022-T026):
Task: "Base Qt View component in risk_calculator/views/qt_base_view.py"
Task: "Qt Equity Tab in risk_calculator/views/qt_equity_tab.py"
Task: "Qt Options Tab in risk_calculator/views/qt_options_tab.py"
Task: "Qt Futures Tab in risk_calculator/views/qt_futures_tab.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify contract tests fail before implementing interfaces
- Preserve existing business logic during Qt migration
- Test on both Windows and Linux throughout development
- Maintain existing calculation accuracy exactly
- Commit after each task completion

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - window_management_interface.py → T004-T006 (WindowManager, ResponsiveLayout, DisplayProfile)
   - qt_view_interface.py → T007-T009 (QtView, QtMainWindow, QtTradingTab)

2. **From Data Model**:
   - Window Configuration → T015 (model creation)
   - Display Profile → T016 (model creation)
   - UI Layout State → T017 (model creation)

3. **From Quickstart Scenarios**:
   - Scenario 1 → T010 (high-DPI integration test)
   - Scenario 2 → T011 (window persistence integration test)
   - Scenario 3 → T012 (calculation preservation integration test)
   - Scenario 4 → T013 (cross-platform integration test)
   - Scenario 5 → T014 (edge cases integration test)

4. **Ordering**:
   - Setup → Tests → Models → Services → Views → Controllers → Integration → Polish
   - Qt-specific dependencies: QSettings before persistence, models before services

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004-T009)
- [x] All entities have model tasks (T015-T017)
- [x] All tests come before implementation (T004-T014 before T015+)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Qt-specific requirements addressed (high-DPI, persistence, responsive)
- [x] Existing functionality preservation validated (calculation accuracy)
- [x] Cross-platform compatibility ensured (Windows + Linux)

## Migration Strategy Notes
- **Incremental approach**: Keep existing Tkinter code functional during development
- **Adapter pattern**: Create Qt adapters for existing controllers to minimize business logic changes
- **Testing strategy**: Ensure Qt calculations produce identical results to Tkinter version
- **Rollback plan**: Maintain ability to revert to Tkinter if critical issues arise