"""Finnhub stock ownership endpoints.

This module provides functions for fetching stock ownership and insider trading data
from the Finnhub API.
"""

from typing import Any

from mcp_finnhub.api.client import FinnhubClient


async def get_insider_transactions(
    client: FinnhubClient,
    symbol: str,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """Get insider transaction data for a company.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format (optional)
        to_date: To date in YYYY-MM-DD format (optional)

    Returns:
        Insider transactions data
    """
    params: dict[str, Any] = {"symbol": symbol}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    return await client.get("/stock/insider-transactions", params=params)


async def get_institutional_ownership(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
    cusip: str | None = None,
) -> dict[str, Any]:
    """Get institutional ownership data for a stock.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format
        to_date: To date in YYYY-MM-DD format
        cusip: CUSIP identifier (optional)

    Returns:
        Institutional ownership data from 13-F filings
    """
    params: dict[str, Any] = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    if cusip is not None:
        params["cusip"] = cusip
    return await client.get("/institutional/ownership", params=params)


async def get_institutional_portfolio(
    client: FinnhubClient,
    cik: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Get institutional investor portfolio holdings.

    Args:
        client: The Finnhub API client
        cik: Central Index Key (CIK) of the institutional investor
        from_date: From date in YYYY-MM-DD format
        to_date: To date in YYYY-MM-DD format

    Returns:
        Portfolio holdings data from 13-F filings
    """
    params = {
        "cik": cik,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/institutional/portfolio", params=params)


async def get_congressional_trades(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Get congressional trading data for a stock.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format
        to_date: To date in YYYY-MM-DD format

    Returns:
        Congressional trading disclosure data
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/stock/congressional-trading", params=params)
