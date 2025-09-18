# Validation Service Contracts for Python Risk Calculator

## Core Validation Models

### ValidationResult
```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ValidationResult:
    is_valid: bool
    error_messages: List[str]
    warning_messages: List[str]
    field_errors: Dict[str, str]  # field_name -> error_message

    def add_error(self, field_name: str, message: str) -> None:
        """Add field-specific error"""
        self.field_errors[field_name] = message
        self.error_messages.append(f"{field_name}: {message}")
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add warning message"""
        self.warning_messages.append(message)

    def clear_field_error(self, field_name: str) -> None:
        """Clear error for specific field"""
        if field_name in self.field_errors:
            del self.field_errors[field_name]
        self.error_messages = [msg for msg in self.error_messages if not msg.startswith(f"{field_name}:")]
        self.is_valid = len(self.field_errors) == 0
```

## Base Validation Service

### Class: BaseValidationService
```python
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

class BaseValidationService(ABC):
    """Base validation service with common validation methods"""

    def validate_positive_decimal(self, value: str, field_name: str) -> Optional[Decimal]:
        """Validate and convert to positive decimal"""
        try:
            decimal_value = Decimal(value.strip())
            if decimal_value <= 0:
                raise ValueError(f"{field_name} must be greater than 0")
            return decimal_value
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"{field_name} must be a valid positive number")

    def validate_decimal_range(self, value: str, field_name: str, min_val: Decimal, max_val: Decimal) -> Decimal:
        """Validate decimal within range"""
        decimal_value = self.validate_positive_decimal(value, field_name)
        if decimal_value < min_val or decimal_value > max_val:
            raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
        return decimal_value

    def validate_required_string(self, value: str, field_name: str) -> str:
        """Validate required string field"""
        if not value or not value.strip():
            raise ValueError(f"{field_name} is required")
        return value.strip()

    def validate_percentage(self, value: str, field_name: str) -> Decimal:
        """Validate percentage (1-5% range)"""
        return self.validate_decimal_range(value, field_name, Decimal('1.0'), Decimal('5.0'))

    def validate_fixed_amount(self, value: str, account_size: Decimal, field_name: str) -> Decimal:
        """Validate fixed risk amount ($10-$500, max 5% of account)"""
        amount = self.validate_decimal_range(value, field_name, Decimal('10'), Decimal('500'))
        max_allowed = account_size * Decimal('0.05')
        if amount > max_allowed:
            raise ValueError(f"{field_name} cannot exceed 5% of account size (${max_allowed:.2f})")
        return amount
```

## Trade Validation Service

### Class: TradeValidationService(BaseValidationService)
```python
from models.trade import Trade
from models.equity_trade import EquityTrade
from models.option_trade import OptionTrade
from models.future_trade import FutureTrade
from models.risk_method import RiskMethod

class TradeValidationService(BaseValidationService):
    """Validates trade objects based on selected risk method"""

    def validate_equity_trade(self, trade: EquityTrade) -> ValidationResult:
        """Validate equity trade based on risk method"""
        result = ValidationResult(True, [], [], {})

        try:
            # Common field validation
            self._validate_common_fields(trade, result)
            self._validate_equity_specific_fields(trade, result)

            # Method-specific validation
            if trade.risk_method == RiskMethod.PERCENTAGE:
                self._validate_percentage_method(trade, result)
                self._validate_stop_loss_equity(trade, result)
            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                self._validate_fixed_amount_method(trade, result)
                self._validate_stop_loss_equity(trade, result)
            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                self._validate_level_based_method_equity(trade, result)

        except Exception as e:
            result.add_error("validation", str(e))

        return result

    def validate_option_trade(self, trade: OptionTrade) -> ValidationResult:
        """Validate option trade (level-based not supported)"""
        result = ValidationResult(True, [], [], {})

        try:
            # Common field validation
            self._validate_common_fields(trade, result)
            self._validate_option_specific_fields(trade, result)

            # Method-specific validation (no level-based for options)
            if trade.risk_method == RiskMethod.PERCENTAGE:
                self._validate_percentage_method(trade, result)
            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                self._validate_fixed_amount_method(trade, result)
            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                result.add_error("risk_method", "Level-based method not supported for options trading")

        except Exception as e:
            result.add_error("validation", str(e))

        return result

    def validate_future_trade(self, trade: FutureTrade) -> ValidationResult:
        """Validate futures trade (all methods supported)"""
        result = ValidationResult(True, [], [], {})

        try:
            # Common field validation
            self._validate_common_fields(trade, result)
            self._validate_future_specific_fields(trade, result)

            # Method-specific validation
            if trade.risk_method == RiskMethod.PERCENTAGE:
                self._validate_percentage_method(trade, result)
                self._validate_stop_loss_future(trade, result)
            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                self._validate_fixed_amount_method(trade, result)
                self._validate_stop_loss_future(trade, result)
            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                self._validate_level_based_method_future(trade, result)

        except Exception as e:
            result.add_error("validation", str(e))

        return result
```

