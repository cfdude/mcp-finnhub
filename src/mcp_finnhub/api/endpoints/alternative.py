"""Finnhub alternative data endpoints.

This module provides functions for fetching alternative data from the Finnhub API.
"""

from typing import Any

from mcp_finnhub.api.client import FinnhubClient


async def get_esg_scores(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get ESG (Environmental, Social, Governance) scores for a company.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        ESG scores data
    """
    params = {"symbol": symbol}
    return await client.get("/stock/esg", params=params)


async def get_social_sentiment(
    client: FinnhubClient,
    symbol: str,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Get social sentiment data from Reddit and Twitter.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format (optional)
        to_date: To date in YYYY-MM-DD format (optional)

    Returns:
        Social sentiment data
    """
    params: dict[str, Any] = {"symbol": symbol}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    return await client.get("/stock/social-sentiment", params=params)


async def get_supply_chain(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get company supply chain relationships.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Supply chain data including customers and suppliers
    """
    params = {"symbol": symbol}
    return await client.get("/stock/supply-chain", params=params)


async def get_patents(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Get USPTO patent data for a company.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format
        to_date: To date in YYYY-MM-DD format

    Returns:
        Patent application and grant data
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/stock/uspto-patent", params=params)
