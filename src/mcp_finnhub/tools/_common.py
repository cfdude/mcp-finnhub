"""Shared utilities for MCP tool implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_finnhub.server import ServerContext


def route_tool_result(
    context: ServerContext,
    data: dict[str, Any] | list[Any],
    project_name: str | None = None,
    operation_name: str = "export",
    export_format: str = "json",
) -> dict[str, Any] | list[Any]:
    """Route tool result through output handler for smart size management.

    This helper should be called by tools before returning results that may
    exceed the token limit. It will:
    - Return data as-is if it fits within the token limit
    - Save to file and return truncated preview if data exceeds limit

    Args:
        context: Server context with output handler
        data: Tool result data (dict or list)
        project_name: Project name for file exports (uses 'default' if None)
        operation_name: Name of the operation (used in filename)
        export_format: Export format ('json' or 'csv')

    Returns:
        Original data if fits, or truncated preview with file path info

    Example:
        >>> async def get_candles(self, context, symbol, ...):
        ...     response = await market.get_candles(...)
        ...     model = CandleResponse(**response)
        ...     data = model.model_dump()
        ...     return route_tool_result(
        ...         context,
        ...         data,
        ...         project_name=project,
        ...         operation_name=f"candles_{symbol}",
        ...         export_format="csv"
        ...     )
    """
    return context.output_handler.route_result(
        data=data,
        project_name=project_name,
        operation_name=operation_name,
        export_format=export_format,
    )


__all__ = ["route_tool_result"]