## Private Validation Methods

### Common Field Validation

#### _validate_common_fields(trade: Trade, result: ValidationResult) -> None
```python
def _validate_common_fields(self, trade: Trade, result: ValidationResult) -> None:
    """Validate fields common to all trade types"""

    # Account size validation
    try:
        if trade.account_size <= 0:
            result.add_error("account_size", "Account size must be greater than $0")
        elif trade.account_size > Decimal('10000000'):  # $10M limit
            result.add_warning("Account size is very large, please verify")
    except (TypeError, AttributeError):
        result.add_error("account_size", "Account size is required")

    # Risk method validation
    if not isinstance(trade.risk_method, RiskMethod):
        result.add_error("risk_method", "Valid risk method must be selected")
```

#### _validate_percentage_method(trade: Trade, result: ValidationResult) -> None
```python
def _validate_percentage_method(self, trade: Trade, result: ValidationResult) -> None:
    """Validate percentage-based risk method fields"""

    try:
        if trade.risk_percentage is None:
            result.add_error("risk_percentage", "Risk percentage is required for percentage method")
        elif trade.risk_percentage < Decimal('1.0') or trade.risk_percentage > Decimal('5.0'):
            result.add_error("risk_percentage", "Risk percentage must be between 1% and 5%")
    except (TypeError, AttributeError):
        result.add_error("risk_percentage", "Valid risk percentage is required")
```

#### _validate_fixed_amount_method(trade: Trade, result: ValidationResult) -> None
```python
def _validate_fixed_amount_method(self, trade: Trade, result: ValidationResult) -> None:
    """Validate fixed amount risk method fields"""

    try:
        if trade.fixed_risk_amount is None:
            result.add_error("fixed_risk_amount", "Fixed risk amount is required for fixed amount method")
        elif trade.fixed_risk_amount < Decimal('10'):
            result.add_error("fixed_risk_amount", "Fixed risk amount must be at least $10")
        elif trade.fixed_risk_amount > Decimal('500'):
            result.add_error("fixed_risk_amount", "Fixed risk amount cannot exceed $500")
        elif trade.account_size > 0:
            max_allowed = trade.account_size * Decimal('0.05')
            if trade.fixed_risk_amount > max_allowed:
                result.add_error("fixed_risk_amount", f"Fixed risk amount cannot exceed 5% of account size (${max_allowed:.2f})")
    except (TypeError, AttributeError):
        result.add_error("fixed_risk_amount", "Valid fixed risk amount is required")
```

### Asset-Specific Validation

#### _validate_equity_specific_fields(trade: EquityTrade, result: ValidationResult) -> None
```python
def _validate_equity_specific_fields(self, trade: EquityTrade, result: ValidationResult) -> None:
    """Validate equity-specific fields"""

    # Symbol validation
    try:
        if not trade.symbol or not trade.symbol.strip():
            result.add_error("symbol", "Stock symbol is required")
        elif len(trade.symbol.strip()) > 10:
            result.add_error("symbol", "Stock symbol cannot exceed 10 characters")
    except AttributeError:
        result.add_error("symbol", "Valid stock symbol is required")

    # Entry price validation
    try:
        if trade.entry_price <= 0:
            result.add_error("entry_price", "Entry price must be greater than $0")
        elif trade.entry_price > Decimal('10000'):
            result.add_warning("Entry price is very high, please verify")
    except (TypeError, AttributeError):
        result.add_error("entry_price", "Valid entry price is required")
```

