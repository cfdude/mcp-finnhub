"""Calendar endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_ipo_calendar(
    client: FinnhubClient,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Get IPO calendar.

    Args:
        client: Finnhub API client
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        IPO calendar data
    """
    params = {"from": from_date, "to": to_date}
    return await client.get("/calendar/ipo", params=params)


async def get_earnings_calendar(
    client: FinnhubClient,
    from_date: str | None = None,
    to_date: str | None = None,
    symbol: str | None = None,
) -> dict[str, Any]:
    """Get earnings calendar.

    Args:
        client: Finnhub API client
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        symbol: Filter by symbol

    Returns:
        Earnings calendar data
    """
    params: dict[str, Any] = {}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if symbol is not None:
        params["symbol"] = symbol
    return await client.get("/calendar/earnings", params=params)


async def get_economic_calendar(
    client: FinnhubClient,
) -> dict[str, Any]:
    """Get economic events calendar.

    Args:
        client: Finnhub API client

    Returns:
        Economic calendar data
    """
    return await client.get("/calendar/economic", params={})


async def get_fda_calendar(
    client: FinnhubClient,
) -> list[dict[str, Any]]:
    """Get FDA committee meeting calendar.

    Args:
        client: Finnhub API client

    Returns:
        FDA calendar data
    """
    return await client.get("/fda-advisory-committee-calendar", params={})
