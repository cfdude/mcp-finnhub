"""Tool for accessing calendar data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import calendar
from mcp_finnhub.api.models.calendar import (
    EarningsCalendar,
    EconomicCalendar,
    FDAEvent,
    IPOCalendar,
)

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class CalendarDataTool:
    """Tool for accessing market calendars.

    Provides 4 operations:
    - get_ipo_calendar: Get IPO calendar
    - get_earnings_calendar: Get earnings calendar
    - get_economic_calendar: Get economic events calendar
    - get_fda_calendar: Get FDA committee meeting calendar
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_ipo_calendar",
        "get_earnings_calendar",
        "get_economic_calendar",
        "get_fda_calendar",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize calendar data tool.

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

    async def get_ipo_calendar(self, from_date: str, to_date: str) -> dict[str, Any]:
        """Get IPO calendar.

        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            IPO calendar data
        """
        response = await calendar.get_ipo_calendar(self.client, from_date, to_date)
        model = IPOCalendar(**response)
        return model.model_dump()

    async def get_earnings_calendar(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get earnings calendar.

        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            symbol: Filter by symbol

        Returns:
            Earnings calendar data
        """
        response = await calendar.get_earnings_calendar(self.client, from_date, to_date, symbol)
        model = EarningsCalendar(**response)
        return model.model_dump()

    async def get_economic_calendar(self) -> dict[str, Any]:
        """Get economic events calendar.

        Returns:
            Economic calendar data
        """
        response = await calendar.get_economic_calendar(self.client)
        model = EconomicCalendar(**response)
        return model.model_dump()

    async def get_fda_calendar(self) -> list[dict[str, Any]]:
        """Get FDA committee meeting calendar.

        Returns:
            FDA calendar data
        """
        response = await calendar.get_fda_calendar(self.client)
        models = [FDAEvent(**event) for event in response]
        return [model.model_dump() for model in models]

    async def execute(self, operation: str, **params: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a calendar data operation.

        Args:
            operation: Operation to execute
            **params: Operation-specific parameters

        Returns:
            Operation result

        Raises:
            ValueError: If operation is invalid or unknown
        """
        self.validate_operation(operation)

        if operation == "get_ipo_calendar":
            return await self.get_ipo_calendar(**params)
        elif operation == "get_earnings_calendar":
            return await self.get_earnings_calendar(**params)
        elif operation == "get_economic_calendar":
            return await self.get_economic_calendar()
        elif operation == "get_fda_calendar":
            return await self.get_fda_calendar()
        else:
            raise ValueError(f"Unknown operation: {operation}")
