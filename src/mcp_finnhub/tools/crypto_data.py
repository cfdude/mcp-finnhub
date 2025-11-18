"""Tool for accessing cryptocurrency data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import crypto
from mcp_finnhub.api.models.crypto import CryptoCandleResponse, CryptoProfile, CryptoSymbol

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class CryptoDataTool:
    """Tool for accessing cryptocurrency market data.

    Provides 4 operations:
    - get_crypto_exchanges: Get list of supported crypto exchanges
    - get_crypto_symbols: Get crypto symbols by exchange
    - get_crypto_profile: Get detailed crypto profile
    - get_crypto_candles: Get historical crypto price data (OHLCV)
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_crypto_exchanges",
        "get_crypto_symbols",
        "get_crypto_profile",
        "get_crypto_candles",
    }

    VALID_RESOLUTIONS: ClassVar[set[str]] = {"1", "5", "15", "30", "60", "D", "W", "M"}

    def __init__(self, client: FinnhubClient):
        """Initialize crypto data tool.

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

    async def get_crypto_exchanges(self) -> list[str]:
        """Get list of supported cryptocurrency exchanges.

        Returns:
            List of exchange names
        """
        response = await crypto.get_crypto_exchanges(self.client)
        return response

    async def get_crypto_symbols(self, exchange: str) -> list[dict[str, Any]]:
        """Get cryptocurrency symbols for a specific exchange.

        Args:
            exchange: Exchange name (e.g., 'binance', 'coinbase')

        Returns:
            List of crypto symbols with metadata
        """
        response = await crypto.get_crypto_symbols(self.client, exchange)
        models = [CryptoSymbol(**symbol) for symbol in response]
        return [model.model_dump() for model in models]

    async def get_crypto_profile(self, symbol: str) -> dict[str, Any]:
        """Get detailed profile for a cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')

        Returns:
            Crypto profile data
        """
        response = await crypto.get_crypto_profile(self.client, symbol)
        model = CryptoProfile(**response)
        return model.model_dump()

    async def get_crypto_candles(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> dict[str, Any]:
        """Get historical cryptocurrency price candles.

        Args:
            symbol: Crypto symbol with exchange (e.g., 'BINANCE:BTCUSDT')
            resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
            from_timestamp: Unix timestamp for start time
            to_timestamp: Unix timestamp for end time

        Returns:
            Candle data with OHLCV arrays

        Raises:
            ValueError: If resolution is invalid
        """
        self.validate_resolution(resolution)
        response = await crypto.get_crypto_candles(
            self.client, symbol, resolution, from_timestamp, to_timestamp
        )
        model = CryptoCandleResponse(**response)
        return model.model_dump()

    async def execute(
        self, operation: str, **params: Any
    ) -> list[str] | list[dict[str, Any]] | dict[str, Any]:
        """Execute a crypto data operation.

        Args:
            operation: Operation to execute
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid or unknown
        """
        self.validate_operation(operation)

        if operation == "get_crypto_exchanges":
            return await self.get_crypto_exchanges()
        elif operation == "get_crypto_symbols":
            return await self.get_crypto_symbols(**params)
        elif operation == "get_crypto_profile":
            return await self.get_crypto_profile(**params)
        elif operation == "get_crypto_candles":
            return await self.get_crypto_candles(**params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
