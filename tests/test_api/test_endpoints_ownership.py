"""Tests for ownership endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import ownership
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
class TestOwnershipEndpoints:
    """Test suite for ownership endpoints."""

    @respx.mock
    async def test_get_insider_transactions(self, test_config: AppConfig):
        """Test get_insider_transactions endpoint."""
        mock_data = {
            "data": [
                {
                    "name": "John Doe",
                    "share": 100000,
                    "change": -5000,
                    "filingDate": "2024-01-15",
                    "transactionDate": "2024-01-10",
                    "transactionCode": "S",
                    "transactionPrice": 150.25,
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/insider-transactions").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await ownership.get_insider_transactions(
                client, "AAPL", "2024-01-01", "2024-01-31"
            )

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "John Doe"

    @respx.mock
    async def test_get_institutional_ownership(self, test_config: AppConfig):
        """Test get_institutional_ownership endpoint."""
        mock_data = {
            "cusip": "037833100",
            "data": [
                {
                    "reportDate": "2024-03-31",
                    "ownership": [
                        {
                            "change": 1000,
                            "cik": "1234567",
                            "name": "Test Fund",
                            "share": 50000,
                            "value": 7500000,
                        }
                    ],
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/institutional/ownership").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await ownership.get_institutional_ownership(
                client, "AAPL", "2024-01-01", "2024-03-31"
            )

        assert result["symbol"] == "AAPL"
        assert result["cusip"] == "037833100"

    @respx.mock
    async def test_get_institutional_portfolio(self, test_config: AppConfig):
        """Test get_institutional_portfolio endpoint."""
        mock_data = {
            "cik": "1000097",
            "name": "Test Investment Fund",
            "data": [
                {
                    "filingDate": "2024-03-31",
                    "reportDate": "2024-03-31",
                    "portfolio": [
                        {
                            "symbol": "AAPL",
                            "name": "Apple Inc",
                            "share": 100000,
                            "value": 15000000,
                        }
                    ],
                }
            ],
        }
        respx.get("https://finnhub.io/api/v1/institutional/portfolio").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await ownership.get_institutional_portfolio(
                client, "1000097", "2024-01-01", "2024-03-31"
            )

        assert result["cik"] == "1000097"
        assert result["name"] == "Test Investment Fund"

    @respx.mock
    async def test_get_congressional_trades(self, test_config: AppConfig):
        """Test get_congressional_trades endpoint."""
        mock_data = {
            "data": [
                {
                    "amountFrom": 1001,
                    "amountTo": 15000,
                    "assetName": "Apple Inc",
                    "filingDate": "2024-01-15",
                    "name": "Senator Smith",
                    "position": "senator",
                    "symbol": "AAPL",
                    "transactionDate": "2024-01-10",
                    "transactionType": "Purchase",
                }
            ],
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/congressional-trading").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await ownership.get_congressional_trades(
                client, "AAPL", "2024-01-01", "2024-01-31"
            )

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Senator Smith"
