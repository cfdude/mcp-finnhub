"""Technical analysis MCP tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import technical
from mcp_finnhub.api.models.technical import (
    AggregateSignalsResponse,
    PatternRecognitionResponse,
    SupportResistanceResponse,
)

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class TechnicalAnalysisTool:
    """Technical analysis tool with 4 operations."""

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_indicator",
        "aggregate_signals",
        "scan_patterns",
        "support_resistance",
    }

    VALID_RESOLUTIONS: ClassVar[set[str]] = {"1", "5", "15", "30", "60", "D", "W", "M"}

    def __init__(self, client: FinnhubClient):
        """Initialize technical analysis tool.

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

    async def get_indicator(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
        indicator: str,
        **indicator_params: Any,
    ) -> dict[str, Any]:
        """Get technical indicator values.

        Args:
            symbol: Stock symbol
            resolution: Time resolution
            from_timestamp: From Unix timestamp
            to_timestamp: To Unix timestamp
            indicator: Indicator name (sma, ema, rsi, macd, etc.)
            **indicator_params: Indicator-specific parameters

        Returns:
            Indicator data with validation
        """
        self.validate_resolution(resolution)

        response = await technical.get_indicator(
            self.client,
            symbol,
            resolution,
            from_timestamp,
            to_timestamp,
            indicator,
            **indicator_params,
        )

        # Validate response with Pydantic model
        # Note: Actual API response structure may vary by indicator
        # For now, return raw response
        return response

    async def aggregate_signals(
        self,
        symbol: str,
        resolution: str,
    ) -> dict[str, Any]:
        """Get aggregated technical signals.

        Args:
            symbol: Stock symbol
            resolution: Time resolution

        Returns:
            Aggregated buy/sell/hold signals
        """
        self.validate_resolution(resolution)

        response = await technical.aggregate_signals(
            self.client,
            symbol,
            resolution,
        )

        # Inject symbol from request (API doesn't return it)
        response["symbol"] = symbol

        # Validate with Pydantic model
        model = AggregateSignalsResponse(**response)
        return model.model_dump()

    async def scan_patterns(
        self,
        symbol: str,
        resolution: str,
    ) -> dict[str, Any]:
        """Scan for chart patterns.

        Args:
            symbol: Stock symbol
            resolution: Time resolution

        Returns:
            Detected chart patterns
        """
        self.validate_resolution(resolution)

        response = await technical.scan_patterns(
            self.client,
            symbol,
            resolution,
        )

        # Validate with Pydantic model
        model = PatternRecognitionResponse(**response)
        return model.model_dump()

    async def support_resistance(
        self,
        symbol: str,
        resolution: str,
    ) -> dict[str, Any]:
        """Get support and resistance levels.

        Args:
            symbol: Stock symbol
            resolution: Time resolution

        Returns:
            Support and resistance levels
        """
        self.validate_resolution(resolution)

        response = await technical.support_resistance(
            self.client,
            symbol,
            resolution,
        )

        # Validate with Pydantic model
        model = SupportResistanceResponse(**response)
        result = model.model_dump()
        # Add request context to response for clarity
        result["symbol"] = symbol
        result["resolution"] = resolution
        return result

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Execute a technical analysis operation.

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
        if operation == "get_indicator":
            return await self.get_indicator(**params)
        elif operation == "aggregate_signals":
            return await self.aggregate_signals(**params)
        elif operation == "scan_patterns":
            return await self.scan_patterns(**params)
        elif operation == "support_resistance":
            return await self.support_resistance(**params)
        else:
            # Should never reach here due to validation
            raise ValueError(f"Unknown operation: {operation}")
