"""Foreign exchange (forex) endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_forex_exchanges(
    client: FinnhubClient,
) -> list[str]:
    """Get list of supported forex exchanges.

    Returns:
        List of exchange names
    """
    return await client.get("/forex/exchange", params={})


async def get_forex_symbols(
    client: FinnhubClient,
    exchange: str,
) -> list[dict[str, Any]]:
    """Get list of forex symbols for a specific exchange.

    Args:
        client: Finnhub API client
        exchange: Exchange name

    Returns:
        List of forex symbols with metadata
    """
    params = {"exchange": exchange}
    return await client.get("/forex/symbol", params=params)


async def get_forex_candles(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
    from_timestamp: int,
    to_timestamp: int,
) -> dict[str, Any]:
    """Get historical forex price candles (OHLC data).

    Args:
        client: Finnhub API client
        symbol: Forex symbol (e.g., 'OANDA:EUR_USD')
        resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
        from_timestamp: Unix timestamp for start time
        to_timestamp: Unix timestamp for end time

    Returns:
        Candle data with OHLC arrays
    """
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_timestamp,
        "to": to_timestamp,
    }
    return await client.get("/forex/candle", params=params)


async def get_forex_rates(
    client: FinnhubClient,
    base: str | None = None,
    date: str | None = None,
) -> dict[str, Any]:
    """Get real-time forex exchange rates.

    Args:
        client: Finnhub API client
        base: Base currency (default: 'USD')
        date: Date in YYYY-MM-DD format for historical rates

    Returns:
        Forex rates data
    """
    params: dict[str, Any] = {}
    if base is not None:
        params["base"] = base
    if date is not None:
        params["date"] = date
    return await client.get("/forex/rates", params=params)
