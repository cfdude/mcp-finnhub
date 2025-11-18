"""Tests for cryptocurrency endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import crypto
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
class TestCryptoEndpoints:
    """Test suite for cryptocurrency endpoints."""

    @respx.mock
    async def test_get_crypto_exchanges(self, test_config: AppConfig):
        """Test get_crypto_exchanges endpoint."""
        mock_data = ["binance", "coinbase", "kraken", "bitfinex"]
        respx.get("https://finnhub.io/api/v1/crypto/exchange").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await crypto.get_crypto_exchanges(client)

        assert isinstance(result, list)
        assert len(result) == 4
        assert "binance" in result

    @respx.mock
    async def test_get_crypto_symbols(self, test_config: AppConfig):
        """Test get_crypto_symbols endpoint."""
        mock_data = [
            {
                "description": "Bitcoin/US Dollar",
                "displaySymbol": "BTC/USDT",
                "symbol": "BINANCE:BTCUSDT",
            }
        ]
        respx.get("https://finnhub.io/api/v1/crypto/symbol").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await crypto.get_crypto_symbols(client, "binance")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["symbol"] == "BINANCE:BTCUSDT"

    @respx.mock
    async def test_get_crypto_profile(self, test_config: AppConfig):
        """Test get_crypto_profile endpoint."""
        mock_data = {
            "name": "Bitcoin",
            "description": "Digital currency",
            "logo": "https://example.com/btc.png",
            "cmc": 1,
            "website": "https://bitcoin.org",
        }
        respx.get("https://finnhub.io/api/v1/crypto/profile").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await crypto.get_crypto_profile(client, "BTC")

        assert result["name"] == "Bitcoin"
        assert result["cmc"] == 1

    @respx.mock
    async def test_get_crypto_candles(self, test_config: AppConfig):
        """Test get_crypto_candles endpoint."""
        mock_data = {
            "c": [45000.0, 45500.0],
            "h": [45200.0, 45700.0],
            "l": [44800.0, 45300.0],
            "o": [44900.0, 45100.0],
            "s": "ok",
            "t": [1609459200, 1609545600],
            "v": [100.5, 120.3],
        }
        respx.get("https://finnhub.io/api/v1/crypto/candle").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await crypto.get_crypto_candles(
                client, "BINANCE:BTCUSDT", "D", 1609459200, 1609545600
            )

        assert result["s"] == "ok"
        assert len(result["c"]) == 2
