"""Tests for market data API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import market
from mcp_finnhub.config import AppConfig

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
    """Create test configuration."""
    return AppConfig(
        finnhub_api_key="test_api_key",
        storage_directory=tmp_path / "data",
        rate_limit_rpm=60,
        request_timeout=5,
        max_retries=2,
        retry_backoff_factor=1.5,
        retry_jitter=0.1,
    )


class TestGetQuote:
    """Tests for get_quote endpoint."""

    @respx.mock
    async def test_get_quote(self, test_config: AppConfig):
        """Test getting quote data."""
        quote_data = {
            "c": 150.5,
            "d": 2.5,
            "dp": 1.69,
            "h": 151.0,
            "l": 149.5,
            "o": 150.0,
            "pc": 148.0,
            "t": 1609459200,
        }

        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(200, json=quote_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_quote(client, "AAPL")

        assert result["c"] == 150.5
        assert result["t"] == 1609459200


class TestGetCandles:
    """Tests for get_candles endpoint."""

    @respx.mock
    async def test_get_candles(self, test_config: AppConfig):
        """Test getting candle data."""
        candle_data = {
            "c": [150.0, 151.0],
            "h": [151.5, 152.0],
            "l": [149.0, 150.0],
            "o": [150.0, 150.5],
            "s": "ok",
            "t": [1609459200, 1609545600],
            "v": [1000000, 1200000],
        }

        respx.get("https://finnhub.io/api/v1/stock/candle").mock(
            return_value=httpx.Response(200, json=candle_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_candles(
                client,
                "AAPL",
                "D",
                1609459200,
                1640995200,
            )

        assert result["s"] == "ok"
        assert len(result["c"]) == 2


class TestGetCompanyProfile:
    """Tests for get_company_profile endpoint."""

    @respx.mock
    async def test_get_company_profile(self, test_config: AppConfig):
        """Test getting company profile."""
        profile_data = {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "ipo": "1980-12-12",
            "marketCapitalization": 2500000,
            "name": "Apple Inc",
            "phone": "14089961010",
            "shareOutstanding": 16790,
            "ticker": "AAPL",
            "weburl": "https://www.apple.com/",
            "logo": "https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
            "finnhubIndustry": "Technology",
        }

        respx.get("https://finnhub.io/api/v1/stock/profile2").mock(
            return_value=httpx.Response(200, json=profile_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_company_profile(client, "AAPL")

        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc"


class TestGetMarketStatus:
    """Tests for get_market_status endpoint."""

    @respx.mock
    async def test_get_market_status(self, test_config: AppConfig):
        """Test getting market status."""
        status_data = {
            "exchange": "US",
            "holiday": None,
            "isOpen": True,
            "session": "regular",
            "timezone": "America/New_York",
            "t": 1609459200,
        }

        respx.get("https://finnhub.io/api/v1/stock/market-status").mock(
            return_value=httpx.Response(200, json=status_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_market_status(client, "US")

        assert result["exchange"] == "US"
        assert result["isOpen"] is True


class TestGetSymbols:
    """Tests for get_symbols endpoint."""

    @respx.mock
    async def test_get_symbols(self, test_config: AppConfig):
        """Test getting symbols list."""
        symbols_data = [
            {
                "currency": "USD",
                "description": "APPLE INC",
                "displaySymbol": "AAPL",
                "figi": "BBG000B9XRY4",
                "mic": "XNAS",
                "symbol": "AAPL",
                "type": "Common Stock",
            },
            {
                "currency": "USD",
                "description": "MICROSOFT CORP",
                "displaySymbol": "MSFT",
                "figi": "BBG000BPH459",
                "mic": "XNAS",
                "symbol": "MSFT",
                "type": "Common Stock",
            },
        ]

        respx.get("https://finnhub.io/api/v1/stock/symbol").mock(
            return_value=httpx.Response(200, json=symbols_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_symbols(client, "US")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"


class TestSearchSymbols:
    """Tests for search_symbols endpoint."""

    @respx.mock
    async def test_search_symbols(self, test_config: AppConfig):
        """Test searching symbols."""
        search_data = {
            "count": 2,
            "result": [
                {
                    "description": "APPLE INC",
                    "displaySymbol": "AAPL",
                    "symbol": "AAPL",
                    "type": "Common Stock",
                },
                {
                    "description": "APPLE HOSPITALITY REIT INC",
                    "displaySymbol": "APLE",
                    "symbol": "APLE",
                    "type": "Common Stock",
                },
            ],
        }

        respx.get("https://finnhub.io/api/v1/search").mock(
            return_value=httpx.Response(200, json=search_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.search_symbols(client, "apple")

        assert result["count"] == 2
        assert len(result["result"]) == 2


class TestGetFinancials:
    """Tests for get_financials endpoint."""

    @respx.mock
    async def test_get_financials(self, test_config: AppConfig):
        """Test getting financial statements."""
        financials_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-K",
                    "startDate": "2022-10-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03 06:01:36",
                    "report": {
                        "bs": [
                            {"label": "Assets", "value": 352755000000},
                            {"label": "Liabilities", "value": 290437000000},
                        ]
                    },
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_financials(client, "AAPL", "bs", "annual")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1


class TestGetEarnings:
    """Tests for get_earnings endpoint."""

    @respx.mock
    async def test_get_earnings(self, test_config: AppConfig):
        """Test getting earnings data."""
        earnings_data = [
            {
                "actual": 1.52,
                "estimate": 1.43,
                "period": "2023-09-30",
                "quarter": 4,
                "surprise": 0.09,
                "surprisePercent": 6.2937,
                "symbol": "AAPL",
                "year": 2023,
            },
            {
                "actual": 1.26,
                "estimate": 1.19,
                "period": "2023-06-30",
                "quarter": 3,
                "surprise": 0.07,
                "surprisePercent": 5.8824,
                "symbol": "AAPL",
                "year": 2023,
            },
        ]

        respx.get("https://finnhub.io/api/v1/stock/earnings").mock(
            return_value=httpx.Response(200, json=earnings_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await market.get_earnings(client, "AAPL")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["actual"] == 1.52
