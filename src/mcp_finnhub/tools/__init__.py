"""MCP tools for Finnhub data access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Data tools (class-based, created in Sprints 3-5)
from mcp_finnhub.tools.alternative_data import AlternativeDataTool
from mcp_finnhub.tools.calendar_data import CalendarDataTool
from mcp_finnhub.tools.crypto_data import CryptoDataTool
from mcp_finnhub.tools.forex_data import ForexDataTool

# Management tools (function-based, created in Sprint 6)
from mcp_finnhub.tools.job_status import finnhub_job_status
from mcp_finnhub.tools.market_events import MarketEventsTool
from mcp_finnhub.tools.news_sentiment import NewsSentimentTool
from mcp_finnhub.tools.project_create import finnhub_project_create
from mcp_finnhub.tools.project_list import finnhub_project_list
from mcp_finnhub.tools.sec_filings import SecFilingsTool
from mcp_finnhub.tools.stock_estimates import StockEstimatesTool
from mcp_finnhub.tools.stock_fundamentals import StockFundamentalsTool
from mcp_finnhub.tools.stock_market_data import StockMarketDataTool
from mcp_finnhub.tools.stock_ownership import StockOwnershipTool
from mcp_finnhub.tools.technical_analysis import TechnicalAnalysisTool

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from mcp_finnhub.server import ServerContext


# Wrapper functions for class-based data tools
async def finnhub_stock_market_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock market data tool handler (wrapper for StockMarketDataTool)."""
    tool = StockMarketDataTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_news_sentiment(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """News and sentiment tool handler (wrapper for NewsSentimentTool)."""
    tool = NewsSentimentTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_technical_analysis(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Technical analysis tool handler (wrapper for TechnicalAnalysisTool)."""
    tool = TechnicalAnalysisTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_stock_fundamentals(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock fundamentals tool handler (wrapper for StockFundamentalsTool)."""
    tool = StockFundamentalsTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_stock_estimates(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock estimates tool handler (wrapper for StockEstimatesTool)."""
    tool = StockEstimatesTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_stock_ownership(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock ownership tool handler (wrapper for StockOwnershipTool)."""
    tool = StockOwnershipTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_alternative_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Alternative data tool handler (wrapper for AlternativeDataTool)."""
    tool = AlternativeDataTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_sec_filings(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """SEC filings tool handler (wrapper for SecFilingsTool)."""
    tool = SecFilingsTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_crypto_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Crypto data tool handler (wrapper for CryptoDataTool)."""
    tool = CryptoDataTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_forex_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Forex data tool handler (wrapper for ForexDataTool)."""
    tool = ForexDataTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_calendar_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Calendar data tool handler (wrapper for CalendarDataTool)."""
    tool = CalendarDataTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


async def finnhub_market_events(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Market events tool handler (wrapper for MarketEventsTool)."""
    tool = MarketEventsTool(context.client)
    tool.validate_operation(operation)
    method = getattr(tool, operation)
    return await method(**kwargs)


__all__ = [
    "finnhub_alternative_data",
    "finnhub_calendar_data",
    "finnhub_crypto_data",
    "finnhub_forex_data",
    "finnhub_job_status",
    "finnhub_market_events",
    "finnhub_news_sentiment",
    "finnhub_project_create",
    "finnhub_project_list",
    "finnhub_sec_filings",
    "finnhub_stock_estimates",
    "finnhub_stock_fundamentals",
    "finnhub_stock_market_data",
    "finnhub_stock_ownership",
    "finnhub_technical_analysis",
]
