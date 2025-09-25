"""Risk calculation service with support for all three calculation methods."""

from decimal import Decimal, getcontext, ROUND_DOWN
from typing import Optional, Dict, Any
from ..models.equity_trade import EquityTrade
from ..models.option_trade import OptionTrade
from ..models.future_trade import FutureTrade
from ..models.calculation_result import CalculationResult
from ..models.risk_method import RiskMethod

# Import interfaces from tests (they define the contracts)
import sys
import os
test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tests', 'contract')
sys.path.insert(0, test_dir)

try:
    from test_options_level_based_interface import OptionsLevelBasedInterface
    from test_options_stop_loss_interface import OptionsStopLossInterface
    INTERFACES_AVAILABLE = True
except ImportError:
    # If interfaces are not available, create dummy base classes
    class OptionsLevelBasedInterface:
        pass
    class OptionsStopLossInterface:
        pass
    INTERFACES_AVAILABLE = False


class RiskCalculationService(OptionsLevelBasedInterface, OptionsStopLossInterface):
    """Provides risk calculation methods for different asset classes."""

    def __init__(self):
        # Set consistent precision for cross-platform compatibility
        getcontext().prec = 28
        self.DEFAULT_LEVEL_RISK_PERCENTAGE = Decimal('0.02')  # 2% for level-based

    def calculate_equity_position(self, trade: EquityTrade) -> CalculationResult:
        """Calculate equity position size based on selected risk method."""
        result = CalculationResult()

        try:
            # Validate basic requirements
            if not self._validate_basic_trade_data(trade):
                result.set_error("Invalid trade data")
                return result

            # Calculate risk amount based on method
            risk_amount = self._calculate_risk_amount(trade)
            if risk_amount <= 0:
                result.set_error("Risk amount must be greater than zero")
                return result

            # Calculate risk per share
            risk_per_share = self._get_equity_risk_per_share(trade)
            if risk_per_share <= 0:
                result.set_error("Risk distance cannot be zero")
                return result

            # Calculate position size
            position_size = int((risk_amount / risk_per_share).quantize(Decimal('1'), rounding=ROUND_DOWN))
            estimated_risk = Decimal(str(position_size)) * risk_per_share

            # Check position size limits
            max_position_by_capital = int(trade.account_size / trade.entry_price)
            if position_size > max_position_by_capital:
                result.add_warning(f"Position size limited by account capital: {max_position_by_capital} shares")
                position_size = max_position_by_capital
                estimated_risk = Decimal(str(position_size)) * risk_per_share

            # Check if position exceeds 25% of account value
            position_value = Decimal(str(position_size)) * trade.entry_price
            if position_value > trade.account_size * Decimal('0.25'):
                result.add_warning("Position size exceeds 25% of account value")

            result.set_success(position_size, estimated_risk, trade.risk_method)

        except Exception as e:
            result.set_error(f"Calculation failed: {str(e)}")

        return result

    def calculate_option_position(self, trade: OptionTrade) -> CalculationResult:
        """Calculate option position size based on selected risk method."""
        result = CalculationResult()

        try:
            # Level-based method now supported for options
            if trade.risk_method == RiskMethod.LEVEL_BASED:
                return self._calculate_option_level_based(trade)

            # Validate basic requirements
            if not self._validate_basic_trade_data(trade):
                result.set_error("Invalid trade data")
                return result

            if trade.premium <= 0:
                result.set_error("Premium must be greater than zero")
                return result

            # Calculate risk amount
            risk_amount = self._calculate_risk_amount(trade)
            if risk_amount <= 0:
                result.set_error("Risk amount must be greater than zero")
                return result

            # Calculate cost per contract
            cost_per_contract = trade.premium * Decimal(str(trade.contract_multiplier))

            # Calculate position size
            position_size = int((risk_amount / cost_per_contract).quantize(Decimal('1'), rounding=ROUND_DOWN))
            estimated_risk = Decimal(str(position_size)) * cost_per_contract

            # Check if premium cost is reasonable
            if estimated_risk > risk_amount * Decimal('1.1'):  # 10% tolerance
                result.add_warning("Premium cost exceeds risk tolerance")

            result.set_success(position_size, estimated_risk, trade.risk_method)

        except Exception as e:
            result.set_error(f"Calculation failed: {str(e)}")

        return result

    def calculate_future_position(self, trade: FutureTrade) -> CalculationResult:
        """Calculate futures position size based on selected risk method."""
        result = CalculationResult()

        try:
            # Validate basic requirements
            if not self._validate_basic_trade_data(trade):
                result.set_error("Invalid trade data")
                return result

            if trade.tick_value <= 0 or trade.tick_size <= 0:
                result.set_error("Tick value and tick size must be greater than zero")
                return result

            # Calculate risk amount
            risk_amount = self._calculate_risk_amount(trade)
            if risk_amount <= 0:
                result.set_error("Risk amount must be greater than zero")
                return result

            # Calculate price risk
            price_risk = self._get_futures_price_risk(trade)
            if price_risk <= 0:
                result.set_error("Price difference must be at least one tick")
                return result

            # Calculate ticks at risk and risk per contract
            ticks_at_risk = price_risk / trade.tick_size
            risk_per_contract = ticks_at_risk * trade.tick_value

            # Calculate position size
            position_size = int((risk_amount / risk_per_contract).quantize(Decimal('1'), rounding=ROUND_DOWN))
            estimated_risk = Decimal(str(position_size)) * risk_per_contract

            # Check margin requirements
            total_margin = Decimal(str(position_size)) * trade.margin_requirement
            if total_margin > trade.account_size:
                result.add_warning("Insufficient margin for calculated position")
                # Adjust position size to fit margin
                max_contracts = int(trade.account_size / trade.margin_requirement)
                position_size = max_contracts
                estimated_risk = Decimal(str(position_size)) * risk_per_contract

            result.set_success(position_size, estimated_risk, trade.risk_method)

        except Exception as e:
            result.set_error(f"Calculation failed: {str(e)}")

        return result

    def _validate_basic_trade_data(self, trade) -> bool:
        """Validate basic trade data common to all asset types."""
        return (hasattr(trade, 'account_size') and
                trade.account_size > 0 and
                hasattr(trade, 'risk_method'))

    def _calculate_risk_amount(self, trade) -> Decimal:
        """Calculate risk amount based on selected method."""
        if trade.risk_method == RiskMethod.PERCENTAGE:
            if not hasattr(trade, 'risk_percentage') or trade.risk_percentage is None:
                return Decimal('0')
            return trade.account_size * trade.risk_percentage / Decimal('100')
        elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
            if not hasattr(trade, 'fixed_risk_amount') or trade.fixed_risk_amount is None:
                return Decimal('0')
            return trade.fixed_risk_amount
        elif trade.risk_method == RiskMethod.LEVEL_BASED:
            return trade.account_size * self.DEFAULT_LEVEL_RISK_PERCENTAGE
        return Decimal('0')

    def _get_equity_risk_per_share(self, trade: EquityTrade) -> Decimal:
        """Calculate risk per share for equity trades."""
        if trade.risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            if trade.stop_loss_price is None or trade.entry_price <= 0:
                return Decimal('0')
            return abs(trade.entry_price - trade.stop_loss_price)
        elif trade.risk_method == RiskMethod.LEVEL_BASED:
            if trade.support_resistance_level is None or trade.entry_price <= 0:
                return Decimal('0')
            return abs(trade.entry_price - trade.support_resistance_level)
        return Decimal('0')

    def _get_futures_price_risk(self, trade: FutureTrade) -> Decimal:
        """Calculate price risk for futures trades."""
        if trade.risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            if trade.stop_loss_price is None or trade.entry_price <= 0:
                return Decimal('0')
            return abs(trade.entry_price - trade.stop_loss_price)
        elif trade.risk_method == RiskMethod.LEVEL_BASED:
            if trade.support_resistance_level is None or trade.entry_price <= 0:
                return Decimal('0')
            return abs(trade.entry_price - trade.support_resistance_level)
        return Decimal('0')

    def _calculate_option_level_based(self, trade: OptionTrade) -> CalculationResult:
        """Calculate option position for level-based method."""
        result = CalculationResult()

        try:
            # Validate level-based specific data
            if not trade.is_valid_level_data():
                result.set_error("Invalid level-based data: support/resistance levels and trade direction required")
                return result

            # Calculate risk amount using level-based logic
            risk_amount = self._calculate_risk_amount(trade)
            if risk_amount <= 0:
                result.set_error("Risk amount must be greater than zero")
                return result

            # Use the level-based calculation from OptionTrade model
            position_size = trade.position_size
            if position_size <= 0:
                result.set_error("Cannot calculate position size with current parameters")
                return result

            cost_per_contract = trade.premium * Decimal(str(trade.contract_multiplier))
            estimated_risk = Decimal(str(position_size)) * cost_per_contract

            # Add level-based specific warnings
            level_diff = abs(trade.resistance_level - trade.support_level)
            if level_diff < trade.premium:
                result.add_warning("Level range is smaller than option premium")

            result.set_success(position_size, estimated_risk, trade.risk_method)

        except Exception as e:
            result.set_error(f"Level-based calculation failed: {str(e)}")

        return result

    # Interface implementations for OptionsLevelBasedInterface
    def calculate_level_based_risk(
        self,
        account_size: Decimal,
        support_level: Decimal,
        resistance_level: Decimal,
        option_premium: Decimal,
        entry_price: Optional[Decimal] = None,
        stop_loss_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Calculate position size using level-based risk method for options."""
        try:
            # Validate inputs
            if support_level >= resistance_level:
                raise ValueError("Support level must be less than resistance level")

            if option_premium <= 0:
                raise ValueError("Option premium must be positive")

            # Calculate risk amount (2% default for level-based)
            risk_amount = account_size * self.DEFAULT_LEVEL_RISK_PERCENTAGE

            # Calculate cost per contract (assuming 100 multiplier)
            cost_per_contract = option_premium * Decimal('100')

            # Calculate contracts
            contracts = int((risk_amount / cost_per_contract).quantize(Decimal('1'), rounding=ROUND_DOWN))
            premium_cost = Decimal(str(contracts)) * cost_per_contract
            level_range = resistance_level - support_level
            risk_percentage = (premium_cost / account_size) * Decimal('100')

            return {
                'contracts': contracts,
                'risk_amount': premium_cost,
                'premium_cost': premium_cost,
                'level_range': level_range,
                'risk_percentage': risk_percentage
            }

        except Exception as e:
            return {
                'contracts': 0,
                'risk_amount': Decimal('0'),
                'premium_cost': Decimal('0'),
                'level_range': Decimal('0'),
                'risk_percentage': Decimal('0'),
                'error': str(e)
            }

    def validate_level_based_fields(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate level-based method specific fields for options."""
        errors = {}

        # Check required fields
        required_fields = ['account_size', 'support_level', 'resistance_level', 'option_premium']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"
                continue

            try:
                value = Decimal(str(form_data[field]))
                if value <= 0:
                    errors[field] = f"{field.replace('_', ' ').title()} must be positive"
            except (ValueError, TypeError):
                errors[field] = f"{field.replace('_', ' ').title()} must be a valid number"

        # Validate support < resistance
        if 'support_level' in form_data and 'resistance_level' in form_data:
            try:
                support = Decimal(str(form_data['support_level']))
                resistance = Decimal(str(form_data['resistance_level']))
                if support >= resistance:
                    errors['support_level'] = "Support level must be less than resistance level"
            except (ValueError, TypeError):
                pass  # Already handled above

        return errors

    def get_required_fields_level_based(self) -> list[str]:
        """Get list of required field names for level-based options trading."""
        return ['account_size', 'support_level', 'resistance_level', 'option_premium', 'trade_direction']

    # Interface implementations for OptionsStopLossInterface
    def calculate_options_with_stop_loss(
        self,
        account_size: Decimal,
        risk_method: str,
        option_premium: Decimal,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        risk_percentage: Optional[Decimal] = None,
        fixed_risk_amount: Optional[Decimal] = None,
        support_level: Optional[Decimal] = None,
        resistance_level: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Calculate options position with stop loss price consideration."""
        try:
            # Calculate base risk amount based on method
            if risk_method == 'percentage':
                if risk_percentage is None:
                    raise ValueError("Risk percentage required for percentage method")
                risk_amount = account_size * risk_percentage / Decimal('100')
            elif risk_method == 'fixed_amount':
                if fixed_risk_amount is None:
                    raise ValueError("Fixed risk amount required for fixed amount method")
                risk_amount = fixed_risk_amount
            elif risk_method == 'level_based':
                risk_amount = account_size * self.DEFAULT_LEVEL_RISK_PERCENTAGE
            else:
                raise ValueError(f"Unknown risk method: {risk_method}")

            # Calculate cost per contract
            cost_per_contract = option_premium * Decimal('100')

            # Calculate contracts based on premium cost
            contracts = int((risk_amount / cost_per_contract).quantize(Decimal('1'), rounding=ROUND_DOWN))
            premium_cost = Decimal(str(contracts)) * cost_per_contract

            # Calculate stop loss risk (simplified - premium is max loss for long options)
            stop_loss_risk = premium_cost
            max_loss = premium_cost  # For long options, max loss is premium paid

            return {
                'contracts': contracts,
                'risk_amount': risk_amount,
                'premium_cost': premium_cost,
                'stop_loss_risk': stop_loss_risk,
                'max_loss': max_loss
            }

        except Exception as e:
            return {
                'contracts': 0,
                'risk_amount': Decimal('0'),
                'premium_cost': Decimal('0'),
                'stop_loss_risk': Decimal('0'),
                'max_loss': Decimal('0'),
                'error': str(e)
            }

    def validate_stop_loss_fields(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate stop loss related fields for options."""
        errors = {}

        # Entry price validation
        if 'entry_price' in form_data and form_data['entry_price']:
            try:
                entry_price = Decimal(str(form_data['entry_price']))
                if entry_price <= 0:
                    errors['entry_price'] = "Entry price must be positive"
            except (ValueError, TypeError):
                errors['entry_price'] = "Entry price must be a valid number"

        # Stop loss price validation
        if 'stop_loss_price' in form_data and form_data['stop_loss_price']:
            try:
                stop_loss = Decimal(str(form_data['stop_loss_price']))
                if stop_loss <= 0:
                    errors['stop_loss_price'] = "Stop loss price must be positive"

                # Check relationship with entry price
                if 'entry_price' in form_data and form_data['entry_price']:
                    try:
                        entry_price = Decimal(str(form_data['entry_price']))
                        if stop_loss == entry_price:
                            errors['stop_loss_price'] = "Stop loss price cannot equal entry price"
                    except (ValueError, TypeError):
                        pass
            except (ValueError, TypeError):
                errors['stop_loss_price'] = "Stop loss price must be a valid number"

        return errors

    def get_required_fields_with_stop_loss(self, risk_method: str) -> list[str]:
        """Get required fields when using stop loss for options."""
        base_fields = ['account_size', 'option_premium', 'entry_price', 'stop_loss_price']

        if risk_method == 'percentage':
            base_fields.append('risk_percentage')
        elif risk_method == 'fixed_amount':
            base_fields.append('fixed_risk_amount')
        elif risk_method == 'level_based':
            base_fields.extend(['support_level', 'resistance_level', 'trade_direction'])

        return base_fields

    def calculate_stop_loss_exit_value(
        self,
        contracts: int,
        option_premium: Decimal,
        entry_price: Decimal,
        stop_loss_price: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate the exit value and loss when stop loss is hit."""
        try:
            # For options, the exit value depends on the relationship between
            # entry price and stop loss price of the underlying
            # Simplified calculation: assume premium goes to zero at stop loss
            exit_value = Decimal('0')  # Assuming option expires worthless at stop loss

            premium_paid = Decimal(str(contracts)) * option_premium * Decimal('100')
            realized_loss = premium_paid - exit_value  # Full premium lost
            remaining_premium = Decimal('0')  # No remaining premium value

            return {
                'exit_value': exit_value,
                'realized_loss': realized_loss,
                'remaining_premium': remaining_premium
            }

        except Exception:
            return {
                'exit_value': Decimal('0'),
                'realized_loss': Decimal('0'),
                'remaining_premium': Decimal('0')
            }