"""Real-time validation service for Tkinter UI field validation."""

from decimal import Decimal
from typing import Optional, Any
from .validators import BaseValidationService
from ..models.risk_method import RiskMethod


class RealTimeValidationService:
    """Handles real-time field validation for Tkinter UI."""

    def __init__(self, trade_validator: BaseValidationService):
        self.trade_validator = trade_validator

    def validate_field(self, field_name: str, value: str, trade_type: str, current_trade: Any) -> Optional[str]:
        """Validate single field and return error message if invalid."""
        if not value or not value.strip():
            # Allow empty values during typing
            return None

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
            elif field_name in ["tick_value", "tick_size", "margin_requirement"]:
                self.trade_validator.validate_positive_decimal(value, field_name.replace('_', ' ').title())

            return None  # No error

        except ValueError as e:
            return str(e)
        except Exception:
            return f"Invalid {field_name.replace('_', ' ')}"

    def validate_method_compatibility(self, risk_method: RiskMethod, trade_type: str) -> Optional[str]:
        """Validate if risk method is compatible with trade type."""
        if trade_type == "option" and risk_method == RiskMethod.LEVEL_BASED:
            return "Level-based method not supported for options trading"

        return None

    def validate_price_relationship(self, entry_price: str, comparison_price: str,
                                  field_name: str, trade_direction: str) -> Optional[str]:
        """Validate price relationships (stop loss, support/resistance vs entry)."""
        try:
            if not entry_price or not comparison_price:
                return None

            entry = Decimal(entry_price.strip())
            comparison = Decimal(comparison_price.strip())

            if field_name == "stop_loss_price":
                if trade_direction == "LONG" and comparison >= entry:
                    return "Stop loss must be below entry price for long positions"
                elif trade_direction == "SHORT" and comparison <= entry:
                    return "Stop loss must be above entry price for short positions"
            elif field_name == "support_resistance_level":
                if trade_direction == "LONG" and comparison >= entry:
                    return "Support level must be below entry price for long positions"
                elif trade_direction == "SHORT" and comparison <= entry:
                    return "Resistance level must be above entry price for short positions"

            return None

        except (ValueError, AttributeError):
            return None  # Don't show error during typing

    def validate_account_percentage(self, fixed_amount: str, account_size: str) -> Optional[str]:
        """Validate fixed amount doesn't exceed 5% of account."""
        try:
            if not fixed_amount or not account_size:
                return None

            amount = Decimal(fixed_amount.strip())
            account = Decimal(account_size.strip())

            if account > 0:
                percentage = (amount / account) * 100
                if percentage > 5:
                    return f"Fixed amount is {percentage:.1f}% of account (max 5%)"

            return None

        except (ValueError, AttributeError):
            return None

    def get_field_suggestions(self, field_name: str, trade_type: str) -> str:
        """Get helpful suggestions for field inputs."""
        suggestions = {
            "risk_percentage": "Enter 1-5% (e.g., 2.0 for 2%)",
            "fixed_risk_amount": "Enter $10-$500 (max 5% of account)",
            "entry_price": "Enter positive price in dollars",
            "stop_loss_price": "Must be below entry for long, above for short",
            "support_resistance_level": "Enter key technical level price",
            "premium": "Enter option premium per share",
            "tick_value": "Dollar value per tick movement",
            "tick_size": "Minimum price increment",
            "margin_requirement": "Initial margin per contract"
        }

        return suggestions.get(field_name, "Enter valid value")

    def format_validation_message(self, field_name: str, error_message: str) -> str:
        """Format validation message for display."""
        field_display = field_name.replace('_', ' ').title()
        return f"{field_display}: {error_message}"