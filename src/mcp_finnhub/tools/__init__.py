"""MCP tools for Finnhub data access."""

from __future__ import annotations

import inspect
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
    from collections.abc import Callable

    from mcp_finnhub.server import ServerContext


def _get_param_info(method: Callable[..., Any]) -> dict[str, Any]:
    """Extract parameter information from a method signature.

    Args:
        method: The method to inspect

    Returns:
        Dict with 'required' and 'optional' parameter lists
    """
    sig = inspect.signature(method)
    required = []
    optional = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            optional.append(f"{name} (default: {param.default!r})")

    return {"required": required, "optional": optional}


def _generate_tool_help(tool: Any, tool_name: str) -> dict[str, Any]:
    """Generate structured help information for a tool.

    Args:
        tool: The tool instance
        tool_name: Name of the MCP tool

    Returns:
        Structured help with all operations, parameters, and examples
    """
    operations = {}

    for op_name in sorted(tool.VALID_OPERATIONS):
        method = getattr(tool, op_name, None)
        if method is None:
            continue

        # Get parameter info
        param_info = _get_param_info(method)

        # Get docstring
        doc = method.__doc__ or "No description available"
        description = doc.split("\n")[0].strip()

        # Get example if available
        example = _get_operation_examples(tool_name, op_name)

        operations[op_name] = {
            "description": description,
            "required_params": param_info["required"],
            "optional_params": param_info["optional"],
        }

        if example:
            operations[op_name]["example"] = example

    return {
        "tool": tool_name,
        "description": tool.__class__.__doc__ or "No description available",
        "operations": operations,
        "hint": "Call with operation='<operation_name>' and required parameters",
    }


def _create_error_response(
    error_type: str,
    message: str,
    tool_name: str,
    operation: str | None = None,
    valid_operations: list[str] | None = None,
    required_params: list[str] | None = None,
    optional_params: list[str] | None = None,
    example: str | None = None,
) -> dict[str, Any]:
    """Create a structured error response for AI agents.

    Args:
        error_type: Type of error (invalid_operation, missing_param, etc.)
        message: Human-readable error message
        tool_name: Name of the MCP tool
        operation: Operation that was attempted
        valid_operations: List of valid operations for this tool
        required_params: Required parameters for the operation
        optional_params: Optional parameters for the operation
        example: Example usage

    Returns:
        Structured error response dict
    """
    response: dict[str, Any] = {
        "error": error_type,
        "message": message,
        "tool": tool_name,
    }

    if operation:
        response["operation"] = operation
    if valid_operations:
        response["valid_operations"] = valid_operations
    if required_params:
        response["required_params"] = required_params
    if optional_params:
        response["optional_params"] = optional_params
    if example:
        response["example"] = example

    return response


def _format_error_message(
    tool_name: str,
    operation: str,
    method: Callable[..., Any],
    provided_params: dict[str, Any],
    error: Exception,
) -> str:
    """Format a helpful error message for AI agents.

    Args:
        tool_name: Name of the MCP tool
        operation: Operation that was attempted
        method: The method that was called
        provided_params: Parameters that were provided
        error: The original exception

    Returns:
        Formatted error message with guidance
    """
    param_info = _get_param_info(method)

    msg_parts = [
        f"Error calling {tool_name}.{operation}(): {error!s}",
        "",
        f"Required parameters: {', '.join(param_info['required']) or 'none'}",
    ]

    if param_info["optional"]:
        msg_parts.append(f"Optional parameters: {', '.join(param_info['optional'])}")

    provided_keys = [k for k in provided_params if provided_params[k] is not None]
    msg_parts.append(f"Provided parameters: {', '.join(provided_keys) or 'none'}")

    # Add operation-specific examples
    examples = _get_operation_examples(tool_name, operation)
    if examples:
        msg_parts.extend(["", "Example usage:", examples])

    return "\n".join(msg_parts)


