"""Command-line interface for running mcp-finnhub MCP server.

Supports multiple transport modes:
- stdio: Standard input/output (default, for Claude Desktop)
- http: HTTP streaming (recommended for persistent/remote connections)
- sse: Server-Sent Events (deprecated, use http instead)

Examples:
    # Run with STDIO (default, for Claude Desktop)
    python -m mcp_finnhub

    # Run with HTTP streaming
    python -m mcp_finnhub --transport http --port 8000

    # Run with custom host (for network access)
    python -m mcp_finnhub --transport http --host 0.0.0.0 --port 8125
"""

from __future__ import annotations

from mcp_finnhub.fastmcp_server import main

if __name__ == "__main__":  # pragma: no cover
    main()
