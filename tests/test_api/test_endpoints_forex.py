"""Tests for forex endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import forex
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
class TestForexEndpoints:
    """Test suite for forex endpoints."""

    @respx.mock
    async def test_get_forex_exchanges(self, test_config: AppConfig):
        """Test get_forex_exchanges endpoint."""
        mock_data = ["oanda", "fxcm", "forex.com"]
        respx.get("https://finnhub.io/api/v1/forex/exchange").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await forex.get_forex_exchanges(client)

        assert isinstance(result, list)
        assert "oanda" in result

    @respx.mock
    async def test_get_forex_symbols(self, test_config: AppConfig):
        """Test get_forex_symbols endpoint."""
        mock_data = [
            {"description": "EUR/USD", "displaySymbol": "EUR/USD", "symbol": "OANDA:EUR_USD"}
        ]
        respx.get("https://finnhub.io/api/v1/forex/symbol").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await forex.get_forex_symbols(client, "oanda")

        assert len(result) == 1

    @respx.mock
    async def test_get_forex_candles(self, test_config: AppConfig):
        """Test get_forex_candles endpoint."""
        mock_data = {
            "c": [1.18],
            "h": [1.19],
            "l": [1.17],
            "o": [1.175],
            "s": "ok",
            "t": [1609459200],
        }
        respx.get("https://finnhub.io/api/v1/forex/candle").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await forex.get_forex_candles(
                client, "OANDA:EUR_USD", "D", 1609459200, 1609545600
            )

        assert result["s"] == "ok"

    @respx.mock
    async def test_get_forex_rates(self, test_config: AppConfig):
        """Test get_forex_rates endpoint."""
        mock_data = {"base": "USD", "quote": {"EUR": 0.85, "GBP": 0.73}}
        respx.get("https://finnhub.io/api/v1/forex/rates").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await forex.get_forex_rates(client)

        assert result["base"] == "USD"
