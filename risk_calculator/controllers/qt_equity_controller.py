"""Qt Equity Controller adapter for equity trading with all risk methods."""

from decimal import Decimal
from typing import Optional, Dict, List, Any

from .qt_base_controller import QtBaseController
from ..models.equity_trade import EquityTrade
from ..models.risk_method import RiskMethod
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService
from ..services.realtime_validator import RealTimeValidationService
from ..views.qt_equity_tab import QtEquityTab


class QtEquityController(QtBaseController):
    """Qt-compatible controller for equity trading with all three risk methods."""

    def __init__(self, view: QtEquityTab, risk_calculator=None, trade_validator=None):
        """
        Initialize Qt equity controller.

        Args:
            view: Qt equity tab view
            risk_calculator: Risk calculation service (optional)
            trade_validator: Trade validation service (optional)
        """
        # Initialize services (dependency injection or default creation)
        self.risk_calculator = risk_calculator or RiskCalculationService()
        self.trade_validator = trade_validator or TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)

        # Initialize trade object
        self.trade = EquityTrade()

        # Call parent constructor
        super().__init__(view)

        # Connect equity-specific signals
        self._setup_equity_connections()

    def _setup_equity_connections(self) -> None:
        """Setup equity-specific signal connections."""
        # Connect direction change signal if available
        if hasattr(self.view, 'direction_changed'):
            self.view.direction_changed.connect(self._on_direction_changed)

    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        base_fields = ['account_size', 'symbol', 'entry_price', 'trade_direction']

        if self.current_risk_method == RiskMethod.PERCENTAGE:
            return base_fields + ['risk_percentage', 'stop_loss_price']
        elif self.current_risk_method == RiskMethod.FIXED_AMOUNT:
            return base_fields + ['fixed_risk_amount', 'stop_loss_price_fixed']
        elif self.current_risk_method == RiskMethod.LEVEL_BASED:
            return base_fields + ['support_resistance_level']

        return base_fields

    def _get_trade_type(self) -> str:
        """Return trade type for validation."""
        return "equity"

    def _create_trade_object(self, form_data: Dict[str, str]) -> EquityTrade:
        """
        Create equity trade object from form data.

        Args:
            form_data: Current form data from view

        Returns:
            EquityTrade: Configured trade object
        """
        trade = EquityTrade()

        try:
            # Common fields
            if form_data.get('account_size'):
                trade.account_size = Decimal(form_data['account_size'])

            trade.risk_method = RiskMethod(form_data.get('risk_method', RiskMethod.PERCENTAGE.value))
            trade.symbol = form_data.get('symbol', '').strip()
            trade.trade_direction = form_data.get('trade_direction', 'LONG')

            # Entry price
            if form_data.get('entry_price'):
                trade.entry_price = Decimal(form_data['entry_price'])

            # Method-specific fields
            if trade.risk_method == RiskMethod.PERCENTAGE:
                if form_data.get('risk_percentage'):
                    trade.risk_percentage = Decimal(form_data['risk_percentage'])
                if form_data.get('stop_loss_price'):
                    trade.stop_loss_price = Decimal(form_data['stop_loss_price'])

            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                if form_data.get('fixed_risk_amount'):
                    trade.fixed_risk_amount = Decimal(form_data['fixed_risk_amount'])
                # Handle different field names for stop loss in fixed amount method
                stop_loss_field = form_data.get('stop_loss_price_fixed') or form_data.get('stop_loss_price')
                if stop_loss_field:
                    trade.stop_loss_price = Decimal(stop_loss_field)

            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                if form_data.get('support_resistance_level'):
                    trade.support_resistance_level = Decimal(form_data['support_resistance_level'])

        except (ValueError, TypeError, KeyError) as e:
            # Log error but return trade object (validation will catch issues)
            pass

        return trade

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if risk method is supported by equity trading."""
        # All methods are supported for equity trading
        return method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]

    def _perform_calculation(self, trade: EquityTrade) -> Optional[Dict[str, Any]]:
        """
        Perform equity position calculation.

        Args:
            trade: Equity trade object

        Returns:
            Dict[str, Any] or None: Calculation result
        """
        try:
            # Validate trade first
            validation_result = self.trade_validator.validate_equity_trade(trade)

            if not validation_result.is_valid:
                # Handle validation errors
                for field_name, error_msg in validation_result.errors.items():
                    self.view.show_field_error(field_name, error_msg)
                return None

            # Perform calculation
            calculation_result = self.risk_calculator.calculate_equity_position(trade)

            if calculation_result.success:
                # Format result for view
                return {
                    'position_size': calculation_result.position_size,
                    'estimated_risk': calculation_result.estimated_risk,
                    'position_value': calculation_result.position_value,
                    'risk_method': trade.risk_method.value,
                    'warnings': calculation_result.warnings,
                    'success': True
                }
            else:
                self.error_occurred.emit(calculation_result.error_message)
                return None

        except Exception as e:
            self.error_occurred.emit(f"Equity calculation failed: {str(e)}")
            return None

    def _on_direction_changed(self, direction: str) -> None:
        """
        Handle trade direction change.

        Args:
            direction: New trade direction (LONG/SHORT)
        """
        # Update internal state
        self.trade.trade_direction = direction

        # Clear previous calculation results
        self._clear_calculation_result()

        # Update validation status
        self._update_validation_status()

    def get_equity_specific_info(self) -> Dict[str, Any]:
        """
        Get equity-specific information for advanced features.

        Returns:
            Dict[str, Any]: Equity-specific data
        """
        form_data = self.get_current_trade_data()

        info = {
            'symbol': form_data.get('symbol', ''),
            'entry_price': form_data.get('entry_price', 0),
            'stop_loss_price': form_data.get('stop_loss_price', 0),
            'support_resistance_level': form_data.get('support_resistance_level', 0),
            'trade_direction': form_data.get('trade_direction', 'LONG'),
            'current_method': self.current_risk_method.value
        }

        # Calculate additional metrics if data is available
        try:
            entry_price = float(info['entry_price'])
            stop_loss = float(info['stop_loss_price'])

            if entry_price > 0 and stop_loss > 0:
                info['risk_per_share'] = abs(entry_price - stop_loss)
                info['risk_reward_ratio'] = self._calculate_risk_reward_ratio(form_data)

        except (ValueError, TypeError):
            pass

        return info

    def _calculate_risk_reward_ratio(self, form_data: Dict[str, Any]) -> Optional[float]:
        """
        Calculate risk-reward ratio for equity trade.

        Args:
            form_data: Current form data

        Returns:
            float or None: Risk-reward ratio
        """
        try:
            entry_price = float(form_data.get('entry_price', 0))
            stop_loss = float(form_data.get('stop_loss_price', 0))
            direction = form_data.get('trade_direction', 'LONG')

            if not entry_price or not stop_loss:
                return None

            risk_per_share = abs(entry_price - stop_loss)

            # For calculation purposes, assume 2:1 risk-reward target
            if direction == 'LONG':
                target_price = entry_price + (2 * risk_per_share)
                reward_per_share = target_price - entry_price
            else:  # SHORT
                target_price = entry_price - (2 * risk_per_share)
                reward_per_share = entry_price - target_price

            if risk_per_share > 0:
                return reward_per_share / risk_per_share

        except (ValueError, TypeError, ZeroDivisionError):
            pass

        return None

    def validate_price_relationships(self) -> List[str]:
        """
        Validate price relationships for equity trades.

        Returns:
            List[str]: List of warning messages
        """
        warnings = []
        form_data = self.get_current_trade_data()

        try:
            entry_price = float(form_data.get('entry_price', 0))
            stop_loss = float(form_data.get('stop_loss_price', 0))
            support_resistance = float(form_data.get('support_resistance_level', 0))
            direction = form_data.get('trade_direction', 'LONG')

            # Check stop loss relationship
            if entry_price > 0 and stop_loss > 0:
                if direction == 'LONG' and stop_loss >= entry_price:
                    warnings.append("Stop loss should be below entry price for long positions")
                elif direction == 'SHORT' and stop_loss <= entry_price:
                    warnings.append("Stop loss should be above entry price for short positions")

                # Check risk distance
                risk_distance = abs(entry_price - stop_loss)
                risk_percentage = (risk_distance / entry_price) * 100

                if risk_percentage < 0.5:
                    warnings.append("Stop loss very close to entry (< 0.5%)")
                elif risk_percentage > 10:
                    warnings.append("Stop loss very far from entry (> 10%)")

            # Check support/resistance relationship
            if entry_price > 0 and support_resistance > 0:
                if direction == 'LONG' and support_resistance >= entry_price:
                    warnings.append("Support level should be below entry for long positions")
                elif direction == 'SHORT' and support_resistance <= entry_price:
                    warnings.append("Resistance level should be above entry for short positions")

        except (ValueError, TypeError):
            pass

        return warnings

    def update_trade_object(self) -> None:
        """Update internal trade object with current form data."""
        form_data = self.view.get_form_data()
        self.trade = self._create_trade_object(form_data)

    def get_calculation_summary(self) -> Dict[str, Any]:
        """
        Get summary of last calculation for reporting.

        Returns:
            Dict[str, Any]: Calculation summary
        """
        if not self.calculation_result:
            return {}

        form_data = self.get_current_trade_data()

        return {
            'trade_type': 'equity',
            'symbol': form_data.get('symbol', ''),
            'account_size': form_data.get('account_size', 0),
            'risk_method': self.current_risk_method.value,
            'position_size': self.calculation_result.get('position_size', 0),
            'estimated_risk': self.calculation_result.get('estimated_risk', 0),
            'position_value': self.calculation_result.get('position_value', 0),
            'calculated_at': self.calculation_result.get('timestamp'),
            'warnings': self.calculation_result.get('warnings', [])
        }