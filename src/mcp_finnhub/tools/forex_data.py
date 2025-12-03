"""Tool for accessing foreign exchange (forex) data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import forex
from mcp_finnhub.api.models.forex import ForexCandleResponse, ForexRate, ForexSymbol

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class ForexDataTool:
    """Tool for accessing forex market data.

    Provides 4 operations:
    - get_forex_exchanges: Get list of supported forex exchanges
    - get_forex_symbols: Get forex symbols by exchange
    - get_forex_candles: Get historical forex price data (OHLC)
    - get_forex_rates: Get real-time forex exchange rates
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_forex_exchanges",
        "get_forex_symbols",
        "get_forex_candles",
        "get_forex_rates",
    }

    VALID_RESOLUTIONS: ClassVar[set[str]] = {"1", "5", "15", "30", "60", "D", "W", "M"}

    def __init__(self, client: FinnhubClient):
        """Initialize forex data tool.

        Args:
            client: Finnhub API client instance
        """
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate that operation is supported.

        Args:
            operation: Operation name to validate

        Raises:
            ValueError: If operation is not valid
        """
        if operation not in self.VALID_OPERATIONS:
            valid_ops = ", ".join(sorted(self.VALID_OPERATIONS))
            raise ValueError(f"Invalid operation: {operation}. Valid operations: {valid_ops}")

    def validate_resolution(self, resolution: str) -> None:
        """Validate candle resolution.

        Args:
            resolution: Resolution to validate

        Raises:
            ValueError: If resolution is not valid
        """
        if resolution not in self.VALID_RESOLUTIONS:
            valid_res = ", ".join(sorted(self.VALID_RESOLUTIONS))
            raise ValueError(f"Invalid resolution: {resolution}. Valid resolutions: {valid_res}")

    async def get_forex_exchanges(self) -> list[str]:
        """Get list of supported forex exchanges.

        Returns:
            List of exchange names
        """
        response = await forex.get_forex_exchanges(self.client)
        return response

    async def get_forex_symbols(self, exchange: str) -> list[dict[str, Any]]:
        """Get forex symbols for a specific exchange.

        Args:
            exchange: Exchange name

        Returns:
            List of forex symbols with metadata
        """
        response = await forex.get_forex_symbols(self.client, exchange)
        models = [ForexSymbol(**symbol) for symbol in response]
        return [model.model_dump() for model in models]

    async def get_forex_candles(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> dict[str, Any]:
        """Get historical forex price candles.

        Args:
            symbol: Forex symbol (e.g., 'OANDA:EUR_USD')
            resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
            from_timestamp: Unix timestamp for start time
            to_timestamp: Unix timestamp for end time

        Returns:
            Candle data with OHLC arrays

        Raises:
            ValueError: If resolution is invalid
        """
        self.validate_resolution(resolution)
        response = await forex.get_forex_candles(
            self.client, symbol, resolution, from_timestamp, to_timestamp
        )
        model = ForexCandleResponse(**response)
        return model.model_dump()

    async def get_forex_rates(
        self, base: str | None = None, date: str | None = None
    ) -> dict[str, Any]:
        """Get real-time forex exchange rates.

        Args:
            base: Base currency (default: 'USD')
            date: Date for historical rates (YYYY-MM-DD)

        Returns:
            Forex rates data
        """
        response = await forex.get_forex_rates(self.client, base, date)
        model = ForexRate(**response)
        return model.model_dump()

    async def execute(
        self, operation: str, **params: Any
    ) -> list[str] | list[dict[str, Any]] | dict[str, Any]:
        """Execute a forex data operation.

        Args:
            operation: Operation to execute
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid or unknown
        """
        self.validate_operation(operation)

        if operation == "get_forex_exchanges":
            return await self.get_forex_exchanges()
        elif operation == "get_forex_symbols":
            return await self.get_forex_symbols(**params)
        elif operation == "get_forex_candles":
            return await self.get_forex_candles(**params)
        elif operation == "get_forex_rates":
            return await self.get_forex_rates(**params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
