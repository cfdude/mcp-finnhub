"""Tests for news and sentiment Pydantic models."""

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models.news import (
    InsiderSentimentResponse,
    InsiderTransaction,
    NewsSentimentResponse,
    SentimentBuzz,
    SentimentScore,
)


class TestSentimentScore:
    """Tests for SentimentScore model."""

    def test_valid_sentiment_score(self):
        """Test creating valid sentiment score."""
        data = {
            "bearishPercent": 0.25,
            "bullishPercent": 0.75,
        }
        score = SentimentScore(**data)
        assert score.bearishPercent == 0.25
        assert score.bullishPercent == 0.75

    def test_is_bullish_property_true(self):
        """Test is_bullish property returns True."""
        score = SentimentScore(bearishPercent=0.25, bullishPercent=0.75)
        assert score.is_bullish is True

    def test_is_bullish_property_false(self):
        """Test is_bullish property returns False."""
        score = SentimentScore(bearishPercent=0.75, bullishPercent=0.25)
        assert score.is_bullish is False

    def test_sentiment_spread_property(self):
        """Test sentiment_spread property calculates correctly."""
        score = SentimentScore(bearishPercent=0.25, bullishPercent=0.75)
        assert score.sentiment_spread == 0.5


class TestSentimentBuzz:
    """Tests for SentimentBuzz model."""

    def test_valid_sentiment_buzz(self):
        """Test creating valid sentiment buzz."""
        data = {
            "articlesInLastWeek": 100,
            "weeklyAverage": 75.0,
            "buzz": 1.33,
        }
        buzz = SentimentBuzz(**data)
        assert buzz.articlesInLastWeek == 100
        assert buzz.weeklyAverage == 75.0
        assert buzz.buzz == 1.33

    def test_is_high_buzz_property_true(self):
        """Test is_high_buzz property returns True."""
        buzz = SentimentBuzz(articlesInLastWeek=100, weeklyAverage=75.0, buzz=1.33)
        assert buzz.is_high_buzz is True

    def test_is_high_buzz_property_false(self):
        """Test is_high_buzz property returns False."""
        buzz = SentimentBuzz(articlesInLastWeek=50, weeklyAverage=75.0, buzz=0.67)
        assert buzz.is_high_buzz is False


class TestNewsSentimentResponse:
    """Tests for NewsSentimentResponse model."""

    def test_valid_news_sentiment_response(self):
        """Test creating valid news sentiment response."""
        data = {
            "symbol": "AAPL",
            "companyNewsScore": 0.75,
            "sectorAverageBullishPercent": 0.60,
            "sectorAverageNewsScore": 0.65,
            "sentiment": {
                "bearishPercent": 0.25,
                "bullishPercent": 0.75,
            },
            "buzz": {
                "articlesInLastWeek": 100,
                "weeklyAverage": 75.0,
                "buzz": 1.33,
            },
        }
        response = NewsSentimentResponse(**data)
        assert response.symbol == "AAPL"
        assert response.companyNewsScore == 0.75

    def test_invalid_score_too_low(self):
        """Test validation fails for score below 0."""
        with pytest.raises(ValidationError, match="between 0 and 1"):
            NewsSentimentResponse(
                symbol="AAPL",
                companyNewsScore=-0.1,
                sectorAverageBullishPercent=0.60,
                sectorAverageNewsScore=0.65,
                sentiment={"bearishPercent": 0.25, "bullishPercent": 0.75},
                buzz={"articlesInLastWeek": 100, "weeklyAverage": 75.0, "buzz": 1.33},
            )

    def test_invalid_score_too_high(self):
        """Test validation fails for score above 1."""
        with pytest.raises(ValidationError, match="between 0 and 1"):
            NewsSentimentResponse(
                symbol="AAPL",
                companyNewsScore=1.5,
                sectorAverageBullishPercent=0.60,
                sectorAverageNewsScore=0.65,
                sentiment={"bearishPercent": 0.25, "bullishPercent": 0.75},
                buzz={"articlesInLastWeek": 100, "weeklyAverage": 75.0, "buzz": 1.33},
            )

    def test_outperforms_sector_property_true(self):
        """Test outperforms_sector property returns True."""
        response = NewsSentimentResponse(
            symbol="AAPL",
            companyNewsScore=0.75,
            sectorAverageBullishPercent=0.60,
            sectorAverageNewsScore=0.65,
            sentiment={"bearishPercent": 0.25, "bullishPercent": 0.75},
            buzz={"articlesInLastWeek": 100, "weeklyAverage": 75.0, "buzz": 1.33},
        )
        assert response.outperforms_sector is True

    def test_outperforms_sector_property_false(self):
        """Test outperforms_sector property returns False."""
        response = NewsSentimentResponse(
            symbol="AAPL",
            companyNewsScore=0.60,
            sectorAverageBullishPercent=0.60,
            sectorAverageNewsScore=0.75,
            sentiment={"bearishPercent": 0.40, "bullishPercent": 0.60},
            buzz={"articlesInLastWeek": 100, "weeklyAverage": 75.0, "buzz": 1.33},
        )
        assert response.outperforms_sector is False


