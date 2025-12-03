"""Integration tests for StockMarketDataTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.stock_market_data import StockMarketDataTool

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


class TestStockMarketDataToolValidation:
    """Tests for validation methods."""

    def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validation passes for valid operations."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        # Should not raise
        for op in [
            "get_quote",
            "get_candles",
            "get_company_profile",
            "get_market_status",
            "get_symbols",
            "search_symbols",
            "get_financials",
            "get_earnings",
        ]:
            tool.validate_operation(op)

    def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        with pytest.raises(ValueError, match="Invalid operation"):
            tool.validate_operation("invalid_operation")

    def test_validate_resolution_valid(self, test_config: AppConfig):
        """Test validation passes for valid resolutions."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        for resolution in ["1", "5", "15", "30", "60", "D", "W", "M"]:
            tool.validate_resolution(resolution)

    def test_validate_resolution_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid resolution."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        with pytest.raises(ValueError, match="Invalid resolution"):
            tool.validate_resolution("2H")

    def test_validate_statement_valid(self, test_config: AppConfig):
        """Test validation passes for valid statements."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        for statement in ["bs", "ic", "cf"]:
            tool.validate_statement(statement)

    def test_validate_statement_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid statement."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        with pytest.raises(ValueError, match="Invalid statement"):
            tool.validate_statement("invalid")

    def test_validate_frequency_valid(self, test_config: AppConfig):
        """Test validation passes for valid frequencies."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        for freq in ["annual", "quarterly"]:
            tool.validate_frequency(freq)

    def test_validate_frequency_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid frequency."""
        client = FinnhubClient(test_config)
        tool = StockMarketDataTool(client)

        with pytest.raises(ValueError, match="Invalid frequency"):
            tool.validate_frequency("monthly")


class TestStockMarketDataToolGetQuote:
    """Tests for get_quote operation."""

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
            tool = StockMarketDataTool(client)
            result = await tool.get_quote(symbol="AAPL")

        assert result["c"] == 150.5
        assert result["t"] == 1609459200


class TestStockMarketDataToolGetCandles:
    """Tests for get_candles operation."""

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
            tool = StockMarketDataTool(client)
            result = await tool.get_candles(
                symbol="AAPL",
                resolution="D",
                from_timestamp=1609459200,
                to_timestamp=1640995200,
            )

        assert result["s"] == "ok"
        assert len(result["c"]) == 2

    @respx.mock
    async def test_get_candles_with_invalid_resolution(self, test_config: AppConfig):
        """Test get_candles rejects invalid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)

            with pytest.raises(ValueError, match="Invalid resolution"):
                await tool.get_candles(
                    symbol="AAPL",
                    resolution="INVALID",
                    from_timestamp=1609459200,
                    to_timestamp=1640995200,
                )