def _get_operation_examples(tool_name: str, operation: str) -> str:
    """Get example usage for specific operations.

    Args:
        tool_name: Name of the MCP tool
        operation: Operation name

    Returns:
        Example usage string or empty string
    """
    examples: dict[str, dict[str, str]] = {
        "finnhub_stock_market_data": {
            "get_quote": '{"operation": "get_quote", "symbol": "AAPL"}',
            "get_company_profile": '{"operation": "get_company_profile", "symbol": "AAPL"}',
            "get_market_status": '{"operation": "get_market_status", "exchange": "US"}',
            "search_symbols": '{"operation": "search_symbols", "query": "apple"}',
            "get_candles": '{"operation": "get_candles", "symbol": "AAPL", "resolution": "D", "from_timestamp": 1704067200, "to_timestamp": 1706745600}',
            "get_symbols": '{"operation": "get_symbols", "exchange": "US"}',
            "get_financials": '{"operation": "get_financials", "symbol": "AAPL", "statement": "ic", "freq": "annual"}',
            "get_earnings": '{"operation": "get_earnings", "symbol": "AAPL"}',
        },
        "finnhub_news_sentiment": {
            "get_company_news": '{"operation": "get_company_news", "symbol": "AAPL", "from_date": "2024-01-01", "to_date": "2024-01-31"}',
            "get_market_news": '{"operation": "get_market_news", "category": "general"}',
            "get_news_sentiment": '{"operation": "get_news_sentiment", "symbol": "AAPL"}',
            "get_insider_sentiment": '{"operation": "get_insider_sentiment", "symbol": "AAPL"}',
        },
        "finnhub_technical_analysis": {
            "scan_patterns": '{"operation": "scan_patterns", "symbol": "AAPL", "resolution": "D"}',
            "support_resistance": '{"operation": "support_resistance", "symbol": "AAPL", "resolution": "D"}',
            "aggregate_signals": '{"operation": "aggregate_signals", "symbol": "AAPL", "resolution": "D"}',
            "get_indicator": '{"operation": "get_indicator", "symbol": "AAPL", "resolution": "D", "indicator": "sma", "timeperiod": 14, "from_timestamp": 1704067200, "to_timestamp": 1706745600}',
        },
        "finnhub_stock_fundamentals": {
            "get_basic_financials": '{"operation": "get_basic_financials", "symbol": "AAPL"}',
            "get_reported_financials": '{"operation": "get_reported_financials", "symbol": "AAPL", "freq": "quarterly"}',
            "get_sec_financials": '{"operation": "get_sec_financials", "symbol": "AAPL"}',
            "get_dividends": '{"operation": "get_dividends", "symbol": "AAPL", "from_date": "2023-01-01", "to_date": "2024-01-01"}',
            "get_splits": '{"operation": "get_splits", "symbol": "AAPL", "from_date": "2020-01-01", "to_date": "2024-01-01"}',
            "get_revenue_breakdown": '{"operation": "get_revenue_breakdown", "symbol": "AAPL"}',
        },
        "finnhub_stock_estimates": {
            "get_earnings_estimates": '{"operation": "get_earnings_estimates", "symbol": "AAPL", "freq": "quarterly"}',
            "get_revenue_estimates": '{"operation": "get_revenue_estimates", "symbol": "AAPL", "freq": "quarterly"}',
            "get_ebitda_estimates": '{"operation": "get_ebitda_estimates", "symbol": "AAPL", "freq": "annual"}',
            "get_price_targets": '{"operation": "get_price_targets", "symbol": "AAPL"}',
            "get_recommendations": '{"operation": "get_recommendations", "symbol": "AAPL"}',
        },
        "finnhub_stock_ownership": {
            "get_insider_transactions": '{"operation": "get_insider_transactions", "symbol": "AAPL"}',
            "get_institutional_ownership": '{"operation": "get_institutional_ownership", "symbol": "AAPL"}',
            "get_institutional_portfolio": '{"operation": "get_institutional_portfolio", "cik": "0001067983"}',
            "get_congressional_trades": '{"operation": "get_congressional_trades", "symbol": "AAPL"}',
        },
        "finnhub_alternative_data": {
            "get_esg_scores": '{"operation": "get_esg_scores", "symbol": "AAPL"}',
            "get_social_sentiment": '{"operation": "get_social_sentiment", "symbol": "AAPL"}',
            "get_supply_chain": '{"operation": "get_supply_chain", "symbol": "AAPL"}',
            "get_patents": '{"operation": "get_patents", "symbol": "AAPL"}',
        },
        "finnhub_sec_filings": {
            "get_sec_filings": '{"operation": "get_sec_filings", "symbol": "AAPL"}',
            "get_filing_sentiment": '{"operation": "get_filing_sentiment", "access_number": "0000320193-23-000077"}',
            "get_similarity_index": '{"operation": "get_similarity_index", "symbol": "AAPL", "freq": "annual"}',
        },
        "finnhub_crypto_data": {
            "get_crypto_exchanges": '{"operation": "get_crypto_exchanges"}',
            "get_crypto_symbols": '{"operation": "get_crypto_symbols", "exchange": "binance"}',
            "get_crypto_profile": '{"operation": "get_crypto_profile", "symbol": "BTC"}',
            "get_crypto_candles": '{"operation": "get_crypto_candles", "symbol": "BINANCE:BTCUSDT", "resolution": "D", "from_timestamp": 1704067200, "to_timestamp": 1706745600}',
        },
        "finnhub_forex_data": {
            "get_forex_exchanges": '{"operation": "get_forex_exchanges"}',
            "get_forex_symbols": '{"operation": "get_forex_symbols", "exchange": "oanda"}',
            "get_forex_rates": '{"operation": "get_forex_rates", "base": "USD"}',
            "get_forex_candles": '{"operation": "get_forex_candles", "symbol": "OANDA:EUR_USD", "resolution": "D", "from_timestamp": 1704067200, "to_timestamp": 1706745600}',
        },
        "finnhub_calendar_data": {
            "get_earnings_calendar": '{"operation": "get_earnings_calendar"}',
            "get_ipo_calendar": '{"operation": "get_ipo_calendar", "from_date": "2024-01-01", "to_date": "2024-01-31"}',
            "get_economic_calendar": '{"operation": "get_economic_calendar"}',
            "get_fda_calendar": '{"operation": "get_fda_calendar"}',
        },
        "finnhub_market_events": {
            "get_market_holidays": '{"operation": "get_market_holidays", "exchange": "US"}',
            "get_upgrade_downgrade": '{"operation": "get_upgrade_downgrade", "symbol": "AAPL"}',
            "get_merger_acquisition": '{"operation": "get_merger_acquisition"}',
        },
    }

    tool_examples = examples.get(tool_name, {})
    return tool_examples.get(operation, "")


