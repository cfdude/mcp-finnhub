# Sprint 6 Plan: MCP Server Integration & Management Tools

**Sprint:** Phase 6, Sprint 6
**Sprint Goal:** Complete MCP server implementation with tool registry, STDIO transport, and management tools
**Story Points:** 90 SP
**Duration:** 1 sprint
**Dependencies:** Sprints 1-5 complete (all 15 data tools implemented)

---

## Sprint Overview

Sprint 6 finalizes the MCP server by integrating all 15 data tools into a production-ready MCP server with:
- Full MCP protocol support (JSON-RPC over STDIO)
- Tool registry with enable/disable configuration
- Server context with dependency injection
- 3 management tools (project creation, project listing, job status)
- Complete integration testing

### Why This Sprint

Sprints 1-5 delivered 15 data tools covering 53 Finnhub API operations, but they're not yet accessible via the MCP protocol. Sprint 6 creates the server infrastructure that:
1. Exposes all tools via MCP's JSON-RPC protocol
2. Enables Claude Desktop integration
3. Provides project and job management capabilities
4. Makes the server production-ready

---

## Architecture Pattern (mcp-fred Reference)

Sprint 6 follows the proven mcp-fred architecture:

### Server Context (Dependency Injection)
```python
class ServerContext:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = FinnhubClient(config.finnhub_api_key)
        # Wire all endpoint APIs
        self.market = MarketAPI(self.client)
        self.news = NewsAPI(self.client)
        # ... 15 total APIs
        # Wire all utilities
        self.token_estimator = TokenEstimator(...)
        self.path_resolver = PathResolver(...)
        self.file_writer = FileWriter()
        self.job_manager = JobManager(...)
        self.background_worker = BackgroundWorker(...)
        self.output_handler = ResultOutputHandler(...)
```

### Tool Registry (Enable/Disable Support)
```python
@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: ToolHandler
    summary: str
    enabled: bool = True

TOOL_REGISTRY = {
    "finnhub_market_data": ToolSpec(...),
    "finnhub_crypto_data": ToolSpec(...),
    # ... 15 total tools
}
```

### STDIO Transport (MCP Protocol)
```python
class STDIOTransport:
    async def handle_request(self, request):
        if method == "initialize":
            return capabilities
        if method == "tools/list":
            return {"tools": [spec for spec in TOOL_REGISTRY.values()]}
        if method == "tools/call":
            handler = TOOL_HANDLERS[name]
            return await handler(context, operation, **arguments)
```

---

## Story 6.1: Server Context & Dependency Injection (15 SP)

### Goal
Implement ServerContext class that wires together all components (API client, endpoints, utilities, job management) with proper async lifecycle.

### Tasks
1. Create `src/mcp_finnhub/server.py`
2. Implement `ServerContext` class
3. Wire FinnhubClient with API key from config
4. Instantiate all 15 endpoint APIs:
   - MarketAPI (market.py)
   - NewsAPI (news.py)
   - TechnicalAPI (technical.py)
   - FundamentalsAPI (fundamentals.py)
   - EstimatesAPI (estimates.py)
   - OwnershipAPI (ownership.py)
   - AlternativeAPI (alternative.py)
   - FilingsAPI (filings.py)
   - CryptoAPI (crypto.py)
   - ForexAPI (forex.py)
   - CalendarAPI (calendar.py)
   - EventsAPI (events.py)
   - (Future: ETF, MutualFund, Bond, Index, Economic, Specialized)
5. Wire all utilities:
   - TokenEstimator
   - PathResolver
   - FileWriter
   - JSONToCSVConverter
   - JobManager
   - BackgroundWorker
   - ResultOutputHandler
6. Implement `async def aclose()` for graceful shutdown
7. Implement `build_server_context(**overrides)` factory function
8. Write 10+ tests for ServerContext initialization and lifecycle

