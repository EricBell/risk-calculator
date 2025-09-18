# Claude Code Context: Risk Calculator

## Project Overview
Windows desktop application for daytrading risk calculation using C# and WPF. Provides tabbed interface for calculating position sizes across equities, options, and futures based on account risk tolerance.

## Tech Stack
- **Language**: C# 12 / .NET 8.0
- **UI Framework**: WPF (Windows Presentation Foundation)
- **Architecture**: MVVM with CommunityToolkit.Mvvm
- **Testing**: NUnit with Moq
- **Target**: Windows 10+ desktop application

## Key Dependencies
- CommunityToolkit.Mvvm (source generators, commands)
- System.ComponentModel.DataAnnotations (validation)
- NUnit (testing framework)
- Moq (mocking for tests)

## Project Structure
```
RiskCalculator.Desktop/
├── Models/           # Trade data models (EquityTrade, OptionTrade, FutureTrade)
├── ViewModels/       # MVVM view models with commands and validation
├── Views/            # WPF user controls and windows
├── Services/         # Risk calculation and validation services
└── Validators/       # Business rule validation logic
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
- 2025-09-17: Initial feature specification and planning complete
- 2025-09-17: Architecture research and technology stack decisions
- 2025-09-17: Data model and service contracts defined