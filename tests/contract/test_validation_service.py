import pytest
from decimal import Decimal
from risk_calculator.models.equity_trade import EquityTrade
from risk_calculator.models.option_trade import OptionTrade
from risk_calculator.models.future_trade import FutureTrade
from risk_calculator.models.risk_method import RiskMethod
from risk_calculator.models.validation_result import ValidationResult
from risk_calculator.services.validators import TradeValidationService


class TestTradeValidationServiceContract:
    """Contract tests for TradeValidationService - these must fail initially"""

    def setup_method(self):
        self.service = TradeValidationService()

    def test_validate_equity_trade_percentage_method_valid(self):
        """Test valid equity trade with percentage method"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('150')
        trade.stop_loss_price = Decimal('145')
        trade.symbol = "AAPL"
        trade.trade_direction = "LONG"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.error_messages) == 0
        assert len(result.field_errors) == 0

    def test_validate_equity_trade_fixed_amount_method_valid(self):
        """Test valid equity trade with fixed amount method"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.FIXED_AMOUNT
        trade.fixed_risk_amount = Decimal('200')  # Within 5% of account
        trade.entry_price = Decimal('100')
        trade.stop_loss_price = Decimal('95')
        trade.symbol = "AAPL"
        trade.trade_direction = "LONG"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert result.is_valid is True

    def test_validate_equity_trade_level_based_method_valid(self):
        """Test valid equity trade with level-based method"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.LEVEL_BASED
        trade.entry_price = Decimal('50')
        trade.support_resistance_level = Decimal('47')
        trade.symbol = "AAPL"
        trade.trade_direction = "LONG"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert result.is_valid is True

    def test_validate_equity_trade_invalid_risk_percentage(self):
        """Test invalid risk percentage (outside 1-5% range)"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('6.0')  # Too high
        trade.entry_price = Decimal('150')
        trade.stop_loss_price = Decimal('145')
        trade.symbol = "AAPL"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert result.is_valid is False
        assert "risk_percentage" in result.field_errors
        assert "1% and 5%" in result.field_errors["risk_percentage"]

    def test_validate_equity_trade_invalid_stop_loss_direction(self):
        """Test invalid stop loss direction for long position"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('150')
        trade.stop_loss_price = Decimal('155')  # Above entry for long position
        trade.symbol = "AAPL"
        trade.trade_direction = "LONG"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert result.is_valid is False
        assert "stop_loss_price" in result.field_errors
        assert "below entry price" in result.field_errors["stop_loss_price"]

    def test_validate_equity_trade_fixed_amount_exceeds_account_limit(self):
        """Test fixed amount exceeding 5% of account size"""
        # Given
        trade = EquityTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.FIXED_AMOUNT
        trade.fixed_risk_amount = Decimal('600')  # 6% of account
        trade.entry_price = Decimal('100')
        trade.stop_loss_price = Decimal('95')
        trade.symbol = "AAPL"

        # When
        result = self.service.validate_equity_trade(trade)

        # Then
        assert result.is_valid is False
        assert "fixed_risk_amount" in result.field_errors
        assert "5% of account size" in result.field_errors["fixed_risk_amount"]


class TestOptionValidationContract:
    """Contract tests for option validation"""

    def setup_method(self):
        self.service = TradeValidationService()

    def test_validate_option_trade_percentage_method_valid(self):
        """Test valid option trade with percentage method"""
        # Given
        trade = OptionTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('3.0')
        trade.premium = Decimal('2.50')
        trade.contract_multiplier = 100
        trade.option_symbol = "AAPL230120C00150000"

        # When
        result = self.service.validate_option_trade(trade)

        # Then
        assert result.is_valid is True

    def test_validate_option_trade_level_based_not_supported(self):
        """Test that level-based method is rejected for options"""
        # Given
        trade = OptionTrade()
        trade.account_size = Decimal('10000')
        trade.risk_method = RiskMethod.LEVEL_BASED
        trade.premium = Decimal('2.50')
        trade.option_symbol = "AAPL230120C00150000"

        # When
        result = self.service.validate_option_trade(trade)

        # Then
        assert result.is_valid is False
        assert "risk_method" in result.field_errors
        assert "not supported for options" in result.field_errors["risk_method"]


class TestFutureValidationContract:
    """Contract tests for futures validation"""

    def setup_method(self):
        self.service = TradeValidationService()

    def test_validate_future_trade_all_methods_supported(self):
        """Test that all three risk methods are supported for futures"""
        # Given - percentage method
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
        result = self.service.validate_future_trade(trade)

        # Then
        assert result.is_valid is True

    def test_validate_future_trade_margin_exceeds_account(self):
        """Test validation when margin requirement exceeds account size"""
        # Given
        trade = FutureTrade()
        trade.account_size = Decimal('1000')  # Small account
        trade.risk_method = RiskMethod.PERCENTAGE
        trade.risk_percentage = Decimal('2.0')
        trade.entry_price = Decimal('4000')
        trade.stop_loss_price = Decimal('3980')
        trade.tick_value = Decimal('12.50')
        trade.tick_size = Decimal('0.25')
        trade.margin_requirement = Decimal('4000')  # Exceeds account
        trade.contract_symbol = "ESH23"

        # When
        result = self.service.validate_future_trade(trade)

        # Then
        assert result.is_valid is False
        assert "margin_requirement" in result.field_errors
        assert "exceeds account size" in result.field_errors["margin_requirement"]