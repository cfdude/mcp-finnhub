"""Tests for technical analysis API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import technical
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


class TestGetIndicator:
    """Tests for get_indicator endpoint."""

    @respx.mock
    async def test_get_indicator_rsi(self, test_config: AppConfig):
        """Test getting RSI indicator."""
        indicator_data = {
            "s": "ok",
            "t": [1609459200, 1609545600],
            "rsi": [45.2, 52.8],
        }

        respx.get("https://finnhub.io/api/v1/indicator").mock(
            return_value=httpx.Response(200, json=indicator_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await technical.get_indicator(
                client,
                "AAPL",
                "D",
                1609459200,
                1640995200,
                "rsi",
                timeperiod=14,
            )

        assert result["s"] == "ok"
        assert len(result["t"]) == 2
        assert "rsi" in result

    @respx.mock
    async def test_get_indicator_sma(self, test_config: AppConfig):
        """Test getting SMA indicator."""
        indicator_data = {
            "s": "ok",
            "t": [1609459200, 1609545600],
            "sma": [150.5, 151.2],
        }

        respx.get("https://finnhub.io/api/v1/indicator").mock(
            return_value=httpx.Response(200, json=indicator_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await technical.get_indicator(
                client,
                "AAPL",
                "D",
                1609459200,
                1640995200,
                "sma",
                timeperiod=20,
            )

        assert result["s"] == "ok"
        assert "sma" in result


class TestAggregateSignals:
    """Tests for aggregate_signals endpoint."""

    @respx.mock
    async def test_aggregate_signals(self, test_config: AppConfig):
        """Test getting aggregated signals."""
        signals_data = {
            "symbol": "AAPL",
            "technicalAnalysis": {
                "count": {"buy": 5, "neutral": 3, "sell": 2},
                "signal": "buy",
            },
            "trend": {"adx": 25.5, "trending": True},
        }

        respx.get("https://finnhub.io/api/v1/scan/technical-indicator").mock(
            return_value=httpx.Response(200, json=signals_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await technical.aggregate_signals(client, "AAPL", "D")

        assert result["symbol"] == "AAPL"
        assert "technicalAnalysis" in result
        assert "trend" in result


class TestScanPatterns:
    """Tests for scan_patterns endpoint."""

    @respx.mock
    async def test_scan_patterns(self, test_config: AppConfig):
        """Test scanning for patterns."""
        patterns_data = {
            "points": [
                {
                    "aprice": 150.0,
                    "atime": 1609459200,
                    "bprice": 155.0,
                    "btime": 1609545600,
                    "cprice": 152.0,
                    "ctime": 1609632000,
                    "dprice": 157.0,
                    "dtime": 1609718400,
                    "mature": True,
                    "patternname": "Double Top",
                    "patterntype": "M",
                    "sortTime": 1609718400,
                    "symbol": "AAPL",
                },
            ]
        }

        respx.get("https://finnhub.io/api/v1/scan/pattern").mock(
            return_value=httpx.Response(200, json=patterns_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await technical.scan_patterns(client, "AAPL", "D")

        assert "points" in result


class TestSupportResistance:
    """Tests for support_resistance endpoint."""

    @respx.mock
    async def test_support_resistance(self, test_config: AppConfig):
        """Test getting support/resistance levels."""
        levels_data = {"levels": [145.0, 150.0, 155.0, 160.0]}

        respx.get("https://finnhub.io/api/v1/scan/support-resistance").mock(
            return_value=httpx.Response(200, json=levels_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await technical.support_resistance(client, "AAPL", "D")

        assert "levels" in result
        assert len(result["levels"]) == 4
