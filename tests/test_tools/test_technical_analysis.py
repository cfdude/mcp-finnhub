"""Integration tests for TechnicalAnalysisTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.technical_analysis import TechnicalAnalysisTool

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


class TestTechnicalAnalysisToolValidation:
    """Tests for validation methods."""

    def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validation passes for valid operations."""
        client = FinnhubClient(test_config)
        tool = TechnicalAnalysisTool(client)

        # Should not raise
        tool.validate_operation("get_indicator")
        tool.validate_operation("aggregate_signals")
        tool.validate_operation("scan_patterns")
        tool.validate_operation("support_resistance")

    def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        client = FinnhubClient(test_config)
        tool = TechnicalAnalysisTool(client)

        with pytest.raises(ValueError, match="Invalid operation"):
            tool.validate_operation("invalid_operation")

    def test_validate_resolution_valid(self, test_config: AppConfig):
        """Test validation passes for valid resolutions."""
        client = FinnhubClient(test_config)
        tool = TechnicalAnalysisTool(client)

        # Should not raise
        for resolution in ["1", "5", "15", "30", "60", "D", "W", "M"]:
            tool.validate_resolution(resolution)

    def test_validate_resolution_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid resolution."""
        client = FinnhubClient(test_config)
        tool = TechnicalAnalysisTool(client)

        with pytest.raises(ValueError, match="Invalid resolution"):
            tool.validate_resolution("2H")


class TestTechnicalAnalysisToolGetIndicator:
    """Tests for get_indicator operation."""

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
            tool = TechnicalAnalysisTool(client)
            result = await tool.get_indicator(
                symbol="AAPL",
                resolution="D",
                from_timestamp=1609459200,
                to_timestamp=1640995200,
                indicator="rsi",
                timeperiod=14,
            )

        assert result["s"] == "ok"
        assert len(result["t"]) == 2
        assert "rsi" in result

    @respx.mock
    async def test_get_indicator_with_invalid_resolution(self, test_config: AppConfig):
        """Test get_indicator rejects invalid resolution."""
        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)

            with pytest.raises(ValueError, match="Invalid resolution"):
                await tool.get_indicator(
                    symbol="AAPL",
                    resolution="INVALID",
                    from_timestamp=1609459200,
                    to_timestamp=1640995200,
                    indicator="rsi",
                )


class TestTechnicalAnalysisToolAggregateSignals:
    """Tests for aggregate_signals operation."""

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
            tool = TechnicalAnalysisTool(client)
            result = await tool.aggregate_signals(
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"
        assert "technicalAnalysis" in result
        assert "trend" in result

    @respx.mock
    async def test_aggregate_signals_validates_response(self, test_config: AppConfig):
        """Test aggregate_signals validates response with Pydantic."""
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
            tool = TechnicalAnalysisTool(client)
            result = await tool.aggregate_signals(
                symbol="AAPL",
                resolution="D",
            )

        # Should be validated and returned as dict
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"


class TestTechnicalAnalysisToolScanPatterns:
    """Tests for scan_patterns operation."""

    @respx.mock
    async def test_scan_patterns(self, test_config: AppConfig):
        """Test scanning for patterns."""
        patterns_data = {
            "symbol": "AAPL",
            "resolution": "D",
            "patterns": [
                {
                    "patternName": "Double Top",
                    "patternType": "M",
                    "mature": True,
                    "entryPoint": 150.0,
                    "target": 160.0,
                    "stopLoss": 145.0,
                },
                {
                    "patternName": "Triangle",
                    "patternType": "W",
                    "mature": False,
                },
            ],
        }

        respx.get("https://finnhub.io/api/v1/scan/pattern").mock(
            return_value=httpx.Response(200, json=patterns_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)
            result = await tool.scan_patterns(
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"
        assert len(result["patterns"]) == 2


class TestTechnicalAnalysisToolSupportResistance:
    """Tests for support_resistance operation."""

    @respx.mock
    async def test_support_resistance(self, test_config: AppConfig):
        """Test getting support/resistance levels."""
        levels_data = {
            "symbol": "AAPL",
            "resolution": "D",
            "levels": [
                {"level": 145.0, "type": "support"},
                {"level": 150.0, "type": "support"},
                {"level": 160.0, "type": "resistance"},
                {"level": 165.0, "type": "resistance"},
            ],
        }

        respx.get("https://finnhub.io/api/v1/scan/support-resistance").mock(
            return_value=httpx.Response(200, json=levels_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)
            result = await tool.support_resistance(
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"
        assert len(result["levels"]) == 4


class TestTechnicalAnalysisToolExecute:
    """Tests for execute method (operation routing)."""

    @respx.mock
    async def test_execute_get_indicator(self, test_config: AppConfig):
        """Test execute routes to get_indicator."""
        indicator_data = {
            "s": "ok",
            "t": [1609459200],
            "rsi": [45.2],
        }

        respx.get("https://finnhub.io/api/v1/indicator").mock(
            return_value=httpx.Response(200, json=indicator_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)
            result = await tool.execute(
                operation="get_indicator",
                symbol="AAPL",
                resolution="D",
                from_timestamp=1609459200,
                to_timestamp=1640995200,
                indicator="rsi",
                timeperiod=14,
            )

        assert result["s"] == "ok"

    @respx.mock
    async def test_execute_aggregate_signals(self, test_config: AppConfig):
        """Test execute routes to aggregate_signals."""
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
            tool = TechnicalAnalysisTool(client)
            result = await tool.execute(
                operation="aggregate_signals",
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_scan_patterns(self, test_config: AppConfig):
        """Test execute routes to scan_patterns."""
        patterns_data = {
            "symbol": "AAPL",
            "resolution": "D",
            "patterns": [{"patternName": "Double Top", "patternType": "M", "mature": True}],
        }

        respx.get("https://finnhub.io/api/v1/scan/pattern").mock(
            return_value=httpx.Response(200, json=patterns_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)
            result = await tool.execute(
                operation="scan_patterns",
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_support_resistance(self, test_config: AppConfig):
        """Test execute routes to support_resistance."""
        levels_data = {
            "symbol": "AAPL",
            "resolution": "D",
            "levels": [
                {"level": 145.0, "type": "support"},
                {"level": 160.0, "type": "resistance"},
            ],
        }

        respx.get("https://finnhub.io/api/v1/scan/support-resistance").mock(
            return_value=httpx.Response(200, json=levels_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)
            result = await tool.execute(
                operation="support_resistance",
                symbol="AAPL",
                resolution="D",
            )

        assert result["symbol"] == "AAPL"

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute rejects invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = TechnicalAnalysisTool(client)

            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute(
                    operation="invalid_op",
                    symbol="AAPL",
                    resolution="D",
                )
