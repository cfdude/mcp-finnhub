"""Tests for news and sentiment API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import news
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


class TestGetCompanyNews:
    """Tests for get_company_news endpoint."""

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
            result = await news.get_company_news(client, "AAPL", "2021-01-01", "2021-01-31")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["headline"] == "Apple announces new product"


class TestGetMarketNews:
    """Tests for get_market_news endpoint."""

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
            result = await news.get_market_news(client, "general")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["category"] == "general"


class TestGetNewsSentiment:
    """Tests for get_news_sentiment endpoint."""

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
            result = await news.get_news_sentiment(client, "AAPL")

        assert result["symbol"] == "AAPL"
        assert result["companyNewsScore"] == 0.75


class TestGetInsiderSentiment:
    """Tests for get_insider_sentiment endpoint."""

    @respx.mock
    async def test_get_insider_sentiment(self, test_config: AppConfig):
        """Test getting insider sentiment."""
        insider_data = {
            "symbol": "AAPL",
            "data": [
                {
                    "year": 2023,
                    "month": 12,
                    "change": 5000,
                    "mspr": 0.65,
                },
                {
                    "year": 2023,
                    "month": 11,
                    "change": -2000,
                    "mspr": 0.45,
                },
            ],
        }

        respx.get("https://finnhub.io/api/v1/stock/insider-sentiment").mock(
            return_value=httpx.Response(200, json=insider_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await news.get_insider_sentiment(client, "AAPL", "2023-01-01", "2023-12-31")

        assert result["symbol"] == "AAPL"
        assert len(result["data"]) == 2