class TestInsiderTransaction:
    """Tests for InsiderTransaction model."""

    def test_valid_insider_transaction(self):
        """Test creating valid insider transaction."""
        data = {
            "year": 2023,
            "month": 12,
            "change": 5000,
            "mspr": 0.65,
        }
        transaction = InsiderTransaction(**data)
        assert transaction.year == 2023
        assert transaction.month == 12
        assert transaction.change == 5000

    def test_invalid_month_too_low(self):
        """Test validation fails for month below 1."""
        with pytest.raises(ValidationError, match="between 1 and 12"):
            InsiderTransaction(
                year=2023,
                month=0,
                change=5000,
                mspr=0.65,
            )

    def test_invalid_month_too_high(self):
        """Test validation fails for month above 12."""
        with pytest.raises(ValidationError, match="between 1 and 12"):
            InsiderTransaction(
                year=2023,
                month=13,
                change=5000,
                mspr=0.65,
            )

    def test_invalid_year(self):
        """Test validation fails for invalid year."""
        with pytest.raises(ValidationError, match="between 1900 and 2100"):
            InsiderTransaction(
                year=1800,
                month=12,
                change=5000,
                mspr=0.65,
            )

    def test_is_buying_property_true(self):
        """Test is_buying property returns True."""
        transaction = InsiderTransaction(year=2023, month=12, change=5000, mspr=0.65)
        assert transaction.is_buying is True

    def test_is_buying_property_false(self):
        """Test is_buying property returns False."""
        transaction = InsiderTransaction(year=2023, month=12, change=-5000, mspr=0.65)
        assert transaction.is_buying is False

    def test_is_selling_property_true(self):
        """Test is_selling property returns True."""
        transaction = InsiderTransaction(year=2023, month=12, change=-5000, mspr=0.65)
        assert transaction.is_selling is True

    def test_is_selling_property_false(self):
        """Test is_selling property returns False."""
        transaction = InsiderTransaction(year=2023, month=12, change=5000, mspr=0.65)
        assert transaction.is_selling is False


class TestInsiderSentimentResponse:
    """Tests for InsiderSentimentResponse model."""

    def test_valid_insider_sentiment_response(self):
        """Test creating valid insider sentiment response."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -2000, "mspr": 0.45},
                {"year": 2023, "month": 10, "change": 3000, "mspr": 0.55},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.symbol == "AAPL"
        assert len(response.data) == 3

    def test_latest_month_property(self):
        """Test latest_month property returns first item."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -2000, "mspr": 0.45},
            ],
        }
        response = InsiderSentimentResponse(**data)
        latest = response.latest_month
        assert latest is not None
        assert latest.month == 12

    def test_net_buying_months_property(self):
        """Test net_buying_months property counts correctly."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -2000, "mspr": 0.45},
                {"year": 2023, "month": 10, "change": 3000, "mspr": 0.55},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.net_buying_months == 2

    def test_net_selling_months_property(self):
        """Test net_selling_months property counts correctly."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -2000, "mspr": 0.45},
                {"year": 2023, "month": 10, "change": -3000, "mspr": 0.55},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.net_selling_months == 2

    def test_overall_sentiment_bullish(self):
        """Test overall_sentiment property returns bullish."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": 3000, "mspr": 0.55},
                {"year": 2023, "month": 10, "change": -1000, "mspr": 0.45},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.overall_sentiment == "bullish"

    def test_overall_sentiment_bearish(self):
        """Test overall_sentiment property returns bearish."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": -5000, "mspr": 0.35},
                {"year": 2023, "month": 11, "change": -3000, "mspr": 0.45},
                {"year": 2023, "month": 10, "change": 1000, "mspr": 0.55},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.overall_sentiment == "bearish"

    def test_overall_sentiment_neutral(self):
        """Test overall_sentiment property returns neutral."""
        data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -3000, "mspr": 0.45},
            ],
        }
        response = InsiderSentimentResponse(**data)
        assert response.overall_sentiment == "neutral"
