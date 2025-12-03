"""Unit tests for Pydantic response models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from mcp_finnhub.api.models import (
    CandleResponse,
    CompanyProfile,
    MarketStatusResponse,
    NewsArticle,
    QuoteResponse,
    Resolution,
    SymbolLookupResult,
)


class TestQuoteResponse:
    """Tests for QuoteResponse model."""

    def test_valid_quote(self):
        """Test creating a valid quote response."""
        data = {
            "c": 150.0,
            "d": 2.5,
            "dp": 1.69,
            "h": 151.0,
            "l": 149.0,
            "o": 149.5,
            "pc": 147.5,
            "t": 1609459200,  # 2021-01-01 00:00:00
        }
        quote = QuoteResponse(**data)
        assert quote.c == 150.0
        assert quote.d == 2.5
        assert quote.t == 1609459200

    def test_timestamp_conversion(self):
        """Test timestamp to datetime conversion."""
        data = {
            "c": 150.0,
            "d": 2.5,
            "dp": 1.69,
            "h": 151.0,
            "l": 149.0,
            "o": 149.5,
            "pc": 147.5,
            "t": 1609459200,  # 2021-01-01 00:00:00 UTC
        }
        quote = QuoteResponse(**data)
        dt = quote.timestamp_dt
        assert isinstance(dt, datetime)
        # Timestamp is in UTC, so may be different year in local timezone
        assert dt.timestamp() == 1609459200

    def test_invalid_timestamp(self):
        """Test validation fails for timestamps before year 2000."""
        data = {
            "c": 150.0,
            "d": 2.5,
            "dp": 1.69,
            "h": 151.0,
            "l": 149.0,
            "o": 149.5,
            "pc": 147.5,
            "t": 900000000,  # Before 2000
        }
        with pytest.raises(ValidationError, match="after year 2000"):
            QuoteResponse(**data)


class TestCandleResponse:
    """Tests for CandleResponse model."""

    def test_valid_candle_response(self):
        """Test creating valid candle response."""
        data = {
            "c": [150.0, 151.0, 152.0],
            "h": [151.0, 152.0, 153.0],
            "l": [149.0, 150.0, 151.0],
            "o": [149.5, 150.5, 151.5],
            "s": "ok",
            "t": [1609459200, 1609545600, 1609632000],
            "v": [1000000, 1100000, 1200000],
        }
        candle = CandleResponse(**data)
        assert candle.s == "ok"
        assert len(candle) == 3
        assert candle.c == [150.0, 151.0, 152.0]

    def test_no_data_response(self):
        """Test candle response with no_data status."""
        data = {
            "c": [],
            "h": [],
            "l": [],
            "o": [],
            "s": "no_data",
            "t": [],
            "v": [],
        }
        candle = CandleResponse(**data)
        assert candle.s == "no_data"
        assert len(candle) == 0

    def test_invalid_status(self):
        """Test validation fails for invalid status."""
        data = {
            "c": [150.0],
            "h": [151.0],
            "l": [149.0],
            "o": [149.5],
            "s": "invalid",
            "t": [1609459200],
            "v": [1000000],
        }
        with pytest.raises(ValidationError, match=r"ok.*no_data"):
            CandleResponse(**data)

    def test_mismatched_array_lengths(self):
        """Test validation fails for mismatched array lengths."""
        data = {
            "c": [150.0, 151.0],
            "h": [151.0],
            "l": [149.0],
            "o": [149.5],
            "s": "ok",
            "t": [1609459200],
            "v": [1000000],
        }
        with pytest.raises(ValidationError, match="same length"):
            CandleResponse(**data)

    def test_timestamps_conversion(self):
        """Test converting Unix timestamps to datetime objects."""
        data = {
            "c": [150.0, 151.0],
            "h": [151.0, 152.0],
            "l": [149.0, 150.0],
            "o": [149.5, 150.5],
            "s": "ok",
            "t": [1609459200, 1609545600],
            "v": [1000000, 1100000],
        }
        candle = CandleResponse(**data)
        timestamps = candle.timestamps_dt
        assert len(timestamps) == 2
        assert all(isinstance(dt, datetime) for dt in timestamps)


class TestNewsArticle:
    """Tests for NewsArticle model."""

    def test_valid_news_article(self):
        """Test creating valid news article."""
        data = {
            "category": "company",
            "datetime": 1609459200,
            "headline": "Test headline",
            "id": 12345,
            "image": "https://example.com/image.jpg",
            "related": "AAPL,MSFT,GOOGL",
            "source": "Reuters",
            "summary": "Test summary",
            "url": "https://example.com/article",
        }
        article = NewsArticle(**data)
        assert article.headline == "Test headline"
        assert article.source == "Reuters"

    def test_datetime_conversion(self):
        """Test datetime conversion."""
        data = {
            "category": "company",
            "datetime": 1609459200,  # 2021-01-01 00:00:00 UTC
            "headline": "Test",
            "id": 1,
            "image": "https://example.com/image.jpg",
            "related": "AAPL",
            "source": "Reuters",
            "summary": "Test",
            "url": "https://example.com/article",
        }
        article = NewsArticle(**data)
        dt = article.datetime_dt
        assert isinstance(dt, datetime)
        # Timestamp is in UTC, so may be different year in local timezone
        assert dt.timestamp() == 1609459200

    def test_related_symbols_parsing(self):
        """Test parsing comma-separated related symbols."""
        data = {
            "category": "company",
            "datetime": 1609459200,
            "headline": "Test",
            "id": 1,
            "image": "https://example.com/image.jpg",
            "related": "AAPL, MSFT, GOOGL",
            "source": "Reuters",
            "summary": "Test",
            "url": "https://example.com/article",
        }
        article = NewsArticle(**data)
        symbols = article.related_symbols
        assert symbols == ["AAPL", "MSFT", "GOOGL"]

    def test_empty_related_symbols(self):
        """Test handling empty related symbols."""
        data = {
            "category": "company",
            "datetime": 1609459200,
            "headline": "Test",
            "id": 1,
            "image": "https://example.com/image.jpg",
            "related": "",
            "source": "Reuters",
            "summary": "Test",
            "url": "https://example.com/article",
        }
        article = NewsArticle(**data)
        assert article.related_symbols == []

    def test_invalid_datetime(self):
        """Test validation fails for invalid datetime."""
        data = {
            "category": "company",
            "datetime": 900000000,  # Before 2000
            "headline": "Test",
            "id": 1,
            "image": "https://example.com/image.jpg",
            "related": "AAPL",
            "source": "Reuters",
            "summary": "Test",
            "url": "https://example.com/article",
        }
        with pytest.raises(ValidationError, match="after year 2000"):
            NewsArticle(**data)


class TestCompanyProfile:
    """Tests for CompanyProfile model."""

    def test_valid_company_profile(self):
        """Test creating valid company profile."""
        data = {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "ipo": "1980-12-12",
            "marketCapitalization": 2500000.0,
            "name": "Apple Inc.",
            "phone": "+1-408-996-1010",
            "shareOutstanding": 16000.0,
            "ticker": "AAPL",
            "weburl": "https://www.apple.com",
            "logo": "https://example.com/logo.png",
            "finnhubIndustry": "Technology",
        }
        profile = CompanyProfile(**data)
        assert profile.name == "Apple Inc."
        assert profile.ticker == "AAPL"
        assert profile.marketCapitalization == 2500000.0

    def test_invalid_ipo_date(self):
        """Test validation fails for invalid IPO date format."""
        data = {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "ipo": "12/12/1980",  # Wrong format
            "marketCapitalization": 2500000.0,
            "name": "Apple Inc.",
            "phone": "+1-408-996-1010",
            "shareOutstanding": 16000.0,
            "ticker": "AAPL",
            "weburl": "https://www.apple.com",
            "logo": "https://example.com/logo.png",
            "finnhubIndustry": "Technology",
        }
        with pytest.raises(ValidationError, match="YYYY-MM-DD"):
            CompanyProfile(**data)

    def test_negative_market_cap(self):
        """Test validation fails for negative market cap."""
        data = {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "ipo": "1980-12-12",
            "marketCapitalization": -1000.0,
            "name": "Apple Inc.",
            "phone": "+1-408-996-1010",
            "shareOutstanding": 16000.0,
            "ticker": "AAPL",
            "weburl": "https://www.apple.com",
            "logo": "https://example.com/logo.png",
            "finnhubIndustry": "Technology",
        }
        with pytest.raises(ValidationError, match="non-negative"):
            CompanyProfile(**data)


class TestSymbolLookupResult:
    """Tests for SymbolLookupResult model."""

    def test_valid_symbol_lookup(self):
        """Test creating valid symbol lookup result."""
        data = {
            "description": "Apple Inc.",
            "displaySymbol": "AAPL",
            "symbol": "AAPL",
            "type": "Common Stock",
        }
        result = SymbolLookupResult(**data)
        assert result.description == "Apple Inc."
        assert result.symbol == "AAPL"


class TestMarketStatusResponse:
    """Tests for MarketStatusResponse model."""

    def test_valid_market_status(self):
        """Test creating valid market status."""
        data = {
            "exchange": "NASDAQ",
            "holiday": None,
            "isOpen": True,
            "session": "regular",
            "timezone": "America/New_York",
            "t": 1609459200,
        }
        status = MarketStatusResponse(**data)
        assert status.exchange == "NASDAQ"
        assert status.isOpen is True
        assert status.session == "regular"

    def test_market_closed_with_holiday(self):
        """Test market status when closed for holiday."""
        data = {
            "exchange": "NYSE",
            "holiday": "New Year's Day",
            "isOpen": False,
            "session": "closed",
            "timezone": "America/New_York",
            "t": 1609459200,
        }
        status = MarketStatusResponse(**data)
        assert status.isOpen is False
        assert status.holiday == "New Year's Day"

    def test_invalid_session(self):
        """Test validation fails for invalid session."""
        data = {
            "exchange": "NASDAQ",
            "holiday": None,
            "isOpen": True,
            "session": "invalid-session",
            "timezone": "America/New_York",
            "t": 1609459200,
        }
        with pytest.raises(ValidationError, match="Session must be one of"):
            MarketStatusResponse(**data)


class TestResolution:
    """Tests for Resolution enum."""

    def test_valid_resolutions(self):
        """Test all valid resolution values."""
        assert Resolution.ONE_MIN == "1"
        assert Resolution.FIVE_MIN == "5"
        assert Resolution.FIFTEEN_MIN == "15"
        assert Resolution.THIRTY_MIN == "30"
        assert Resolution.SIXTY_MIN == "60"
        assert Resolution.DAY == "D"
        assert Resolution.WEEK == "W"
        assert Resolution.MONTH == "M"
