
# Implementation Plan: UI Bug Fixes and Window Responsiveness

**Branch**: `003-there-are-several` | **Date**: 2025-09-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-there-are-several/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Fix critical UI bugs affecting user experience and implement responsive window management for cross-platform desktop application. Primary issues: disabled Calculate Position button despite valid form data, non-functional menu items, and inadequate window sizing on high-resolution displays. Solution requires button state management fixes, error message visibility improvements, and persistent window configuration system with responsive layout support.

## Technical Context
**Language/Version**: Python 3.12+
**Primary Dependencies**: Tkinter (Python standard library), JSON for configuration storage
**Storage**: Local JSON file in ~/.risk_calculator/ directory for window configuration persistence
**Testing**: pytest with unittest.mock (existing test framework)
**Target Platform**: Windows 10+ and Linux desktop applications (cross-platform desktop)
**Project Type**: single (desktop application with MVC architecture)
**Performance Goals**: UI responsiveness <100ms, window resize operations smooth at 60fps, startup <3 seconds
**Constraints**: No external dependencies beyond Python standard library, offline-capable, <50MB memory usage
**Scale/Scope**: Single-user desktop application, existing codebase ~17 service tests, 3 asset types (equity/options/futures)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Desktop-First**: ✅ PASS - All fixes target native desktop UI with no server dependencies
**II. Native UI Design**: ✅ PASS - Tkinter provides native desktop experience on Windows/Linux
**III. Performance**: ✅ PASS - Window operations maintain <100ms responsiveness, startup <3s unchanged
**IV. Accessibility**: ✅ PASS - Tkinter accessibility maintained, keyboard navigation preserved
**V. Platform Compatibility**: ✅ PASS - JSON config storage works cross-platform, no new dependencies

**Overall**: ✅ PASS - No constitutional violations detected

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project) - Desktop application using existing MVC structure

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract interface → contract test task [P]
- Each entity (WindowConfiguration, FieldValidationState, FormValidationState) → model creation task [P]
- Each user scenario from quickstart → integration test task
- Implementation tasks organized by MVC layer to make tests pass

**Specific Task Categories**:
1. **Contract Tests** [P]: ConfigurationService, ValidationService, UIController interfaces
2. **Model Implementation** [P]: WindowConfiguration, FieldValidationState, FormValidationState
3. **Service Enhancement**: Extend existing ValidationService with error messaging
4. **Service Creation**: New ConfigurationService for window persistence
5. **Controller Enhancement**: Extend BaseController for improved validation and error display
6. **Controller Enhancement**: Extend MainWindow for responsive layout and window management
7. **View Enhancement**: Add error display widgets and responsive grid configuration
8. **Integration Tests**: End-to-end scenarios from quickstart guide
9. **Cross-Platform Testing**: Windows and Linux compatibility verification

**Ordering Strategy**:
- TDD order: Contract tests → Models → Services → Controllers → Views → Integration tests
- Dependency order: Data models before services, services before controllers, controllers before views
- Mark [P] for parallel execution where files are independent
- Sequential execution for interdependent components

**Estimated Output**: 28-32 numbered, ordered tasks in tasks.md covering:
- 3 contract test tasks [P]
- 3 model implementation tasks [P]
- 2 service tasks (enhance + create)
- 4 controller enhancement tasks
- 3 view enhancement tasks
- 8 integration test tasks
- 4 cross-platform verification tasks
- 3 quickstart validation tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
