# Tasks: Cross-Platform Desktop Risk Calculator for Daytrading

**Input**: Design documents from `/specs/001-create-a-windows/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.12+, Tkinter, decimal, dataclasses, pytest
   → Structure: Single project with MVC pattern
   → Target: Cross-platform desktop (Windows/Linux)
2. Load design documents: ✓
   → data-model.md: 7 entities (RiskMethod, Trade, EquityTrade, OptionTrade, FutureTrade, ValidationResult, CalculationResult)
   → contracts/: 4 contract files (risk-calculation-service, controller-contracts, tkinter-view-contracts, validation-service-contracts)
   → quickstart.md: 5 acceptance test scenarios
3. Generate tasks by category: ✓
   → Setup: project init, dependencies, linting
   → Tests: 4 contract tests, 5 integration tests
   → Core: 7 models, 4 services, 4 controllers, 4 views
   → Integration: Tkinter binding, cross-platform testing
   → Polish: unit tests, performance, documentation
4. Apply task rules: ✓
   → Different files = mark [P] for parallel
   → Tests before implementation (TDD)
   → Models before services before controllers
5. Number tasks sequentially (T001-T040)
6. Generate dependency graph and parallel execution examples
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths relative to repository root

## Path Conventions
Single project structure per plan.md:
```
risk_calculator/
├── models/          # Trade data models and business logic
├── views/           # Tkinter UI components and windows
├── controllers/     # Application controllers and event handling
├── services/        # Risk calculation and validation services
└── main.py          # Application entry point

tests/
├── contract/        # Contract tests for services
├── integration/     # End-to-end acceptance tests
└── unit/           # Unit tests for individual components
```

## Phase 3.1: Setup
- [ ] T001 Create Python project structure in risk_calculator/ with models/, views/, controllers/, services/ directories
- [ ] T002 Create Python virtual environment (python -m venv .venv) and initialize requirements.txt (pytest>=7.0.0, pytest-mock>=3.10.0)
- [ ] T003 [P] Configure pytest.ini and setup.py for cross-platform testing

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests [P] - Different service contracts
- [ ] T004 [P] Contract test RiskCalculationService.calculate_equity_position() in tests/contract/test_risk_calculation_service.py
- [ ] T005 [P] Contract test TradeValidationService.validate_equity_trade() in tests/contract/test_validation_service.py
- [ ] T006 [P] Contract test EquityController.calculate_position() in tests/contract/test_equity_controller.py
- [ ] T007 [P] Contract test EquityTab Tkinter view bindings in tests/contract/test_equity_view.py

### Integration Tests [P] - Different acceptance scenarios
- [ ] T008 [P] Integration test percentage-based equity calculation in tests/integration/test_percentage_method.py
- [ ] T009 [P] Integration test fixed amount risk calculation in tests/integration/test_fixed_amount_method.py
- [ ] T010 [P] Integration test level-based risk calculation in tests/integration/test_level_based_method.py
- [ ] T011 [P] Integration test risk method switching UI in tests/integration/test_method_switching.py
- [ ] T012 [P] Integration test clear functionality in tests/integration/test_clear_functionality.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models [P] - Different model files
- [ ] T013 [P] RiskMethod enum in risk_calculator/models/risk_method.py
- [ ] T014 [P] Base Trade abstract class in risk_calculator/models/trade.py
- [ ] T015 [P] EquityTrade model with calculation logic in risk_calculator/models/equity_trade.py
- [ ] T016 [P] OptionTrade model with contract multiplier in risk_calculator/models/option_trade.py
- [ ] T017 [P] FutureTrade model with tick calculations in risk_calculator/models/future_trade.py
- [ ] T018 [P] ValidationResult dataclass in risk_calculator/models/validation_result.py
- [ ] T019 [P] CalculationResult dataclass in risk_calculator/models/calculation_result.py

### Service Layer [P] - Different service files
- [ ] T020 [P] RiskCalculationService with all three calculation methods in risk_calculator/services/risk_calculator.py
- [ ] T021 [P] TradeValidationService with method-specific validation in risk_calculator/services/validators.py
- [ ] T022 [P] RealTimeValidationService for Tkinter field validation in risk_calculator/services/realtime_validator.py

### Controller Layer - Sequential (shared dependencies)
- [ ] T023 BaseController abstract class with Tkinter variable management in risk_calculator/controllers/base_controller.py
- [ ] T024 EquityController with risk method switching logic in risk_calculator/controllers/equity_controller.py
- [ ] T025 OptionController with level-based method disabled in risk_calculator/controllers/option_controller.py
- [ ] T026 FutureController with margin requirement validation in risk_calculator/controllers/future_controller.py
- [ ] T027 MainController for tab management and coordination in risk_calculator/controllers/main_controller.py

### View Layer [P] - Different view files
- [ ] T028 [P] BaseTradingTab abstract Tkinter frame in risk_calculator/views/base_tab.py
- [ ] T029 [P] EquityTab with all three risk method fields in risk_calculator/views/equity_tab.py
- [ ] T030 [P] OptionsTab with level-based method disabled in risk_calculator/views/option_tab.py
- [ ] T031 [P] FuturesTab with tick value inputs in risk_calculator/views/future_tab.py
- [ ] T032 [P] MainWindow with ttk.Notebook tab container in risk_calculator/views/main_window.py

### Application Entry Point
- [ ] T033 Main application launcher with cross-platform Tkinter setup in risk_calculator/main.py

## Phase 3.4: Integration
- [ ] T034 Connect controllers to services with dependency injection in risk_calculator/controllers/
- [ ] T035 Wire Tkinter variable trace callbacks for real-time validation
- [ ] T036 Implement cross-platform widget styling and layout
- [ ] T037 Add keyboard navigation and accessibility features

## Phase 3.5: Polish
- [ ] T038 [P] Unit tests for calculation edge cases in tests/unit/test_calculations.py
- [ ] T039 [P] Performance tests (<100ms response time) in tests/unit/test_performance.py
- [ ] T040 [P] Cross-platform compatibility tests (Windows/Linux) in tests/unit/test_cross_platform.py

## Dependencies
**Critical Path**:
- Setup (T001-T003) before everything
- Contract tests (T004-T007) before models (T013-T019)
- Integration tests (T008-T012) before controllers (T023-T027)
- Models (T013-T019) before services (T020-T022)
- Services (T020-T022) before controllers (T023-T027)
- Controllers (T023-T027) before views (T028-T032)
- Views (T028-T032) before main app (T033)
- Implementation (T013-T033) before integration (T034-T037)
- Integration (T034-T037) before polish (T038-T040)

**Blocking Dependencies**:
- T014 (Trade base) blocks T015, T016, T017
- T023 (BaseController) blocks T024, T025, T026, T027
- T028 (BaseTradingTab) blocks T029, T030, T031
- T020, T021 (Services) block T024, T025, T026 (Controllers)

## Parallel Example
```bash
# Phase 3.2: Launch contract tests together (T004-T007):
Task: "Contract test RiskCalculationService.calculate_equity_position() in tests/contract/test_risk_calculation_service.py"
Task: "Contract test TradeValidationService.validate_equity_trade() in tests/contract/test_validation_service.py"
Task: "Contract test EquityController.calculate_position() in tests/contract/test_equity_controller.py"
Task: "Contract test EquityTab Tkinter view bindings in tests/contract/test_equity_view.py"

