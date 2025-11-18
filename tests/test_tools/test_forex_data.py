"""Tests for ForexDataTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.forex_data import ForexDataTool

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
class TestForexDataTool:
    """Test suite for ForexDataTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_forex_exchanges",
            "get_forex_symbols",
            "get_forex_candles",
            "get_forex_rates",
        }
        assert expected_operations == ForexDataTool.VALID_OPERATIONS

    @respx.mock
    async def test_get_forex_exchanges(self, test_config: AppConfig):
        """Test get_forex_exchanges operation."""
        mock_data = ["oanda"]
        respx.get("https://finnhub.io/api/v1/forex/exchange").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = ForexDataTool(client)
            result = await tool.get_forex_exchanges()

        assert isinstance(result, list)

    @respx.mock
    async def test_get_forex_candles_invalid_resolution(self, test_config: AppConfig):
        """Test get_forex_candles with invalid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = ForexDataTool(client)
            with pytest.raises(ValueError, match="Invalid resolution"):
                await tool.get_forex_candles("OANDA:EUR_USD", "invalid", 1, 2)

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validate_operation with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = ForexDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = ForexDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_operation")
