# Feature Specification: Cross-Platform Desktop Risk Calculator for Daytrading

**Feature Branch**: `001-create-a-windows`
**Created**: 2025-09-17
**Status**: Draft
**Input**: User description: "Create a cross-platform desktop app (Windows and Linux) taking inputs for daytrading trades, calculate the risk size for equities, options and futures. The mvp has tabs, one for each of the asset classes just enumerated."

## Execution Flow (main)
```
1. Parse user description from Input
   � Description: Cross-platform desktop app for daytrading risk calculation
2. Extract key concepts from description
   � Actors: Daytraders
   � Actions: Input trade parameters, calculate risk size
   � Data: Trade inputs, risk calculations, asset class parameters
   � Constraints: Windows and Linux desktop environment, MVP with tabs
3. Clarified aspects with reasonable assumptions:
   → Risk calculation: Percentage-based position sizing using account capital and stop loss distance
   → Account input: Total trading capital in dollars
   → Risk tolerance: Percentage of account per trade (1-5% range)
4. Fill User Scenarios & Testing section
   � Primary user flow: Select asset class � Input trade details � Calculate risk size
5. Generate Functional Requirements
   � Each requirement testable for MVP functionality
6. Identify Key Entities
   � Trade, Asset Class, Risk Parameters
7. Run Review Checklist
   → All requirements clarified with reasonable assumptions
8. Return: SUCCESS (spec ready for planning)
```

---

## � Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
A daytrader wants to quickly determine the appropriate position size for a trade across different asset classes (equities, options, futures) using their preferred risk calculation method (percentage-based, fixed dollar amount, or technical level-based) by inputting trade parameters and receiving calculated risk sizing to maintain proper risk management within their trading account.

### Acceptance Scenarios

#### Percentage-Based Risk Method Scenarios
1. **Given** the application is open, **When** user selects the "Equities" tab, chooses "Percentage-based" risk method, and enters stock symbol, entry price ($50), stop loss ($45), account size ($10,000), and risk tolerance (2%), **Then** the system calculates and displays the maximum share quantity (40 shares) to risk $200
2. **Given** user is on the "Options" tab with "Percentage-based" method, **When** user enters option contract details, premium ($2.50), account size ($10,000), and risk tolerance (3%), **Then** the system calculates the appropriate number of contracts (12 contracts) to risk $300
3. **Given** user is on the "Futures" tab with "Percentage-based" method, **When** user enters futures contract specifications, margin requirement ($4,000), tick value ($12.50), account size ($25,000), and risk tolerance (2%), **Then** the system calculates position sizing (1 contract) based on $500 risk

#### Fixed Amount Risk Method Scenarios
4. **Given** user selects "Fixed Amount" risk method on the "Equities" tab, **When** user enters stock symbol, entry price ($100), stop loss ($95), and fixed risk amount ($50), **Then** the system calculates and displays 10 shares regardless of account size
5. **Given** user selects "Fixed Amount" method on the "Options" tab, **When** user enters premium ($1.00) and fixed risk amount ($100), **Then** the system calculates 1 contract (100 shares × $1.00 = $100 risk)
6. **Given** user enters a fixed risk amount of $600 with account size $10,000, **When** they attempt to calculate, **Then** the system displays a warning "Fixed risk amount exceeds 5% of account size" and suggests reducing the amount

#### Level-Based Risk Method Scenarios
7. **Given** user selects "Level-Based" risk method on the "Equities" tab, **When** user enters stock symbol, entry price ($50), support level ($47), selects "Long" trade direction, and account size ($10,000), **Then** the system calculates position sizing using 2% default risk ($200) divided by $3 risk per share (67 shares)
8. **Given** user selects "Level-Based" method on the "Futures" tab, **When** user enters contract details, entry price (4000), resistance level (4020), selects "Short" trade direction, tick size (0.25), and tick value ($12.50), **Then** the system calculates contracts based on 80 ticks × $12.50 = $1000 risk per contract
9. **Given** user attempts to select "Level-Based" method on the "Options" tab, **When** they click the level-based radio button, **Then** the system displays "Level-based method not supported for options trading" and keeps previous method selected

