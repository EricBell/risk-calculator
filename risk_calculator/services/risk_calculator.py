"""Risk calculation service with support for all three calculation methods."""

from decimal import Decimal, getcontext, ROUND_DOWN
from typing import Optional
from ..models.equity_trade import EquityTrade
from ..models.option_trade import OptionTrade
from ..models.future_trade import FutureTrade
from ..models.calculation_result import CalculationResult
from ..models.risk_method import RiskMethod


class RiskCalculationService:
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
            # Level-based method not supported for options
            if trade.risk_method == RiskMethod.LEVEL_BASED:
                result.set_error("Level-based method not applicable for options")
                return result

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