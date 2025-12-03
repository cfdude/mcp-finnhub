"""Alternative data tool for the Finnhub MCP server."""

from typing import Any, ClassVar

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import alternative
from mcp_finnhub.api.models.alternative import ESGScore, Patents, SocialSentiment, SupplyChain


class AlternativeDataTool:
    """Tool for accessing alternative data.

    Provides 4 operations:
    - get_esg_scores: Get ESG scores
    - get_social_sentiment: Get social media sentiment
    - get_supply_chain: Get supply chain relationships
    - get_patents: Get USPTO patent data
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_esg_scores",
        "get_social_sentiment",
        "get_supply_chain",
        "get_patents",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize the alternative data tool."""
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate that the operation is supported."""
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation: {operation}. "
                f"Valid operations: {', '.join(sorted(self.VALID_OPERATIONS))}"
            )

    async def get_esg_scores(self, symbol: str) -> dict[str, Any]:
        """Get ESG scores for a company."""
        response = await alternative.get_esg_scores(self.client, symbol)
        model = ESGScore(**response)
        return model.model_dump()

    async def get_social_sentiment(
        self, symbol: str, from_date: str | None = None, to_date: str | None = None
    ) -> dict[str, Any]:
        """Get social sentiment data."""
        response = await alternative.get_social_sentiment(self.client, symbol, from_date, to_date)
        model = SocialSentiment(**response)
        return model.model_dump()

    async def get_supply_chain(self, symbol: str) -> dict[str, Any]:
        """Get supply chain relationships."""
        response = await alternative.get_supply_chain(self.client, symbol)
        model = SupplyChain(**response)
        return model.model_dump()

    async def get_patents(self, symbol: str, from_date: str, to_date: str) -> dict[str, Any]:
        """Get USPTO patent data."""
        response = await alternative.get_patents(self.client, symbol, from_date, to_date)
        model = Patents(**response)
        return model.model_dump()

    async def execute(self, operation: str, **params: Any) -> dict[str, Any]:
        """Execute an alternative data operation."""
        self.validate_operation(operation)

        if operation == "get_esg_scores":
            return await self.get_esg_scores(**params)
        elif operation == "get_social_sentiment":
            return await self.get_social_sentiment(**params)
        elif operation == "get_supply_chain":
            return await self.get_supply_chain(**params)
        elif operation == "get_patents":
            return await self.get_patents(**params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
