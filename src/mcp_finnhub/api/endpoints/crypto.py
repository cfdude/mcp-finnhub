"""Cryptocurrency endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_crypto_exchanges(
    client: FinnhubClient,
) -> list[str]:
    """Get list of supported cryptocurrency exchanges.

    Returns:
        List of exchange names
    """
    return await client.get("/crypto/exchange", params={})


async def get_crypto_symbols(
    client: FinnhubClient,
    exchange: str,
) -> list[dict[str, Any]]:
    """Get list of cryptocurrency symbols for a specific exchange.

    Args:
        client: Finnhub API client
        exchange: Exchange name (e.g., 'binance', 'coinbase')

    Returns:
        List of crypto symbols with metadata
    """
    params = {"exchange": exchange}
    return await client.get("/crypto/symbol", params=params)


async def get_crypto_profile(
    client: FinnhubClient,
    symbol: str,
) -> dict[str, Any]:
    """Get detailed profile information for a cryptocurrency.

    Args:
        client: Finnhub API client
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')

    Returns:
        Crypto profile data
    """
    params = {"symbol": symbol}
    return await client.get("/crypto/profile", params=params)


async def get_crypto_candles(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
    from_timestamp: int,
    to_timestamp: int,
) -> dict[str, Any]:
    """Get historical cryptocurrency price candles (OHLCV data).

    Args:
        client: Finnhub API client
        symbol: Crypto symbol with exchange prefix (e.g., 'BINANCE:BTCUSDT')
        resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
        from_timestamp: Unix timestamp for start time
        to_timestamp: Unix timestamp for end time

    Returns:
        Candle data with OHLCV arrays
    """
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_timestamp,
        "to": to_timestamp,
    }
    return await client.get("/crypto/candle", params=params)
