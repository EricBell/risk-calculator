"""Calculation result model for encapsulating calculation outcomes."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from .risk_method import RiskMethod


@dataclass
class CalculationResult:
    """Encapsulates calculation outcome and results."""

    is_success: bool = False
    position_size: int = 0
    estimated_risk: Decimal = field(default_factory=lambda: Decimal('0'))
    risk_method_used: Optional[RiskMethod] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def set_success(self, position_size: int, estimated_risk: Decimal,
                   risk_method: RiskMethod) -> None:
        """Set successful calculation result."""
        self.is_success = True
        self.position_size = position_size
        self.estimated_risk = estimated_risk
        self.risk_method_used = risk_method
        self.error_message = None

    def set_error(self, message: str) -> None:
        """Set error result."""
        self.is_success = False
        self.position_size = 0
        self.estimated_risk = Decimal('0')
        self.error_message = message

    def add_warning(self, message: str) -> None:
        """Add warning message."""
        self.warnings.append(message)

    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0

    @property
    def success(self) -> bool:
        """Backward compatibility property for is_success."""
        return self.is_success

    @property
    def risk_method(self) -> Optional[RiskMethod]:
        """Backward compatibility property for risk_method_used."""
        return self.risk_method_used

    def get_risk_amount(self, account_size: Decimal, risk_method: RiskMethod,
                       risk_percentage: Optional[Decimal] = None,
                       fixed_risk_amount: Optional[Decimal] = None) -> Decimal:
        """Calculate the risk amount based on method (for display purposes)."""
        if risk_method == RiskMethod.PERCENTAGE and risk_percentage is not None:
            return account_size * risk_percentage / Decimal('100')
        elif risk_method == RiskMethod.FIXED_AMOUNT and fixed_risk_amount is not None:
            return fixed_risk_amount
        elif risk_method == RiskMethod.LEVEL_BASED:
            return account_size * Decimal('0.02')  # Default 2%
        return Decimal('0')