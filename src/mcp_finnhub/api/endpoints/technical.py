"""Technical analysis API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


async def get_indicator(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
    from_timestamp: int,
    to_timestamp: int,
    indicator: str,
    **indicator_params: Any,
) -> dict[str, Any]:
    """Get technical indicator values.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)
        from_timestamp: From Unix timestamp
        to_timestamp: To Unix timestamp
        indicator: Indicator name (sma, ema, rsi, macd, bbands, stoch, adx, cci, etc.)
        **indicator_params: Indicator-specific parameters (timeperiod, etc.)

    Returns:
        Indicator data with timestamps and values

    Example:
        >>> data = await get_indicator(
        ...     client, "AAPL", "D", 1609459200, 1640995200,
        ...     "rsi", timeperiod=14
        ... )
    """
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_timestamp,
        "to": to_timestamp,
        "indicator": indicator,
        **indicator_params,
    }
    return await client.get("/indicator", params=params)


async def aggregate_signals(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
) -> dict[str, Any]:
    """Get aggregated technical indicator signals (buy/sell/hold).

    Provides consensus signals across multiple technical indicators.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)

    Returns:
        Aggregated signals with buy/sell/hold recommendations

    Example:
        >>> signals = await aggregate_signals(client, "AAPL", "D")
    """
    params = {"symbol": symbol, "resolution": resolution}
    return await client.get("/scan/technical-indicator", params=params)


async def scan_patterns(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
) -> dict[str, Any]:
    """Scan for chart patterns.

    Detects patterns like Head & Shoulders, triangles, candlestick patterns, etc.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)

    Returns:
        Detected patterns with confidence scores

    Example:
        >>> patterns = await scan_patterns(client, "AAPL", "D")
    """
    params = {"symbol": symbol, "resolution": resolution}
    return await client.get("/scan/pattern", params=params)


async def support_resistance(
    client: FinnhubClient,
    symbol: str,
    resolution: str,
) -> dict[str, Any]:
    """Get support and resistance levels.

    Identifies key support and resistance price levels.

    Args:
        client: FinnhubClient instance
        symbol: Stock symbol
        resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)

    Returns:
        Support and resistance levels

    Example:
        >>> levels = await support_resistance(client, "AAPL", "D")
    """
    params = {"symbol": symbol, "resolution": resolution}
    return await client.get("/scan/support-resistance", params=params)