### Implementation Pattern (from mcp-fred)
```python
# src/mcp_finnhub/server.py
from .api import FinnhubClient
from .api.endpoints import (
    MarketAPI,
    NewsAPI,
    TechnicalAPI,
    # ... all 12 current endpoint APIs
)
from .config import AppConfig, load_config
from .utils import (
    TokenEstimator,
    PathResolver,
    FileWriter,
    JSONToCSVConverter,
    JobManager,
    BackgroundWorker,
    ResultOutputHandler,
)

class ServerContext:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

        # API Client
        self.client = FinnhubClient(
            api_key=config.finnhub_api_key,
            base_url=config.finnhub_base_url,
            timeout=config.finnhub_timeout,
            rate_limit_per_minute=config.finnhub_rate_limit_per_minute,
        )

        # Endpoint APIs (12 current)
        self.market = MarketAPI(self.client)
        self.news = NewsAPI(self.client)
        self.technical = TechnicalAPI(self.client)
        self.fundamentals = FundamentalsAPI(self.client)
        self.estimates = EstimatesAPI(self.client)
        self.ownership = OwnershipAPI(self.client)
        self.alternative = AlternativeAPI(self.client)
        self.filings = FilingsAPI(self.client)
        self.crypto = CryptoAPI(self.client)
        self.forex = ForexAPI(self.client)
        self.calendar = CalendarAPI(self.client)
        self.events = EventsAPI(self.client)

        # Utilities
        self.token_estimator = TokenEstimator(
            assume_context_used=config.output.assume_context_used,
            default_safe_limit=config.output.safe_token_limit,
        )
        self.csv_converter = JSONToCSVConverter()
        self.path_resolver = PathResolver(config.storage.directory)
        self.file_writer = FileWriter()
        self.job_manager = JobManager(retention_hours=config.job.retention_hours)
        self.background_worker = BackgroundWorker(
            self.job_manager,
            max_retries=config.job.max_retries,
        )
        self.output_handler = ResultOutputHandler(
            config,
            self.token_estimator,
            self.csv_converter,
            self.path_resolver,
            self.file_writer,
            self.job_manager,
        )

    async def aclose(self) -> None:
        await self.client.aclose()

def build_server_context(**overrides) -> ServerContext:
    config = load_config(**overrides)
    return ServerContext(config)
```

### Definition of Done
- ✅ ServerContext class implemented with all 12 endpoint APIs
- ✅ All utilities wired (TokenEstimator, PathResolver, FileWriter, JobManager, BackgroundWorker, ResultOutputHandler)
- ✅ Async lifecycle (aclose) working
- ✅ build_server_context() factory function
- ✅ 10+ tests with 90%+ coverage
- ✅ Zero linting errors

---

## Story 6.2: Tool Registry & Handlers (15 SP)

### Goal
Create tool registry system that maps all 15 data tools to MCP tool specs with enable/disable support based on ToolConfig.

### Tasks
1. Create `src/mcp_finnhub/transports/__init__.py`
2. Define `ToolHandler` type alias: `Callable[..., Awaitable[dict[str, Any]]]`
3. Create `ToolSpec` dataclass with name, handler, summary, enabled
4. Import all 15 tool implementations from `src/mcp_finnhub/tools/`:
   - finnhub_market_data (from tools/market_data.py)
   - finnhub_news_data (from tools/news_data.py)
   - finnhub_technical_analysis (from tools/technical_analysis.py)
   - finnhub_stock_fundamentals (from tools/stock_fundamentals.py)
   - finnhub_stock_estimates (from tools/stock_estimates.py)
   - finnhub_stock_ownership (from tools/stock_ownership.py)
   - finnhub_alternative_data (from tools/alternative_data.py)
   - finnhub_sec_filings (from tools/sec_filings.py)
   - finnhub_crypto_data (from tools/crypto_data.py)
   - finnhub_forex_data (from tools/forex_data.py)
   - finnhub_calendar_data (from tools/calendar_data.py)
   - finnhub_market_events (from tools/market_events.py)
   - finnhub_project_create (Story 6.4)
   - finnhub_project_list (Story 6.4)
   - finnhub_job_status (Story 6.4)
