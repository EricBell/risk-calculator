# Migration Plan: Tkinter → Flet

## Executive Summary

Migrate Risk Calculator from Tkinter to Flet framework while preserving all business logic and cross-platform compatibility (Linux + Windows 11).

**Impact Analysis:**
- **Keep as-is (46%)**: 12 files - All models and services (framework-agnostic)
- **Modify (23%)**: 6 files - Controllers (remove tk.StringVar, add dict-based state)
- **Rewrite (27%)**: 7 files - All views + main.py entry point
- **Delete/Update**: All Tkinter documentation references (33 files total affected)

---

## Critical Files & Changes

### Phase 1: Controller Refactoring (MODIFY)

**Base Controller** - `/risk_calculator/controllers/base_controller.py`
- Remove: `import tkinter as tk` (line 3)
- Replace: `self.tk_vars: Dict[str, tk.StringVar]` → `self.field_values: Dict[str, str] = {}`
- Remove: All `trace_add()` binding logic
- Add: `get_field_value(field_name)` and `set_field_value(field_name, value)` methods
- Keep: All business logic, validation, error management unchanged

**Asset Controllers** - Apply same pattern to:
- `/risk_calculator/controllers/equity_controller.py`
- `/risk_calculator/controllers/option_controller.py`
- `/risk_calculator/controllers/future_controller.py`
- `/risk_calculator/controllers/main_controller.py`

**Testing Checkpoint**: Unit tests pass 100% (controllers work headless)

---

### Phase 2: View Layer Rewrite (COMPLETE REWRITE)

**Base View** - Create new `/risk_calculator/views/base_view.py`
```python
import flet as ft
from abc import ABC, abstractmethod

class BaseTradingView(ft.UserControl, ABC):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

    def build(self):
        return ft.Container(
            padding=10,
            content=ft.Column([
                self.build_trade_parameters(),
                self.build_risk_method_selector(),
                self.build_method_fields(),
                self.build_action_buttons(),
                self.build_results_display()
            ])
        )

    @abstractmethod
    def build_trade_parameters(self) -> ft.Control:
        """Build asset-specific input fields."""
        pass
```

**Asset Views** - Rewrite with Flet controls:
- `/risk_calculator/views/equity_tab.py` → `equity_view.py`
- `/risk_calculator/views/option_tab.py` → `options_view.py`
- `/risk_calculator/views/future_tab.py` → `futures_view.py`

**Main Window** - Create new `/risk_calculator/views/main_view.py`
```python
import flet as ft

class MainView(ft.UserControl):
    def build(self):
        return ft.Column([
            ft.Container(content=ft.Text("Risk Calculator", size=18)),
            ft.Tabs(
                tabs=[
                    ft.Tab(text="Equity Trading", content=EquityView()),
                    ft.Tab(text="Options Trading", content=OptionsView()),
                    ft.Tab(text="Futures Trading", content=FuturesView()),
                ]
            )
        ])
```

**Widget Mapping:**
| Tkinter | Flet | Notes |
|---------|------|-------|
| `ttk.Entry` | `ft.TextField` | Use `error_text` for validation |
| `ttk.Label` | `ft.Text` | Styling via `weight`, `size`, `color` |
| `ttk.Button` | `ft.ElevatedButton` | Material Design |
| `ttk.Radiobutton` | `ft.Radio` in `ft.RadioGroup` | Simpler grouping |
| `ttk.Notebook` | `ft.Tabs` | Desktop-friendly |
| `tk.Text` | `ft.TextField(multiline=True)` | For results display |

**Testing Checkpoint**: Visual inspection, field validation works, events fire correctly

---

### Phase 3: Application Entry Point (REWRITE)

**Main Entry** - `/risk_calculator/main.py`
- Remove: All Tkinter imports and platform-specific setup (Linux X11/XCB fixes)
- Replace with Flet initialization:

```python
import flet as ft
from risk_calculator.views.main_view import MainView
from risk_calculator.controllers.main_controller import MainController

def main(page: ft.Page):
    page.title = "Risk Calculator - Daytrading Position Sizing"
    page.window_width = 800
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT

    main_view = MainView()
    main_controller = MainController(main_view)
    main_view.controller = main_controller

    page.add(main_view)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```

---

### Phase 4: Dependencies & Configuration

**Update pyproject.toml**
```toml
[project]
dependencies = ["flet>=0.25.0"]  # Current stable version

[project.scripts]
risk-calculator = "risk_calculator.main:main"
```

**Deployment**
- Use `flet build` instead of PyInstaller:
  ```bash
  flet build windows  # For Windows 11 PC
  flet build linux    # For Linux laptop
  ```

---

### Phase 5: Documentation Cleanup

**DELETE ENTIRELY:**
- `/specs/001-create-a-windows/` directory (all 10 files including contracts, research, plan, tasks, quickstart)
  - No historical reference needed - clean slate for Flet implementation

**UPDATE:**

**CLAUDE.md** - Lines to change:
- Line 5: "Tkinter (Python standard library)" → "Flet (modern Python GUI framework)"
- Line 8: Update UI Framework description
- Line 14: Remove standard library reference
- Lines 68-82: Update developer workflow section

