"""Trade validation service with method-specific validation rules."""

from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from ..models.validation_result import ValidationResult
from ..models.equity_trade import EquityTrade
from ..models.option_trade import OptionTrade
from ..models.future_trade import FutureTrade
from ..models.risk_method import RiskMethod


class BaseValidationService:
    """Base validation service with common validation methods."""

    def validate_positive_decimal(self, value: str, field_name: str) -> Decimal:
        """Validate and convert to positive decimal."""
        try:
            decimal_value = Decimal(value.strip())
            if decimal_value <= 0:
                raise ValueError(f"{field_name} must be greater than 0")
            return decimal_value
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"{field_name} must be a valid positive number")

    def validate_decimal_range(self, value: str, field_name: str, min_val: Decimal, max_val: Decimal) -> Decimal:
        """Validate decimal within range."""
        decimal_value = self.validate_positive_decimal(value, field_name)
        if decimal_value < min_val or decimal_value > max_val:
            raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
        return decimal_value

    def validate_required_string(self, value: str, field_name: str) -> str:
        """Validate required string field."""
        if not value or not value.strip():
            raise ValueError(f"{field_name} is required")
        return value.strip()

    def validate_percentage(self, value: str, field_name: str) -> Decimal:
        """Validate percentage (1-5% range)."""
        return self.validate_decimal_range(value, field_name, Decimal('1.0'), Decimal('5.0'))

    def validate_fixed_amount(self, value: str, account_size: Decimal, field_name: str) -> Decimal:
        """Validate fixed risk amount ($10-$500, max 5% of account)."""
        amount = self.validate_decimal_range(value, field_name, Decimal('10'), Decimal('500'))
        max_allowed = account_size * Decimal('0.05')
        if amount > max_allowed:
            raise ValueError(f"{field_name} cannot exceed 5% of account size (${max_allowed:.2f})")
        return amount


class TradeValidationService(BaseValidationService):
    """Validates trade objects based on selected risk method."""

    def validate_equity_trade(self, trade: EquityTrade) -> ValidationResult:
        """Validate equity trade based on risk method."""
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
        """Validate option trade (level-based not supported)."""
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
        """Validate futures trade (all methods supported)."""
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

    def _validate_common_fields(self, trade, result: ValidationResult) -> None:
        """Validate fields common to all trade types."""
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

    def _validate_percentage_method(self, trade, result: ValidationResult) -> None:
        """Validate percentage-based risk method fields."""
        try:
            if trade.risk_percentage is None:
                result.add_error("risk_percentage", "Risk percentage is required for percentage method")
            elif trade.risk_percentage < Decimal('1.0') or trade.risk_percentage > Decimal('5.0'):
                result.add_error("risk_percentage", "Risk percentage must be between 1% and 5%")
        except (TypeError, AttributeError):
            result.add_error("risk_percentage", "Valid risk percentage is required")

    def _validate_fixed_amount_method(self, trade, result: ValidationResult) -> None:
        """Validate fixed amount risk method fields."""
        try:
            if trade.fixed_risk_amount is None:
                result.add_error("fixed_risk_amount", "Fixed risk amount is required for fixed amount method")
            elif trade.fixed_risk_amount < Decimal('10'):
                result.add_error("fixed_risk_amount", "Fixed risk amount must be at least $10")
            elif trade.account_size > 0:
                max_allowed = trade.account_size * Decimal('0.05')
                if trade.fixed_risk_amount > max_allowed:
                    result.add_error("fixed_risk_amount", f"Fixed risk amount cannot exceed 5% of account size (${max_allowed:.2f})")
                elif trade.fixed_risk_amount > Decimal('500'):
                    result.add_error("fixed_risk_amount", "Fixed risk amount cannot exceed $500")
            elif trade.fixed_risk_amount > Decimal('500'):
                result.add_error("fixed_risk_amount", "Fixed risk amount cannot exceed $500")
        except (TypeError, AttributeError):
            result.add_error("fixed_risk_amount", "Valid fixed risk amount is required")

    def _validate_equity_specific_fields(self, trade: EquityTrade, result: ValidationResult) -> None:
        """Validate equity-specific fields."""
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

    def _validate_option_specific_fields(self, trade: OptionTrade, result: ValidationResult) -> None:
        """Validate options-specific fields."""
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

    def _validate_future_specific_fields(self, trade: FutureTrade, result: ValidationResult) -> None:
        """Validate futures-specific fields."""
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

    def _validate_stop_loss_equity(self, trade: EquityTrade, result: ValidationResult) -> None:
        """Validate stop loss for equity trades."""
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

    def _validate_stop_loss_future(self, trade: FutureTrade, result: ValidationResult) -> None:
        """Validate stop loss for futures trades."""
        # Similar logic to equity but with futures-specific considerations
        self._validate_stop_loss_equity(trade, result)

    def _validate_level_based_method_equity(self, trade: EquityTrade, result: ValidationResult) -> None:
        """Validate level-based method for equity trades."""
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

    def _validate_level_based_method_future(self, trade: FutureTrade, result: ValidationResult) -> None:
        """Validate level-based method for futures trades."""
        # Similar logic to equity but for futures
        self._validate_level_based_method_equity(trade, result)