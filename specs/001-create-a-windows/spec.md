# Feature Specification: Windows Desktop Risk Calculator for Daytrading

**Feature Branch**: `001-create-a-windows`
**Created**: 2025-09-17
**Status**: Draft
**Input**: User description: "Create a windows desktop app taking inputs for daytrading trades, calculate the risk size for equities, options and futures. The mvp has tabs, one for each of the asset classes just enumerated."

## Execution Flow (main)
```
1. Parse user description from Input
   ’ Description: Windows desktop app for daytrading risk calculation
2. Extract key concepts from description
   ’ Actors: Daytraders
   ’ Actions: Input trade parameters, calculate risk size
   ’ Data: Trade inputs, risk calculations, asset class parameters
   ’ Constraints: Windows desktop environment, MVP with tabs
3. For each unclear aspect:
   ’ [NEEDS CLARIFICATION: Risk calculation methodology not specified]
   ’ [NEEDS CLARIFICATION: Account size/capital input method not specified]
   ’ [NEEDS CLARIFICATION: Risk percentage or dollar amount limits not specified]
4. Fill User Scenarios & Testing section
   ’ Primary user flow: Select asset class ’ Input trade details ’ Calculate risk size
5. Generate Functional Requirements
   ’ Each requirement testable for MVP functionality
6. Identify Key Entities
   ’ Trade, Asset Class, Risk Parameters
7. Run Review Checklist
   ’ WARN "Spec has uncertainties regarding risk calculation methods"
8. Return: SUCCESS (spec ready for planning)
```

---

## ¡ Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
A daytrader wants to quickly determine the appropriate position size for a trade across different asset classes (equities, options, futures) by inputting trade parameters and receiving calculated risk sizing to maintain proper risk management within their trading account.

### Acceptance Scenarios
1. **Given** the application is open, **When** user selects the "Equities" tab and enters stock symbol, entry price, stop loss, and account size, **Then** the system calculates and displays the maximum share quantity to risk
2. **Given** user is on the "Options" tab, **When** user enters option contract details, premium, and risk parameters, **Then** the system calculates the appropriate number of contracts to trade
3. **Given** user is on the "Futures" tab, **When** user enters futures contract specifications and risk tolerance, **Then** the system calculates position sizing based on margin and tick value
4. **Given** user has entered invalid data (negative prices, missing fields), **When** they attempt to calculate, **Then** the system displays clear error messages and prevents calculation
5. **Given** user switches between asset class tabs, **When** they return to a previously used tab, **Then** their previous inputs remain saved within the session

### Edge Cases
- What happens when stop loss price is above entry price for long positions?
- How does system handle when calculated position size exceeds account capital?
- What occurs when required fields are left empty?
- How does the system behave with extremely small or large numeric inputs?

## Requirements

### Functional Requirements
- **FR-001**: System MUST provide a tabbed interface with three tabs: Equities, Options, and Futures
- **FR-002**: System MUST accept trade input parameters specific to each asset class (price, quantity, stop loss, etc.)
- **FR-003**: System MUST calculate appropriate position sizing based on risk parameters and account size
- **FR-004**: System MUST display calculated results clearly showing recommended position size
- **FR-005**: System MUST validate all numeric inputs and prevent calculation with invalid data
- **FR-006**: System MUST persist user inputs within each tab during the application session
- **FR-007**: System MUST provide clear error messaging for invalid inputs or calculation errors
- **FR-008**: System MUST calculate risk for equities using [NEEDS CLARIFICATION: risk calculation method - percentage of account, dollar amount, volatility-based?]
- **FR-009**: System MUST calculate options risk considering [NEEDS CLARIFICATION: premium cost, delta, or other Greeks?]
- **FR-010**: System MUST calculate futures risk accounting for [NEEDS CLARIFICATION: margin requirements, contract specifications, or tick values?]
- **FR-011**: Users MUST be able to input their account size or available capital for risk calculation
- **FR-012**: System MUST allow users to set risk tolerance as [NEEDS CLARIFICATION: percentage of account, fixed dollar amount, or both?]

### Key Entities
- **Trade**: Represents a potential trading position with entry price, stop loss, asset type, and calculated risk parameters
- **Asset Class**: Defines the type of financial instrument (equity, option, future) with specific calculation requirements
- **Risk Parameters**: Contains account size, risk tolerance settings, and calculated position sizing results
- **Account**: Represents trader's capital and risk management settings for position sizing calculations

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
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
- [ ] Review checklist passed (pending clarification of risk calculation methods)

---