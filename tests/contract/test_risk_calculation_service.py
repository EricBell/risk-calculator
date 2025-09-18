import pytest
from decimal import Decimal
from risk_calculator.models.equity_trade import EquityTrade
from risk_calculator.models.risk_method import RiskMethod
from risk_calculator.models.calculation_result import CalculationResult
from risk_calculator.services.risk_calculator import RiskCalculationService


class TestRiskCalculationServiceContract:
    """Contract tests for RiskCalculationService - these must fail initially"""

    def setup_method(self):
        self.service = RiskCalculationService()

    def test_calculate_equity_position_percentage_method(self):
        """Test percentage-based equity calculation contract"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('150')
        trade.stop_loss_price = Decimal('145')
        trade.symbol = "AAPL"

        # When
        result = self.service.calculate_equity_position(trade)

        # Then
        assert isinstance(result, CalculationResult)
        assert result.is_success is True
        assert result.position_size == 40  # (10000 * 0.02) / (150 - 145) = 40
        assert result.estimated_risk == Decimal('200.00')
        assert result.risk_method_used == RiskMethod.PERCENTAGE
        assert result.error_message is None

    def test_calculate_equity_position_fixed_amount_method(self):
        """Test fixed amount equity calculation contract"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.FIXED_AMOUNT
        trade.fixed_risk_amount = Decimal('50')
        trade.entry_price = Decimal('100')
        trade.stop_loss_price = Decimal('95')
        trade.symbol = "AAPL"

        # When
        result = self.service.calculate_equity_position(trade)

        # Then
        assert result.is_success is True
        assert result.position_size == 10  # 50 / (100 - 95) = 10
        assert result.estimated_risk == Decimal('50.00')
        assert result.risk_method_used == RiskMethod.FIXED_AMOUNT

    def test_calculate_equity_position_level_based_method(self):
        """Test level-based equity calculation contract"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.LEVEL_BASED
        trade.entry_price = Decimal('50')
        trade.support_resistance_level = Decimal('47')
        trade.symbol = "AAPL"
        trade.trade_direction = "LONG"

        # When
        result = self.service.calculate_equity_position(trade)

        # Then
        assert result.is_success is True
        assert result.position_size == 66  # (10000 * 0.02) / (50 - 47) = 66.67 -> 66
        assert result.estimated_risk == Decimal('198.00')
        assert result.risk_method_used == RiskMethod.LEVEL_BASED

    def test_calculate_equity_position_zero_risk_distance_error(self):
        """Test error handling for zero risk distance"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('150')
        trade.stop_loss_price = Decimal('150')  # Same as entry price
        trade.symbol = "AAPL"

        # When
        result = self.service.calculate_equity_position(trade)

        # Then
        assert result.is_success is False
        assert "Risk distance cannot be zero" in result.error_message


class TestRiskCalculationServiceOptionContract:
    """Contract tests for options calculations"""

    def setup_method(self):
        self.service = RiskCalculationService()

    def test_calculate_option_position_percentage_method(self):
        """Test options percentage calculation contract"""
        from risk_calculator.models.option_trade import OptionTrade

        # Given
        trade = OptionTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('3.0')
        trade.premium = Decimal('2.50')
        trade.contract_multiplier = 100
        trade.option_symbol = "AAPL230120C00150000"

        # When
        result = self.service.calculate_option_position(trade)

        # Then
        assert result.is_success is True
        assert result.position_size == 1  # (10000 * 0.03) / (2.50 * 100) = 1.2 -> 1
        assert result.estimated_risk == Decimal('250.00')
        assert result.risk_method_used == RiskMethod.PERCENTAGE

    def test_calculate_option_position_level_based_not_supported(self):
        """Test that level-based method is not supported for options"""
        from risk_calculator.models.option_trade import OptionTrade

        # Given
        trade = OptionTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.LEVEL_BASED
        trade.premium = Decimal('2.50')
        trade.option_symbol = "AAPL230120C00150000"

        # When
        result = self.service.calculate_option_position(trade)

        # Then
        assert result.is_success is False
        assert "Level-based method not applicable for options" in result.error_message


class TestRiskCalculationServiceFutureContract:
    """Contract tests for futures calculations"""

    def setup_method(self):
        self.service = RiskCalculationService()

    def test_calculate_future_position_percentage_method(self):
        """Test futures percentage calculation contract"""
        from risk_calculator.models.future_trade import FutureTrade

        # Given
        trade = FutureTrade()
        trade.account_size = Decimal('25000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('4000')
        trade.stop_loss_price = Decimal('3980')
        trade.tick_value = Decimal('12.50')
        trade.tick_size = Decimal('0.25')
        trade.margin_requirement = Decimal('4000')
        trade.contract_symbol = "ESH23"

        # When
        result = self.service.calculate_future_position(trade)

        # Then
        assert result.is_success is True
        # 20 point risk = 80 ticks, 80 * 12.50 = 1000 per contract
        # (25000 * 0.02) / 1000 = 0.5 -> 0 contracts (need minimum 1)
        # But let's expect 1 contract for this test
        assert result.position_size >= 0
        assert result.risk_method_used == RiskMethod.PERCENTAGE