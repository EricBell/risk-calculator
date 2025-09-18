"""Equity trade model with specific calculation logic."""

from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass, field
from typing import Optional
from .trade import Trade
from .risk_method import RiskMethod


@dataclass
class EquityTrade(Trade):
    """Represents equity/stock trade with entry and stop/level prices."""

    symbol: str = ""
    entry_price: Decimal = field(default_factory=lambda: Decimal('0'))
    stop_loss_price: Optional[Decimal] = None  # For PERCENTAGE/FIXED_AMOUNT methods
    support_resistance_level: Optional[Decimal] = None  # For LEVEL_BASED method
    trade_direction: str = "LONG"  # LONG or SHORT

    @property
    def position_size(self) -> int:
        """Calculate number of shares based on risk method."""
        risk_per_share = self._get_risk_per_share()
        if risk_per_share <= 0:
            return 0

        shares = self.calculated_risk_amount / risk_per_share
        return int(shares.quantize(Decimal('1'), rounding=ROUND_DOWN))

    @property
    def estimated_risk(self) -> Decimal:
        """Actual risk amount for calculated position."""
        shares = self.position_size
        risk_per_share = self._get_risk_per_share()
        return Decimal(str(shares)) * risk_per_share

    def _get_risk_per_share(self) -> Decimal:
        """Calculate risk per share based on selected method."""
        if self.risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            if self.stop_loss_price is None or self.entry_price <= 0:
                return Decimal('0')
            return abs(self.entry_price - self.stop_loss_price)
        elif self.risk_method == RiskMethod.LEVEL_BASED:
            if self.support_resistance_level is None or self.entry_price <= 0:
                return Decimal('0')
            return abs(self.entry_price - self.support_resistance_level)
        return Decimal('0')

    def is_valid_symbol(self) -> bool:
        """Validate symbol is not empty."""
        return bool(self.symbol and self.symbol.strip())

    def is_valid_entry_price(self) -> bool:
        """Validate entry price is positive."""
        return self.entry_price > 0

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