5. Create `_TOOL_SPECS` tuple with all 15 tool specs
6. Implement `build_tool_registry(config: ToolConfig)` that filters based on enabled tools
7. Create `TOOL_REGISTRY` and `TOOL_HANDLERS` module-level constants
8. Write 8+ tests for registry filtering and handler lookup

### Implementation Pattern (from mcp-fred)
```python
# src/mcp_finnhub/transports/__init__.py
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

from ..tools import (
    finnhub_market_data,
    finnhub_news_data,
    finnhub_technical_analysis,
    finnhub_stock_fundamentals,
    finnhub_stock_estimates,
    finnhub_stock_ownership,
    finnhub_alternative_data,
    finnhub_sec_filings,
    finnhub_crypto_data,
    finnhub_forex_data,
    finnhub_calendar_data,
    finnhub_market_events,
    finnhub_project_create,
    finnhub_project_list,
    finnhub_job_status,
)

ToolHandler = Callable[..., Awaitable[dict[str, Any]]]

@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: ToolHandler
    summary: str
    enabled: bool = True

_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec("finnhub_market_data", finnhub_market_data, "Real-time quotes, candles, profiles"),
    ToolSpec("finnhub_news_data", finnhub_news_data, "Company news and sentiment"),
    ToolSpec("finnhub_technical_analysis", finnhub_technical_analysis, "Indicators and patterns"),
    ToolSpec("finnhub_stock_fundamentals", finnhub_stock_fundamentals, "Financials and earnings"),
    ToolSpec("finnhub_stock_estimates", finnhub_stock_estimates, "Analyst estimates"),
    ToolSpec("finnhub_stock_ownership", finnhub_stock_ownership, "Insider trades"),
    ToolSpec("finnhub_alternative_data", finnhub_alternative_data, "ESG and sentiment"),
    ToolSpec("finnhub_sec_filings", finnhub_sec_filings, "SEC filings"),
    ToolSpec("finnhub_crypto_data", finnhub_crypto_data, "Cryptocurrency data"),
    ToolSpec("finnhub_forex_data", finnhub_forex_data, "Foreign exchange data"),
    ToolSpec("finnhub_calendar_data", finnhub_calendar_data, "IPO and earnings calendars"),
    ToolSpec("finnhub_market_events", finnhub_market_events, "Holidays and M&A"),
    ToolSpec("finnhub_project_create", finnhub_project_create, "Create project workspaces"),
    ToolSpec("finnhub_project_list", finnhub_project_list, "List projects"),
    ToolSpec("finnhub_job_status", finnhub_job_status, "Check job status"),
)

def build_tool_registry(config: ToolConfig) -> Mapping[str, ToolSpec]:
    specs = (spec for spec in _TOOL_SPECS if config.is_tool_enabled(spec.name))
    return OrderedDict((spec.name, spec) for spec in specs)

TOOL_REGISTRY: Mapping[str, ToolSpec] = build_tool_registry(ToolConfig())
TOOL_HANDLERS: Mapping[str, ToolHandler] = OrderedDict(
    (name, spec.handler) for name, spec in TOOL_REGISTRY.items()
)
```

### Definition of Done
- ✅ ToolSpec dataclass defined
- ✅ All 15 tools registered in _TOOL_SPECS
- ✅ build_tool_registry() with enable/disable logic
- ✅ TOOL_REGISTRY and TOOL_HANDLERS created
- ✅ 8+ tests with 95%+ coverage
- ✅ Zero linting errors

---

## Story 6.3: STDIO Transport & MCP Protocol (20 SP)