class TestStockMarketDataToolGetCompanyProfile:
    """Tests for get_company_profile operation."""

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
            "logo": "https://static.finnhub.io/logo/test.png",
            "finnhubIndustry": "Technology",
        }

        respx.get("https://finnhub.io/api/v1/stock/profile2").mock(
            return_value=httpx.Response(200, json=profile_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.get_company_profile(symbol="AAPL")

        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc"


class TestStockMarketDataToolGetMarketStatus:
    """Tests for get_market_status operation."""

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
            tool = StockMarketDataTool(client)
            result = await tool.get_market_status(exchange="US")

        assert result["exchange"] == "US"
        assert result["isOpen"] is True


class TestStockMarketDataToolGetSymbols:
    """Tests for get_symbols operation."""

    @respx.mock
    async def test_get_symbols(self, test_config: AppConfig):
        """Test getting symbols list."""
        symbols_data = [
            {"symbol": "AAPL", "description": "APPLE INC"},
            {"symbol": "MSFT", "description": "MICROSOFT CORP"},
        ]

        respx.get("https://finnhub.io/api/v1/stock/symbol").mock(
            return_value=httpx.Response(200, json=symbols_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.get_symbols(exchange="US")

        assert isinstance(result, list)
        assert len(result) == 2


class TestStockMarketDataToolSearchSymbols:
    """Tests for search_symbols operation."""

    @respx.mock
    async def test_search_symbols(self, test_config: AppConfig):
        """Test searching symbols."""
        search_data = {
            "count": 2,
            "result": [
                {"symbol": "AAPL", "description": "APPLE INC"},
                {"symbol": "APLE", "description": "APPLE HOSPITALITY"},
            ],
        }

        respx.get("https://finnhub.io/api/v1/search").mock(
            return_value=httpx.Response(200, json=search_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.search_symbols(query="apple")

        assert result["count"] == 2
        assert len(result["result"]) == 2


class TestStockMarketDataToolGetFinancials:
    """Tests for get_financials operation."""

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
                    "form": "10-Q",
                    "startDate": "2023-07-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03",
                    "report": {"bs": [{"label": "Assets", "value": 352755000000}]},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.get_financials(
                symbol="AAPL",
                statement="bs",
                freq="annual",
            )

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_financials_with_invalid_statement(self, test_config: AppConfig):
        """Test get_financials rejects invalid statement."""
        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)

            with pytest.raises(ValueError, match="Invalid statement"):
                await tool.get_financials(
                    symbol="AAPL",
                    statement="invalid",
                    freq="annual",
                )

    @respx.mock
    async def test_get_financials_with_invalid_frequency(self, test_config: AppConfig):
        """Test get_financials rejects invalid frequency."""
        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)

            with pytest.raises(ValueError, match="Invalid frequency"):
                await tool.get_financials(
                    symbol="AAPL",
                    statement="bs",
                    freq="monthly",
                )


class TestStockMarketDataToolGetEarnings:
    """Tests for get_earnings operation."""

    @respx.mock
    async def test_get_earnings(self, test_config: AppConfig):
        """Test getting earnings data."""
        earnings_data = [
            {
                "actual": 1.52,
                "estimate": 1.43,
                "period": "2023-09-30",
                "quarter": 4,
                "symbol": "AAPL",
                "year": 2023,
            },
            {
                "actual": 1.26,
                "estimate": 1.19,
                "period": "2023-06-30",
                "quarter": 3,
                "symbol": "AAPL",
                "year": 2023,
            },
        ]

        respx.get("https://finnhub.io/api/v1/stock/earnings").mock(
            return_value=httpx.Response(200, json=earnings_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.get_earnings(symbol="AAPL")

        assert "earnings" in result
        assert len(result["earnings"]) == 2


class TestStockMarketDataToolExecute:
    """Tests for execute method (operation routing)."""

    @respx.mock
    async def test_execute_get_quote(self, test_config: AppConfig):
        """Test execute routes to get_quote."""
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
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_quote",
                symbol="AAPL",
            )

        assert result["c"] == 150.5

    @respx.mock
    async def test_execute_get_candles(self, test_config: AppConfig):
        """Test execute routes to get_candles."""
        candle_data = {
            "c": [150.0],
            "h": [151.5],
            "l": [149.0],
            "o": [150.0],
            "s": "ok",
            "t": [1609459200],
            "v": [1000000],
        }

        respx.get("https://finnhub.io/api/v1/stock/candle").mock(
            return_value=httpx.Response(200, json=candle_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_candles",
                symbol="AAPL",
                resolution="D",
                from_timestamp=1609459200,
                to_timestamp=1640995200,
            )

        assert result["s"] == "ok"

    @respx.mock
    async def test_execute_get_company_profile(self, test_config: AppConfig):
        """Test execute routes to get_company_profile."""
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
            "logo": "https://static.finnhub.io/logo/test.png",
            "finnhubIndustry": "Technology",
        }

        respx.get("https://finnhub.io/api/v1/stock/profile2").mock(
            return_value=httpx.Response(200, json=profile_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_company_profile",
                symbol="AAPL",
            )

        assert result["ticker"] == "AAPL"

    @respx.mock
    async def test_execute_get_market_status(self, test_config: AppConfig):
        """Test execute routes to get_market_status."""
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
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_market_status",
                exchange="US",
            )

        assert result["exchange"] == "US"

    @respx.mock
    async def test_execute_get_symbols(self, test_config: AppConfig):
        """Test execute routes to get_symbols."""
        symbols_data = [{"symbol": "AAPL"}]

        respx.get("https://finnhub.io/api/v1/stock/symbol").mock(
            return_value=httpx.Response(200, json=symbols_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_symbols",
                exchange="US",
            )

        assert isinstance(result, list)

    @respx.mock
    async def test_execute_search_symbols(self, test_config: AppConfig):
        """Test execute routes to search_symbols."""
        search_data = {
            "count": 1,
            "result": [{"symbol": "AAPL"}],
        }

        respx.get("https://finnhub.io/api/v1/search").mock(
            return_value=httpx.Response(200, json=search_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="search_symbols",
                query="apple",
            )

        assert result["count"] == 1

    @respx.mock
    async def test_execute_get_financials(self, test_config: AppConfig):
        """Test execute routes to get_financials."""
        financials_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "year": 2023,
                    "form": "10-K",
                    "startDate": "2022-10-01",
                    "endDate": "2023-09-30",
                    "acceptedDate": "2023-11-03",
                    "report": {},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_financials",
                symbol="AAPL",
                statement="bs",
                freq="annual",
            )

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_earnings(self, test_config: AppConfig):
        """Test execute routes to get_earnings."""
        earnings_data = [
            {
                "actual": 1.52,
                "period": "2023-09-30",
                "quarter": 4,
                "symbol": "AAPL",
                "year": 2023,
            }
        ]

        respx.get("https://finnhub.io/api/v1/stock/earnings").mock(
            return_value=httpx.Response(200, json=earnings_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)
            result = await tool.execute(
                operation="get_earnings",
                symbol="AAPL",
            )

        assert "earnings" in result

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute rejects invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockMarketDataTool(client)

            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute(
                    operation="invalid_op",
                    symbol="AAPL",
                )
