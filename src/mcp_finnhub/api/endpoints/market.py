"""Market data API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_quote(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get real-time quote data for a symbol.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol

    Returns:
        Real-time quote data
    """
    params = {"symbol": symbol}
    return await client.get("/quote", params=params)


async def get_candles(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
    from_timestamp: int,
    to_timestamp: int,
) -> dict[str, Any]:
    """Get historical OHLC (candlestick) data.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)
        from_timestamp: From Unix timestamp
        to_timestamp: To Unix timestamp

    Returns:
        Historical OHLC data
    """
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_timestamp,
        "to": to_timestamp,
    }
    return await client.get("/stock/candle", params=params)


async def get_company_profile(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get company profile information.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol

    Returns:
        Company profile data
    """
    params = {"symbol": symbol}
    return await client.get("/stock/profile2", params=params)


async def get_market_status(
    client: FinnhubClient,
    exchange: str,
) -> dict[str, Any]:
    """Get market status (open/closed) for an exchange.

    Args:
        client: FinnhubClient instance
        exchange: Exchange code (US, UK, etc.)

    Returns:
        Market status information
    """
    params = {"exchange": exchange}
    return await client.get("/stock/market-status", params=params)


async def get_symbols(
    client: FinnhubClient,
    exchange: str,
) -> list[dict[str, Any]]:
    """Get list of supported symbols for an exchange.

    Args:
        client: FinnhubClient instance
        exchange: Exchange code (US, UK, etc.)

    Returns:
        List of symbol information
    """
    params = {"exchange": exchange}
    return await client.get("/stock/symbol", params=params)


async def search_symbols(
    client: FinnhubClient,
    query: str,
) -> dict[str, Any]:
    """Search for symbols by name or ticker.

    Args:
        client: FinnhubClient instance
        query: Search query (symbol or company name)

    Returns:
        Search results with matching symbols
    """
    params = {"q": query}
    return await client.get("/search", params=params)


async def get_financials(
    client: FinnhubClient,
    symbol: str,
    statement: str,
    freq: str,
) -> dict[str, Any]:
    """Get financial statements.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        statement: Statement type (bs=balance sheet, ic=income, cf=cash flow)
        freq: Frequency (annual, quarterly)

    Returns:
        Financial statement data
    """
    params = {
        "symbol": symbol,
        "statement": statement,
        "freq": freq,
    }
    return await client.get("/stock/financials-reported", params=params)


async def get_earnings(
    client: FinnhubClient,
    symbol: str,
) -> list[dict[str, Any]]:
    """Get earnings data.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol

    Returns:
        Historical earnings data
    """
    params = {"symbol": symbol}
    return await client.get("/stock/earnings", params=params)
