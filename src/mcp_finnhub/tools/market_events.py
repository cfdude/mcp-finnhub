"""Tool for accessing market events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import events
from mcp_finnhub.api.models.events import MarketHoliday, MergerAcquisition, UpgradeDowngrade

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class MarketEventsTool:
    """Tool for accessing market events.

    Provides 3 operations:
    - get_market_holidays: Get market holiday calendar
    - get_upgrade_downgrade: Get analyst upgrades/downgrades
    - get_merger_acquisition: Get M&A news
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_market_holidays",
        "get_upgrade_downgrade",
        "get_merger_acquisition",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize market events tool.

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

    async def get_market_holidays(self, exchange: str) -> dict[str, Any]:
        """Get market holiday calendar.

        Args:
            exchange: Exchange code

        Returns:
            Market holiday data
        """
        response = await events.get_market_holidays(self.client, exchange)
        model = MarketHoliday(**response)
        return model.model_dump()

    async def get_upgrade_downgrade(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get analyst upgrade/downgrade history.

        Args:
            symbol: Stock symbol
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            List of upgrade/downgrade events
        """
        response = await events.get_upgrade_downgrade(self.client, symbol, from_date, to_date)
        models = [UpgradeDowngrade(**event) for event in response]
        return [model.model_dump() for model in models]

    async def get_merger_acquisition(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get M&A news.

        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            List of M&A events
        """
        response = await events.get_merger_acquisition(self.client, from_date, to_date)
        models = [MergerAcquisition(**event) for event in response]
        return [model.model_dump() for model in models]

    async def execute(self, operation: str, **params: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a market events operation.

        Args:
            operation: Operation to execute
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid or unknown
        """
        self.validate_operation(operation)

        if operation == "get_market_holidays":
            return await self.get_market_holidays(**params)
        elif operation == "get_upgrade_downgrade":
            return await self.get_upgrade_downgrade(**params)
        elif operation == "get_merger_acquisition":
            return await self.get_merger_acquisition(**params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
