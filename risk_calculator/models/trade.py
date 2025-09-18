"""Base trade model with common properties for all asset classes."""

from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional
from .risk_method import RiskMethod


@dataclass
class Trade(ABC):
    """Base abstract class for all trade types with common properties."""

    account_size: Decimal = field(default_factory=lambda: Decimal('0'))
    risk_method: RiskMethod = RiskMethod.PERCENTAGE
    risk_percentage: Optional[Decimal] = field(default_factory=lambda: Decimal('2.0'))  # Default 2%
    fixed_risk_amount: Optional[Decimal] = None

    @property
    def calculated_risk_amount(self) -> Decimal:
        """Calculate risk amount based on selected method."""
        if self.risk_method == RiskMethod.PERCENTAGE:
            if self.risk_percentage is None:
                return Decimal('0')
            return self.account_size * self.risk_percentage / Decimal('100')
        elif self.risk_method == RiskMethod.FIXED_AMOUNT:
            return self.fixed_risk_amount or Decimal('0')
        elif self.risk_method == RiskMethod.LEVEL_BASED:
            return self.account_size * Decimal('0.02')  # Default 2%
        return Decimal('0')

    @property
    @abstractmethod
    def position_size(self) -> int:
        """Calculate position size based on asset type and risk method."""
        pass

    @property
    @abstractmethod
    def estimated_risk(self) -> Decimal:
        """Actual risk amount for calculated position."""
        pass

    def is_valid_account_size(self) -> bool:
        """Validate account size is positive."""
        return self.account_size > 0

    def is_valid_risk_percentage(self) -> bool:
        """Validate risk percentage is within 1-5% range."""
        if self.risk_percentage is None:
            return self.risk_method != RiskMethod.PERCENTAGE
        return Decimal('1.0') <= self.risk_percentage <= Decimal('5.0')

    def is_valid_fixed_risk_amount(self) -> bool:
        """Validate fixed risk amount is within range and account limits."""
        if self.fixed_risk_amount is None:
            return self.risk_method != RiskMethod.FIXED_AMOUNT

        # Check range $10-$500
        if not (Decimal('10') <= self.fixed_risk_amount <= Decimal('500')):
            return False

        # Check 5% of account limit
        if self.account_size > 0:
            max_allowed = self.account_size * Decimal('0.05')
            return self.fixed_risk_amount <= max_allowed

        return True