### Goal
Implement STDIO transport layer handling JSON-RPC protocol for MCP (initialize, tools/list, tools/call, ping).

### Tasks
1. Create `src/mcp_finnhub/transports/stdio.py`
2. Implement `STDIOTransport` class
3. Implement `async def run()` - main event loop reading from stdin
4. Implement `async def handle_request(request)` - JSON-RPC dispatcher
5. Handle `initialize` method - return protocol version and capabilities
6. Handle `tools/list` method - return all tools from TOOL_REGISTRY
7. Handle `tools/call` method - dispatch to tool handler with operation parameter
8. Handle `ping` method - return empty response
9. Handle `prompts/list` method - return empty (not implemented)
10. Handle `resources/list` method - return empty (not implemented)
11. Implement `async def _write_response(response)` - write JSON to stdout
12. Add error handling for malformed JSON and unknown methods
13. Write 15+ tests for all protocol methods and error cases

### Implementation Pattern (from mcp-fred)
```python
# src/mcp_finnhub/transports/stdio.py
import asyncio
import json
import sys
from typing import Any

from ..server import ServerContext, build_server_context
from . import TOOL_HANDLERS, TOOL_REGISTRY

class STDIOTransport:
    """JSON-RPC transport over stdin/stdout for MCP protocol."""

    def __init__(self, context: ServerContext | None = None) -> None:
        self._context = context or build_server_context()
        self._lock = asyncio.Lock()

    async def run(self) -> None:
        """Process messages from stdin until EOF."""
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
                    await self._write_response({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"},
                    })
                    continue
                response = await self.handle_request(request)
                if response is not None:
                    await self._write_response(response)
        finally:
            await self._context.aclose()

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process a single JSON-RPC request."""
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Handle notifications (no response)
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
                                # Tool-specific parameters added dynamically
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
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    async def _write_response(self, response: dict[str, Any]) -> None:
        loop = asyncio.get_running_loop()
        data = json.dumps(response, ensure_ascii=False)
        await loop.run_in_executor(None, sys.stdout.write, data + "\n")
        await loop.run_in_executor(None, sys.stdout.flush)
```

### Definition of Done
- ✅ STDIOTransport class implemented
- ✅ All MCP protocol methods handled (initialize, tools/list, tools/call, ping)
- ✅ JSON-RPC error handling
- ✅ Async lock for thread safety
- ✅ 15+ tests with 95%+ coverage
- ✅ Zero linting errors

---

## Story 6.4: Management Tools (20 SP)

### Goal
Implement 3 management tools for project and job management (create projects, list projects, check job status).

### Tasks

#### 6.4.1: finnhub_project_create (8 SP)
1. Create `src/mcp_finnhub/tools/project_create.py`
2. Implement `finnhub_project_create(context, operation, **kwargs)` async function
3. Support `create` operation with required `project` parameter
4. Validate project name (alphanumeric, hyphens, underscores only)
5. Create project directory: `{storage_dir}/{project_name}/`
6. Create subdirectories: `candles/`, `quotes/`, `news/`, `fundamentals/`, `technical/`, `jobs/`
7. Create `.project.json` metadata file with:
   ```json
   {
     "project": "project_name",
     "created_at": "2025-11-18T10:30:00Z",
     "subdirectories": ["candles", "quotes", ...]
   }
   ```
8. Return success response with project path and metadata
9. Handle errors: invalid name, project exists
10. Write 8 tests

#### 6.4.2: finnhub_project_list (6 SP)
1. Create `src/mcp_finnhub/tools/project_list.py`
2. Implement `finnhub_project_list(context, operation, **kwargs)` async function
3. Support `list` operation (no required parameters)
4. Scan `{storage_dir}/` for directories with `.project.json`
5. For each project, return:
   - Project name
   - Created date
   - Subdirectories
   - File counts per subdirectory
   - Total size
6. Sort by created date (newest first)
7. Write 6 tests

