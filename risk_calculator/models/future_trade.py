"""Futures trade model with margin and tick value calculations."""

from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass, field
from typing import Optional
from .trade import Trade
from .risk_method import RiskMethod


@dataclass
class FutureTrade(Trade):
    """Represents futures trade with margin and tick value."""

    contract_symbol: str = ""
    entry_price: Decimal = field(default_factory=lambda: Decimal('0'))
    stop_loss_price: Optional[Decimal] = None  # For PERCENTAGE/FIXED_AMOUNT methods
    support_resistance_level: Optional[Decimal] = None  # For LEVEL_BASED method
    tick_value: Decimal = field(default_factory=lambda: Decimal('0'))  # Dollar value per tick
    tick_size: Decimal = field(default_factory=lambda: Decimal('0'))   # Minimum price increment
    margin_requirement: Decimal = field(default_factory=lambda: Decimal('0'))  # Initial margin per contract
    trade_direction: str = "LONG"  # LONG or SHORT

    @property
    def position_size(self) -> int:
        """Calculate number of contracts based on risk method."""
        risk_per_contract = self._get_risk_per_contract()
        if risk_per_contract <= 0:
            return 0

        contracts = self.calculated_risk_amount / risk_per_contract
        return int(contracts.quantize(Decimal('1'), rounding=ROUND_DOWN))

    @property
    def estimated_risk(self) -> Decimal:
        """Actual risk amount for calculated position."""
        contracts = self.position_size
        risk_per_contract = self._get_risk_per_contract()
        return Decimal(str(contracts)) * risk_per_contract

    def _get_risk_per_contract(self) -> Decimal:
        """Calculate risk per contract based on ticks at risk."""
        price_risk = self._get_price_risk()
        if price_risk <= 0 or self.tick_size <= 0:
            return Decimal('0')

        ticks_at_risk = price_risk / self.tick_size
        return ticks_at_risk * self.tick_value

    def _get_price_risk(self) -> Decimal:
        """Calculate price risk based on method."""
        if self.risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            if self.stop_loss_price is None or self.entry_price <= 0:
                return Decimal('0')
            return abs(self.entry_price - self.stop_loss_price)
        elif self.risk_method == RiskMethod.LEVEL_BASED:
            if self.support_resistance_level is None or self.entry_price <= 0:
                return Decimal('0')
            return abs(self.entry_price - self.support_resistance_level)
        return Decimal('0')

    def is_valid_contract_symbol(self) -> bool:
        """Validate contract symbol is not empty."""
        return bool(self.contract_symbol and self.contract_symbol.strip())

    def is_valid_entry_price(self) -> bool:
        """Validate entry price is positive."""
        return self.entry_price > 0

    def is_valid_tick_value(self) -> bool:
        """Validate tick value is positive."""
        return self.tick_value > 0

    def is_valid_tick_size(self) -> bool:
        """Validate tick size is positive."""
        return self.tick_size > 0

    def is_valid_margin_requirement(self) -> bool:
        """Validate margin requirement."""
        if self.margin_requirement <= 0:
            return False
        # Check if margin exceeds account size
        if self.account_size > 0:
            return self.margin_requirement <= self.account_size
        return True

    def is_valid_stop_loss_price(self) -> bool:
        """Validate stop loss price based on trade direction."""
        if self.risk_method not in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            return True

        if self.stop_loss_price is None or self.stop_loss_price <= 0:
            return False

        if self.trade_direction == "LONG":
            return self.stop_loss_price < self.entry_price
        elif self.trade_direction == "SHORT":
            return self.stop_loss_price > self.entry_price

        return True

    def is_valid_support_resistance_level(self) -> bool:
        """Validate support/resistance level based on trade direction."""
        if self.risk_method != RiskMethod.LEVEL_BASED:
            return True

        if self.support_resistance_level is None or self.support_resistance_level <= 0:
            return False

        if self.trade_direction == "LONG":
            return self.support_resistance_level < self.entry_price
        elif self.trade_direction == "SHORT":
            return self.support_resistance_level > self.entry_price

        return True

    def calculate_position_size(self) -> int:
        """Calculate position size - for compatibility with tests."""
        return self.position_size