"""Command-line interface for running mcp-finnhub via STDIO transport."""

from __future__ import annotations

import asyncio
from contextlib import suppress

from mcp_finnhub.server import build_server_context
from mcp_finnhub.transports.stdio import STDIOTransport


def main() -> None:
    """Run the mcp-finnhub server using STDIO transport for Claude Desktop.

    This is the main entry point for the MCP server. It creates a server
    context with all dependencies, initializes the STDIO transport, and runs
    the async event loop to process MCP protocol requests.

    The server will continue running until:
    - EOF is received on stdin (client disconnect)
    - KeyboardInterrupt (Ctrl+C)
    - Unhandled exception (server error)

    Example:
        >>> # Run directly
        >>> python -m mcp_finnhub

        >>> # Or use installed script
        >>> mcp-finnhub
    """
    context = build_server_context()
    transport = STDIOTransport(context)
    with suppress(KeyboardInterrupt):  # pragma: no cover - CLI behaviour
        asyncio.run(transport.run())


if __name__ == "__main__":  # pragma: no cover
    main()
