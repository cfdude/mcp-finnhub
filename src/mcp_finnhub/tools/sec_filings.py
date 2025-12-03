"""SEC filings tool for the Finnhub MCP server."""

from typing import Any, ClassVar

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import filings
from mcp_finnhub.api.models.filings import FilingData, FilingSentiment, SimilarityIndex


class SecFilingsTool:
    """Tool for accessing SEC filing data.

    Provides 3 operations:
    - get_sec_filings: Get SEC filings
    - get_filing_sentiment: Get filing sentiment analysis
    - get_similarity_index: Get filing similarity index
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_sec_filings",
        "get_filing_sentiment",
        "get_similarity_index",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize the SEC filings tool."""
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate that the operation is supported."""
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation: {operation}. "
                f"Valid operations: {', '.join(sorted(self.VALID_OPERATIONS))}"
            )

    async def get_sec_filings(
        self, symbol: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[dict[str, Any]]:
        """Get SEC filings for a company."""
        response = await filings.get_sec_filings(self.client, symbol, from_date, to_date)
        models = [FilingData(**filing) for filing in response]
        return [model.model_dump() for model in models]

    async def get_filing_sentiment(self, access_number: str) -> dict[str, Any]:
        """Get sentiment analysis for a specific filing."""
        response = await filings.get_filing_sentiment(self.client, access_number)
        model = FilingSentiment(**response)
        return model.model_dump()

    async def get_similarity_index(
        self, symbol: str, cik: str | None = None, freq: str = "annual"
    ) -> dict[str, Any]:
        """Get filing similarity index."""
        response = await filings.get_similarity_index(self.client, symbol, cik, freq)
        model = SimilarityIndex(**response)
        return model.model_dump()

    async def execute(self, operation: str, **params: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a SEC filings operation."""
        self.validate_operation(operation)

        if operation == "get_sec_filings":
            return await self.get_sec_filings(**params)
        elif operation == "get_filing_sentiment":
            return await self.get_filing_sentiment(**params)
        elif operation == "get_similarity_index":
            return await self.get_similarity_index(**params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
