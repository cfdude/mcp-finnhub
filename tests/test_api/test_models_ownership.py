"""Tests for ownership Pydantic models."""

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.ownership import (
    CongressionalTrade,
    CongressionalTrading,
    InsiderTransactionData,
    InsiderTransactions,
    InstitutionalOwnership,
    InstitutionalOwnershipPosition,
    InstitutionalPortfolio,
    PortfolioHolding,
)


class TestInsiderTransactionData:
    """Test InsiderTransactionData model."""

    def test_valid_insider_transaction(self):
        """Test creating valid insider transaction."""
        data = {
            "name": "John Doe",
            "share": 100000,
            "change": -5000,
            "filingDate": "2024-01-15",
            "transactionDate": "2024-01-10",
            "transactionCode": "S",
            "transactionPrice": 150.25,
        }
        model = InsiderTransactionData(**data)
        assert model.name == "John Doe"
        assert model.change == -5000
        assert model.is_sale

    def test_is_purchase_property(self):
        """Test is_purchase property."""
        purchase = InsiderTransactionData(name="Jane Doe", change=1000)
        assert purchase.is_purchase
        assert not purchase.is_sale

    def test_transaction_value_property(self):
        """Test transaction_value property."""
        model = InsiderTransactionData(name="John Doe", change=-5000, transactionPrice=150.25)
        assert model.transaction_value == 751250.0


class TestInsiderTransactions:
    """Test InsiderTransactions model."""

    def test_valid_insider_transactions(self):
        """Test creating valid insider transactions response."""
        data = {
            "data": [
                {
                    "name": "John Doe",
                    "share": 100000,
                    "change": -5000,
                }
            ],
            "symbol": "AAPL",
        }
        model = InsiderTransactions(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 1


class TestInstitutionalOwnershipPosition:
    """Test InstitutionalOwnershipPosition model."""

    def test_valid_position(self):
        """Test creating valid institutional position."""
        data = {
            "change": 1000,
            "cik": "1234567",
            "name": "Test Fund",
            "share": 50000,
            "soleVoting": 40000,
            "sharedVoting": 10000,
            "value": 7500000,
        }
        model = InstitutionalOwnershipPosition(**data)
        assert model.name == "Test Fund"
        assert model.total_voting_shares == 50000

    def test_invalid_negative_shares(self):
        """Test validation fails for negative shares."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            InstitutionalOwnershipPosition(
                name="Test Fund",
                share=-1000,
            )

    def test_invalid_percentage_too_high(self):
        """Test validation fails for percentage > 100."""
        with pytest.raises(ValidationError, match="less than or equal to"):
            InstitutionalOwnershipPosition(
                name="Test Fund",
                percentage=150.0,
            )


class TestInstitutionalOwnership:
    """Test InstitutionalOwnership model."""

    def test_valid_institutional_ownership(self):
        """Test creating valid institutional ownership."""
        data = {
            "cusip": "037833100",
            "data": [
                {
                    "reportDate": "2024-03-31",
                    "ownership": [
                        {
                            "name": "Test Fund",
                            "share": 50000,
                        }
                    ],
                }
            ],
            "symbol": "AAPL",
        }
        model = InstitutionalOwnership(**data)
        assert model.symbol == "AAPL"
        assert model.cusip == "037833100"


class TestPortfolioHolding:
    """Test PortfolioHolding model."""

    def test_valid_portfolio_holding(self):
        """Test creating valid portfolio holding."""
        data = {
            "symbol": "AAPL",
            "name": "Apple Inc",
            "share": 100000,
            "value": 15000000,
            "percentage": 5.5,
        }
        model = PortfolioHolding(**data)
        assert model.symbol == "AAPL"
        assert model.percentage == 5.5


class TestInstitutionalPortfolio:
    """Test InstitutionalPortfolio model."""

    def test_valid_institutional_portfolio(self):
        """Test creating valid institutional portfolio."""
        data = {
            "cik": "1000097",
            "name": "Test Investment Fund",
            "data": [
                {
                    "filingDate": "2024-03-31",
                    "reportDate": "2024-03-31",
                    "portfolio": [
                        {
                            "symbol": "AAPL",
                            "name": "Apple Inc",
                        }
                    ],
                }
            ],
        }
        model = InstitutionalPortfolio(**data)
        assert model.cik == "1000097"
        assert model.name == "Test Investment Fund"


class TestCongressionalTrade:
    """Test CongressionalTrade model."""

    def test_valid_congressional_trade(self):
        """Test creating valid congressional trade."""
        data = {
            "amountFrom": 1001,
            "amountTo": 15000,
            "assetName": "Apple Inc",
            "filingDate": "2024-01-15",
            "name": "Senator Smith",
            "position": "senator",
            "symbol": "AAPL",
            "transactionDate": "2024-01-10",
            "transactionType": "Purchase",
        }
        model = CongressionalTrade(**data)
        assert model.name == "Senator Smith"
        assert model.is_purchase
        assert not model.is_sale

    def test_is_sale_property(self):
        """Test is_sale property."""
        sale = CongressionalTrade(name="Representative Jones", transactionType="Sale")
        assert sale.is_sale
        assert not sale.is_purchase

    def test_estimated_value_property(self):
        """Test estimated_value property."""
        model = CongressionalTrade(name="Senator Smith", amountFrom=10000, amountTo=50000)
        assert model.estimated_value == 30000.0

    def test_invalid_negative_amount(self):
        """Test validation fails for negative amount."""
        with pytest.raises(ValidationError, match="greater than or equal to"):
            CongressionalTrade(
                name="Senator Smith",
                amountFrom=-1000,
            )


class TestCongressionalTrading:
    """Test CongressionalTrading model."""

    def test_valid_congressional_trading(self):
        """Test creating valid congressional trading response."""
        data = {
            "data": [
                {
                    "name": "Senator Smith",
                    "symbol": "AAPL",
                    "transactionType": "Purchase",
                }
            ],
            "symbol": "AAPL",
        }
        model = CongressionalTrading(**data)
        assert model.symbol == "AAPL"
        assert len(model.data) == 1
