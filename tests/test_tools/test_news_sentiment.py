"""Integration tests for NewsSentimentTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.news_sentiment import NewsSentimentTool

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


class TestNewsSentimentToolValidation:
    """Tests for validation methods."""

    def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validation passes for valid operations."""
        client = FinnhubClient(test_config)
        tool = NewsSentimentTool(client)

        for op in [
            "get_company_news",
            "get_market_news",
            "get_news_sentiment",
            "get_insider_sentiment",
        ]:
            tool.validate_operation(op)

    def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid operation."""
        client = FinnhubClient(test_config)
        tool = NewsSentimentTool(client)

        with pytest.raises(ValueError, match="Invalid operation"):
            tool.validate_operation("invalid_operation")

    def test_validate_category_valid(self, test_config: AppConfig):
        """Test validation passes for valid categories."""
        client = FinnhubClient(test_config)
        tool = NewsSentimentTool(client)

        for category in ["general", "forex", "crypto", "merger"]:
            tool.validate_category(category)

    def test_validate_category_invalid(self, test_config: AppConfig):
        """Test validation fails for invalid category."""
        client = FinnhubClient(test_config)
        tool = NewsSentimentTool(client)

        with pytest.raises(ValueError, match="Invalid category"):
            tool.validate_category("invalid")


class TestNewsSentimentToolGetCompanyNews:
    """Tests for get_company_news operation."""

    @respx.mock
    async def test_get_company_news(self, test_config: AppConfig):
        """Test getting company news."""
        news_data = [
            {
                "category": "company news",
                "datetime": 1609459200,
                "headline": "Apple announces new product",
                "id": 12345,
                "image": "https://example.com/image.jpg",
                "related": "AAPL",
                "source": "Reuters",
                "summary": "Apple unveils new iPhone model",
                "url": "https://example.com/article",
            }
        ]

        respx.get("https://finnhub.io/api/v1/company-news").mock(
            return_value=httpx.Response(200, json=news_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.get_company_news(
                symbol="AAPL",
                from_date="2021-01-01",
                to_date="2021-01-31",
            )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["headline"] == "Apple announces new product"


class TestNewsSentimentToolGetMarketNews:
    """Tests for get_market_news operation."""

    @respx.mock
    async def test_get_market_news(self, test_config: AppConfig):
        """Test getting market news."""
        news_data = [
            {
                "category": "general",
                "datetime": 1609459200,
                "headline": "Market update",
                "id": 12346,
                "image": "https://example.com/image2.jpg",
                "related": "",
                "source": "Bloomberg",
                "summary": "Markets rise on positive news",
                "url": "https://example.com/article2",
            }
        ]

        respx.get("https://finnhub.io/api/v1/news").mock(
            return_value=httpx.Response(200, json=news_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.get_market_news(category="general")

        assert isinstance(result, list)
        assert len(result) == 1

    @respx.mock
    async def test_get_market_news_with_invalid_category(self, test_config: AppConfig):
        """Test get_market_news rejects invalid category."""
        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)

            with pytest.raises(ValueError, match="Invalid category"):
                await tool.get_market_news(category="invalid")


class TestNewsSentimentToolGetNewsSentiment:
    """Tests for get_news_sentiment operation."""

    @respx.mock
    async def test_get_news_sentiment(self, test_config: AppConfig):
        """Test getting news sentiment."""
        sentiment_data = {
            "symbol": "AAPL",
            "companyNewsScore": 0.75,
            "sectorAverageBullishPercent": 0.60,
            "sectorAverageNewsScore": 0.65,
            "sentiment": {
                "bearishPercent": 0.25,
                "bullishPercent": 0.75,
            },
            "buzz": {
                "articlesInLastWeek": 100,
                "weeklyAverage": 75.0,
                "buzz": 1.33,
            },
        }

        respx.get("https://finnhub.io/api/v1/news-sentiment").mock(
            return_value=httpx.Response(200, json=sentiment_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.get_news_sentiment(symbol="AAPL")

        assert result["symbol"] == "AAPL"
        assert result["companyNewsScore"] == 0.75


class TestNewsSentimentToolGetInsiderSentiment:
    """Tests for get_insider_sentiment operation."""

    @respx.mock
    async def test_get_insider_sentiment(self, test_config: AppConfig):
        """Test getting insider sentiment."""
        insider_data = {
            "symbol": "AAPL",
            "data": [
                {"year": 2023, "month": 12, "change": 5000, "mspr": 0.65},
                {"year": 2023, "month": 11, "change": -2000, "mspr": 0.45},
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/insider-sentiment").mock(
            return_value=httpx.Response(200, json=insider_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.get_insider_sentiment(
                symbol="AAPL",
                from_date="2023-01-01",
                to_date="2023-12-31",
            )

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 2


class TestNewsSentimentToolExecute:
    """Tests for execute method (operation routing)."""

    @respx.mock
    async def test_execute_get_company_news(self, test_config: AppConfig):
        """Test execute routes to get_company_news."""
        news_data = [
            {
                "category": "company news",
                "datetime": 1609459200,
                "headline": "Test headline",
                "id": 12345,
                "image": "https://example.com/image.jpg",
                "related": "AAPL",
                "source": "Reuters",
                "summary": "Test summary",
                "url": "https://example.com/article",
            }
        ]

        respx.get("https://finnhub.io/api/v1/company-news").mock(
            return_value=httpx.Response(200, json=news_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.execute(
                operation="get_company_news",
                symbol="AAPL",
                from_date="2021-01-01",
                to_date="2021-01-31",
            )

        assert isinstance(result, list)
        assert len(result) == 1

    @respx.mock
    async def test_execute_get_market_news(self, test_config: AppConfig):
        """Test execute routes to get_market_news."""
        news_data = [
            {
                "category": "general",
                "datetime": 1609459200,
                "headline": "Test headline",
                "id": 12346,
                "image": "https://example.com/image2.jpg",
                "related": "",
                "source": "Bloomberg",
                "summary": "Test summary",
                "url": "https://example.com/article2",
            }
        ]

        respx.get("https://finnhub.io/api/v1/news").mock(
            return_value=httpx.Response(200, json=news_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.execute(
                operation="get_market_news",
                category="general",
            )

        assert isinstance(result, list)

    @respx.mock
    async def test_execute_get_news_sentiment(self, test_config: AppConfig):
        """Test execute routes to get_news_sentiment."""
        sentiment_data = {
            "symbol": "AAPL",
            "companyNewsScore": 0.75,
            "sectorAverageBullishPercent": 0.60,
            "sectorAverageNewsScore": 0.65,
            "sentiment": {"bearishPercent": 0.25, "bullishPercent": 0.75},
            "buzz": {"articlesInLastWeek": 100, "weeklyAverage": 75.0, "buzz": 1.33},
        }

        respx.get("https://finnhub.io/api/v1/news-sentiment").mock(
            return_value=httpx.Response(200, json=sentiment_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.execute(
                operation="get_news_sentiment",
                symbol="AAPL",
            )

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_insider_sentiment(self, test_config: AppConfig):
        """Test execute routes to get_insider_sentiment."""
        insider_data = {
            "symbol": "AAPL",
            "data": [{"year": 2023, "month": 12, "change": 5000, "mspr": 0.65}],
        }

        respx.get("https://finnhub.io/api/v1/stock/insider-sentiment").mock(
            return_value=httpx.Response(200, json=insider_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)
            result = await tool.execute(
                operation="get_insider_sentiment",
                symbol="AAPL",
                from_date="2023-01-01",
                to_date="2023-12-31",
            )

        assert result["symbol"] == "AAPL"

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute rejects invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = NewsSentimentTool(client)

            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute(
                    operation="invalid_op",
                    symbol="AAPL",
                )