#### _validate_option_specific_fields(trade: OptionTrade, result: ValidationResult) -> None
```python
def _validate_option_specific_fields(self, trade: OptionTrade, result: ValidationResult) -> None:
    """Validate options-specific fields"""

    # Option symbol validation
    try:
        if not trade.option_symbol or not trade.option_symbol.strip():
            result.add_error("option_symbol", "Option symbol is required")
    except AttributeError:
        result.add_error("option_symbol", "Valid option symbol is required")

    # Premium validation
    try:
        if trade.premium <= 0:
            result.add_error("premium", "Premium must be greater than $0")
        elif trade.premium > Decimal('1000'):
            result.add_warning("Premium is very high, please verify")
    except (TypeError, AttributeError):
        result.add_error("premium", "Valid premium is required")

    # Contract multiplier validation
    try:
        if trade.contract_multiplier <= 0:
            result.add_error("contract_multiplier", "Contract multiplier must be greater than 0")
        elif trade.contract_multiplier != 100:
            result.add_warning("Non-standard contract multiplier detected")
    except (TypeError, AttributeError):
        result.add_error("contract_multiplier", "Valid contract multiplier is required")
```

#### _validate_future_specific_fields(trade: FutureTrade, result: ValidationResult) -> None
```python
def _validate_future_specific_fields(self, trade: FutureTrade, result: ValidationResult) -> None:
    """Validate futures-specific fields"""

    # Contract symbol validation
    try:
        if not trade.contract_symbol or not trade.contract_symbol.strip():
            result.add_error("contract_symbol", "Contract symbol is required")
    except AttributeError:
        result.add_error("contract_symbol", "Valid contract symbol is required")

    # Tick value validation
    try:
        if trade.tick_value <= 0:
            result.add_error("tick_value", "Tick value must be greater than $0")
    except (TypeError, AttributeError):
        result.add_error("tick_value", "Valid tick value is required")

    # Tick size validation
    try:
        if trade.tick_size <= 0:
            result.add_error("tick_size", "Tick size must be greater than 0")
    except (TypeError, AttributeError):
        result.add_error("tick_size", "Valid tick size is required")

    # Margin requirement validation
    try:
        if trade.margin_requirement <= 0:
            result.add_error("margin_requirement", "Margin requirement must be greater than $0")
        elif trade.margin_requirement > trade.account_size:
            result.add_error("margin_requirement", "Margin requirement exceeds account size")
    except (TypeError, AttributeError):
        result.add_error("margin_requirement", "Valid margin requirement is required")
```

### Stop Loss and Level Validation

#### _validate_stop_loss_equity(trade: EquityTrade, result: ValidationResult) -> None
```python
def _validate_stop_loss_equity(self, trade: EquityTrade, result: ValidationResult) -> None:
    """Validate stop loss for equity trades"""

    try:
        if trade.stop_loss_price is None:
            result.add_error("stop_loss_price", "Stop loss price is required")
            return

        if trade.stop_loss_price <= 0:
            result.add_error("stop_loss_price", "Stop loss price must be greater than $0")
            return

        # Direction-based validation
        if trade.trade_direction == "LONG":
            if trade.stop_loss_price >= trade.entry_price:
                result.add_error("stop_loss_price", "Stop loss must be below entry price for long positions")
        elif trade.trade_direction == "SHORT":
            if trade.stop_loss_price <= trade.entry_price:
                result.add_error("stop_loss_price", "Stop loss must be above entry price for short positions")

        # Risk distance validation
        risk_distance = abs(trade.entry_price - trade.stop_loss_price)
        if risk_distance < Decimal('0.01'):
            result.add_error("stop_loss_price", "Stop loss too close to entry price (minimum $0.01 difference)")

    except (TypeError, AttributeError):
        result.add_error("stop_loss_price", "Valid stop loss price is required")
```

