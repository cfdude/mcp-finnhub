"""Stock estimates tool for the Finnhub MCP server.

This tool provides access to analyst estimates including earnings, revenue,
EBITDA estimates, price targets, and recommendation trends.
"""

from typing import Any, ClassVar

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import estimates
from mcp_finnhub.api.models.estimates import (
    EarningsEstimates,
    EbitdaEstimates,
    PriceTarget,
    RecommendationTrend,
    RevenueEstimates,
)


class StockEstimatesTool:
    """Tool for accessing stock analyst estimates and recommendations.

    Provides 5 operations:
    - get_earnings_estimates: Get EPS estimates
    - get_revenue_estimates: Get revenue estimates
    - get_ebitda_estimates: Get EBITDA estimates
    - get_price_targets: Get analyst price targets
    - get_recommendations: Get analyst recommendation trends
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_earnings_estimates",
        "get_revenue_estimates",
        "get_ebitda_estimates",
        "get_price_targets",
        "get_recommendations",
    }

    VALID_FREQUENCIES: ClassVar[set[str]] = {"annual", "quarterly"}

    def __init__(self, client: FinnhubClient):
        """Initialize the stock estimates tool.

        Args:
            client: The Finnhub API client
        """
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate that the operation is supported.

        Args:
            operation: The operation to validate

        Raises:
            ValueError: If the operation is not valid
        """
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation: {operation}. "
                f"Valid operations: {', '.join(sorted(self.VALID_OPERATIONS))}"
            )

    def validate_freq(self, freq: str | None) -> None:
        """Validate frequency parameter.

        Args:
            freq: The frequency to validate

        Raises:
            ValueError: If freq is not valid
        """
        if freq is not None and freq not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency: {freq}. "
                f"Valid frequencies: {', '.join(sorted(self.VALID_FREQUENCIES))}"
            )

    async def get_earnings_estimates(
        self,
        symbol: str,
        freq: str | None = None,
    ) -> dict[str, Any]:
        """Get company EPS (earnings per share) estimates.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

        Returns:
            Validated earnings estimates data

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_freq(freq)
        response = await estimates.get_earnings_estimates(
            self.client,
            symbol,
            freq,
        )
        # Validate with Pydantic model
        model = EarningsEstimates(**response)
        return model.model_dump()

    async def get_revenue_estimates(
        self,
        symbol: str,
        freq: str | None = None,
    ) -> dict[str, Any]:
        """Get company revenue estimates.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

        Returns:
            Validated revenue estimates data

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_freq(freq)
        response = await estimates.get_revenue_estimates(
            self.client,
            symbol,
            freq,
        )
        # Validate with Pydantic model
        model = RevenueEstimates(**response)
        return model.model_dump()

    async def get_ebitda_estimates(
        self,
        symbol: str,
        freq: str | None = None,
    ) -> dict[str, Any]:
        """Get company EBITDA estimates.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            freq: Frequency - 'annual' or 'quarterly' (default: 'quarterly')

        Returns:
            Validated EBITDA estimates data

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_freq(freq)
        response = await estimates.get_ebitda_estimates(
            self.client,
            symbol,
            freq,
        )
        # Validate with Pydantic model
        model = EbitdaEstimates(**response)
        return model.model_dump()

    async def get_price_targets(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """Get latest analyst price target consensus.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Validated price target data
        """
        response = await estimates.get_price_targets(
            self.client,
            symbol,
        )
        # Validate with Pydantic model
        model = PriceTarget(**response)
        return model.model_dump()

    async def get_recommendations(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:
        """Get latest analyst recommendation trends.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of validated recommendation trend data
        """
        response = await estimates.get_recommendations(
            self.client,
            symbol,
        )
        # Validate each recommendation with Pydantic model
        recommendations = [RecommendationTrend(**rec) for rec in response]
        return [rec.model_dump() for rec in recommendations]

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a stock estimates operation.

        Args:
            operation: The operation to execute
            **params: Operation-specific parameters

        Returns:
            The operation result (dict or list of dicts)

        Raises:
            ValueError: If operation or parameters are invalid
        """
        self.validate_operation(operation)

        if operation == "get_earnings_estimates":
            return await self.get_earnings_estimates(**params)
        elif operation == "get_revenue_estimates":
            return await self.get_revenue_estimates(**params)
        elif operation == "get_ebitda_estimates":
            return await self.get_ebitda_estimates(**params)
        elif operation == "get_price_targets":
            return await self.get_price_targets(**params)
        elif operation == "get_recommendations":
            return await self.get_recommendations(**params)
        else:
            # This should never happen due to validate_operation
            raise ValueError(f"Unknown operation: {operation}")
