"""Transport-facing tool registry helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from mcp_finnhub.tools import (
    finnhub_alternative_data,
    finnhub_calendar_data,
    finnhub_crypto_data,
    finnhub_forex_data,
    finnhub_job_status,
    finnhub_market_events,
    finnhub_news_sentiment,
    finnhub_project_create,
    finnhub_project_list,
    finnhub_sec_filings,
    finnhub_stock_estimates,
    finnhub_stock_fundamentals,
    finnhub_stock_market_data,
    finnhub_stock_ownership,
    finnhub_technical_analysis,
)

if TYPE_CHECKING:
    from mcp_finnhub.config import ToolConfig

ToolHandler = Callable[..., Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class ToolSpec:
    """Specification for an MCP tool.

    Attributes:
        name: Tool identifier (e.g., "finnhub_market_data")
        handler: Async function that implements the tool
        summary: Brief description of tool functionality
        config_key: Configuration key for enable/disable (optional)
    """

    name: str
    handler: ToolHandler
    summary: str
    config_key: str | None = None


_TOOL_SPECS: tuple[ToolSpec, ...] = (
    # Data tools (can be enabled/disabled)
    ToolSpec(
        "finnhub_stock_market_data",
        finnhub_stock_market_data,
        "Real-time quotes, historical candles, and company profiles",
        "stock_market_data",
    ),
    ToolSpec(
        "finnhub_news_sentiment",
        finnhub_news_sentiment,
        "Company news, market news, and sentiment analysis",
        "news_sentiment",
    ),
    ToolSpec(
        "finnhub_technical_analysis",
        finnhub_technical_analysis,
        "Technical indicators, patterns, and signals",
        "technical_analysis",
    ),
    ToolSpec(
        "finnhub_stock_fundamentals",
        finnhub_stock_fundamentals,
        "Financial statements, earnings, dividends, and splits",
        "stock_fundamentals",
    ),
    ToolSpec(
        "finnhub_stock_estimates",
        finnhub_stock_estimates,
        "Analyst estimates for earnings, revenue, EBITDA, and price targets",
        "stock_estimates",
    ),
    ToolSpec(
        "finnhub_stock_ownership",
        finnhub_stock_ownership,
        "Insider trades, institutional ownership, and congressional trading",
        "stock_ownership",
    ),
    ToolSpec(
        "finnhub_alternative_data",
        finnhub_alternative_data,
        "ESG scores, social sentiment, supply chain, and patents",
        "alternative_data",
    ),
    ToolSpec(
        "finnhub_sec_filings",
        finnhub_sec_filings,
        "SEC filings, filing sentiment, and similarity analysis",
        "sec_filings",
    ),
    ToolSpec(
        "finnhub_crypto_data",
        finnhub_crypto_data,
        "Cryptocurrency exchanges, symbols, profiles, and candles",
        "crypto",
    ),
    ToolSpec(
        "finnhub_forex_data",
        finnhub_forex_data,
        "Foreign exchange rates, symbols, and candles",
        "forex",
    ),
    ToolSpec(
        "finnhub_calendar_data",
        finnhub_calendar_data,
        "IPO calendar, earnings calendar, economic events, and FDA meetings",
        "calendar",
    ),
    ToolSpec(
        "finnhub_market_events",
        finnhub_market_events,
        "Market holidays, analyst upgrades/downgrades, and M&A activity",
        "market_events",
    ),
    # Management tools (always enabled)
    ToolSpec(
        "finnhub_project_create",
        finnhub_project_create,
        "Create project workspaces for organizing data",
        None,  # Always enabled
    ),
    ToolSpec(
        "finnhub_project_list",
        finnhub_project_list,
        "List all project workspaces with statistics",
        None,  # Always enabled
    ),
    ToolSpec(
        "finnhub_job_status",
        finnhub_job_status,
        "Check status of background jobs",
        None,  # Always enabled
    ),
)


def build_tool_registry(config: ToolConfig | None = None) -> Mapping[str, ToolSpec]:
    """Build tool registry with optional configuration filtering.

    Args:
        config: Tool configuration for enable/disable filtering.
                If None, all tools are enabled.

    Returns:
        Ordered mapping of tool name to ToolSpec for enabled tools

    Example:
        >>> config = ToolConfig()  # All tools enabled by default
        >>> registry = build_tool_registry(config)
        >>> len(registry)
        15
        >>> "finnhub_market_data" in registry
        True
    """
    if config is None:
        # All tools enabled when no config provided
        specs = _TOOL_SPECS
    else:
        # Filter based on config
        specs = (
            spec
            for spec in _TOOL_SPECS
            if spec.config_key is None or config.is_tool_enabled(spec.config_key)
        )

    return OrderedDict((spec.name, spec) for spec in specs)


# Default registry with all tools enabled
TOOL_REGISTRY: Mapping[str, ToolSpec] = build_tool_registry()
TOOL_HANDLERS: Mapping[str, ToolHandler] = OrderedDict(
    (name, spec.handler) for name, spec in TOOL_REGISTRY.items()
)

__all__ = [
    "TOOL_HANDLERS",
    "TOOL_REGISTRY",
    "ToolHandler",
    "ToolSpec",
    "build_tool_registry",
]
