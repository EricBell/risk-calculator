"""Qt Options Controller adapter for options trading (percentage and fixed amount only)."""

from decimal import Decimal
from typing import Optional, Dict, List, Any

from .qt_base_controller import QtBaseController
from ..models.option_trade import OptionTrade
from ..models.risk_method import RiskMethod
from ..services.risk_calculator import RiskCalculationService
from ..services.validators import TradeValidationService
from ..services.realtime_validator import RealTimeValidationService
from ..services.button_state_service import ButtonStateService
from ..views.qt_options_tab import QtOptionsTab


class QtOptionsController(QtBaseController):
    """Qt-compatible controller for options trading (no level-based method)."""

    def __init__(self, view: QtOptionsTab, risk_calculator=None, trade_validator=None):
        """
        Initialize Qt options controller.

        Args:
            view: Qt options tab view
            risk_calculator: Risk calculation service (optional)
            trade_validator: Trade validation service (optional)
        """
        # Initialize services
        self.risk_calculator = risk_calculator or RiskCalculationService()
        self.trade_validator = trade_validator or TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)
        self.button_service = ButtonStateService()

        # Initialize trade object
        self.trade = OptionTrade()

        # Call parent constructor
        super().__init__(view)

        # Connect options-specific signals
        self._setup_options_connections()

    def _setup_options_connections(self) -> None:
        """Setup options-specific signal connections."""
        # Connect direction change signal if available
        if hasattr(self.view, 'direction_changed'):
            self.view.direction_changed.connect(self._on_direction_changed)

        # Setup button state management
        self._setup_button_state_management()

    def get_required_fields(self) -> List[str]:
        """Return list of required fields based on current risk method."""
        base_fields = ['account_size', 'option_symbol', 'premium', 'contract_multiplier', 'trade_direction']

        if self.current_risk_method == RiskMethod.PERCENTAGE:
            return base_fields + ['risk_percentage']
        elif self.current_risk_method == RiskMethod.FIXED_AMOUNT:
            return base_fields + ['fixed_risk_amount']
        # Level-based not supported for options

        return base_fields

    def _get_trade_type(self) -> str:
        """Return trade type for validation."""
        return "option"

    def _create_trade_object(self, form_data: Dict[str, str]) -> OptionTrade:
        """
        Create option trade object from form data.

        Args:
            form_data: Current form data from view

        Returns:
            OptionTrade: Configured trade object
        """
        trade = OptionTrade()

        try:
            # Common fields
            if form_data.get('account_size'):
                trade.account_size = Decimal(form_data['account_size'])

            trade.risk_method = RiskMethod(form_data.get('risk_method', RiskMethod.PERCENTAGE.value))
            trade.option_symbol = form_data.get('option_symbol', '').strip()
            trade.trade_direction = form_data.get('trade_direction', 'LONG')

            # Options-specific fields
            if form_data.get('premium'):
                trade.premium = Decimal(form_data['premium'])

            if form_data.get('contract_multiplier'):
                trade.contract_multiplier = Decimal(form_data['contract_multiplier'])
            else:
                trade.contract_multiplier = Decimal('100')  # Standard default

            # Method-specific fields
            if trade.risk_method == RiskMethod.PERCENTAGE:
                if form_data.get('risk_percentage'):
                    trade.risk_percentage = Decimal(form_data['risk_percentage'])

            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                if form_data.get('fixed_risk_amount'):
                    trade.fixed_risk_amount = Decimal(form_data['fixed_risk_amount'])

            # Level-based method not supported for options

        except (ValueError, TypeError, KeyError):
            # Log error but return trade object (validation will catch issues)
            pass

        return trade

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if risk method is supported by options trading."""
        # Level-based method not supported for options
        return method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]

    def _perform_calculation(self, trade: OptionTrade) -> Optional[Dict[str, Any]]:
        """
        Perform options position calculation.

        Args:
            trade: Option trade object

        Returns:
            Dict[str, Any] or None: Calculation result
        """
        try:
            # Check if level-based method is selected (should not be available in UI)
            if trade.risk_method == RiskMethod.LEVEL_BASED:
                self.error_occurred.emit("Level-based method not supported for options trading")
                return None

            # Validate trade first
            validation_result = self.trade_validator.validate_option_trade(trade)

            if not validation_result.is_valid:
                # Handle validation errors
                for field_name, error_msg in validation_result.errors.items():
                    self.view.show_field_error(field_name, error_msg)
                return None

            # Perform calculation
            calculation_result = self.risk_calculator.calculate_option_position(trade)

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
            self.error_occurred.emit(f"Options calculation failed: {str(e)}")
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

    def get_options_specific_info(self) -> Dict[str, Any]:
        """
        Get options-specific information for advanced features.

        Returns:
            Dict[str, Any]: Options-specific data
        """
        form_data = self.get_current_trade_data()

        info = {
            'option_symbol': form_data.get('option_symbol', ''),
            'premium': form_data.get('premium', 0),
            'contract_multiplier': form_data.get('contract_multiplier', 100),
            'trade_direction': form_data.get('trade_direction', 'LONG'),
            'current_method': self.current_risk_method.value
        }

        # Calculate additional metrics
        try:
            premium = float(info['premium'])
            multiplier = float(info['contract_multiplier'])

            if premium > 0 and multiplier > 0:
                info['cost_per_contract'] = premium * multiplier

                # For bought options, risk is limited to premium paid
                if form_data.get('trade_direction') == 'LONG':
                    info['max_risk_per_contract'] = info['cost_per_contract']

        except (ValueError, TypeError):
            pass

        return info

    def validate_options_constraints(self) -> List[str]:
        """
        Validate options-specific constraints.

        Returns:
            List[str]: List of warning messages
        """
        warnings = []
        form_data = self.get_current_trade_data()

        try:
            premium = float(form_data.get('premium', 0))
            multiplier = float(form_data.get('contract_multiplier', 100))
            direction = form_data.get('trade_direction', 'LONG')

            # Check premium reasonableness
            if premium <= 0:
                warnings.append("Premium must be positive")
            elif premium > 50:  # Arbitrary high threshold
                warnings.append("Premium appears unusually high")

            # Check multiplier
            if multiplier != 100:
                warnings.append("Contract multiplier differs from standard 100")

            # Check direction-specific warnings
            if direction == 'SHORT' and premium < 1:
                warnings.append("Selling low-premium options may have limited profit potential")

        except (ValueError, TypeError):
            pass

        return warnings

    def calculate_options_greeks_impact(self) -> Dict[str, Any]:
        """
        Calculate basic options Greeks impact (simplified).

        Returns:
            Dict[str, Any]: Greeks impact information
        """
        form_data = self.get_current_trade_data()

        # This is a simplified implementation
        # In a real application, you'd integrate with an options pricing library
        impact = {
            'delta_impact': 'Options price sensitivity to underlying price changes',
            'theta_impact': 'Time decay - options lose value over time',
            'vega_impact': 'Volatility sensitivity - higher IV increases option premium',
            'gamma_impact': 'Rate of change of delta',
            'recommendation': 'Consider time to expiration and implied volatility'
        }

        try:
            premium = float(form_data.get('premium', 0))
            if premium > 0:
                # Basic time decay estimate (very simplified)
                impact['estimated_daily_theta'] = f"Approximately ${premium * 0.05:.2f} per day"

        except (ValueError, TypeError):
            pass

        return impact

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
            'trade_type': 'option',
            'option_symbol': form_data.get('option_symbol', ''),
            'account_size': form_data.get('account_size', 0),
            'risk_method': self.current_risk_method.value,
            'position_size': self.calculation_result.get('position_size', 0),
            'estimated_risk': self.calculation_result.get('estimated_risk', 0),
            'position_value': self.calculation_result.get('position_value', 0),
            'premium': form_data.get('premium', 0),
            'contract_multiplier': form_data.get('contract_multiplier', 100),
            'calculated_at': self.calculation_result.get('timestamp'),
            'warnings': self.calculation_result.get('warnings', [])
        }

    def _setup_button_state_management(self) -> None:
        """Setup button state management for the options tab."""
        # Register button with the service
        button_id = "options_calculate_button"

        # Register callback for button state changes
        def on_button_state_change(state, reason):
            """Handle button state changes."""
            if hasattr(self.view, 'calculate_button'):
                self.view.calculate_button.setEnabled(state.value == "enabled")
                tooltip = self.button_service.get_button_tooltip(
                    self.get_current_trade_data(),
                    "options"  # Options use special method
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
            risk_method = "options"  # Options always use options method
            button_id = "options_calculate_button"

            # Update button state through service
            self.button_service.update_button_model(button_id, form_data, risk_method)

        except Exception as e:
            # Silently handle errors to prevent UI crashes
            print(f"Error updating button state in options controller: {e}")

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
                'option_symbol': '',
                'premium': '',
                'risk_method': 'options'
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