# Phase 3.2: Launch integration tests together (T008-T012):
Task: "Integration test percentage-based equity calculation in tests/integration/test_percentage_method.py"
Task: "Integration test fixed amount risk calculation in tests/integration/test_fixed_amount_method.py"
Task: "Integration test level-based risk calculation in tests/integration/test_level_based_method.py"
Task: "Integration test risk method switching UI in tests/integration/test_method_switching.py"
Task: "Integration test clear functionality in tests/integration/test_clear_functionality.py"

# Phase 3.3: Launch model creation together (T013-T019):
Task: "RiskMethod enum in risk_calculator/models/risk_method.py"
Task: "ValidationResult dataclass in risk_calculator/models/validation_result.py"
Task: "CalculationResult dataclass in risk_calculator/models/calculation_result.py"
# Note: T015-T017 must wait for T014 (Trade base class)

# Phase 3.3: Launch service creation together (T020-T022):
Task: "RiskCalculationService with all three calculation methods in risk_calculator/services/risk_calculator.py"
Task: "TradeValidationService with method-specific validation in risk_calculator/services/validators.py"
Task: "RealTimeValidationService for Tkinter field validation in risk_calculator/services/realtime_validator.py"

# Phase 3.3: Launch view creation together (T029-T032):
Task: "EquityTab with all three risk method fields in risk_calculator/views/equity_tab.py"
Task: "OptionsTab with level-based method disabled in risk_calculator/views/option_tab.py"
Task: "FuturesTab with tick value inputs in risk_calculator/views/future_tab.py"
Task: "MainWindow with ttk.Notebook tab container in risk_calculator/views/main_window.py"
# Note: Must wait for T028 (BaseTradingTab)
```

## Notes
- [P] tasks = different files, no dependencies between them
- All tests must fail before implementing corresponding functionality
- Commit after each task completion
- Cross-platform testing required on both Windows and Linux
- Use decimal.Decimal for all financial calculations
- Tkinter variable traces for real-time validation

## Task Generation Rules Applied
✓ **From Contracts**: 4 contract files → 4 contract test tasks [P]
✓ **From Data Model**: 7 entities → 7 model creation tasks [P] (except inheritance dependencies)
✓ **From User Stories**: 5 quickstart scenarios → 5 integration test tasks [P]
✓ **From Architecture**: MVC pattern → Controllers, Views, Services separation
✓ **Ordering**: Setup → Tests → Models → Services → Controllers → Views → Integration → Polish

## Validation Checklist
✓ All 4 contracts have corresponding tests (T004-T007)
✓ All 7 entities have model tasks (T013-T019)
✓ All tests come before implementation (T004-T012 before T013+)
✓ Parallel tasks are truly independent (different files, no shared dependencies)
✓ Each task specifies exact file path
✓ No [P] task modifies same file as another [P] task
✓ TDD enforced: failing tests before implementation
✓ Cross-platform requirements addressed (T036, T040)
✓ Performance requirements specified (<100ms in T039)