#### 6.4.3: finnhub_job_status (6 SP)
1. Create `src/mcp_finnhub/tools/job_status.py`
2. Implement `finnhub_job_status(context, operation, **kwargs)` async function
3. Support `get` operation with required `job_id` parameter
4. Use `context.job_manager.get_job(job_id)` to fetch job
5. Return job details:
   - job_id
   - status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
   - progress (percent complete)
   - created_at, updated_at
   - result (if completed)
   - error (if failed)
6. Handle error: job not found
7. Write 5 tests

### Implementation Patterns
```python
# src/mcp_finnhub/tools/project_create.py
import re
from datetime import UTC, datetime
from typing import Any

SUPPORTED_OPERATIONS = ["create"]
VALID_NAME = re.compile(r"^[A-Za-z0-9_-]+$")
SUBDIRECTORIES = ["candles", "quotes", "news", "fundamentals", "technical", "jobs"]

async def finnhub_project_create(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    if operation != "create":
        return {"error": f"Unknown operation: {operation}"}

    project_name = kwargs.get("project")
    if not project_name:
        return {"error": "Missing required parameter: project"}

    if not VALID_NAME.fullmatch(project_name):
        return {"error": "Invalid project name"}

    root = context.path_resolver.root
    project_dir = root / project_name
    if project_dir.exists():
        return {"error": f"Project '{project_name}' already exists"}

    # Create directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    for subdir in SUBDIRECTORIES:
        (project_dir / subdir).mkdir(exist_ok=True)

    # Create metadata
    metadata = {
        "project": project_name,
        "created_at": datetime.now(UTC).isoformat(),
        "subdirectories": SUBDIRECTORIES,
    }
    metadata_path = project_dir / ".project.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    return {
        "project": project_name,
        "path": str(project_dir),
        "metadata_file": str(metadata_path),
    }
```

### Definition of Done
- ✅ finnhub_project_create implemented with validation
- ✅ finnhub_project_list implemented with file stats
- ✅ finnhub_job_status implemented with JobManager integration
- ✅ 19 tests total with 90%+ coverage
- ✅ Zero linting errors

---

## Story 6.5: Main Entry Point & CLI (10 SP)

### Goal
Create main entry point (__main__.py) and CLI script for running the MCP server.

### Tasks
1. Create `src/mcp_finnhub/__main__.py`
2. Implement `main()` function:
   - Build server context from config
   - Create STDIOTransport
   - Run transport with asyncio.run()
   - Handle KeyboardInterrupt gracefully
3. Add entry point to `pyproject.toml`:
   ```toml
   [project.scripts]
   mcp-finnhub = "mcp_finnhub.__main__:main"
   ```
4. Test CLI execution: `python -m mcp_finnhub`
5. Test installed script: `mcp-finnhub` (after `uv pip install -e .`)
6. Write 3 tests for main() execution

### Implementation Pattern (from mcp-fred)
```python
# src/mcp_finnhub/__main__.py
"""Command-line interface for running mcp-finnhub via STDIO transport."""

from __future__ import annotations

import asyncio
from contextlib import suppress

from .server import build_server_context
from .transports.stdio import STDIOTransport


def main() -> None:
    """Run the mcp-finnhub server using STDIO transport for Claude Desktop."""
    context = build_server_context()
    transport = STDIOTransport(context)
    with suppress(KeyboardInterrupt):
        asyncio.run(transport.run())


if __name__ == "__main__":
    main()
```

### Definition of Done
- ✅ __main__.py implemented
- ✅ CLI script added to pyproject.toml
- ✅ CLI execution working (`python -m mcp_finnhub`)
- ✅ Installed script working (`mcp-finnhub`)
- ✅ 3 tests with 100% coverage
- ✅ Zero linting errors

---

## Story 6.6: Integration Testing & Quality (10 SP)

### Goal
Create comprehensive integration tests for MCP server, tool registry, and end-to-end tool execution.

