"""Stock market data MCP tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import market
from mcp_finnhub.api.models.common import (
    CandleResponse,
    CompanyProfile,
    MarketStatusResponse,
    QuoteResponse,
)
from mcp_finnhub.api.models.market import (
    EarningsResponse,
    FinancialsResponse,
    SymbolSearchResponse,
)

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class StockMarketDataTool:
    """Stock market data tool with 8 operations."""

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_quote",
        "get_candles",
        "get_company_profile",
        "get_market_status",
        "get_symbols",
        "search_symbols",
        "get_financials",
        "get_earnings",
    }

    VALID_RESOLUTIONS: ClassVar[set[str]] = {"1", "5", "15", "30", "60", "D", "W", "M"}

    VALID_STATEMENTS: ClassVar[set[str]] = {"bs", "ic", "cf"}

    VALID_FREQUENCIES: ClassVar[set[str]] = {"annual", "quarterly"}

    def __init__(self, client: FinnhubClient):
        """Initialize stock market data tool.

        Args:
            client: FinnhubClient instance
        """
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate operation name.

        Args:
            operation: Operation to validate

        Raises:
            ValueError: If operation is invalid
        """
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation: {operation}. "
                f"Valid operations: {', '.join(sorted(self.VALID_OPERATIONS))}"
            )

    def validate_resolution(self, resolution: str) -> None:
        """Validate time resolution.

        Args:
            resolution: Resolution to validate

        Raises:
            ValueError: If resolution is invalid
        """
        if resolution not in self.VALID_RESOLUTIONS:
            raise ValueError(
                f"Invalid resolution: {resolution}. "
                f"Valid resolutions: {', '.join(sorted(self.VALID_RESOLUTIONS))}"
            )

    def validate_statement(self, statement: str) -> None:
        """Validate financial statement type.

        Args:
            statement: Statement type to validate

        Raises:
            ValueError: If statement type is invalid
        """
        if statement not in self.VALID_STATEMENTS:
            raise ValueError(
                f"Invalid statement: {statement}. "
                f"Valid statements: {', '.join(sorted(self.VALID_STATEMENTS))}"
            )

    def validate_frequency(self, freq: str) -> None:
        """Validate financial report frequency.

        Args:
            freq: Frequency to validate

        Raises:
            ValueError: If frequency is invalid
        """
        if freq not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency: {freq}. "
                f"Valid frequencies: {', '.join(sorted(self.VALID_FREQUENCIES))}"
            )

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Get real-time quote data.

        Args:
            symbol: Stock symbol

        Returns:
            Quote data with validation
        """
        response = await market.get_quote(self.client, symbol)

        # Validate with Pydantic model
        model = QuoteResponse(**response)
        return model.model_dump()

    async def get_candles(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> dict[str, Any]:
        """Get historical candlestick data.

        Args:
            symbol: Stock symbol
            resolution: Time resolution
            from_timestamp: From Unix timestamp
            to_timestamp: To Unix timestamp

        Returns:
            OHLC candle data
        """
        self.validate_resolution(resolution)

        response = await market.get_candles(
            self.client,
            symbol,
            resolution,
            from_timestamp,
            to_timestamp,
        )

        # Validate with Pydantic model
        model = CandleResponse(**response)
        return model.model_dump()

    async def get_company_profile(self, symbol: str) -> dict[str, Any]:
        """Get company profile information.

        Args:
            symbol: Stock symbol

        Returns:
            Company profile data
        """
        response = await market.get_company_profile(self.client, symbol)

        # Validate with Pydantic model
        model = CompanyProfile(**response)
        return model.model_dump()

    async def get_market_status(self, exchange: str) -> dict[str, Any]:
        """Get market status for an exchange.

        Args:
            exchange: Exchange code (US, UK, etc.)

        Returns:
            Market status information
        """
        response = await market.get_market_status(self.client, exchange)

        # Validate with Pydantic model
        model = MarketStatusResponse(**response)
        return model.model_dump()

    async def get_symbols(self, exchange: str) -> list[dict[str, Any]]:
        """Get list of symbols for an exchange.

        Args:
            exchange: Exchange code (US, UK, etc.)

        Returns:
            List of symbol information
        """
        # Returns list directly from API
        response = await market.get_symbols(self.client, exchange)
        return response

    async def search_symbols(self, query: str) -> dict[str, Any]:
        """Search for symbols by name or ticker.

        Args:
            query: Search query

        Returns:
            Search results
        """
        response = await market.search_symbols(self.client, query)

        # Validate with Pydantic model
        model = SymbolSearchResponse(**response)
        return model.model_dump()

    async def get_financials(
        self,
        symbol: str,
        statement: str,
        freq: str,
    ) -> dict[str, Any]:
        """Get financial statements.

        Args:
            symbol: Stock symbol
            statement: Statement type (bs, ic, cf)
            freq: Frequency (annual, quarterly)

        Returns:
            Financial statement data
        """
        self.validate_statement(statement)
        self.validate_frequency(freq)

        response = await market.get_financials(
            self.client,
            symbol,
            statement,
            freq,
        )

        # Validate with Pydantic model
        model = FinancialsResponse(**response)
        return model.model_dump()

    async def get_earnings(self, symbol: str) -> dict[str, Any]:
        """Get earnings data.

        Args:
            symbol: Stock symbol

        Returns:
            Earnings history
        """
        response = await market.get_earnings(self.client, symbol)

        # Wrap list response in model
        earnings_response = {"earnings": response}
        model = EarningsResponse(**earnings_response)
        return model.model_dump()

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a stock market data operation.

        Args:
            operation: Operation name
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid
        """
        self.validate_operation(operation)

        # Route to operation handler
        if operation == "get_quote":
            return await self.get_quote(**params)
        elif operation == "get_candles":
            return await self.get_candles(**params)
        elif operation == "get_company_profile":
            return await self.get_company_profile(**params)
        elif operation == "get_market_status":
            return await self.get_market_status(**params)
        elif operation == "get_symbols":
            return await self.get_symbols(**params)
        elif operation == "search_symbols":
            return await self.search_symbols(**params)
        elif operation == "get_financials":
            return await self.get_financials(**params)
        elif operation == "get_earnings":
            return await self.get_earnings(**params)
        else:
            # Should never reach here due to validation
            raise ValueError(f"Unknown operation: {operation}")
