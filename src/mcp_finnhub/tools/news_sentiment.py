"""News and sentiment MCP tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from mcp_finnhub.api.endpoints import news
from mcp_finnhub.api.models.news import InsiderSentimentResponse, NewsSentimentResponse

if TYPE_CHECKING:
    from mcp_finnhub.api.client import FinnhubClient


class NewsSentimentTool:
    """News and sentiment analysis tool with 4 operations."""

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "get_company_news",
        "get_market_news",
        "get_news_sentiment",
        "get_insider_sentiment",
    }

    VALID_CATEGORIES: ClassVar[set[str]] = {"general", "forex", "crypto", "merger"}

    def __init__(self, client: FinnhubClient):
        """Initialize news and sentiment tool.

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

    def validate_category(self, category: str) -> None:
        """Validate news category.

        Args:
            category: Category to validate

        Raises:
            ValueError: If category is invalid
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {category}. "
                f"Valid categories: {', '.join(sorted(self.VALID_CATEGORIES))}"
            )

    async def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, Any]]:
        """Get company-specific news articles.

        Args:
            symbol: Stock symbol
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)

        Returns:
            List of news articles
        """
        # Returns list directly from API (already NewsArticle compatible)
        response = await news.get_company_news(
            self.client,
            symbol,
            from_date,
            to_date,
        )
        return response

    async def get_market_news(
        self,
        category: str,
    ) -> list[dict[str, Any]]:
        """Get general market news by category.

        Args:
            category: News category (general, forex, crypto, merger)

        Returns:
            List of news articles
        """
        self.validate_category(category)

        # Returns list directly from API
        response = await news.get_market_news(self.client, category)
        return response

    async def get_news_sentiment(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """Get news sentiment analysis.

        Args:
            symbol: Stock symbol

        Returns:
            News sentiment scores and statistics
        """
        response = await news.get_news_sentiment(self.client, symbol)

        # Validate with Pydantic model
        model = NewsSentimentResponse(**response)
        return model.model_dump()

    async def get_insider_sentiment(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:
        """Get insider trading sentiment.

        Args:
            symbol: Stock symbol
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)

        Returns:
            Insider sentiment data
        """
        response = await news.get_insider_sentiment(
            self.client,
            symbol,
            from_date,
            to_date,
        )

        # Validate with Pydantic model
        model = InsiderSentimentResponse(**response)
        return model.model_dump()

    async def execute(
        self,
        operation: str,
        **params: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Execute a news/sentiment operation.

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
        if operation == "get_company_news":
            return await self.get_company_news(**params)
        elif operation == "get_market_news":
            return await self.get_market_news(**params)
        elif operation == "get_news_sentiment":
            return await self.get_news_sentiment(**params)
        elif operation == "get_insider_sentiment":
            return await self.get_insider_sentiment(**params)
        else:
            # Should never reach here due to validation
            raise ValueError(f"Unknown operation: {operation}")
