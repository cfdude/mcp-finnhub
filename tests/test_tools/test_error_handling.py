"""Tests for AI-friendly error handling in tool wrappers."""

from __future__ import annotations

import pytest

from mcp_finnhub.tools import (
    _format_error_message,
    _get_operation_examples,
    _get_param_info,
)
from mcp_finnhub.tools.stock_market_data import StockMarketDataTool


class TestParamInfo:
    """Tests for parameter extraction."""

    def test_get_param_info_required_only(self):
        """Test extracting required parameters only."""
        # Use a simple method with only required params
        tool = StockMarketDataTool(None)
        info = _get_param_info(tool.get_quote)

        assert "symbol" in info["required"]
        assert len(info["optional"]) == 0

    def test_get_param_info_with_defaults(self):
        """Test extracting parameters with defaults."""
        # get_candles has required params
        tool = StockMarketDataTool(None)
        info = _get_param_info(tool.get_candles)

        assert "symbol" in info["required"]
        assert "resolution" in info["required"]
        assert "from_timestamp" in info["required"]
        assert "to_timestamp" in info["required"]


class TestOperationExamples:
    """Tests for operation example lookup."""

    def test_get_example_for_known_operation(self):
        """Test getting example for a known operation."""
        example = _get_operation_examples("finnhub_stock_market_data", "get_quote")

        assert example != ""
        assert "AAPL" in example
        assert "get_quote" in example

    def test_get_example_for_exchange_operation(self):
        """Test getting example for get_market_status (uses exchange, not symbol)."""
        example = _get_operation_examples("finnhub_stock_market_data", "get_market_status")

        assert example != ""
        assert "exchange" in example
        assert "US" in example

    def test_get_example_for_query_operation(self):
        """Test getting example for search_symbols (uses query, not symbol)."""
        example = _get_operation_examples("finnhub_stock_market_data", "search_symbols")

        assert example != ""
        assert "query" in example
        assert "apple" in example

    def test_get_example_for_unknown_operation(self):
        """Test getting example for unknown operation returns empty string."""
        example = _get_operation_examples("finnhub_stock_market_data", "unknown_operation")

        assert example == ""

    def test_get_example_for_unknown_tool(self):
        """Test getting example for unknown tool returns empty string."""
        example = _get_operation_examples("unknown_tool", "get_quote")

        assert example == ""


class TestFormatErrorMessage:
    """Tests for error message formatting."""

    def test_format_error_message_includes_required_params(self):
        """Test that error message includes required parameters."""
        tool = StockMarketDataTool(None)
        error = TypeError("missing required argument: 'exchange'")

        msg = _format_error_message(
            "finnhub_stock_market_data",
            "get_market_status",
            tool.get_market_status,
            {"symbol": "US"},
            error,
        )

        assert "Required parameters: exchange" in msg
        assert "Provided parameters: symbol" in msg
        assert "Error calling" in msg

    def test_format_error_message_includes_example(self):
        """Test that error message includes usage example."""
        tool = StockMarketDataTool(None)
        error = TypeError("got unexpected keyword argument 'symbol'")

        msg = _format_error_message(
            "finnhub_stock_market_data",
            "get_market_status",
            tool.get_market_status,
            {"symbol": "US"},
            error,
        )

        assert "Example usage:" in msg
        assert '"exchange": "US"' in msg

    def test_format_error_message_shows_provided_params(self):
        """Test that error message shows what parameters were provided."""
        tool = StockMarketDataTool(None)
        error = TypeError("missing required argument")

        msg = _format_error_message(
            "finnhub_stock_market_data",
            "get_candles",
            tool.get_candles,
            {"symbol": "AAPL", "resolution": "D"},
            error,
        )

        assert "symbol, resolution" in msg
        # from_timestamp and to_timestamp are missing
        assert "from_timestamp" in msg
        assert "to_timestamp" in msg


class TestExecuteToolOperation:
    """Tests for execute_tool_operation wrapper."""

    @pytest.mark.asyncio
    async def test_execute_tool_operation_catches_type_error(self):
        """Test that TypeError is caught and returns structured error response."""
        from mcp_finnhub.tools import finnhub_stock_market_data
        from mcp_finnhub.server import build_server_context

        # Create a mock context - we'll get a TypeError before API is called
        # because wrong parameters are passed
        context = build_server_context(
            finnhub_api_key="test_key",
            storage_directory="/tmp/test",
        )

        try:
            # Pass symbol when exchange is expected
            result = await finnhub_stock_market_data(
                context,
                "get_market_status",
                symbol="US",  # Wrong param name!
            )

            # Should return structured error response
            assert result["error"] == "parameter_error"
            assert "exchange" in result["required_params"]
            assert result["operation"] == "get_market_status"
            assert result["tool"] == "finnhub_stock_market_data"
            assert "example" in result
        finally:
            await context.aclose()

    @pytest.mark.asyncio
    async def test_execute_tool_operation_valid_params_passes_through(self):
        """Test that valid parameters work correctly."""
        from unittest.mock import AsyncMock, patch

        from mcp_finnhub.tools import finnhub_stock_market_data
        from mcp_finnhub.server import build_server_context

        context = build_server_context(
            finnhub_api_key="test_key",
            storage_directory="/tmp/test",
        )

        try:
            # Mock the API call
            with patch.object(
                context.client, "get", new_callable=AsyncMock
            ) as mock_get:
                mock_get.return_value = {
                    "exchange": "US",
                    "isOpen": True,
                    "session": "regular",
                    "timezone": "America/New_York",
                    "t": 1700000000,
                }

                # Correct parameter name
                result = await finnhub_stock_market_data(
                    context,
                    "get_market_status",
                    exchange="US",
                )

                assert result["exchange"] == "US"
        finally:
            await context.aclose()