async def _execute_tool_operation(
    tool: Any,
    tool_name: str,
    operation: str,
    kwargs: dict[str, Any],
    context: ServerContext | None = None,
) -> dict[str, Any]:
    """Execute a tool operation with AI-friendly error handling.

    Args:
        tool: The tool instance
        tool_name: Name of the MCP tool
        operation: Operation to execute
        kwargs: Parameters for the operation
        context: Server context for output routing (optional)

    Returns:
        Operation result or structured error/help response
    """
    # Handle help/discovery operation
    if operation == "help":
        return _generate_tool_help(tool, tool_name)

    # Validate operation with structured error
    if operation not in tool.VALID_OPERATIONS:
        return _create_error_response(
            error_type="invalid_operation",
            message=f"Operation '{operation}' not found in {tool_name}",
            tool_name=tool_name,
            operation=operation,
            valid_operations=sorted(tool.VALID_OPERATIONS),
        )

    method = getattr(tool, operation)
    param_info = _get_param_info(method)

    try:
        # Extract project name before passing kwargs to method
        # (project is used for output routing, not by the tool methods)
        project_name = kwargs.pop("project", None)

        # Execute the tool operation
        result = await method(**kwargs)

        # Route result through output handler if context available
        if context is not None:
            # Determine export format - use CSV for list data
            export_format = "csv" if isinstance(result, list) else "json"

            # Create operation identifier for filename
            symbol = kwargs.get("symbol", "")
            op_name = f"{operation}_{symbol}" if symbol else operation

            result = context.output_handler.route_result(
                data=result,
                project_name=project_name,
                operation_name=op_name,
                export_format=export_format,
            )

        return result
    except TypeError as e:
        # Parameter mismatch - provide structured error
        error_str = str(e)
        example = _get_operation_examples(tool_name, operation)

        return _create_error_response(
            error_type="parameter_error",
            message=f"Parameter error in {operation}(): {error_str}",
            tool_name=tool_name,
            operation=operation,
            required_params=param_info["required"],
            optional_params=param_info["optional"],
            example=example if example else None,
        )


# Wrapper functions for class-based data tools
async def finnhub_stock_market_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock market data tool handler (wrapper for StockMarketDataTool)."""
    tool = StockMarketDataTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_stock_market_data", operation, kwargs, context
    )


async def finnhub_news_sentiment(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """News and sentiment tool handler (wrapper for NewsSentimentTool)."""
    tool = NewsSentimentTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_news_sentiment", operation, kwargs, context)


async def finnhub_technical_analysis(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Technical analysis tool handler (wrapper for TechnicalAnalysisTool)."""
    tool = TechnicalAnalysisTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_technical_analysis", operation, kwargs, context
    )


async def finnhub_stock_fundamentals(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock fundamentals tool handler (wrapper for StockFundamentalsTool)."""
    tool = StockFundamentalsTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_stock_fundamentals", operation, kwargs, context
    )


async def finnhub_stock_estimates(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock estimates tool handler (wrapper for StockEstimatesTool)."""
    tool = StockEstimatesTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_stock_estimates", operation, kwargs, context
    )


async def finnhub_stock_ownership(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Stock ownership tool handler (wrapper for StockOwnershipTool)."""
    tool = StockOwnershipTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_stock_ownership", operation, kwargs, context
    )


async def finnhub_alternative_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Alternative data tool handler (wrapper for AlternativeDataTool)."""
    tool = AlternativeDataTool(context.client)
    return await _execute_tool_operation(
        tool, "finnhub_alternative_data", operation, kwargs, context
    )


async def finnhub_sec_filings(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """SEC filings tool handler (wrapper for SecFilingsTool)."""
    tool = SecFilingsTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_sec_filings", operation, kwargs, context)


async def finnhub_crypto_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Crypto data tool handler (wrapper for CryptoDataTool)."""
    tool = CryptoDataTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_crypto_data", operation, kwargs, context)


async def finnhub_forex_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Forex data tool handler (wrapper for ForexDataTool)."""
    tool = ForexDataTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_forex_data", operation, kwargs, context)


async def finnhub_calendar_data(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Calendar data tool handler (wrapper for CalendarDataTool)."""
    tool = CalendarDataTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_calendar_data", operation, kwargs, context)


async def finnhub_market_events(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    """Market events tool handler (wrapper for MarketEventsTool)."""
    tool = MarketEventsTool(context.client)
    return await _execute_tool_operation(tool, "finnhub_market_events", operation, kwargs, context)


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
