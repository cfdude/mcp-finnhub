"""Tests for calendar endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import calendar
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
class TestCalendarEndpoints:
    @respx.mock
    async def test_get_ipo_calendar(self, test_config: AppConfig):
        mock_data = {"ipoCalendar": [{"date": "2024-01-15", "symbol": "TEST", "name": "Test Inc"}]}
        respx.get("https://finnhub.io/api/v1/calendar/ipo").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        async with FinnhubClient(test_config) as client:
            result = await calendar.get_ipo_calendar(client, "2024-01-01", "2024-01-31")
        assert "ipoCalendar" in result

    @respx.mock
    async def test_get_earnings_calendar(self, test_config: AppConfig):
        mock_data = {"earningsCalendar": [{"date": "2024-01-15", "symbol": "AAPL"}]}
        respx.get("https://finnhub.io/api/v1/calendar/earnings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        async with FinnhubClient(test_config) as client:
            result = await calendar.get_earnings_calendar(client)
        assert "earningsCalendar" in result