### Tasks
1. Create `tests/test_integration/test_sprint6_integration.py`
2. Test ServerContext initialization:
   - All 12 endpoint APIs wired correctly
   - All utilities initialized
   - Config propagated correctly
3. Test tool registry:
   - All 15 tools registered
   - Enable/disable filtering works
   - Tool handlers callable
4. Test STDIO transport:
   - initialize method returns correct capabilities
   - tools/list returns all 15 tools
   - tools/call dispatches to correct handler
   - Error handling for unknown tools
5. Test end-to-end tool execution:
   - Call finnhub_market_data via transport
   - Call finnhub_project_create via transport
   - Verify response format matches MCP spec
6. Test graceful shutdown:
   - Context closes cleanly
   - Client connection closed
7. Run full test suite: `pytest --cov=mcp_finnhub --cov-fail-under=90`
8. Run linting: `ruff check .`
9. Run formatting: `ruff format .`
10. Write 12+ integration tests

### Definition of Done
- ✅ 12+ integration tests covering all components
- ✅ All 584+ tests passing (previous + new)
- ✅ 90%+ overall test coverage
- ✅ Zero linting errors
- ✅ Zero formatting issues

---

## Sprint 6 Deliverables

### Code Deliverables
1. **Server Infrastructure**
   - `src/mcp_finnhub/server.py` - ServerContext with DI
   - `src/mcp_finnhub/transports/__init__.py` - Tool registry
   - `src/mcp_finnhub/transports/stdio.py` - STDIO transport
   - `src/mcp_finnhub/__main__.py` - CLI entry point

2. **Management Tools (3)**
   - `src/mcp_finnhub/tools/project_create.py`
   - `src/mcp_finnhub/tools/project_list.py`
   - `src/mcp_finnhub/tools/job_status.py`

3. **Tests**
   - `tests/test_server.py` - ServerContext tests (10 tests)
   - `tests/test_transports/test_registry.py` - Tool registry tests (8 tests)
   - `tests/test_transports/test_stdio.py` - STDIO transport tests (15 tests)
   - `tests/test_tools/test_project_create.py` - Project create tests (8 tests)
   - `tests/test_tools/test_project_list.py` - Project list tests (6 tests)
   - `tests/test_tools/test_job_status.py` - Job status tests (5 tests)
   - `tests/test_integration/test_sprint6_integration.py` - E2E tests (12 tests)

### Key Metrics
- **Story Points:** 90 SP (15+15+20+20+10+10)
- **Files Created:** ~10 implementation + test files
- **Lines of Code:** ~2,000 lines
- **Tests:** 64 new tests (previous 584 + 64 = 648 total)
- **Coverage:** 90%+ overall
- **Tools Total:** 15 tools (12 data + 3 management)

---

## Integration Points

### With Previous Sprints
- **Sprint 1-2:** Uses AppConfig, ToolConfig, JobManager, BackgroundWorker, all utilities
- **Sprint 3:** Integrates finnhub_market_data, finnhub_news_data, finnhub_technical_analysis
- **Sprint 4:** Integrates 5 stock analysis tools
- **Sprint 5:** Integrates 4 multi-asset tools

### With Future Sprints
- **Sprint 7:** Documentation will reference MCP server usage, tool list, example tool calls

---

## Testing Strategy

### Unit Tests (52 tests)
- ServerContext: 10 tests
- Tool registry: 8 tests
- STDIO transport: 15 tests
- Project create: 8 tests
- Project list: 6 tests
- Job status: 5 tests

### Integration Tests (12 tests)
- ServerContext + Config integration
- Tool registry + ToolConfig integration
- STDIO transport + Tool handlers integration
- End-to-end tool execution via transport
- Graceful shutdown and cleanup

### Coverage Goals
- server.py: 95%+
- transports/: 95%+
- tools/management/: 90%+
- Overall: 90%+

---