#### General Validation and Navigation Scenarios
10. **Given** user has entered invalid data (negative prices, missing fields, risk tolerance above 5%), **When** they attempt to calculate, **Then** the system displays clear error messages specific to their selected risk method and prevents calculation
11. **Given** user switches between asset class tabs, **When** they return to a previously used tab, **Then** their previous inputs and risk method selection remain saved within the session
12. **Given** user enters a stop loss above entry price for a long position, **When** they attempt to calculate, **Then** the system displays an error message "Stop loss must be below entry price for long positions" (percentage/fixed methods) or "Support level must be below entry price for long positions" (level-based method)
13. **Given** calculated position size exceeds available account capital, **When** calculation is performed, **Then** the system displays a warning and suggests reducing position size, risk tolerance, or fixed amount depending on selected method
14. **Given** user switches risk calculation methods within a tab, **When** they select a different method, **Then** the UI shows/hides relevant fields, clears previous calculations, and maintains common field values (symbol, account size, entry price)

### Edge Cases
- How does the system handle risk tolerance settings below 1% or above 5% in percentage-based method?
- How does the system handle fixed risk amounts below $10 or above $500 in fixed amount method?
- What occurs when fixed risk amount exceeds 5% of account size?
- How does the system handle support/resistance levels equal to entry price in level-based method?
- What occurs when account size is insufficient for minimum position requirements across all methods?
- How does the system behave with extremely small entry prices (penny stocks) or large contract values?
- How does level-based method handle very close support/resistance levels (minimal risk distance)?
- How does the system maintain method preferences when switching between asset classes?

## Requirements

### Functional Requirements
- **FR-001**: System MUST provide a tabbed interface with three tabs: Equities, Options, and Futures
- **FR-002**: System MUST provide three risk calculation methods: Percentage-based, Fixed Amount, and Level-based
- **FR-003**: System MUST accept trade input parameters specific to each asset class and selected risk method
- **FR-004**: System MUST calculate appropriate position sizing based on selected risk method and asset-specific parameters
- **FR-005**: System MUST display calculated results clearly showing recommended position size and risk method used
- **FR-006**: System MUST validate all numeric inputs and prevent calculation with invalid data based on selected method
- **FR-007**: System MUST persist user inputs and risk method selection within each tab during the application session
- **FR-008**: System MUST provide clear error messaging for invalid inputs or calculation errors specific to each risk method
- **FR-009**: System MUST support percentage-based risk calculation using account percentage (1-5%) with stop loss distance for equities and futures
- **FR-010**: System MUST support fixed amount risk calculation using dollar amounts ($10-$500, max 5% of account) with stop loss distance for equities and futures
- **FR-011**: System MUST support level-based risk calculation using technical support/resistance levels with trade direction for equities and futures
- **FR-012**: System MUST calculate options risk using percentage-based or fixed amount methods (level-based not supported for options)
- **FR-013**: System MUST calculate futures risk accounting for margin requirements, contract specifications, and tick values across all three risk methods
- **FR-014**: Users MUST be able to input their account size or available capital for risk calculation
- **FR-015**: System MUST show/hide input fields dynamically based on selected risk calculation method
- **FR-016**: System MUST maintain risk method availability per asset class (all methods for equities/futures, percentage/fixed for options)
- **FR-017**: System MUST provide method-specific validation and error messages
- **FR-018**: System MUST clear previous calculations when risk method is changed but preserve common field values

### Key Entities
- **Trade**: Represents a potential trading position with entry price, stop loss/level, asset type, risk method, and calculated risk parameters
- **Risk Method**: Defines the calculation approach (Percentage-based, Fixed Amount, Level-based) with method-specific parameters
- **Asset Class**: Defines the type of financial instrument (equity, option, future) with specific calculation requirements and method availability
- **Risk Parameters**: Contains account size, selected risk method, method-specific settings (percentage, fixed amount, or technical level), and calculated position sizing results
- **Account**: Represents trader's capital and risk management settings for position sizing calculations across all risk methods

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---