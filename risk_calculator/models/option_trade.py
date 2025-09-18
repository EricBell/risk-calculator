"""Option trade model with contract multiplier calculations."""

from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass, field
from .trade import Trade
from .risk_method import RiskMethod


@dataclass
class OptionTrade(Trade):
    """Represents options trade with premium and contract details."""

    option_symbol: str = ""
    premium: Decimal = field(default_factory=lambda: Decimal('0'))
    contract_multiplier: int = 100  # Shares per contract (default 100)

    @property
    def position_size(self) -> int:
        """Calculate number of contracts based on risk method."""
        # Level-based method not supported for options
        if self.risk_method == RiskMethod.LEVEL_BASED:
            return 0

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
        """Level-based method not supported for options."""
        return False

    def calculate_position_size(self) -> int:
        """Calculate position size - for compatibility with tests."""
        return self.position_size