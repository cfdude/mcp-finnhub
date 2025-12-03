"""Tests for CryptoDataTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.crypto_data import CryptoDataTool

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
class TestCryptoDataTool:
    """Test suite for CryptoDataTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_crypto_exchanges",
            "get_crypto_symbols",
            "get_crypto_profile",
            "get_crypto_candles",
        }
        assert expected_operations == CryptoDataTool.VALID_OPERATIONS

    def test_valid_resolutions(self):
        """Test that all valid resolutions are defined."""
        expected_resolutions = {"1", "5", "15", "30", "60", "D", "W", "M"}
        assert expected_resolutions == CryptoDataTool.VALID_RESOLUTIONS

    @respx.mock
    async def test_get_crypto_exchanges(self, test_config: AppConfig):
        """Test get_crypto_exchanges operation."""
        mock_data = ["binance", "coinbase"]
        respx.get("https://finnhub.io/api/v1/crypto/exchange").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            result = await tool.get_crypto_exchanges()

        assert isinstance(result, list)
        assert len(result) == 2

    @respx.mock
    async def test_get_crypto_symbols(self, test_config: AppConfig):
        """Test get_crypto_symbols operation."""
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
            tool = CryptoDataTool(client)
            result = await tool.get_crypto_symbols("binance")

        assert isinstance(result, list)
        assert len(result) == 1

    @respx.mock
    async def test_get_crypto_profile(self, test_config: AppConfig):
        """Test get_crypto_profile operation."""
        mock_data = {
            "name": "Bitcoin",
            "cmc": 1,
        }
        respx.get("https://finnhub.io/api/v1/crypto/profile").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            result = await tool.get_crypto_profile("BTC")

        assert result["name"] == "Bitcoin"

    @respx.mock
    async def test_get_crypto_candles(self, test_config: AppConfig):
        """Test get_crypto_candles operation."""
        mock_data = {
            "c": [45000.0],
            "h": [45200.0],
            "l": [44800.0],
            "o": [44900.0],
            "s": "ok",
            "t": [1609459200],
            "v": [100.5],
        }
        respx.get("https://finnhub.io/api/v1/crypto/candle").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            result = await tool.get_crypto_candles("BINANCE:BTCUSDT", "D", 1609459200, 1609545600)

        assert result["s"] == "ok"

    @respx.mock
    async def test_get_crypto_candles_invalid_resolution(self, test_config: AppConfig):
        """Test get_crypto_candles with invalid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            with pytest.raises(ValueError, match="Invalid resolution"):
                await tool.get_crypto_candles("BINANCE:BTCUSDT", "invalid", 1, 2)

    async def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validate_operation with valid operation."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            # Should not raise
            tool.validate_operation("get_crypto_exchanges")

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validate_operation with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_validate_resolution_valid(self, test_config: AppConfig):
        """Test validate_resolution with valid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            # Should not raise
            tool.validate_resolution("D")
            tool.validate_resolution("1")

    async def test_validate_resolution_invalid(self, test_config: AppConfig):
        """Test validate_resolution with invalid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            with pytest.raises(ValueError, match="Invalid resolution"):
                tool.validate_resolution("invalid")

    @respx.mock
    async def test_execute_get_crypto_exchanges(self, test_config: AppConfig):
        """Test execute method with get_crypto_exchanges operation."""
        mock_data = ["binance"]
        respx.get("https://finnhub.io/api/v1/crypto/exchange").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            result = await tool.execute("get_crypto_exchanges")

        assert isinstance(result, list)

    @respx.mock
    async def test_execute_get_crypto_symbols(self, test_config: AppConfig):
        """Test execute method with get_crypto_symbols operation."""
        mock_data = [{"symbol": "BINANCE:BTCUSDT"}]
        respx.get("https://finnhub.io/api/v1/crypto/symbol").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            result = await tool.execute("get_crypto_symbols", exchange="binance")

        assert isinstance(result, list)

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = CryptoDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_operation")
