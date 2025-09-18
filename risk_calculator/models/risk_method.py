"""Risk calculation method enumeration for the risk calculator."""

from enum import Enum


class RiskMethod(Enum):
    """Defines the three available risk calculation approaches."""

    PERCENTAGE = "percentage"
    """Risk based on percentage of account size (1-5%)"""

    FIXED_AMOUNT = "fixed_amount"
    """Risk based on fixed dollar amount ($10-$500)"""

    LEVEL_BASED = "level_based"
    """Risk based on technical support/resistance levels"""

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return self.value.replace('_', ' ').title()