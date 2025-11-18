"""Tests for events endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import events
from mcp_finnhub.config import AppConfig

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
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
class TestEventsEndpoints:
    @respx.mock
    async def test_get_market_holidays(self, test_config: AppConfig):
        mock_data = {"data": [], "exchange": "US", "timezone": "America/New_York"}
        respx.get("https://finnhub.io/api/v1/stock/market-holiday").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        async with FinnhubClient(test_config) as client:
            result = await events.get_market_holidays(client, "US")
        assert result["exchange"] == "US"

    @respx.mock
    async def test_get_upgrade_downgrade(self, test_config: AppConfig):
        mock_data = [{"symbol": "AAPL", "action": "upgrade", "company": "Test Firm"}]
        respx.get("https://finnhub.io/api/v1/stock/upgrade-downgrade").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        async with FinnhubClient(test_config) as client:
            result = await events.get_upgrade_downgrade(client, "AAPL")
        assert len(result) == 1
