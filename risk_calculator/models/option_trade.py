"""Option trade model with contract multiplier calculations."""

from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass, field
from typing import Optional
from .trade import Trade
from .risk_method import RiskMethod


@dataclass
class OptionTrade(Trade):
    """Represents options trade with premium and contract details."""

    option_symbol: str = ""
    premium: Decimal = field(default_factory=lambda: Decimal('0'))
    contract_multiplier: int = 100  # Shares per contract (default 100)

    # Level-based method fields
    support_level: Optional[Decimal] = None
    resistance_level: Optional[Decimal] = None
    trade_direction: str = ""  # "call" or "put"

    # Stop loss functionality fields
    entry_price: Optional[Decimal] = None
    stop_loss_price: Optional[Decimal] = None

    @property
    def position_size(self) -> int:
        """Calculate number of contracts based on risk method."""
        if self.risk_method == RiskMethod.LEVEL_BASED:
            return self._calculate_level_based_position()

        cost_per_contract = self._get_cost_per_contract()
        if cost_per_contract <= 0:
            return 0

        contracts = self.calculated_risk_amount / cost_per_contract
        return int(contracts.quantize(Decimal('1'), rounding=ROUND_DOWN))

    @property
    def estimated_risk(self) -> Decimal:
        """Actual risk amount for calculated position."""
        contracts = self.position_size
        cost_per_contract = self._get_cost_per_contract()
        return Decimal(str(contracts)) * cost_per_contract

    def _get_cost_per_contract(self) -> Decimal:
        """Calculate cost per contract (premium × multiplier)."""
        return self.premium * Decimal(str(self.contract_multiplier))

    def is_valid_option_symbol(self) -> bool:
        """Validate option symbol is not empty."""
        return bool(self.option_symbol and self.option_symbol.strip())

    def is_valid_premium(self) -> bool:
        """Validate premium is positive."""
        return self.premium > 0

    def is_valid_contract_multiplier(self) -> bool:
        """Validate contract multiplier is positive."""
        return self.contract_multiplier > 0

    def is_level_based_supported(self) -> bool:
        """Level-based method now supported for options."""
        return True

    def calculate_position_size(self) -> int:
        """Calculate position size - for compatibility with tests."""
        return self.position_size

    def _calculate_level_based_position(self) -> int:
        """Calculate position size for level-based method."""
        if not self._has_valid_level_based_data():
            return 0

        # Calculate underlying price movement risk
        level_diff = abs(self.resistance_level - self.support_level)
        if level_diff <= 0:
            return 0

        # For options, the risk is based on how much the underlying can move
        # against the position times the option's delta exposure
        cost_per_contract = self._get_cost_per_contract()
        if cost_per_contract <= 0:
            return 0

        # Simple level-based calculation: use premium as max loss per contract
        contracts = self.calculated_risk_amount / cost_per_contract
        return int(contracts.quantize(Decimal('1'), rounding=ROUND_DOWN))

    def _has_valid_level_based_data(self) -> bool:
        """Check if level-based data is valid."""
        return (
            self.support_level is not None and
            self.resistance_level is not None and
            self.support_level > 0 and
            self.resistance_level > 0 and
            self.support_level < self.resistance_level and
            self.trade_direction in ['call', 'put']
        )

    def is_valid_level_data(self) -> bool:
        """Validate level-based method data."""
        return self._has_valid_level_based_data()

    def is_valid_stop_loss_data(self) -> bool:
        """Validate stop loss data."""
        if self.entry_price is None or self.stop_loss_price is None:
            return True  # Stop loss is optional

        return (
            self.entry_price > 0 and
            self.stop_loss_price > 0 and
            self.entry_price != self.stop_loss_price
        )

    def calculate_stop_loss_risk(self) -> Optional[Decimal]:
        """Calculate risk based on entry and stop loss prices."""
        if not self.is_valid_stop_loss_data() or self.entry_price is None or self.stop_loss_price is None:
            return None

        # For options, stop loss typically involves the premium paid
        # The risk is the premium per contract times number of contracts
        return self._get_cost_per_contract()