"""FastMCP-based server for mcp-finnhub.

Supports multiple transport modes:
- stdio: Standard input/output (default, for Claude Desktop)
- http: HTTP streaming (recommended for remote connections)
- sse: Server-Sent Events (deprecated, use http instead)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_finnhub.config import load_config
from mcp_finnhub.server import ServerContext

# Global server context - initialized in lifespan
_context: ServerContext | None = None


def get_context() -> ServerContext:
    """Get the global server context.

    Raises:
        RuntimeError: If context not initialized
    """
    if _context is None:
        raise RuntimeError("Server context not initialized")
    return _context


@asynccontextmanager
async def lifespan(app: FastMCP):
    """Manage server lifecycle - initialize and cleanup resources."""
    global _context
    config = load_config()
    _context = ServerContext(config)
    try:
        yield
    finally:
        await _context.aclose()
        _context = None


# Initialize FastMCP server
mcp = FastMCP(
    "mcp-finnhub",
    log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
    lifespan=lifespan,
)


# =============================================================================
# Stock Market Data Tools
# =============================================================================


@mcp.tool()
async def finnhub_stock_market_data(
    operation: str,
    symbol: str | None = None,
    exchange: str | None = None,
    query: str | None = None,
    resolution: str | None = None,
    from_timestamp: int | None = None,
    to_timestamp: int | None = None,
    statement: str | None = None,
    freq: str | None = None,
    project: str | None = None,
) -> str:
    """Real-time quotes, historical candles, and company profiles.

    Operations:
    - get_quote: Get real-time quote for a symbol
    - get_company_profile: Get company profile and details
    - get_market_status: Get market open/close status
    - search_symbols: Search for symbols by name
    - get_candles: Get historical OHLCV candles
    - get_symbols: List symbols for an exchange
    - get_financials: Get financial statements
    - get_earnings: Get earnings data
    """
    from mcp_finnhub.tools import finnhub_stock_market_data as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "exchange": exchange,
            "query": query,
            "resolution": resolution,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
            "statement": statement,
            "freq": freq,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_news_sentiment(
    operation: str,
    symbol: str | None = None,
    category: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    project: str | None = None,
) -> str:
    """Company news, market news, and sentiment analysis.

    Operations:
    - get_company_news: Get news for a specific company
    - get_market_news: Get general market news
    - get_news_sentiment: Get sentiment analysis for news
    - get_insider_sentiment: Get insider sentiment data
    """
    from mcp_finnhub.tools import finnhub_news_sentiment as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "category": category,
            "from_date": from_date,
            "to_date": to_date,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_technical_analysis(
    operation: str,
    symbol: str | None = None,
    resolution: str | None = None,
    indicator: str | None = None,
    timeperiod: int | None = None,
    from_timestamp: int | None = None,
    to_timestamp: int | None = None,
    project: str | None = None,
) -> str:
    """Technical indicators, patterns, and signals.

    Operations:
    - scan_patterns: Scan for technical chart patterns
    - support_resistance: Get support and resistance levels
    - aggregate_signals: Get aggregated technical signals
    - get_indicator: Calculate specific technical indicator
    """
    from mcp_finnhub.tools import finnhub_technical_analysis as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "resolution": resolution,
            "indicator": indicator,
            "timeperiod": timeperiod,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_stock_fundamentals(
    operation: str,
    symbol: str | None = None,
    freq: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    include_series: bool | None = None,
    series_limit: int | None = None,
    project: str | None = None,
) -> str:
    """Financial statements, earnings, dividends, and splits.

    Operations:
    - get_basic_financials: Get key financial metrics
    - get_reported_financials: Get reported financial statements
    - get_sec_financials: Get SEC-reported financials
    - get_dividends: Get dividend history
    - get_splits: Get stock split history
    - get_revenue_breakdown: Get revenue by segment/geography

    For get_basic_financials:
    - include_series: Include historical time series (default: False, saves ~100K+ tokens)
    - series_limit: Max periods per metric when include_series=True (e.g., 4 = last 4 periods)
    """
    from mcp_finnhub.tools import finnhub_stock_fundamentals as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "freq": freq,
            "from_date": from_date,
            "to_date": to_date,
            "include_series": include_series,
            "series_limit": series_limit,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_stock_estimates(
    operation: str,
    symbol: str | None = None,
    freq: str | None = None,
    project: str | None = None,
) -> str:
    """Analyst estimates for earnings, revenue, EBITDA, and price targets.

    Operations:
    - get_earnings_estimates: Get analyst earnings estimates
    - get_revenue_estimates: Get analyst revenue estimates
    - get_ebitda_estimates: Get analyst EBITDA estimates
    - get_price_targets: Get analyst price targets (Premium)
    - get_recommendations: Get analyst recommendations
    """
    from mcp_finnhub.tools import finnhub_stock_estimates as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "freq": freq,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_stock_ownership(
    operation: str,
    symbol: str | None = None,
    cik: str | None = None,
    project: str | None = None,
) -> str:
    """Insider trades, institutional ownership, and congressional trading.

    Operations:
    - get_insider_transactions: Get insider trading activity
    - get_institutional_ownership: Get institutional holders
    - get_institutional_portfolio: Get institution's portfolio by CIK
    - get_congressional_trades: Get congressional trading activity
    """
    from mcp_finnhub.tools import finnhub_stock_ownership as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "cik": cik,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_alternative_data(
    operation: str,
    symbol: str | None = None,
    project: str | None = None,
) -> str:
    """ESG scores, social sentiment, supply chain, and patents.

    Operations:
    - get_esg_scores: Get ESG (Environmental, Social, Governance) scores
    - get_social_sentiment: Get social media sentiment
    - get_supply_chain: Get supply chain relationships
    - get_patents: Get patent filings
    """
    from mcp_finnhub.tools import finnhub_alternative_data as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_sec_filings(
    operation: str,
    symbol: str | None = None,
    access_number: str | None = None,
    freq: str | None = None,
    project: str | None = None,
) -> str:
    """SEC filings, filing sentiment, and similarity analysis.

    Operations:
    - get_sec_filings: Get SEC filing history
    - get_filing_sentiment: Get sentiment analysis of a filing
    - get_similarity_index: Get filing similarity index
    """
    from mcp_finnhub.tools import finnhub_sec_filings as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "access_number": access_number,
            "freq": freq,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_crypto_data(
    operation: str,
    symbol: str | None = None,
    exchange: str | None = None,
    resolution: str | None = None,
    from_timestamp: int | None = None,
    to_timestamp: int | None = None,
    project: str | None = None,
) -> str:
    """Cryptocurrency exchanges, symbols, profiles, and candles.

    Operations:
    - get_crypto_exchanges: List crypto exchanges
    - get_crypto_symbols: List symbols for an exchange
    - get_crypto_profile: Get crypto profile (e.g., BTC)
    - get_crypto_candles: Get historical OHLCV candles
    """
    from mcp_finnhub.tools import finnhub_crypto_data as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "exchange": exchange,
            "resolution": resolution,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_forex_data(
    operation: str,
    symbol: str | None = None,
    exchange: str | None = None,
    base: str | None = None,
    resolution: str | None = None,
    from_timestamp: int | None = None,
    to_timestamp: int | None = None,
    project: str | None = None,
) -> str:
    """Foreign exchange rates, symbols, and candles.

    Operations:
    - get_forex_exchanges: List forex exchanges
    - get_forex_symbols: List symbols for an exchange
    - get_forex_rates: Get exchange rates for base currency
    - get_forex_candles: Get historical OHLCV candles
    """
    from mcp_finnhub.tools import finnhub_forex_data as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "exchange": exchange,
            "base": base,
            "resolution": resolution,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_calendar_data(
    operation: str,
    symbol: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    project: str | None = None,
) -> str:
    """IPO calendar, earnings calendar, economic events, and FDA meetings.

    Operations:
    - get_ipo_calendar: Get upcoming IPOs
    - get_earnings_calendar: Get earnings announcements
    - get_economic_calendar: Get economic events
    - get_fda_calendar: Get FDA advisory committee meetings
    """
    from mcp_finnhub.tools import finnhub_calendar_data as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "from_date": from_date,
            "to_date": to_date,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_market_events(
    operation: str,
    symbol: str | None = None,
    exchange: str | None = None,
    project: str | None = None,
) -> str:
    """Market holidays, analyst upgrades/downgrades, and M&A activity.

    Operations:
    - get_market_holidays: Get market holiday schedule
    - get_upgrade_downgrade: Get analyst rating changes
    - get_merger_acquisition: Get M&A activity
    """
    from mcp_finnhub.tools import finnhub_market_events as handler

    ctx = get_context()
    kwargs = {
        k: v
        for k, v in {
            "symbol": symbol,
            "exchange": exchange,
            "project": project,
        }.items()
        if v is not None
    }
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# Management Tools
# =============================================================================


@mcp.tool()
async def finnhub_project_create(
    operation: str,
    name: str | None = None,
    description: str | None = None,
) -> str:
    """Create project workspaces for organizing data.

    Operations:
    - create: Create a new project workspace
    """
    from mcp_finnhub.tools import finnhub_project_create as handler

    ctx = get_context()
    kwargs: dict[str, Any] = {}
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_project_list(
    operation: str,
) -> str:
    """List all project workspaces with statistics.

    Operations:
    - list: List all projects
    """
    from mcp_finnhub.tools import finnhub_project_list as handler

    ctx = get_context()
    result = await handler(ctx, operation)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def finnhub_job_status(
    operation: str,
    job_id: str | None = None,
) -> str:
    """Check status of background jobs.

    Operations:
    - get_status: Get status of a specific job
    - list_jobs: List all jobs
    """
    from mcp_finnhub.tools import finnhub_job_status as handler

    ctx = get_context()
    kwargs: dict[str, Any] = {}
    if job_id is not None:
        kwargs["job_id"] = job_id
    result = await handler(ctx, operation, **kwargs)
    return json.dumps(result, indent=2, default=str)


# =============================================================================
# CLI Entry Point
# =============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for transport configuration."""
    parser = argparse.ArgumentParser(
        description="MCP-Finnhub Server - Financial market data via Model Context Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with STDIO (default, for Claude Desktop)
  mcp-finnhub

  # Run with HTTP streaming (recommended for remote connections)
  mcp-finnhub --transport http --port 8000

  # Run with SSE (deprecated)
  mcp-finnhub --transport sse --port 8000

  # Custom host binding
  mcp-finnhub --transport http --host 0.0.0.0 --port 8125
        """,
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport method (default: stdio). Use 'http' for remote connections.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for HTTP/SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind for HTTP/SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Log level (default: INFO, or MCP_LOG_LEVEL env var)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the MCP-Finnhub server."""
    args = parse_arguments()

    # Set log level from args or env
    if args.log_level:
        os.environ["MCP_LOG_LEVEL"] = args.log_level

    try:
        if args.transport == "http":
            # HTTP streaming transport (recommended for remote)
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            print(f"Starting MCP-Finnhub HTTP server on {args.host}:{args.port}")
            mcp.run(transport="streamable-http")

        elif args.transport == "sse":
            # SSE transport (deprecated but supported)
            print("Warning: SSE transport is deprecated. Consider using HTTP transport instead.")
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            print(f"Starting MCP-Finnhub SSE server on {args.host}:{args.port}")
            mcp.run(transport="sse")

        else:
            # STDIO transport (default, for Claude Desktop)
            mcp.run(transport="stdio")

    except Exception as e:
        if args.transport in ["http", "sse"]:
            print(f"Error starting {args.transport} server: {e}", file=sys.stderr)
            print(f"Server was configured for {args.host}:{args.port}", file=sys.stderr)
            print("\nCommon solutions:", file=sys.stderr)
            print(f"1. Ensure port {args.port} is available", file=sys.stderr)
            print(f"2. Check if another service is using port {args.port}", file=sys.stderr)
            print("3. Try a different port with --port <PORT>", file=sys.stderr)
        else:
            print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
