"""Tests for CalendarDataTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.calendar_data import CalendarDataTool

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
class TestCalendarDataTool:
    def test_valid_operations(self):
        expected = {
            "get_ipo_calendar",
            "get_earnings_calendar",
            "get_economic_calendar",
            "get_fda_calendar",
        }
        assert expected == CalendarDataTool.VALID_OPERATIONS

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        async with FinnhubClient(test_config) as client:
            tool = CalendarDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        async with FinnhubClient(test_config) as client:
            tool = CalendarDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_operation")
