"""Tests for StockOwnershipTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.stock_ownership import StockOwnershipTool

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
class TestStockOwnershipTool:
    """Test suite for StockOwnershipTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_insider_transactions",
            "get_institutional_ownership",
            "get_institutional_portfolio",
            "get_congressional_trades",
        }
        assert expected_operations == StockOwnershipTool.VALID_OPERATIONS

    @respx.mock
    async def test_get_insider_transactions(self, test_config: AppConfig):
        """Test get_insider_transactions operation."""
        mock_data = {
            "data": [
                {
                    "name": "John Doe",
                    "share": 100000,
                    "change": -5000,
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/insider-transactions").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            result = await tool.get_insider_transactions("AAPL")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_institutional_ownership(self, test_config: AppConfig):
        """Test get_institutional_ownership operation."""
        mock_data = {
            "cusip": "037833100",
            "data": [
                {
                    "reportDate": "2024-03-31",
                    "ownership": [{"name": "Test Fund"}],
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/institutional/ownership").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            result = await tool.get_institutional_ownership("AAPL", "2024-01-01", "2024-03-31")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_get_institutional_portfolio(self, test_config: AppConfig):
        """Test get_institutional_portfolio operation."""
        mock_data = {
            "cik": "1000097",
            "data": [
                {
                    "portfolio": [{"symbol": "AAPL"}],
                }
            ],
        }
        respx.get("https://finnhub.io/api/v1/institutional/portfolio").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            result = await tool.get_institutional_portfolio("1000097", "2024-01-01", "2024-03-31")

        assert result["cik"] == "1000097"

    @respx.mock
    async def test_get_congressional_trades(self, test_config: AppConfig):
        """Test get_congressional_trades operation."""
        mock_data = {
            "data": [
                {
                    "name": "Senator Smith",
                    "symbol": "AAPL",
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/congressional-trading").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            result = await tool.get_congressional_trades("AAPL", "2024-01-01", "2024-01-31")

        assert result["symbol"] == "AAPL"

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    @respx.mock
    async def test_execute_get_insider_transactions(self, test_config: AppConfig):
        """Test execute with get_insider_transactions operation."""
        mock_data = {
            "data": [{"name": "John Doe"}],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/insider-transactions").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            result = await tool.execute("get_insider_transactions", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute fails for invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = StockOwnershipTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_op", symbol="AAPL")
