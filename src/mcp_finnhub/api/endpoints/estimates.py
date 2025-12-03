"""Finnhub stock estimates endpoints.

This module provides functions for fetching stock estimates data from the Finnhub API.
"""

from typing import Any

from mcp_finnhub.api.client import FinnhubClient


async def get_earnings_estimates(
    client: FinnhubClient,
    symbol: str,
    freq: str | None = None,
) -> dict[str, Any]:
    """Get company EPS (earnings per share) estimates.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

    Returns:
        EPS estimates data including analyst consensus
    """
    params: dict[str, Any] = {"symbol": symbol}
    if freq is not None:
        params["freq"] = freq
    return await client.get("/stock/eps-estimate", params=params)


async def get_revenue_estimates(
    client: FinnhubClient,
    symbol: str,
    freq: str | None = None,
) -> dict[str, Any]:
    """Get company revenue estimates.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

    Returns:
        Revenue estimates data including analyst consensus
    """
    params: dict[str, Any] = {"symbol": symbol}
    if freq is not None:
        params["freq"] = freq
    return await client.get("/stock/revenue-estimate", params=params)


async def get_ebitda_estimates(
    client: FinnhubClient,
    symbol: str,
    freq: str | None = None,
) -> dict[str, Any]:
    """Get company EBITDA estimates.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

    Returns:
        EBITDA estimates data including analyst consensus
    """
    params: dict[str, Any] = {"symbol": symbol}
    if freq is not None:
        params["freq"] = freq
    return await client.get("/stock/ebitda-estimate", params=params)


async def get_price_targets(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get latest price target consensus.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Price target data including high, low, mean, and median targets
    """
    params = {"symbol": symbol}
    return await client.get("/stock/price-target", params=params)


async def get_recommendations(
    client: FinnhubClient,
    symbol: str,
) -> list[dict[str, Any]]:
    """Get latest analyst recommendation trends.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        List of recommendation trend data by period
    """
    params = {"symbol": symbol}
    return await client.get("/stock/recommendation", params=params)
