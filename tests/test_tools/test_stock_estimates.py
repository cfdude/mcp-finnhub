"""Tests for StockEstimatesTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.stock_estimates import StockEstimatesTool

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


@pytest.mark.asyncio
class TestStockEstimatesTool:
    """Test suite for StockEstimatesTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_earnings_estimates",
            "get_revenue_estimates",
            "get_ebitda_estimates",
            "get_price_targets",
            "get_recommendations",
        }
        assert expected_operations == StockEstimatesTool.VALID_OPERATIONS

    def test_valid_frequencies(self):
        """Test that valid frequencies are defined."""
        expected_frequencies = {"annual", "quarterly"}
        assert expected_frequencies == StockEstimatesTool.VALID_FREQUENCIES

    @respx.mock
    async def test_get_earnings_estimates(self, test_config: AppConfig):
        """Test get_earnings_estimates operation."""
        mock_data = {
            "data": [
                {
                    "epsAvg": 1.25,
                    "epsHigh": 1.50,
                    "epsLow": 1.00,
                    "numberAnalysts": 30,
                    "period": "2024-03-31",
                    "year": 2024,
                    "quarter": 1,
                }
            ],
            "freq": "quarterly",
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/eps-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.get_earnings_estimates("AAPL", "quarterly")

        assert result["symbol"] == "AAPL"
        assert result["freq"] == "quarterly"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_revenue_estimates(self, test_config: AppConfig):
        """Test get_revenue_estimates operation."""
        mock_data = {
            "data": [
                {
                    "revenueAvg": 100000000000,
                    "revenueHigh": 110000000000,
                    "revenueLow": 90000000000,
                    "numberAnalysts": 25,
                    "period": "2024-03-31",
                    "year": 2024,
                    "quarter": 1,
                }
            ],
            "freq": "annual",
            "symbol": "TSLA",
        }
        respx.get("https://finnhub.io/api/v1/stock/revenue-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.get_revenue_estimates("TSLA", "annual")

        assert result["symbol"] == "TSLA"
        assert result["freq"] == "annual"

    @respx.mock
    async def test_get_ebitda_estimates(self, test_config: AppConfig):
        """Test get_ebitda_estimates operation."""
        mock_data = {
            "data": [
                {
                    "ebitdaAvg": 25000000000,
                    "ebitdaHigh": 28000000000,
                    "ebitdaLow": 22000000000,
                    "numberAnalysts": 20,
                    "period": "2024-12-31",
                    "year": 2024,
                    "quarter": 0,
                }
            ],
            "freq": "annual",
            "symbol": "MSFT",
        }
        respx.get("https://finnhub.io/api/v1/stock/ebitda-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.get_ebitda_estimates("MSFT", "annual")

        assert result["symbol"] == "MSFT"
        assert result["data"][0]["ebitdaAvg"] == 25000000000

    @respx.mock
    async def test_get_price_targets(self, test_config: AppConfig):
        """Test get_price_targets operation."""
        mock_data = {
            "symbol": "NFLX",
            "targetHigh": 500.0,
            "targetLow": 300.0,
            "targetMean": 400.0,
            "targetMedian": 395.0,
            "numberAnalysts": 35,
            "lastUpdated": "2024-01-15 00:00:00",
        }
        respx.get("https://finnhub.io/api/v1/stock/price-target").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.get_price_targets("NFLX")

        assert result["symbol"] == "NFLX"
        assert result["targetMean"] == 400.0

    @respx.mock
    async def test_get_recommendations(self, test_config: AppConfig):
        """Test get_recommendations operation."""
        mock_data = [
            {
                "buy": 20,
                "hold": 5,
                "sell": 1,
                "strongBuy": 10,
                "strongSell": 0,
                "period": "2024-01-01",
                "symbol": "AAPL",
            }
        ]
        respx.get("https://finnhub.io/api/v1/stock/recommendation").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.get_recommendations("AAPL")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["symbol"] == "AAPL"

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_validate_freq_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid frequency."""
        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            with pytest.raises(ValueError, match="Invalid frequency"):
                tool.validate_freq("monthly")

    async def test_validate_freq_valid(self, test_config: AppConfig):
        """Test validation succeeds for valid frequency."""
        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            # Should not raise
            tool.validate_freq("annual")
            tool.validate_freq("quarterly")
            tool.validate_freq(None)

    @respx.mock
    async def test_execute_get_earnings_estimates(self, test_config: AppConfig):
        """Test execute with get_earnings_estimates operation."""
        mock_data = {
            "data": [
                {
                    "epsAvg": 1.25,
                    "numberAnalysts": 30,
                    "period": "2024-03-31",
                }
            ],
            "freq": "quarterly",
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/eps-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.execute("get_earnings_estimates", symbol="AAPL", freq="quarterly")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_price_targets(self, test_config: AppConfig):
        """Test execute with get_price_targets operation."""
        mock_data = {
            "symbol": "NFLX",
            "targetMean": 400.0,
        }
        respx.get("https://finnhub.io/api/v1/stock/price-target").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            result = await tool.execute("get_price_targets", symbol="NFLX")

        assert result["symbol"] == "NFLX"

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute fails for invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_op", symbol="AAPL")

    @respx.mock
    async def test_execute_invalid_freq(self, test_config: AppConfig):
        """Test execute fails for invalid frequency."""
        async with FinnhubClient(test_config) as client:
            tool = StockEstimatesTool(client)
            with pytest.raises(ValueError, match="Invalid frequency"):
                await tool.execute("get_earnings_estimates", symbol="AAPL", freq="monthly")