**IMPLEMENTATION_SUMMARY.md** - Update:
- Line 12: Technology stack
- Lines 64-68: UI framework section
- Lines 172-173: Cross-platform support (no more X11 fixes needed)

**CREATE NEW:**
- `specs/002-migrate-to-flet/flet-architecture.md`
- `specs/002-migrate-to-flet/migration-summary.md`

---

### Phase 6: Test Updates

**Integration Tests (MODIFY)** - 5 files in `/tests/integration/`:
- Remove Tkinter test setup
- Test controllers directly (headless)
- Keep all business logic assertions

**Contract Tests (REWRITE)** - 2 files in `/tests/contract/`:
- `/tests/contract/test_equity_view.py` - Rewrite for Flet
- `/tests/contract/test_equity_controller.py` - Remove tk.StringVar mocking

**Example modification:**
```python
# OLD:
controller.tk_vars['account_size'].set('10000')

# NEW:
controller.set_field_value('account_size', '10000')
```

---

## Implementation Strategy

### Recommended Order

1. **Week 1-2**: Controller refactoring
   - Modify BaseController first
   - Apply pattern to asset controllers
   - Verify all unit tests pass

2. **Week 3-4**: Base view + Equity implementation
   - Create BaseTradingView component
   - Implement EquityView fully
   - Test end-to-end equity calculations

3. **Week 5**: Options & Futures views
   - Apply Equity pattern
   - Implement asset-specific fields

4. **Week 6**: Main window & navigation
   - Create MainView with Tabs
   - Implement keyboard shortcuts
   - Wire all controllers

5. **Week 7**: Entry point & testing
   - Rewrite main.py
   - Update integration tests
   - Cross-platform testing

6. **Week 8**: Documentation & deployment
   - Clean up Tkinter references
   - Test `flet build` on both platforms
   - Verify standalone executables

---

## Key Technical Decisions

### State Management
**Decision**: Use plain dict in controllers + Flet's built-in TextField.value
- Controllers store values in `self.field_values: Dict[str, str]`
- Views bind directly to TextField controls
- Validation errors set via `TextField.error_text` property

### Navigation
**Decision**: Use `ft.Tabs` for desktop-friendly interface (per user preference)
- Familiar tab pattern for desktop users
- Matches current Tkinter behavior
- Supports keyboard shortcuts (Ctrl+1/2/3)
- Simpler than NavigationBar for 3 tabs

### Validation Pattern
**Decision**: Real-time validation using TextField's built-in error_text
```python
def on_field_changed(self, e: ft.ControlEvent):
    error = self.controller.validate_field(field_name, e.control.value)
    e.control.error_text = error if error else None
    e.page.update()
```

### Packaging
**Decision**: Use `flet build` (official Flet packaging)
- Produces optimized executables with Flutter runtime
- Simpler than PyInstaller for Flet apps
- Cross-platform: `flet build windows` and `flet build linux`

---

## Files Preserved (No Changes)

**Models (8 files)** - 100% framework-agnostic:
- `/risk_calculator/models/risk_method.py`
- `/risk_calculator/models/trade.py`
- `/risk_calculator/models/equity_trade.py`
- `/risk_calculator/models/option_trade.py`
- `/risk_calculator/models/future_trade.py`
- `/risk_calculator/models/validation_result.py`
- `/risk_calculator/models/calculation_result.py`

**Services (4 files)** - 100% framework-agnostic:
- `/risk_calculator/services/risk_calculator.py`
- `/risk_calculator/services/validators.py`
- `/risk_calculator/services/realtime_validator.py`
- `/risk_calculator/services/base_validation_service.py`

---

## Risk Mitigation

**Technical Risks:**
1. **Flet Performance**: Benchmark early; use `page.update()` strategically
2. **State Management**: Test controller-view binding in Week 1
3. **Packaging**: Verify `flet build` works in initial setup

**Migration Risks:**
1. **Incomplete Migration**: Use feature branch, testing checkpoints each week
2. **Breaking Changes**: 46% of code unchanged, comprehensive tests protect business logic
3. **Documentation Drift**: Update docs in final week before deployment

---

## Success Criteria

- ✅ All 3 asset types (Equity, Options, Futures) functional
- ✅ All 3 risk methods working per asset type
- ✅ Real-time validation displays errors
- ✅ Calculations match original acceptance criteria
- ✅ Keyboard shortcuts work (Ctrl+1/2/3, Ctrl+Enter)
- ✅ Standalone executables for Windows 11 and Linux
- ✅ No Tkinter references in codebase or documentation
- ✅ All tests passing (unit, integration, contract)
- ✅ <100ms calculation performance maintained
- ✅ <50MB memory usage maintained

---

## Estimated Timeline

**Total Duration**: 8 weeks (40 working days)
**Effort**: ~180-250 hours

**Breakdown:**
- Controllers: 12-18 hours (5%)
- Views: 48-72 hours (30%)
- Main window: 30-40 hours (15%)
- Testing: 30-40 hours (15%)
- Documentation: 20-30 hours (10%)
- Infrastructure: 40-50 hours (25%)
