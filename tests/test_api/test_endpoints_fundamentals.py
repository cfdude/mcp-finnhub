"""Tests for fundamental data API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import fundamentals
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


class TestGetBasicFinancials:
    """Tests for get_basic_financials endpoint."""

    @respx.mock
    async def test_get_basic_financials(self, test_config: AppConfig):
        """Test getting basic financials."""
        financials_data = {
            "symbol": "AAPL",
            "metric": {
                "marketCapitalization": 2500000,
                "peBasicExclExtraTTM": 25.5,
                "roeTTM": 0.85,
                "netProfitMarginTTM": 0.25,
            },
        }

        respx.get("https://finnhub.io/api/v1/stock/metric").mock(
            return_value=httpx.Response(200, json=financials_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_basic_financials(client, "AAPL")

        assert result["symbol"] == "AAPL"
        assert "metric" in result


class TestGetReportedFinancials:
    """Tests for get_reported_financials endpoint."""

    @respx.mock
    async def test_get_reported_financials_annual(self, test_config: AppConfig):
        """Test getting annual reported financials."""
        reported_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "0000320193-23-000077",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2022-09-25",
                    "endDate": "2023-09-30",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=reported_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_reported_financials(client, "AAPL", "annual")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_reported_financials_quarterly(self, test_config: AppConfig):
        """Test getting quarterly reported financials."""
        reported_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "0000320193-23-000106",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 4,
                    "form": "10-Q",
                    "startDate": "2023-07-02",
                    "endDate": "2023-09-30",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:04:01",
                    "report": {},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials-reported").mock(
            return_value=httpx.Response(200, json=reported_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_reported_financials(client, "AAPL", "quarterly")

        assert result["symbol"] == "AAPL"
        assert result["data"][0]["quarter"] == 4


class TestGetSecFinancials:
    """Tests for get_sec_financials endpoint."""

    @respx.mock
    async def test_get_sec_financials_balance_sheet(self, test_config: AppConfig):
        """Test getting SEC balance sheet."""
        sec_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "0000320193-23-000077",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2022-09-25",
                    "endDate": "2023-09-30",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {"bs": []},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials").mock(
            return_value=httpx.Response(200, json=sec_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_sec_financials(client, "AAPL", "bs", "annual")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_sec_financials_income_statement(self, test_config: AppConfig):
        """Test getting SEC income statement."""
        sec_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "0000320193-23-000077",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": 0,
                    "form": "10-K",
                    "startDate": "2022-09-25",
                    "endDate": "2023-09-30",
                    "filedDate": "2023-11-03",
                    "acceptedDate": "2023-11-03 18:01:14",
                    "report": {"ic": []},
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/financials").mock(
            return_value=httpx.Response(200, json=sec_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_sec_financials(client, "AAPL", "ic")

        assert result["symbol"] == "AAPL"


class TestGetDividends:
    """Tests for get_dividends endpoint."""

    @respx.mock
    async def test_get_dividends(self, test_config: AppConfig):
        """Test getting dividend history."""
        dividends_data = [
            {
                "symbol": "AAPL",
                "date": "2023-11-10",
                "amount": 0.24,
                "adjustedAmount": 0.24,
                "payDate": "2023-11-16",
                "recordDate": "2023-11-13",
                "declarationDate": "2023-11-02",
                "currency": "USD",
            },
            {
                "symbol": "AAPL",
                "date": "2023-08-11",
                "amount": 0.24,
                "adjustedAmount": 0.24,
                "payDate": "2023-08-17",
                "recordDate": "2023-08-14",
                "declarationDate": "2023-08-03",
                "currency": "USD",
            },
        ]

        respx.get("https://finnhub.io/api/v1/stock/dividend").mock(
            return_value=httpx.Response(200, json=dividends_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_dividends(client, "AAPL", "2023-01-01", "2023-12-31")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["amount"] == 0.24


class TestGetSplits:
    """Tests for get_splits endpoint."""

    @respx.mock
    async def test_get_splits(self, test_config: AppConfig):
        """Test getting stock split history."""
        splits_data = [
            {
                "symbol": "AAPL",
                "date": "2020-08-31",
                "fromFactor": 1.0,
                "toFactor": 4.0,
            }
        ]

        respx.get("https://finnhub.io/api/v1/stock/split").mock(
            return_value=httpx.Response(200, json=splits_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_splits(client, "AAPL", "2020-01-01", "2023-12-31")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["fromFactor"] == 1.0
        assert result[0]["toFactor"] == 4.0


class TestGetRevenueBreakdown:
    """Tests for get_revenue_breakdown endpoint."""

    @respx.mock
    async def test_get_revenue_breakdown(self, test_config: AppConfig):
        """Test getting revenue breakdown."""
        revenue_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [
                {
                    "accessNumber": "0000320193-23-000077",
                    "symbol": "AAPL",
                    "cik": "0000320193",
                    "year": 2023,
                    "quarter": None,
                    "breakdown": [
                        {"product": "iPhone", "revenue": 200616000000},
                        {"product": "Mac", "revenue": 29357000000},
                    ],
                }
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/revenue-breakdown").mock(
            return_value=httpx.Response(200, json=revenue_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_revenue_breakdown(client, "AAPL")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1

    @respx.mock
    async def test_get_revenue_breakdown_with_cik(self, test_config: AppConfig):
        """Test getting revenue breakdown with CIK."""
        revenue_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "data": [],
        }

        respx.get("https://finnhub.io/api/v1/stock/revenue-breakdown").mock(
            return_value=httpx.Response(200, json=revenue_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await fundamentals.get_revenue_breakdown(client, "AAPL", cik="0000320193")

        assert result["symbol"] == "AAPL"
        assert result["cik"] == "0000320193"
