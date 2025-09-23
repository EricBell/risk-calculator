"""Qt Futures Controller adapter for futures trading with all risk methods and margin validation."""

from decimal import Decimal
from typing import Optional, Dict, List, Any

from .qt_base_controller import QtBaseController
from ..models.future_trade import FutureTrade
from ..models.risk_method import RiskMethod
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService
from ..services.realtime_validator import RealTimeValidationService
from ..services.button_state_service import ButtonStateService
from ..views.qt_futures_tab import QtFuturesTab


class QtFuturesController(QtBaseController):
    """Qt-compatible controller for futures trading with all three risk methods."""

    def __init__(self, view: QtFuturesTab, risk_calculator=None, trade_validator=None):
        """
        Initialize Qt futures controller.

        Args:
            view: Qt futures tab view
            risk_calculator: Risk calculation service (optional)
            trade_validator: Trade validation service (optional)
        """
        # Initialize services
        self.risk_calculator = risk_calculator or RiskCalculationService()
        self.trade_validator = trade_validator or TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)
        self.button_service = ButtonStateService()

        # Initialize trade object
        self.trade = FutureTrade()

        # Call parent constructor
        super().__init__(view)

        # Connect futures-specific signals
        self._setup_futures_connections()

    def _setup_futures_connections(self) -> None:
        """Setup futures-specific signal connections."""
        # Connect direction change signal if available
        if hasattr(self.view, 'direction_changed'):
            self.view.direction_changed.connect(self._on_direction_changed)

        # Setup button state management
        self._setup_button_state_management()

    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        base_fields = ['account_size', 'contract_symbol', 'entry_price', 'tick_value',
                      'tick_size', 'margin_requirement', 'trade_direction']

        if self.current_risk_method == RiskMethod.PERCENTAGE:
            return base_fields + ['risk_percentage', 'stop_loss_ticks']
        elif self.current_risk_method == RiskMethod.FIXED_AMOUNT:
            return base_fields + ['fixed_risk_amount', 'stop_loss_ticks_fixed']
        elif self.current_risk_method == RiskMethod.LEVEL_BASED:
            return base_fields + ['support_resistance_level']

        return base_fields

    def _get_trade_type(self) -> str:
        """Return trade type for validation."""
        return "future"

    def _create_trade_object(self, form_data: Dict[str, str]) -> FutureTrade:
        """
        Create future trade object from form data.

        Args:
            form_data: Current form data from view

        Returns:
            FutureTrade: Configured trade object
        """
        trade = FutureTrade()

        try:
            # Common fields
            if form_data.get('account_size'):
                trade.account_size = Decimal(form_data['account_size'])

            trade.risk_method = RiskMethod(form_data.get('risk_method', RiskMethod.PERCENTAGE.value))
            trade.contract_symbol = form_data.get('contract_symbol', '').strip()
            trade.trade_direction = form_data.get('trade_direction', 'LONG')

            # Price and contract specification fields
            if form_data.get('entry_price'):
                trade.entry_price = Decimal(form_data['entry_price'])

            if form_data.get('tick_value'):
                trade.tick_value = Decimal(form_data['tick_value'])

            if form_data.get('tick_size'):
                trade.tick_size = Decimal(form_data['tick_size'])

            if form_data.get('margin_requirement'):
                trade.margin_requirement = Decimal(form_data['margin_requirement'])

            # Method-specific fields
            if trade.risk_method == RiskMethod.PERCENTAGE:
                if form_data.get('risk_percentage'):
                    trade.risk_percentage = Decimal(form_data['risk_percentage'])
                # Handle stop loss in ticks for futures
                if form_data.get('stop_loss_ticks'):
                    trade.stop_loss_ticks = int(form_data['stop_loss_ticks'])

            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                if form_data.get('fixed_risk_amount'):
                    trade.fixed_risk_amount = Decimal(form_data['fixed_risk_amount'])
                # Handle different field names for stop loss in fixed amount method
                stop_loss_field = form_data.get('stop_loss_ticks_fixed') or form_data.get('stop_loss_ticks')
                if stop_loss_field:
                    trade.stop_loss_ticks = int(stop_loss_field)

            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                if form_data.get('support_resistance_level'):
                    trade.support_resistance_level = Decimal(form_data['support_resistance_level'])

        except (ValueError, TypeError, KeyError):
            # Log error but return trade object (validation will catch issues)
            pass

        return trade

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if risk method is supported by futures trading."""
        # All methods are supported for futures trading
        return method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]

    def _perform_calculation(self, trade: FutureTrade) -> Optional[Dict[str, Any]]:
        """
        Perform futures position calculation.

        Args:
            trade: Future trade object

        Returns:
            Dict[str, Any] or None: Calculation result
        """
        try:
            # Validate trade first
            validation_result = self.trade_validator.validate_future_trade(trade)

            if not validation_result.is_valid:
                # Handle validation errors
                for field_name, error_msg in validation_result.errors.items():
                    self.view.show_field_error(field_name, error_msg)
                return None

            # Perform calculation
            calculation_result = self.risk_calculator.calculate_future_position(trade)

            if calculation_result.success:
                # Calculate margin required
                margin_required = calculation_result.position_size * trade.margin_requirement

                # Format result for view
                return {
                    'position_size': calculation_result.position_size,
                    'estimated_risk': calculation_result.estimated_risk,
                    'margin_required': margin_required,
                    'risk_method': trade.risk_method.value,
                    'warnings': calculation_result.warnings,
                    'success': True
                }
            else:
                self.error_occurred.emit(calculation_result.error_message)
                return None

        except Exception as e:
            self.error_occurred.emit(f"Futures calculation failed: {str(e)}")
            return None

    def _handle_field_change(self, field_name: str, new_value: str) -> None:
        """
        Override to handle futures-specific field changes.

        Args:
            field_name: Name of changed field
            new_value: New field value
        """
        # Call parent handler
        super()._handle_field_change(field_name, new_value)

        # Handle margin-specific validation
        if field_name == 'margin_requirement':
            self._validate_margin_requirement(new_value)

    def _validate_margin_requirement(self, margin_value: str) -> None:
        """
        Validate margin requirement against account size.

        Args:
            margin_value: Margin requirement value
        """
        try:
            form_data = self.view.get_form_data()
            account_size = float(form_data.get('account_size', 0))
            margin = float(margin_value) if margin_value.strip() else 0

            if account_size > 0 and margin > 0:
                # Check if account can support at least one contract
                if margin > account_size:
                    self.view.show_field_error('margin_requirement',
                                             'Margin requirement exceeds account size')
                elif margin > account_size * 0.5:
                    # Warning for high margin utilization
                    pass  # Could add warning here

        except (ValueError, TypeError):
            pass

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

    def get_futures_specific_info(self) -> Dict[str, Any]:
        """
        Get futures-specific information for advanced features.

        Returns:
            Dict[str, Any]: Futures-specific data
        """
        form_data = self.get_current_trade_data()

        info = {
            'contract_symbol': form_data.get('contract_symbol', ''),
            'entry_price': form_data.get('entry_price', 0),
            'tick_value': form_data.get('tick_value', 0),
            'tick_size': form_data.get('tick_size', 0),
            'margin_requirement': form_data.get('margin_requirement', 0),
            'trade_direction': form_data.get('trade_direction', 'LONG'),
            'current_method': self.current_risk_method.value
        }

        # Calculate additional metrics
        try:
            tick_value = float(info['tick_value'])
            tick_size = float(info['tick_size'])
            margin = float(info['margin_requirement'])

            if tick_value > 0 and tick_size > 0:
                info['dollar_per_tick'] = tick_value
                info['minimum_price_move'] = tick_size

            # Calculate max contracts based on margin
            account_size = float(form_data.get('account_size', 0))
            if account_size > 0 and margin > 0:
                info['max_contracts_by_margin'] = int(account_size / margin)

        except (ValueError, TypeError):
            pass

        return info

    def calculate_margin_utilization(self, position_size: int = None) -> Dict[str, Any]:
        """
        Calculate margin utilization for given or current position.

        Args:
            position_size: Number of contracts (uses last calculation if None)

        Returns:
            Dict[str, Any]: Margin utilization information
        """
        if position_size is None and self.calculation_result:
            position_size = int(self.calculation_result.get('position_size', 0))

        if not position_size:
            return {}

        form_data = self.get_current_trade_data()

        try:
            account_size = float(form_data.get('account_size', 0))
            margin_req = float(form_data.get('margin_requirement', 0))

            if account_size > 0 and margin_req > 0:
                total_margin = position_size * margin_req
                utilization_pct = (total_margin / account_size) * 100

                return {
                    'position_size': position_size,
                    'margin_per_contract': margin_req,
                    'total_margin_required': total_margin,
                    'account_size': account_size,
                    'margin_utilization_pct': utilization_pct,
                    'available_margin': account_size - total_margin,
                    'max_additional_contracts': int((account_size - total_margin) / margin_req) if margin_req > 0 else 0,
                    'risk_level': self._get_margin_risk_level(utilization_pct)
                }

        except (ValueError, TypeError, ZeroDivisionError):
            pass

        return {}

    def _get_margin_risk_level(self, utilization_pct: float) -> str:
        """
        Get risk level based on margin utilization.

        Args:
            utilization_pct: Margin utilization percentage

        Returns:
            str: Risk level description
        """
        if utilization_pct <= 25:
            return "Conservative"
        elif utilization_pct <= 50:
            return "Moderate"
        elif utilization_pct <= 75:
            return "Aggressive"
        else:
            return "Very High Risk"

    def validate_futures_constraints(self) -> List[str]:
        """
        Validate futures-specific constraints.

        Returns:
            List[str]: List of warning messages
        """
        warnings = []
        form_data = self.get_current_trade_data()

        try:
            tick_value = float(form_data.get('tick_value', 0))
            tick_size = float(form_data.get('tick_size', 0))
            margin = float(form_data.get('margin_requirement', 0))
            account_size = float(form_data.get('account_size', 0))

            # Validate tick specifications
            if tick_value <= 0:
                warnings.append("Tick value must be positive")
            if tick_size <= 0:
                warnings.append("Tick size must be positive")

            # Validate margin requirements
            if margin <= 0:
                warnings.append("Margin requirement must be positive")
            elif account_size > 0:
                if margin > account_size * 0.8:
                    warnings.append("High margin requirement relative to account size")

            # Check reasonable relationships
            if tick_value > 100:  # Arbitrary threshold
                warnings.append("Unusually high tick value - verify contract specifications")

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
        margin_info = self.calculate_margin_utilization()

        return {
            'trade_type': 'future',
            'contract_symbol': form_data.get('contract_symbol', ''),
            'account_size': form_data.get('account_size', 0),
            'risk_method': self.current_risk_method.value,
            'position_size': self.calculation_result.get('position_size', 0),
            'estimated_risk': self.calculation_result.get('estimated_risk', 0),
            'margin_required': self.calculation_result.get('margin_required', 0),
            'margin_utilization': margin_info.get('margin_utilization_pct', 0),
            'tick_value': form_data.get('tick_value', 0),
            'tick_size': form_data.get('tick_size', 0),
            'calculated_at': self.calculation_result.get('timestamp'),
            'warnings': self.calculation_result.get('warnings', [])
        }

    def _setup_button_state_management(self) -> None:
        """Setup button state management for the futures tab."""
        # Register button with the service
        button_id = "futures_calculate_button"

        # Register callback for button state changes
        def on_button_state_change(state, reason):
            """Handle button state changes."""
            if hasattr(self.view, 'calculate_button'):
                self.view.calculate_button.setEnabled(state.value == "enabled")
                tooltip = self.button_service.get_button_tooltip(
                    self.get_current_trade_data(),
                    "futures"  # Futures use special method
                )
                self.view.calculate_button.setToolTip(tooltip or "")

        self.button_service.register_button_callback(button_id, on_button_state_change)

        # Connect field changes to button state updates
        if hasattr(self.view, 'input_fields'):
            for field_name, field_widget in self.view.input_fields.items():
                if hasattr(field_widget, 'textChanged'):
                    field_widget.textChanged.connect(self._update_button_state)

        # Connect risk method changes to button state updates
        if hasattr(self.view, 'risk_method_combo'):
            self.view.risk_method_combo.currentIndexChanged.connect(self._update_button_state)

        # Perform initial button state update
        self._update_button_state()

    def _update_button_state(self) -> None:
        """Update button state based on current form data."""
        try:
            form_data = self.get_current_trade_data()
            risk_method = "futures"  # Futures always use futures method
            button_id = "futures_calculate_button"

            # Update button state through service
            self.button_service.update_button_model(button_id, form_data, risk_method)

        except Exception as e:
            # Silently handle errors to prevent UI crashes
            print(f"Error updating button state in futures controller: {e}")

    def get_current_trade_data(self) -> Dict[str, Any]:
        """
        Get current form data for validation and button state management.

        Returns:
            Dictionary with current form data
        """
        if hasattr(self.view, 'get_form_data'):
            return self.view.get_form_data()
        else:
            # Fallback if view doesn't have get_form_data method
            return {
                'account_size': '',
                'contract_symbol': '',
                'entry_price': '',
                'tick_value': '',
                'tick_size': '',
                'margin_requirement': '',
                'risk_method': 'futures'
            }

    def validate_current_form(self) -> bool:
        """
        Validate the current form state.

        Returns:
            True if form is valid, False otherwise
        """
        if hasattr(self.view, 'is_form_valid'):
            return self.view.is_form_valid()
        else:
            # Fallback validation
            form_data = self.get_current_trade_data()
            required_fields = self.get_required_fields()

            for field in required_fields:
                if not form_data.get(field, '').strip():
                    return False

            return True