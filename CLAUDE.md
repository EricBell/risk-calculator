# Claude Code Context: Risk Calculator

## Project Overview
Cross-platform desktop application for daytrading risk calculation using Python and Tkinter. Runs on Windows and Linux. Provides tabbed interface for calculating position sizes across equities, options, and futures based on account risk tolerance.

## Tech Stack
- **Language**: Python 3.12+
- **UI Framework**: Tkinter (Python standard library)
- **Architecture**: MVC with separation of concerns
- **Testing**: pytest with unittest.mock
- **Target**: Windows 10+ and Linux desktop application

## Key Dependencies
- Python 3.12+ standard library (tkinter, decimal, dataclasses, typing)
- pytest (testing framework)
- pytest-mock (mocking for tests)
- PyInstaller (deployment packaging)

## Project Structure
```
risk_calculator/
├── main.py                    # Application entry point
├── models/                    # Trade data models (EquityTrade, OptionTrade, FutureTrade)
├── views/                     # Tkinter UI components and windows
├── controllers/               # Application controllers and event handling
├── services/                  # Risk calculation and validation services
└── tests/                     # Unit and integration tests
```

## Current Status
**Phase**: Planning Complete (001-create-a-windows branch)
**Artifacts Generated**:
- Feature specification with acceptance criteria
- Technical research and architecture decisions
- Data model design with entity relationships
- Service contracts and API specifications
- Quickstart implementation guide

## Key Features
1. **Tabbed Interface**: Separate tabs for Equities, Options, Futures
2. **Risk Calculation**: Percentage-based position sizing with stop loss
3. **Input Validation**: Real-time validation with clear error messages
4. **Session Persistence**: Maintain inputs within application session
5. **Performance**: <100ms calculations, <50MB memory usage

## Business Logic
- **Equities**: Shares = (Account × Risk%) / (Entry - StopLoss)
- **Options**: Contracts = (Account × Risk%) / (Premium × 100)
- **Futures**: Contracts = (Account × Risk%) / (TickValue × TicksAtRisk)

## Next Steps
Ready for `/tasks` command to generate implementation tasks from design artifacts.

## Recent Changes
- 2025-09-18: Updated specifications from Windows-only C#/.NET to cross-platform Python
- 2025-09-17: Initial feature specification and planning complete
- 2025-09-17: Architecture research and technology stack decisions