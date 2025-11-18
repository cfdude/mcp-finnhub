"""Market events endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_market_holidays(
    client: FinnhubClient,
    exchange: str,
) -> dict[str, Any]:
    """Get market holiday calendar for an exchange.

    Args:
        client: Finnhub API client
        exchange: Exchange code (e.g., 'US', 'UK')

    Returns:
        Market holiday data
    """
    params = {"exchange": exchange}
    return await client.get("/stock/market-holiday", params=params)


async def get_upgrade_downgrade(
    client: FinnhubClient,
    symbol: str,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dict[str, Any]]:
    """Get analyst upgrade/downgrade history.

    Args:
        client: Finnhub API client
        symbol: Stock symbol
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        List of upgrade/downgrade events
    """
    params: dict[str, Any] = {"symbol": symbol}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    return await client.get("/stock/upgrade-downgrade", params=params)


async def get_merger_acquisition(
    client: FinnhubClient,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dict[str, Any]]:
    """Get M&A news and announcements.

    Args:
        client: Finnhub API client
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        List of M&A events
    """
    params: dict[str, Any] = {}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    return await client.get("/stock/merger-acquisition", params=params)
