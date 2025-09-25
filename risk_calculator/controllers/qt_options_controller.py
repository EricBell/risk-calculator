"""Qt Options Controller adapter for options trading with level-based and stop loss support."""

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
    """Qt-compatible controller for options trading with level-based and stop loss support."""

    def __init__(self, view: QtOptionsTab, risk_calculator=None, trade_validator=None):
        """
        Initialize Qt options controller.

        Args:
            view: Qt options tab view
            risk_calculator: Risk calculation service (optional)
            trade_validator: Trade validation service (optional)
        """
        # Call parent constructor first
        super().__init__(view)

        # Initialize services AFTER parent constructor (dependency injection or default creation)
        self.risk_calculator = risk_calculator or RiskCalculationService()
        self.trade_validator = trade_validator or TradeValidationService()
        self.realtime_validator = RealTimeValidationService(self.trade_validator)
        self.button_service = ButtonStateService()

        # Initialize trade object
        self.trade = OptionTrade()

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
        elif self.current_risk_method == RiskMethod.LEVEL_BASED:
            return base_fields + ['support_level', 'resistance_level']

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

            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                if form_data.get('support_level'):
                    trade.support_level = Decimal(form_data['support_level'])
                if form_data.get('resistance_level'):
                    trade.resistance_level = Decimal(form_data['resistance_level'])

            # Stop loss fields (optional for all methods)
            if form_data.get('entry_price'):
                trade.entry_price = Decimal(form_data['entry_price'])
            if form_data.get('stop_loss_price'):
                trade.stop_loss_price = Decimal(form_data['stop_loss_price'])

        except (ValueError, TypeError, KeyError):
            # Log error but return trade object (validation will catch issues)
            pass

        return trade

    def _is_method_supported(self, method: RiskMethod) -> bool:
        """Check if risk method is supported by options trading."""
        # All methods now supported for options
        return method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT, RiskMethod.LEVEL_BASED]

    def _perform_calculation(self, trade: OptionTrade) -> Optional[Dict[str, Any]]:
        """
        Perform options position calculation.

        Args:
            trade: Option trade object

        Returns:
            Dict[str, Any] or None: Calculation result
        """
        try:
            # Validate trade first
            validation_result = self.trade_validator.validate_option_trade(trade)

            if not validation_result.is_valid:
                # Handle validation errors
                for field_name, error_msg in validation_result.errors.items():
                    self.view.show_field_error(field_name, error_msg)
                return None

            # Check if stop loss price is provided and use enhanced calculation
            if trade.stop_loss_price is not None:
                # Use stop loss enhanced calculation (use premium as entry price)
                if hasattr(self.risk_calculator, 'calculate_options_with_stop_loss'):
                    calculation_result = self.risk_calculator.calculate_options_with_stop_loss(
                        account_size=trade.account_size,
                        risk_method=trade.risk_method.value,
                        option_premium=trade.premium,
                        entry_price=trade.premium,  # For options, premium is the entry price
                        stop_loss_price=trade.stop_loss_price,
                        risk_percentage=trade.risk_percentage,
                        fixed_risk_amount=trade.fixed_risk_amount,
                        support_level=trade.support_level,
                        resistance_level=trade.resistance_level
                    )

                    # Convert enhanced calculation result format
                    if isinstance(calculation_result, dict) and 'contracts' in calculation_result:
                        from ..models.calculation_result import CalculationResult
                        calculation_result = CalculationResult(
                            success=True,
                            position_size=calculation_result['contracts'],
                            estimated_risk=float(calculation_result['risk_amount']),
                            warnings=[]
                        )
                else:
                    # Fallback to standard calculation
                    calculation_result = self.risk_calculator.calculate_option_position(trade)
            else:
                # Standard calculation without stop loss
                calculation_result = self.risk_calculator.calculate_option_position(trade)

            if calculation_result.success:
                # Calculate position value (position_size * premium * contract_multiplier)
                try:
                    position_value = float(calculation_result.position_size) * float(trade.premium) * float(trade.contract_multiplier)
                except (ValueError, TypeError, AttributeError):
                    position_value = 0.0

                # Format result for view
                return {
                    'position_size': calculation_result.position_size,
                    'estimated_risk': float(calculation_result.estimated_risk),
                    'position_value': position_value,
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
                enabled = (state.value == "enabled")
                self.view.calculate_button.setEnabled(enabled)
                form_data = self.get_current_trade_data()
                risk_method = "options"  # Options use special validation
                tooltip = self.button_service.get_button_tooltip(form_data, risk_method)
                self.view.calculate_button.setToolTip(tooltip or "")

        self.button_service.register_button_callback(button_id, on_button_state_change)

        # Connect field changes from view to button state updates
        if hasattr(self.view, 'field_changed'):
            self.view.field_changed.connect(self._on_field_change_for_button_state)

        # Connect risk method changes to button state updates
        if hasattr(self.view, 'risk_method_combo'):
            self.view.risk_method_combo.currentIndexChanged.connect(self._update_button_state)

        # Perform initial button state update
        self._update_button_state()

    def _on_field_change_for_button_state(self, field_name: str, new_value: str) -> None:
        """
        Handle field change events for button state management.

        Args:
            field_name: Name of the field that changed
            new_value: New value of the field
        """
        # Update button state when any field changes
        self._update_button_state()

    def _update_button_state(self) -> None:
        """Update button state based on current form data."""
        try:
            form_data = self.get_current_trade_data()
            risk_method = "options"  # Options always use special validation
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

    def _update_validation_status(self) -> None:
        """
        Override base controller validation status update to prevent button conflicts.
        The QtOptionsController uses its own button state management system.
        """
        # Check if we have any field errors
        had_errors = self.has_errors
        self.has_errors = len(self.field_errors) > 0

        # Emit validation change signal if status changed
        if had_errors != self.has_errors:
            self.validation_changed.emit(self.has_errors)

        # Note: We do NOT call self.view.set_calculate_button_enabled() here
        # because this controller uses the ButtonStateService for button management

    def calculate_level_based_options(self) -> Optional[Dict[str, Any]]:
        """
        Calculate options position using level-based risk method.

        Returns:
            Dict[str, Any] or None: Level-based calculation result
        """
        try:
            form_data = self.get_current_trade_data()

            # Validate required fields for level-based method
            required_fields = ['account_size', 'support_level', 'resistance_level', 'premium']
            for field in required_fields:
                if not form_data.get(field, '').strip():
                    self.error_occurred.emit(f"Missing required field for level-based calculation: {field}")
                    return None

            # Use level-based calculation service method
            if hasattr(self.risk_calculator, 'calculate_level_based_risk'):
                result = self.risk_calculator.calculate_level_based_risk(
                    account_size=Decimal(form_data['account_size']),
                    support_level=Decimal(form_data['support_level']),
                    resistance_level=Decimal(form_data['resistance_level']),
                    option_premium=Decimal(form_data['premium']),
                    entry_price=Decimal(form_data['entry_price']) if form_data.get('entry_price') else None,
                    stop_loss_price=Decimal(form_data['stop_loss_price']) if form_data.get('stop_loss_price') else None
                )

                # Format result for consistency with other methods
                return {
                    'position_size': result['contracts'],
                    'estimated_risk': float(result['risk_amount']),
                    'position_value': float(result['premium_cost']),
                    'risk_method': 'level_based',
                    'level_range': float(result['level_range']),
                    'risk_percentage': float(result['risk_percentage']),
                    'warnings': [],
                    'success': True
                }
            else:
                self.error_occurred.emit("Level-based calculation not available")
                return None

        except Exception as e:
            self.error_occurred.emit(f"Level-based calculation failed: {str(e)}")
            return None

    def validate_stop_loss_constraints(self, form_data: Dict[str, Any]) -> List[str]:
        """
        Validate stop loss constraints for options trading.

        Args:
            form_data: Current form data

        Returns:
            List[str]: List of validation error messages
        """
        errors = []

        try:
            entry_price = form_data.get('entry_price')
            stop_loss_price = form_data.get('stop_loss_price')
            trade_direction = form_data.get('trade_direction', 'call').lower()

            if entry_price and stop_loss_price:
                entry_val = Decimal(str(entry_price))
                stop_val = Decimal(str(stop_loss_price))

                # For call options (or default), stop loss should be below entry
                # For put options, stop loss should be above entry
                if trade_direction in ['call', 'long', '']:  # Default to call behavior
                    if stop_val >= entry_val:
                        errors.append("Stop loss price must be below entry price for call options")
                elif trade_direction in ['put', 'short']:
                    if stop_val <= entry_val:
                        errors.append("Stop loss price must be above entry price for put options")

                # Additional stop loss validations
                price_diff = abs(entry_val - stop_val)
                if price_diff == 0:
                    errors.append("Stop loss price cannot equal entry price")
                elif price_diff < Decimal('0.01'):
                    errors.append("Stop loss price too close to entry price")

        except (ValueError, TypeError) as e:
            errors.append(f"Invalid price values for stop loss validation: {str(e)}")

        return errors

    def get_enhanced_calculation_summary(self) -> Dict[str, Any]:
        """
        Get enhanced calculation summary including level-based and stop loss data.

        Returns:
            Dict[str, Any]: Enhanced calculation summary
        """
        base_summary = self.get_calculation_summary()
        form_data = self.get_current_trade_data()

        # Add level-based specific data
        if self.current_risk_method == RiskMethod.LEVEL_BASED:
            base_summary.update({
                'support_level': form_data.get('support_level', 0),
                'resistance_level': form_data.get('resistance_level', 0),
                'level_range': self.calculation_result.get('level_range', 0) if self.calculation_result else 0
            })

        # Add stop loss data if present
        if form_data.get('entry_price') or form_data.get('stop_loss_price'):
            base_summary.update({
                'entry_price': form_data.get('entry_price', 0),
                'stop_loss_price': form_data.get('stop_loss_price', 0),
                'has_stop_loss': bool(form_data.get('stop_loss_price'))
            })

            # Calculate stop loss metrics if both prices available
            if form_data.get('entry_price') and form_data.get('stop_loss_price'):
                try:
                    entry = Decimal(str(form_data['entry_price']))
                    stop = Decimal(str(form_data['stop_loss_price']))
                    base_summary['stop_loss_distance'] = float(abs(entry - stop))
                    base_summary['stop_loss_percentage'] = float((abs(entry - stop) / entry) * 100)
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        return base_summary

    def handle_level_based_method_change(self) -> None:
        """Handle switching to level-based risk method."""
        # Clear any previous calculation results
        self._clear_calculation_result()

        # Update required fields
        self._update_validation_status()

        # Update button state
        self._update_button_state()

        # Emit signal if view needs to update UI
        if hasattr(self.view, 'level_based_method_selected'):
            self.view.level_based_method_selected.emit()

    def handle_stop_loss_field_change(self, field_name: str, value: str) -> None:
        """
        Handle changes to stop loss related fields.

        Args:
            field_name: Name of the field that changed
            value: New field value
        """
        # Update internal trade object
        self.update_trade_object()

        # Perform stop loss validation
        if field_name in ['entry_price', 'stop_loss_price']:
            form_data = self.get_current_trade_data()
            errors = self.validate_stop_loss_constraints(form_data)

            # Show validation errors
            if errors and hasattr(self.view, 'show_field_error'):
                for error in errors:
                    self.view.show_field_error(field_name, error)
            elif hasattr(self.view, 'clear_field_error'):
                self.view.clear_field_error(field_name)

        # Update validation status
        self._update_validation_status()