"""Fundamental data API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_basic_financials(
    client: FinnhubClient,
    symbol: str,
    metric: str = "all",
) -> dict[str, Any]:
    """Get basic financial metrics for a company.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        metric: Metric type (all, price, valuation, margin, etc.)

    Returns:
        Basic financial metrics
    """
    params = {
        "symbol": symbol,
        "metric": metric,
    }
    return await client.get("/stock/metric", params=params)


async def get_reported_financials(
    client: FinnhubClient,
    symbol: str,
    freq: str = "annual",
) -> dict[str, Any]:
    """Get company's reported financials as reported to SEC.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        freq: Frequency (annual or quarterly)

    Returns:
        Reported financial statements
    """
    params = {
        "symbol": symbol,
        "freq": freq,
    }
    return await client.get("/stock/financials-reported", params=params)


async def get_sec_financials(
    client: FinnhubClient,
    symbol: str,
    statement: str,
    freq: str = "annual",
) -> dict[str, Any]:
    """Get standardized SEC financial statements.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        statement: Statement type (bs, ic, cf)
        freq: Frequency (annual or quarterly)

    Returns:
        SEC-standardized financial data
    """
    params = {
        "symbol": symbol,
        "statement": statement,
        "freq": freq,
    }
    return await client.get("/stock/financials", params=params)


async def get_dividends(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> list[dict[str, Any]]:
    """Get dividend history.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        from_date: From date (YYYY-MM-DD)
        to_date: To date (YYYY-MM-DD)

    Returns:
        List of dividend payments
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/stock/dividend", params=params)


async def get_splits(
    client: FinnhubClient,
    symbol: str,
    from_date: str,
    to_date: str,
) -> list[dict[str, Any]]:
    """Get stock split history.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        from_date: From date (YYYY-MM-DD)
        to_date: To date (YYYY-MM-DD)

    Returns:
        List of stock splits
    """
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
    }
    return await client.get("/stock/split", params=params)


async def get_revenue_breakdown(
    client: FinnhubClient,
    symbol: str,
    cik: str | None = None,
) -> dict[str, Any]:
    """Get revenue breakdown by product and geography.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        cik: Optional CIK number

    Returns:
        Revenue breakdown data
    """
    params = {"symbol": symbol}
    if cik:
        params["cik"] = cik

    return await client.get("/stock/revenue-breakdown", params=params)