## Success Criteria

### Functional
- ✅ MCP server starts via `python -m mcp_finnhub`
- ✅ Server responds to `initialize` request
- ✅ Server lists all 15 enabled tools via `tools/list`
- ✅ Server executes tools via `tools/call` with operation parameter
- ✅ Management tools create projects, list projects, check job status
- ✅ Server handles errors gracefully (unknown tool, invalid operation, missing params)

### Quality
- ✅ 648+ tests passing (100% pass rate)
- ✅ 90%+ test coverage
- ✅ Zero linting errors (ruff check)
- ✅ Zero formatting issues (ruff format)
- ✅ Type hints on all public APIs
- ✅ Docstrings on all public functions/classes

### Performance
- ✅ Server starts in <1 second
- ✅ Tool dispatch adds <10ms overhead
- ✅ Async operations non-blocking

---

## Risk Mitigation

### Risk 1: STDIO Transport Complexity
**Mitigation:** Follow mcp-fred's proven STDIO implementation exactly. Use their test patterns.

### Risk 2: Tool Handler Signatures
**Mitigation:** All 15 tools already use `async def tool_name(context, operation, **kwargs)` signature from Sprints 3-5.

### Risk 3: Integration Testing Scope
**Mitigation:** Focus on smoke tests (one tool per category). Detailed tool testing already done in Sprints 3-5.

---

## Dependencies

### Required Before Sprint 6
- ✅ Sprint 1: Configuration system (AppConfig, ToolConfig)
- ✅ Sprint 2: JobManager, BackgroundWorker, utilities
- ✅ Sprint 3-5: All 15 data tools implemented

### Blocking Issues
- None. All dependencies satisfied.

---

## Timeline

**Sprint Duration:** 1 session (4-6 hours)

### Execution Order
1. Story 6.1: Server Context (foundation for everything else)
2. Story 6.4: Management Tools (needed by tool registry)
3. Story 6.2: Tool Registry (all 15 tools must exist first)
4. Story 6.3: STDIO Transport (needs registry)
5. Story 6.5: Main Entry Point (needs transport)
6. Story 6.6: Integration Testing (needs everything)

---

## Post-Sprint: What's Next?

### Sprint 7: Documentation & Release (70 SP)
With Sprint 6 complete, Sprint 7 will focus on:
1. Comprehensive README.md with installation, configuration, examples
2. API_REFERENCE.md mapping all 108 endpoints to 15 tools
3. CONTRIBUTING.md for open source
4. GitHub Actions CI/CD (test, lint, coverage, publish)
5. End-to-end and performance testing
6. PyPI package preparation and publish
7. v1.0.0 release

---

## Sprint 6 Completion Checklist

### Before Starting
- [ ] Review Sprint 5 completion (all 15 tools working)
- [ ] Review mcp-fred reference implementation
- [ ] Understand MCP protocol specification

### During Sprint
- [ ] Story 6.1: ServerContext complete
- [ ] Story 6.2: Tool registry complete
- [ ] Story 6.3: STDIO transport complete
- [ ] Story 6.4: Management tools complete
- [ ] Story 6.5: Main entry point complete
- [ ] Story 6.6: Integration tests complete

### Before Completion
- [ ] All 648+ tests passing
- [ ] 90%+ coverage maintained
- [ ] Zero linting errors
- [ ] Zero formatting issues
- [ ] Git commits follow semantic versioning
- [ ] CHANGELOG.md updated
- [ ] Serena memories updated

### Final Validation
- [ ] `python -m mcp_finnhub` starts server
- [ ] Server responds to MCP protocol methods
- [ ] All 15 tools accessible via MCP
- [ ] Management tools working (project create/list, job status)
- [ ] Comprehensive sprint summary provided

---

**Sprint 6 will complete the core MCP server implementation, making mcp-finnhub a fully functional MCP server ready for Claude Desktop integration!** 🚀
