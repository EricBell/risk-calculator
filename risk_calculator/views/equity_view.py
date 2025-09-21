"""
EquityView - Contract compatibility wrapper for EquityTab.
Provides EquityView interface for contract testing.
"""

from .equity_tab import EquityTab


class EquityView(EquityTab):
    """EquityView wrapper for contract compatibility."""

    def __init__(self, parent, controller=None):
        """
        Initialize EquityView as EquityTab wrapper.

        Args:
            parent: Parent widget
            controller: Optional controller
        """
        super().__init__(parent, controller)