"""Stock ownership tool for the Finnhub MCP server.

This tool provides access to stock ownership data including insider transactions,
institutional ownership, institutional portfolios, and congressional trading.
"""

from typing import Any, ClassVar

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import ownership
from mcp_finnhub.api.models.ownership import (
    CongressionalTrading,
    InsiderTransactions,
    InstitutionalOwnership,
    InstitutionalPortfolio,
)


class StockOwnershipTool:
    """Tool for accessing stock ownership and insider trading data.

    Provides 4 operations:
    - get_insider_transactions: Get insider transaction data
    - get_institutional_ownership: Get institutional ownership data
    - get_institutional_portfolio: Get institutional investor portfolio
    - get_congressional_trades: Get congressional trading data
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_insider_transactions",
        "get_institutional_ownership",
        "get_institutional_portfolio",
        "get_congressional_trades",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize the stock ownership tool.

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

    async def get_insider_transactions(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, Any]:
        """Get insider transaction data for a company.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: From date in YYYY-MM-DD format (optional)
            to_date: To date in YYYY-MM-DD format (optional)

        Returns:
            Validated insider transactions data
        """
        response = await ownership.get_insider_transactions(
            self.client,
            symbol,
            from_date,
            to_date,
        )
        # Validate with Pydantic model
        model = InsiderTransactions(**response)
        return model.model_dump()

    async def get_institutional_ownership(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        cusip: str | None = None,
    ) -> dict[str, Any]:
        """Get institutional ownership data for a stock.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: From date in YYYY-MM-DD format
            to_date: To date in YYYY-MM-DD format
            cusip: CUSIP identifier (optional)

        Returns:
            Validated institutional ownership data
        """
        response = await ownership.get_institutional_ownership(
            self.client,
            symbol,
            from_date,
            to_date,
            cusip,
        )
        # Validate with Pydantic model
        model = InstitutionalOwnership(**response)
        return model.model_dump()

    async def get_institutional_portfolio(
        self,
        cik: str,
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:
        """Get institutional investor portfolio holdings.

        Args:
            cik: Central Index Key (CIK) of the institutional investor
            from_date: From date in YYYY-MM-DD format
            to_date: To date in YYYY-MM-DD format

        Returns:
            Validated portfolio holdings data
        """
        response = await ownership.get_institutional_portfolio(
            self.client,
            cik,
            from_date,
            to_date,
        )
        # Validate with Pydantic model
        model = InstitutionalPortfolio(**response)
        return model.model_dump()

    async def get_congressional_trades(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:
        """Get congressional trading data for a stock.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: From date in YYYY-MM-DD format
            to_date: To date in YYYY-MM-DD format

        Returns:
            Validated congressional trading data
        """
        response = await ownership.get_congressional_trades(
            self.client,
            symbol,
            from_date,
            to_date,
        )
        # Validate with Pydantic model
        model = CongressionalTrading(**response)
        return model.model_dump()

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Execute a stock ownership operation.

        Args:
            operation: The operation to execute
            **params: Operation-specific parameters

        Returns:
            The operation result

        Raises:
            ValueError: If operation or parameters are invalid
        """
        self.validate_operation(operation)

        if operation == "get_insider_transactions":
            return await self.get_insider_transactions(**params)
        elif operation == "get_institutional_ownership":
            return await self.get_institutional_ownership(**params)
        elif operation == "get_institutional_portfolio":
            return await self.get_institutional_portfolio(**params)
        elif operation == "get_congressional_trades":
            return await self.get_congressional_trades(**params)
        else:
            # This should never happen due to validate_operation
            raise ValueError(f"Unknown operation: {operation}")
