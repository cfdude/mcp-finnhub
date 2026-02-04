"""Integration tests for StockFundamentalsTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.stock_fundamentals import StockFundamentalsTool

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


class TestStockFundamentalsToolValidation:
    """Tests for validation methods."""

    def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validation passes for valid operations."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        for op in [
            "get_basic_financials",
            "get_reported_financials",
            "get_sec_financials",
            "get_dividends",
            "get_splits",
            "get_revenue_breakdown",
        ]:
            tool.validate_operation(op)

    def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        with pytest.raises(ValueError, match="Invalid operation"):
            tool.validate_operation("invalid_operation")

    def test_validate_frequency_valid(self, test_config: AppConfig):
        """Test validation passes for valid frequencies."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        for freq in ["annual", "quarterly"]:
            tool.validate_frequency(freq)

    def test_validate_frequency_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid frequency."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        with pytest.raises(ValueError, match="Invalid frequency"):
            tool.validate_frequency("monthly")

    def test_validate_statement_valid(self, test_config: AppConfig):
        """Test validation passes for valid statements."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        for stmt in ["bs", "ic", "cf"]:
            tool.validate_statement(stmt)

    def test_validate_statement_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid statement."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        with pytest.raises(ValueError, match="Invalid statement"):
            tool.validate_statement("invalid")

    def test_validate_metric_valid(self, test_config: AppConfig):
        """Test validation passes for valid metrics."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        for metric in ["all", "price", "valuation", "margin", "growth"]:
            tool.validate_metric(metric)

    def test_validate_metric_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid metric."""
        client = FinnhubClient(test_config)
        tool = StockFundamentalsTool(client)

        with pytest.raises(ValueError, match="Invalid metric"):
            tool.validate_metric("invalid")


class TestStockFundamentalsToolGetBasicFinancials:
    """Tests for get_basic_financials operation."""

    @respx.mock
    async def test_get_basic_financials(self, test_config: AppConfig):
        """Test getting basic financials - excludes series by default."""
        financials_data = {
            "symbol": "AAPL",
            "metric": {
                "marketCapitalization": 2500000,
                "peBasicExclExtraTTM": 25.5,
                "roeTTM": 0.85,
            },
            "series": {
                "annual": {
                    "currentRatio": [{"period": "2023", "v": 1.5}],
                },
            },
        }

        respx.get("https://finnhub.io/api/v1/stock/metric").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_basic_financials(symbol="AAPL")

        assert result["symbol"] == "AAPL"
        assert "metric" in result
        # Series should be excluded by default for context window management
        assert "series" not in result

    @respx.mock
    async def test_get_basic_financials_with_series(self, test_config: AppConfig):
        """Test getting basic financials with series included."""
        financials_data = {
            "symbol": "AAPL",
            "metric": {
                "marketCapitalization": 2500000,
            },
            "series": {
                "annual": {
                    "currentRatio": [
                        {"period": "2023", "v": 1.5},
                        {"period": "2022", "v": 1.4},
                    ],
                },
            },
        }

        respx.get("https://finnhub.io/api/v1/stock/metric").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_basic_financials(symbol="AAPL", include_series=True)

        assert result["symbol"] == "AAPL"
        assert "metric" in result
        assert "series" in result
        assert "annual" in result["series"]

    @respx.mock
    async def test_get_basic_financials_with_series_limit(self, test_config: AppConfig):
        """Test getting basic financials with limited series periods."""
        financials_data = {
            "symbol": "AAPL",
            "metric": {
                "marketCapitalization": 2500000,
            },
            "series": {
                "annual": {
                    "currentRatio": [
                        {"period": "2023", "v": 1.5},
                        {"period": "2022", "v": 1.4},
                        {"period": "2021", "v": 1.3},
                        {"period": "2020", "v": 1.2},
                    ],
                    "grossMargin": [
                        {"period": "2023", "v": 0.45},
                        {"period": "2022", "v": 0.44},
                        {"period": "2021", "v": 0.43},
                    ],
                },
            },
        }

        respx.get("https://finnhub.io/api/v1/stock/metric").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_basic_financials(
                symbol="AAPL", include_series=True, series_limit=2
            )

        assert result["symbol"] == "AAPL"
        assert "series" in result
        # Should only have 2 periods per metric
        assert len(result["series"]["annual"]["currentRatio"]) == 2
        assert len(result["series"]["annual"]["grossMargin"]) == 2
        # Should be most recent periods (first in list)
        assert result["series"]["annual"]["currentRatio"][0]["period"] == "2023"

    @respx.mock
    async def test_get_basic_financials_with_invalid_metric(self, test_config: AppConfig):
        """Test get_basic_financials rejects invalid metric."""
        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)

            with pytest.raises(ValueError, match="Invalid metric"):
                await tool.get_basic_financials(symbol="AAPL", metric="invalid")


class TestStockFundamentalsToolGetReportedFinancials:
    """Tests for get_reported_financials operation."""

    @respx.mock
    async def test_get_reported_financials(self, test_config: AppConfig):
        """Test getting reported financials."""
        reported_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=reported_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_reported_financials(symbol="AAPL", freq="annual")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_reported_financials_invalid_frequency(self, test_config: AppConfig):
        """Test get_reported_financials rejects invalid frequency."""
        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)

            with pytest.raises(ValueError, match="Invalid frequency"):
                await tool.get_reported_financials(symbol="AAPL", freq="monthly")


class TestStockFundamentalsToolGetSecFinancials:
    """Tests for get_sec_financials operation."""

    @respx.mock
    async def test_get_sec_financials(self, test_config: AppConfig):
        """Test getting SEC financials."""
        sec_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2023-01-01",
                    "endDate": "2023-12-31",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {"bs": []},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials").mock(
            return_value=httpx.Response(200, json=sec_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_sec_financials(symbol="AAPL", statement="bs", freq="annual")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_sec_financials_invalid_statement(self, test_config: AppConfig):
        """Test get_sec_financials rejects invalid statement."""
        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)

            with pytest.raises(ValueError, match="Invalid statement"):
                await tool.get_sec_financials(symbol="AAPL", statement="invalid", freq="annual")


class TestStockFundamentalsToolGetDividends:
    """Tests for get_dividends operation."""

    @respx.mock
    async def test_get_dividends(self, test_config: AppConfig):
        """Test getting dividends."""
        dividends_data = [
            {
                "symbol": "AAPL",
                "date": "2023-11-10",
                "amount": 0.24,
            },
            {
                "symbol": "AAPL",
                "date": "2023-08-11",
                "amount": 0.24,
            },
        ]

        respx.get("https://finnhub.io/api/v1/stock/dividend").mock(
            return_value=httpx.Response(200, json=dividends_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_dividends(
                symbol="AAPL", from_date="2023-01-01", to_date="2023-12-31"
            )

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["amount"] == 0.24


class TestStockFundamentalsToolGetSplits:
    """Tests for get_splits operation."""

    @respx.mock
    async def test_get_splits(self, test_config: AppConfig):
        """Test getting splits."""
        splits_data = [
            {
                "symbol": "AAPL",
                "date": "2020-08-31",
                "fromFactor": 1.0,
                "toFactor": 4.0,
            }
        ]

        respx.get("https://finnhub.io/api/v1/stock/split").mock(
            return_value=httpx.Response(200, json=splits_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_splits(
                symbol="AAPL", from_date="2020-01-01", to_date="2023-12-31"
            )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["toFactor"] == 4.0


class TestStockFundamentalsToolGetRevenueBreakdown:
    """Tests for get_revenue_breakdown operation."""

    @respx.mock
    async def test_get_revenue_breakdown(self, test_config: AppConfig):
        """Test getting revenue breakdown."""
        revenue_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "123",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": None,
                    "breakdown": [
                        {"product": "iPhone", "revenue": 200616000000},
                    ],
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/revenue-breakdown").mock(
            return_value=httpx.Response(200, json=revenue_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.get_revenue_breakdown(symbol="AAPL")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1


class TestStockFundamentalsToolExecute:
    """Tests for execute method (operation routing)."""

    @respx.mock
    async def test_execute_get_basic_financials(self, test_config: AppConfig):
        """Test execute routes to get_basic_financials."""
        financials_data = {
            "symbol": "AAPL",
            "metric": {"marketCapitalization": 2500000},
        }

        respx.get("https://finnhub.io/api/v1/stock/metric").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.execute(operation="get_basic_financials", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_dividends(self, test_config: AppConfig):
        """Test execute routes to get_dividends."""
        dividends_data = [{"symbol": "AAPL", "date": "2023-11-10", "amount": 0.24}]

        respx.get("https://finnhub.io/api/v1/stock/dividend").mock(
            return_value=httpx.Response(200, json=dividends_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)
            result = await tool.execute(
                operation="get_dividends",
                symbol="AAPL",
                from_date="2023-01-01",
                to_date="2023-12-31",
            )

        assert isinstance(result, list)
        assert len(result) == 1

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute rejects invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockFundamentalsTool(client)

            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute(operation="invalid_op", symbol="AAPL")
