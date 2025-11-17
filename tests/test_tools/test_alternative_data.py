"""Tests for AlternativeDataTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.alternative_data import AlternativeDataTool

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
class TestAlternativeDataTool:
    """Test suite for AlternativeDataTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_esg_scores",
            "get_social_sentiment",
            "get_supply_chain",
            "get_patents",
        }
        assert expected_operations == AlternativeDataTool.VALID_OPERATIONS

    @respx.mock
    async def test_get_esg_scores(self, test_config: AppConfig):
        """Test get_esg_scores operation."""
        mock_data = {
            "symbol": "AAPL",
            "totalESG": 85.5,
            "environmentScore": 90.2,
            "socialScore": 82.3,
            "governanceScore": 84.0,
        }
        respx.get("https://finnhub.io/api/v1/stock/esg").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.get_esg_scores("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["totalESG"] == 85.5
        assert result["environmentScore"] == 90.2

    @respx.mock
    async def test_get_social_sentiment(self, test_config: AppConfig):
        """Test get_social_sentiment operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [
                {
                    "atTime": "2024-01-15T10:00:00Z",
                    "mention": 1500,
                    "positiveScore": 0.75,
                    "negativeScore": 0.25,
                    "score": 0.50,
                }
            ],
        }
        respx.get("https://finnhub.io/api/v1/stock/social-sentiment").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.get_social_sentiment("AAPL", "2024-01-01", "2024-01-31")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1
        assert result["data"][0]["mention"] == 1500

    @respx.mock
    async def test_get_social_sentiment_no_dates(self, test_config: AppConfig):
        """Test get_social_sentiment operation without date parameters."""
        mock_data = {
            "symbol": "AAPL",
            "data": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/social-sentiment").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.get_social_sentiment("AAPL")

        assert result["symbol"] == "AAPL"
        assert isinstance(result["data"], list)

    @respx.mock
    async def test_get_supply_chain(self, test_config: AppConfig):
        """Test get_supply_chain operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [
                {
                    "symbol": "TSM",
                    "name": "Taiwan Semiconductor Manufacturing",
                    "country": "TW",
                },
                {
                    "symbol": "QCOM",
                    "name": "Qualcomm Inc",
                    "country": "US",
                },
            ],
        }
        respx.get("https://finnhub.io/api/v1/stock/supply-chain").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.get_supply_chain("AAPL")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 2
        assert result["data"][0]["symbol"] == "TSM"

    @respx.mock
    async def test_get_patents(self, test_config: AppConfig):
        """Test get_patents operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [
                {
                    "applicationNumber": "16/123,456",
                    "filingDate": "2024-01-15",
                    "patentNumber": "US11234567B2",
                    "publicationDate": "2024-06-15",
                    "title": "Mobile Device Technology",
                    "url": "https://patents.uspto.gov/patent/US11234567B2",
                }
            ],
        }
        respx.get("https://finnhub.io/api/v1/stock/uspto-patent").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.get_patents("AAPL", "2024-01-01", "2024-12-31")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 1
        assert result["data"][0]["patentNumber"] == "US11234567B2"

    @respx.mock
    async def test_execute_get_esg_scores(self, test_config: AppConfig):
        """Test execute method with get_esg_scores operation."""
        mock_data = {
            "symbol": "AAPL",
            "totalESG": 85.5,
        }
        respx.get("https://finnhub.io/api/v1/stock/esg").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.execute("get_esg_scores", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_social_sentiment(self, test_config: AppConfig):
        """Test execute method with get_social_sentiment operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/social-sentiment").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.execute("get_social_sentiment", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_supply_chain(self, test_config: AppConfig):
        """Test execute method with get_supply_chain operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/supply-chain").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.execute("get_supply_chain", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_patents(self, test_config: AppConfig):
        """Test execute method with get_patents operation."""
        mock_data = {
            "symbol": "AAPL",
            "data": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/uspto-patent").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            result = await tool.execute(
                "get_patents",
                symbol="AAPL",
                from_date="2024-01-01",
                to_date="2024-12-31",
            )

        assert result["symbol"] == "AAPL"

    async def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validate_operation with valid operation."""
        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            # Should not raise
            tool.validate_operation("get_esg_scores")

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validate_operation with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = AlternativeDataTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_operation", symbol="AAPL")
