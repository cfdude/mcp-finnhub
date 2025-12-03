"""STDIO transport implementation for MCP-Finnhub."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from mcp_finnhub.server import ServerContext

from mcp_finnhub.server import build_server_context
from mcp_finnhub.transports import TOOL_HANDLERS, TOOL_REGISTRY


class STDIOTransport:
    """JSON-RPC transport over stdin/stdout for MCP protocol.

    Implements the Model Context Protocol (MCP) 2024-11-05 specification
    for communication with Claude Desktop and other MCP clients.

    The transport handles JSON-RPC requests from stdin and writes responses
    to stdout, managing the full lifecycle of tool discovery and execution.
    """

    def __init__(self, context: ServerContext | None = None) -> None:
        """Initialize STDIO transport with server context.

        Args:
            context: Server context with client and utilities.
                     If None, builds a new context from environment.
        """
        self._context = context or build_server_context()
        self._lock = asyncio.Lock()

    async def run(self) -> None:
        """Start processing messages from stdin until EOF.

        Reads JSON-RPC requests line by line from stdin, processes each
        request, and writes responses to stdout. Continues until EOF or
        until a KeyboardInterrupt is received.

        The transport ensures graceful shutdown by closing the server
        context when the event loop terminates.
        """
        loop = asyncio.get_running_loop()
        try:
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                except json.JSONDecodeError:
                    await self._write_response(
                        {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": "Parse error: Failed to decode request",
                            },
                        }
                    )
                    continue
                response = await self.handle_request(request)
                if response is not None:  # Don't send responses for notifications
                    await self._write_response(response)
        finally:
            await self._context.aclose()

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Process a single JSON-RPC request.

        Args:
            request: JSON-RPC request dict with method, params, and id

        Returns:
            JSON-RPC response dict, or None for notifications

        Supported Methods:
            - initialize: Returns protocol version and capabilities
            - tools/list: Returns all enabled tools from registry
            - tools/call: Dispatches to tool handler with operation
            - ping: Health check endpoint
            - prompts/list: Returns empty list (not implemented)
            - resources/list: Returns empty list (not implemented)
        """
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Handle notifications (no response needed for notifications)
        if method and method.startswith("notifications/"):
            return None

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "mcp-finnhub", "version": "0.1.0"},
                    },
                }

            if method == "tools/list":
                tools = [
                    {
                        "name": spec.name,
                        "description": spec.summary,
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "description": "Operation to perform",
                                },
                                # Common parameters for all tools
                                "symbol": {"type": "string"},
                                "project": {"type": "string"},
                                "job_id": {"type": "string"},
                            },
                            "required": ["operation"],
                            "additionalProperties": True,
                        },
                    }
                    for spec in TOOL_REGISTRY.values()
                ]
                return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

            if method == "tools/call":
                name = params.get("name")
                if name not in TOOL_HANDLERS:
                    raise ValueError(f"Unknown tool '{name}'")
                arguments = params.get("arguments", {})
                operation = arguments.pop("operation", None)
                if operation is None:
                    raise ValueError("'operation' parameter is required")
                handler = TOOL_HANDLERS[name]
                async with self._lock:
                    result = await handler(self._context, operation, **arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2, default=str)}
                        ]
                    },
                }

            if method == "ping":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}

            if method == "prompts/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": []}}

            if method == "resources/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}

            raise ValueError(f"Unsupported method '{method}'")
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(exc),
                },
            }

    async def _write_response(self, response: dict[str, Any]) -> None:
        """Write JSON-RPC response to stdout.

        Args:
            response: JSON-RPC response dict to write
        """
        loop = asyncio.get_running_loop()
        data = json.dumps(response, ensure_ascii=False)
        await loop.run_in_executor(None, sys.stdout.write, data + "\n")
        await loop.run_in_executor(None, sys.stdout.flush)


__all__ = ["STDIOTransport"]
