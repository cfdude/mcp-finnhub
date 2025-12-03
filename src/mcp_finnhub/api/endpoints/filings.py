"""Finnhub SEC filings endpoints.

This module provides functions for fetching SEC filing data from the Finnhub API.
"""

from typing import Any

from mcp_finnhub.api.client import FinnhubClient


async def get_sec_filings(
    client: FinnhubClient,
    symbol: str,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dict[str, Any]]:
    """Get SEC filings for a company.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        from_date: From date in YYYY-MM-DD format (optional)
        to_date: To date in YYYY-MM-DD format (optional)

    Returns:
        List of SEC filing data
    """
    params: dict[str, Any] = {"symbol": symbol}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    return await client.get("/stock/filings", params=params)


async def get_filing_sentiment(
    client: FinnhubClient,
    access_number: str,
) -> dict[str, Any]:
    """Get sentiment analysis for a specific SEC filing.

    Args:
        client: The Finnhub API client
        access_number: SEC filing access number

    Returns:
        Filing sentiment analysis data
    """
    params = {"accessNumber": access_number}
    return await client.get("/stock/filings-sentiment", params=params)


async def get_similarity_index(
    client: FinnhubClient,
    symbol: str,
    cik: str | None = None,
    freq: str = "annual",
) -> dict[str, Any]:
    """Get filing similarity index to detect boilerplate changes.

    Args:
        client: The Finnhub API client
        symbol: Stock symbol (e.g., 'AAPL')
        cik: Company CIK (optional)
        freq: Frequency - 'annual' or 'quarterly' (default: 'annual')

    Returns:
        Similarity index data
    """
    params: dict[str, Any] = {"symbol": symbol, "freq": freq}
    if cik is not None:
        params["cik"] = cik
    return await client.get("/stock/similarity-index", params=params)