#### _validate_level_based_method_equity(trade: EquityTrade, result: ValidationResult) -> None
```python
def _validate_level_based_method_equity(self, trade: EquityTrade, result: ValidationResult) -> None:
    """Validate level-based method for equity trades"""

    try:
        if trade.support_resistance_level is None:
            result.add_error("support_resistance_level", "Support/resistance level is required")
            return

        if trade.support_resistance_level <= 0:
            result.add_error("support_resistance_level", "Support/resistance level must be greater than $0")
            return

        # Direction-based validation
        if trade.trade_direction == "LONG":
            if trade.support_resistance_level >= trade.entry_price:
                result.add_error("support_resistance_level", "Support level must be below entry price for long positions")
        elif trade.trade_direction == "SHORT":
            if trade.support_resistance_level <= trade.entry_price:
                result.add_error("support_resistance_level", "Resistance level must be above entry price for short positions")

        # Level distance validation
        level_distance = abs(trade.entry_price - trade.support_resistance_level)
        if level_distance < Decimal('0.01'):
            result.add_error("support_resistance_level", "Support/resistance level too close to entry price")

    except (TypeError, AttributeError):
        result.add_error("support_resistance_level", "Valid support/resistance level is required")
```

## Real-Time Validation Service

### Class: RealTimeValidationService
```python
class RealTimeValidationService:
    """Handles real-time field validation for Tkinter UI"""

    def __init__(self, trade_validator: TradeValidationService):
        self.trade_validator = trade_validator

    def validate_field(self, field_name: str, value: str, trade_type: str, current_trade: Any) -> Optional[str]:
        """Validate single field and return error message if invalid"""

        try:
            if field_name == "account_size":
                self.trade_validator.validate_positive_decimal(value, "Account size")
            elif field_name == "risk_percentage":
                self.trade_validator.validate_percentage(value, "Risk percentage")
            elif field_name == "fixed_risk_amount":
                if hasattr(current_trade, 'account_size') and current_trade.account_size > 0:
                    self.trade_validator.validate_fixed_amount(value, current_trade.account_size, "Fixed risk amount")
                else:
                    self.trade_validator.validate_decimal_range(value, "Fixed risk amount", Decimal('10'), Decimal('500'))
            elif field_name in ["entry_price", "stop_loss_price", "support_resistance_level", "premium"]:
                self.trade_validator.validate_positive_decimal(value, field_name.replace('_', ' ').title())
            elif field_name in ["symbol", "option_symbol", "contract_symbol"]:
                self.trade_validator.validate_required_string(value, field_name.replace('_', ' ').title())

            return None  # No error

        except ValueError as e:
            return str(e)
        except Exception:
            return f"Invalid {field_name.replace('_', ' ')}"

    def validate_method_compatibility(self, risk_method: RiskMethod, trade_type: str) -> Optional[str]:
        """Validate if risk method is compatible with trade type"""

        if trade_type == "option" and risk_method == RiskMethod.LEVEL_BASED:
            return "Level-based method not supported for options trading"

        return None
```

## Validation Error Messages

### Standard Error Messages
```python
VALIDATION_MESSAGES = {
    "required": "{field} is required",
    "positive_number": "{field} must be a positive number",
    "range": "{field} must be between {min} and {max}",
    "percentage_range": "Risk percentage must be between 1% and 5%",
    "fixed_amount_range": "Fixed risk amount must be between $10 and $500",
    "fixed_amount_account_limit": "Fixed risk amount cannot exceed 5% of account size",
    "stop_loss_direction_long": "Stop loss must be below entry price for long positions",
    "stop_loss_direction_short": "Stop loss must be above entry price for short positions",
    "level_direction_long": "Support level must be below entry price for long positions",
    "level_direction_short": "Resistance level must be above entry price for short positions",
    "level_based_options": "Level-based method not supported for options trading",
    "minimum_risk_distance": "Risk distance too small (minimum $0.01 difference)",
    "margin_exceeds_account": "Margin requirement exceeds account size",
}

def get_validation_message(key: str, **kwargs) -> str:
    """Get formatted validation message"""
    return VALIDATION_MESSAGES.get(key, "Validation error").format(**kwargs)
```