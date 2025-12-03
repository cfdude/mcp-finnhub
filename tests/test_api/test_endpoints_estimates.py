"""Tests for estimates endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import estimates
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


@pytest.mark.asyncio
class TestEstimatesEndpoints:
    """Test suite for estimates endpoints."""

    @respx.mock
    async def test_get_earnings_estimates(self, test_config: AppConfig):
        """Test get_earnings_estimates endpoint."""
        mock_data = {
            "data": [
                {
                    "epsAvg": 1.5,
                    "epsHigh": 1.8,
                    "epsLow": 1.2,
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
            result = await estimates.get_earnings_estimates(client, "AAPL", "quarterly")

        assert result["symbol"] == "AAPL"
        assert result["freq"] == "quarterly"
        assert len(result["data"]) == 1
        assert result["data"][0]["epsAvg"] == 1.5

    @respx.mock
    async def test_get_revenue_estimates(self, test_config: AppConfig):
        """Test get_revenue_estimates endpoint."""
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
            "freq": "quarterly",
            "symbol": "TSLA",
        }
        respx.get("https://finnhub.io/api/v1/stock/revenue-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await estimates.get_revenue_estimates(client, "TSLA", "quarterly")

        assert result["symbol"] == "TSLA"
        assert result["data"][0]["revenueAvg"] == 100000000000

    @respx.mock
    async def test_get_ebitda_estimates(self, test_config: AppConfig):
        """Test get_ebitda_estimates endpoint."""
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
            result = await estimates.get_ebitda_estimates(client, "MSFT", "annual")

        assert result["symbol"] == "MSFT"
        assert result["freq"] == "annual"
        assert result["data"][0]["ebitdaAvg"] == 25000000000

    @respx.mock
    async def test_get_price_targets(self, test_config: AppConfig):
        """Test get_price_targets endpoint."""
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
            result = await estimates.get_price_targets(client, "NFLX")

        assert result["symbol"] == "NFLX"
        assert result["targetMean"] == 400.0
        assert result["numberAnalysts"] == 35

    @respx.mock
    async def test_get_recommendations(self, test_config: AppConfig):
        """Test get_recommendations endpoint."""
        mock_data = [
            {
                "buy": 20,
                "hold": 5,
                "sell": 1,
                "strongBuy": 10,
                "strongSell": 0,
                "period": "2024-01-01",
                "symbol": "AAPL",
            },
            {
                "buy": 18,
                "hold": 7,
                "sell": 2,
                "strongBuy": 12,
                "strongSell": 0,
                "period": "2023-12-01",
                "symbol": "AAPL",
            },
        ]
        respx.get("https://finnhub.io/api/v1/stock/recommendation").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await estimates.get_recommendations(client, "AAPL")

        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[0]["strongBuy"] == 10
        assert result[1]["period"] == "2023-12-01"

    @respx.mock
    async def test_get_earnings_estimates_no_freq(self, test_config: AppConfig):
        """Test get_earnings_estimates endpoint without freq parameter."""
        mock_data = {
            "data": [],
            "freq": "quarterly",
            "symbol": "GOOGL",
        }
        respx.get("https://finnhub.io/api/v1/stock/eps-estimate").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await estimates.get_earnings_estimates(client, "GOOGL")

        assert result["symbol"] == "GOOGL"
        assert result["data"] == []
