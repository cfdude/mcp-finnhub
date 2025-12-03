"""News and sentiment API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_company_news(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> list[dict[str, Any]]:
    """Get company-specific news articles.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        from_date: From date (YYYY-MM-DD)
        to_date: To date (YYYY-MM-DD)

    Returns:
        List of news articles
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/company-news", params=params)


async def get_market_news(
    client: FinnhubClient,
    category: str,
) -> list[dict[str, Any]]:
    """Get general market news by category.

    Args:
        client: FinnhubClient instance
        category: News category (general, forex, crypto, merger)

    Returns:
        List of news articles
    """
    params = {"category": category}
    return await client.get("/news", params=params)


async def get_news_sentiment(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get news sentiment analysis for a symbol.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol

    Returns:
        News sentiment scores and statistics
    """
    params = {"symbol": symbol}
    return await client.get("/news-sentiment", params=params)


async def get_insider_sentiment(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Get insider trading sentiment.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        from_date: From date (YYYY-MM-DD)
        to_date: To date (YYYY-MM-DD)

    Returns:
        Insider sentiment data
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/stock/insider-sentiment", params=params)
