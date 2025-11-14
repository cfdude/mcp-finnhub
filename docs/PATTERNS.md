# MCP Server Patterns - Learnings from Existing Servers

Analysis of Python MCP servers to identify proven patterns and best practices for mcp-finnhub.

---

## Servers Analyzed

1. **mcp-fred** - Federal Reserve Economic Data API
2. **alpha-vantage-mcp** - Alpha Vantage Financial API (Python & TypeScript)
3. **snowflake-mcp-server** - Snowflake Database Access

---

## Pattern 1: Project Structure

### mcp-fred Structure ✅ (Primary Reference)

```
mcp-fred/
├── src/mcp_fred/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py              # Configuration with Pydantic
│   ├── server.py              # ServerContext, dependency injection
│   ├── api/
│   │   ├── client.py          # HTTP client (httpx)
│   │   ├── endpoints/         # API endpoint implementations
│   │   └── models/            # Pydantic response models
│   ├── tools/                 # MCP tool implementations
│   │   ├── _common.py         # Shared utilities
│   │   └── *.py               # Individual tools
│   ├── utils/                 # Utilities
│   │   ├── token_estimator.py
│   │   ├── file_writer.py
│   │   ├── json_to_csv.py
│   │   ├── output_handler.py
│   │   ├── job_manager.py
│   │   └── background_worker.py
│   └── transports/
│       └── stdio.py
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── pyproject.toml
├── .env.example
└── README.md
```

**Key Takeaways:**
- Clean separation: api, tools, utils, transports
- ServerContext pattern for dependency injection
- Comprehensive utils for file handling, tokens, jobs
- Type safety with Pydantic throughout

---

### alpha-vantage-mcp Structure (Python)

```
alpha-vantage-mcp/server/
├── lambda_function.py         # AWS Lambda entry point
├── local_http_server.py       # Local HTTP server
├── src/
│   ├── stdio_server.py        # STDIO server
│   ├── common.py              # Shared utilities
│   ├── context.py             # Request context
│   ├── decorators.py          # Tool decorators
│   ├── oauth.py               # OAuth support
│   ├── tools/
│   │   ├── registry.py        # ⭐ Central tool registration
│   │   ├── *_router.py        # Tool routers
│   │   ├── *_schema.py        # Pydantic schemas
│   │   └── *_unified.py       # Unified implementations
│   ├── decision/              # Decision-making logic
│   ├── output/                # Output handling
│   │   └── token_estimator.py
│   ├── utils/                 # Utilities
│   └── integration/           # Third-party integrations
├── pyproject.toml
└── tests/
```

**Key Takeaways:**
- **Registry pattern** for tool management (central registration)
- **Router/Schema/Unified pattern** for tool organization
- Multiple transport options (STDIO, HTTP, Lambda)
- OAuth support for authenticated APIs
- Decision module for smart routing
- Decorators for consistent tool behavior

---

### snowflake-mcp-server Structure

```
snowflake-mcp-server/
├── snowflake_mcp_server/
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration
│   ├── security/              # ⭐ Security module
│   │   ├── authentication.py
│   │   └── sql_injection.py
│   ├── rate_limiting/         # ⭐ Rate limiting
│   │   ├── rate_limiter.py
│   │   ├── circuit_breaker.py
│   │   ├── quota_manager.py
│   │   └── backoff.py
│   ├── monitoring/            # ⭐ Monitoring & metrics
│   │   ├── metrics.py
│   │   ├── alerts.py
│   │   ├── dashboards.py
│   │   └── structured_logging.py
│   ├── transports/
│   │   └── http_server.py
│   └── utils/
│       ├── token_estimator.py
│       ├── output_handler.py
│       ├── session_manager.py
│       ├── connection_multiplexer.py
│       ├── health_monitor.py
│       └── ...
├── pyproject.toml
└── tests/
```

**Key Takeaways:**
- **Security-first** with dedicated security module
- **Comprehensive rate limiting** (circuit breaker, backoff, quota)
- **Production monitoring** (metrics, alerts, structured logging)
- Session management for stateful connections
- Health monitoring built-in

---

## Pattern 2: Configuration Management

### mcp-fred Configuration ✅

```python
# config.py
from pydantic import BaseModel, Field
from dotenv import load_dotenv

class AppConfig(BaseModel):
    # Required
    fred_api_key: str

    # Storage
    storage_directory: str = Field(default="./fred-data")
    default_project: str = Field(default="default")

    # Output
    output_format: str = Field(default="csv")
    safe_token_limit: int = Field(default=50_000, ge=1)

    # Rate limiting
    max_requests_per_minute: int = Field(default=120, ge=1)

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        return cls(
            fred_api_key=os.getenv("FRED_API_KEY"),
            storage_directory=os.getenv("FRED_STORAGE_DIR", "./fred-data"),
            # ... etc
        )
```

**Benefits:**
- Type safety with Pydantic validation
- Default values for optional config
- Environment variable loading
- Field validation (ge, le, etc.)

---

### alpha-vantage Configuration (Registry Pattern)

```python
# tools/registry.py
TOOL_MODULES = {
    "core_stock_apis": "src.tools.core_stock_apis",
    "technical_indicators": "src.tools.technical_indicators",
    # ... etc
}

ENTITLEMENT_CATEGORIES = {
    "core_stock_apis",
    "technical_indicators",
    # Tools that need premium access
}

def register_tools(server, config):
    """Dynamically register tools based on config."""
    for name, module_path in TOOL_MODULES.items():
        if config.is_enabled(name):
            module = importlib.import_module(module_path)
            for tool in module.get_tools():
                server.add_tool(tool)
```

**Benefits:**
- Lazy loading of tools
- Easy enable/disable per category
- Entitlement tracking
- Dynamic tool discovery

---

## Pattern 3: API Client Architecture

### mcp-fred HTTP Client ✅

```python
# api/client.py
import httpx
from typing import Any, Dict, Optional

class FREDClient:
    def __init__(self, config: FREDClientConfig):
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout),
            limits=httpx.Limits(
                max_connections=config.max_connections
            )
        )
        self.rate_limiter = RateLimiter(config.max_requests_per_minute)

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Add API key
        params = params or {}
        params["api_key"] = self.api_key

        # Rate limiting
        await self.rate_limiter.acquire()

        # Make request with retry
        response = await self._request_with_retry(
            "GET",
            f"{self.base_url}{endpoint}",
            params=params
        )

        return response.json()

    async def _request_with_retry(self, method: str, url: str, **kwargs):
        """Retry with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise FREDAPIError.from_response(e.response)
```

**Benefits:**
- Async HTTP client (httpx)
- Built-in rate limiting
- Automatic retry with exponential backoff
- Error handling with custom exceptions
- Connection pooling

---

## Pattern 4: Tool Implementation

### mcp-fred Tool Pattern ✅

```python
# tools/series.py
from typing import Any, Dict
from ..server import ServerContext
from . import _common

SUPPORTED_OPERATIONS = [
    "get",
    "search",
    "get_observations",
    # ... etc
]

async def fred_series(
    context: ServerContext,
    operation: str,
    **kwargs: Any
) -> Dict[str, Any]:
    # Validate output options
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    # Route to operation
    if operation == "get_observations":
        symbol, err = _common.require_str(kwargs, "series_id")
        if err:
            return err

        # Call API
        result = await context.series.get_series_observations(
            symbol, params=_common.build_query(kwargs)
        )

        # Estimate size
        estimated_tokens = _estimate_tokens(context, result.observations)

        # Smart output handling
        return await _common.success_response(
            context,
            result,
            operation=operation,
            options=options,
            estimated_rows=len(result.observations),
            estimated_tokens=estimated_tokens,
            category="series"
        )

    # ... handle other operations
```

**Benefits:**
- Operation-based routing (one tool, multiple operations)
- Shared validation via _common module
- Consistent error handling
- Token estimation for smart output
- Contextual response handling

---

### alpha-vantage Router/Schema/Unified Pattern

```python
# tools/moving_average_router.py
def create_moving_average_tool():
    """Factory function for moving average tool."""
    return {
        "name": "moving_average",
        "description": "Calculate moving averages (SMA, EMA, WMA, etc.)",
        "inputSchema": MOVING_AVERAGE_SCHEMA,
        "handler": handle_moving_average
    }

# tools/moving_average_schema.py
MOVING_AVERAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "indicator": {
            "type": "string",
            "enum": ["SMA", "EMA", "WMA", "DEMA", "TEMA"]
        },
        "interval": {"type": "string"},
        "time_period": {"type": "integer"},
    },
    "required": ["symbol", "indicator", "interval"]
}

# tools/moving_average_unified.py
async def handle_moving_average(symbol: str, indicator: str, **params):
    """Unified handler for all moving average indicators."""
    # Route to appropriate API endpoint
    endpoint = INDICATOR_ENDPOINTS[indicator]
    return await fetch_indicator_data(endpoint, symbol, **params)
```

**Benefits:**
- Clear separation of concerns
- Schema-first design
- Factory pattern for tool creation
- Unified handlers reduce duplication

---

## Pattern 5: Output Handling

### mcp-fred Smart Output Handler ✅

```python
# utils/output_handler.py
class ResultOutputHandler:
    def __init__(
        self,
        config: AppConfig,
        token_estimator: TokenEstimator,
        csv_converter: JSONToCSVConverter,
        path_resolver: PathResolver,
        file_writer: FileWriter,
        job_manager: JobManager
    ):
        self.config = config
        self.token_estimator = token_estimator
        self.csv_converter = csv_converter
        self.path_resolver = path_resolver
        self.file_writer = file_writer
        self.job_manager = job_manager

    async def handle(
        self,
        data: Any,
        operation: str,
        output: str,  # auto, screen, file
        format: str,  # csv, json
        project: Optional[str],
        filename: Optional[str],
        estimated_rows: Optional[int],
        estimated_tokens: Optional[int],
        subdir: Optional[str],
        job_id: Optional[str]
    ) -> Dict[str, Any]:
        """Smart output handling based on size and mode."""

        # Determine output mode
        if output == "auto":
            # Check if data exceeds token limit
            if estimated_tokens and estimated_tokens > self.config.safe_token_limit:
                output = "file"
            else:
                output = "screen"

        if output == "screen":
            # Return data directly
            return {"data": data, "format": format}

        elif output == "file":
            # Save to file
            file_path = await self._save_to_file(
                data, format, project, filename, subdir
            )
            return {
                "status": "success",
                "file_path": str(file_path),
                "format": format,
                "rows": estimated_rows
            }
```

**Benefits:**
- Auto mode for smart decisions
- Token-based output routing
- File streaming for large datasets
- Consistent response format

---

## Pattern 6: Token Estimation

### All Servers Use tiktoken ✅

```python
# utils/token_estimator.py
import tiktoken
from typing import Any, List, Dict

class TokenEstimator:
    def __init__(
        self,
        assume_context_used: float = 0.75,
        default_safe_limit: int = 50_000
    ):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.assume_context_used = assume_context_used
        self.safe_limit = int(default_safe_limit * (1 - assume_context_used))

    def estimate_records(self, records: List[Dict[str, Any]]) -> int:
        """Estimate tokens for list of records."""
        # Sample first few records
        sample_size = min(10, len(records))
        sample_tokens = sum(
            self.estimate_text(str(record))
            for record in records[:sample_size]
        )

        # Extrapolate
        avg_tokens_per_record = sample_tokens / sample_size
        total_estimated = int(avg_tokens_per_record * len(records))

        return total_estimated

    def estimate_text(self, text: str) -> int:
        """Estimate tokens for text string."""
        return len(self.encoder.encode(text))

    def exceeds_limit(self, estimated_tokens: int) -> bool:
        """Check if estimated tokens exceed safe limit."""
        return estimated_tokens > self.safe_limit
```

**Benefits:**
- Conservative estimation (assume 75% context used)
- Sampling for large datasets
- LLM-specific safe limits
- Fast estimation

---

## Pattern 7: Rate Limiting

### snowflake-mcp Comprehensive Rate Limiting

```python
# rate_limiting/rate_limiter.py
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = deque()

    async def acquire(self) -> None:
        """Acquire permission to make request."""
        now = datetime.now()

        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()

        # Check if we can make request
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest = self.requests[0]
            wait_until = oldest + self.window
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

        # Record this request
        self.requests.append(now)

# rate_limiting/circuit_breaker.py
class CircuitBreaker:
    """Circuit breaker for failing endpoints."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"  # closed, open, half_open
        self.next_attempt = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if datetime.now() < self.next_attempt:
                raise CircuitBreakerOpenError()
            self.state = "half_open"

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failures = 0
        self.state = "closed"

    def _on_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.next_attempt = datetime.now() + timedelta(
                seconds=self.recovery_timeout
            )
```

**Benefits:**
- Token bucket algorithm
- Circuit breaker for reliability
- Automatic recovery
- Configurable thresholds

---

## Pattern 8: Background Jobs

### mcp-fred Job Management ✅

```python
# utils/job_manager.py
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JobManager:
    """Manage background jobs."""

    def __init__(self, retention_hours: int = 24):
        self.jobs: Dict[str, Job] = {}
        self.retention_hours = retention_hours

    async def create_job(self) -> Job:
        """Create a new job."""
        job = Job(
            job_id=f"finnhub-job-{uuid.uuid4().hex[:8]}",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.jobs[job.job_id] = job
        return job

    async def update_progress(
        self,
        job_id: str,
        progress: Optional[int] = None,
        estimated_total: Optional[int] = None,
        **metadata
    ):
        """Update job progress."""
        job = self.jobs[job_id]
        job.status = "running"
        job.progress = progress
        job.estimated_total = estimated_total
        job.metadata.update(metadata)
        job.updated_at = datetime.now()

    async def complete_job(self, job_id: str, result: Any):
        """Mark job as completed."""
        job = self.jobs[job_id]
        job.status = "completed"
        job.result = result
        job.completed_at = datetime.now()

    async def fail_job(self, job_id: str, error: Dict[str, Any]):
        """Mark job as failed."""
        job = self.jobs[job_id]
        job.status = "failed"
        job.error = error
        job.completed_at = datetime.now()

    async def cleanup_old_jobs(self):
        """Remove old completed/failed jobs."""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        self.jobs = {
            job_id: job
            for job_id, job in self.jobs.items()
            if job.updated_at > cutoff or job.status == "running"
        }

# utils/background_worker.py
class BackgroundWorker:
    """Execute background jobs."""

    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager
        self.tasks: Dict[str, asyncio.Task] = {}

    async def submit(self, job_id: str, coro):
        """Submit coroutine as background task."""
        task = asyncio.create_task(coro())
        self.tasks[job_id] = task

        # Cleanup on completion
        task.add_done_callback(lambda t: self.tasks.pop(job_id, None))

    async def cancel(self, job_id: str):
        """Cancel a running job."""
        if job_id in self.tasks:
            self.tasks[job_id].cancel()
            await self.job_manager.fail_job(
                job_id,
                {"code": "CANCELLED", "message": "Job cancelled by user"}
            )
```

**Benefits:**
- Async task management
- Progress tracking
- Job retention/cleanup
- Cancellation support

---

## Pattern 9: File Handling

### mcp-fred CSV Streaming ✅

```python
# utils/json_to_csv.py
import csv
from typing import Any, List, Dict
from pathlib import Path

class JSONToCSVConverter:
    """Convert JSON data to CSV with streaming support."""

    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    async def convert_and_save(
        self,
        data: List[Dict[str, Any]],
        file_path: Path,
        mode: str = "w"
    ):
        """Convert JSON records to CSV and save."""
        if not data:
            return

        # Get fieldnames from first record
        fieldnames = list(data[0].keys())

        # Write with chunking
        with open(file_path, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if mode == "w":
                writer.writeheader()

            for i in range(0, len(data), self.chunk_size):
                chunk = data[i:i + self.chunk_size]
                writer.writerows(chunk)
                # Flush periodically
                if i % (self.chunk_size * 10) == 0:
                    f.flush()
```

**Benefits:**
- Streaming for memory efficiency
- Chunked writes with periodic flush
- Append mode support
- UTF-8 encoding

---

## Pattern 10: Error Handling

### Consistent Error Response Format (All Servers)

```python
# api/client.py
class FinnhubAPIError(Exception):
    """Custom exception for Finnhub API errors."""

    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to error response format."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code
            }
        }

    @classmethod
    def from_response(cls, response: httpx.Response) -> "FinnhubAPIError":
        """Create error from HTTP response."""
        try:
            error_data = response.json()
            return cls(
                code=error_data.get("error", "API_ERROR"),
                message=error_data.get("message", str(response.text)),
                status_code=response.status_code
            )
        except:
            return cls(
                code="API_ERROR",
                message=str(response.text),
                status_code=response.status_code
            )

# tools/_common.py
def missing_parameter(name: str) -> Dict[str, Any]:
    return {
        "error": {
            "code": "MISSING_PARAMETER",
            "message": f"Missing required parameter '{name}'",
            "details": {"parameter": name}
        }
    }

def invalid_parameter(name: str, expected: str) -> Dict[str, Any]:
    return {
        "error": {
            "code": "INVALID_PARAMETER",
            "message": f"Parameter '{name}' must be {expected}",
            "details": {"parameter": name, "expected": expected}
        }
    }
```

**Benefits:**
- Consistent error format
- Error codes for programmatic handling
- Detailed error context
- HTTP status code mapping

---

## Pattern 11: Testing

### mcp-fred Testing Approach ✅

```python
# tests/conftest.py
import pytest
from mcp_fred.config import AppConfig
from mcp_fred.server import ServerContext

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return AppConfig(
        finnhub_api_key="test_key",
        storage_directory="/tmp/finnhub-test",
        safe_token_limit=50000,
    )

@pytest.fixture
async def server_context(mock_config):
    """Server context with mocked dependencies."""
    context = ServerContext(mock_config)
    yield context
    await context.aclose()

# tests/test_tools/test_quote.py
import pytest
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_quote_success(server_context):
    """Test successful quote retrieval."""

    # Mock API response
    with respx.mock:
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=Response(
                200,
                json={
                    "c": 150.25,
                    "h": 151.00,
                    "l": 149.50,
                    "o": 150.00,
                    "pc": 149.75
                }
            )
        )

        # Call tool
        result = await finnhub_quote(
            server_context,
            operation="get",
            symbol="AAPL"
        )

        # Assert
        assert result["status"] == "success"
        assert result["data"]["c"] == 150.25
```

**Benefits:**
- pytest-asyncio for async tests
- respx for HTTP mocking
- Fixture-based setup
- Isolated tests

---

## Recommended Patterns for mcp-finnhub

### Must Have (From mcp-fred)

1. ✅ **ServerContext pattern** - Dependency injection
2. ✅ **Operation-based tools** - One tool, multiple operations
3. ✅ **Smart output handling** - Auto/screen/file modes
4. ✅ **Token estimation** - tiktoken-based sizing
5. ✅ **Background jobs** - Async processing for large datasets
6. ✅ **Project-based storage** - Organized file management
7. ✅ **CSV/JSON streaming** - Memory-efficient file writes

### Should Have (From alpha-vantage)

8. ✅ **Tool registry** - Central tool management
9. ✅ **Enable/disable config** - Per-tool configuration
10. ✅ **Factory pattern** - Tool creation pattern

### Nice to Have (From snowflake)

11. ⚠️ **Circuit breaker** - For production reliability (future)
12. ⚠️ **Monitoring** - Metrics and alerts (future)
13. ⚠️ **Health checks** - Health endpoints (future)

---

## Implementation Priority

### Phase 1: Core Infrastructure (Week 1)
- mcp-fred patterns (#1-7)
- Basic tool registry (#8)
- Enable/disable configuration (#9)

### Phase 2: Tool Implementation (Week 2-3)
- Implement 23 tools
- Factory pattern for tools (#10)
- Full test coverage

### Phase 3: Production Hardening (Future)
- Circuit breaker (#11)
- Monitoring (#12)
- Health checks (#13)

---

## Anti-Patterns to Avoid

❌ **Don't** create one tool per API endpoint (use operation-based routing)
❌ **Don't** load all data into memory (use streaming)
❌ **Don't** return large datasets to screen (use token estimation)
❌ **Don't** hard-code configuration (use environment variables)
❌ **Don't** skip error handling (consistent error format)
❌ **Don't** forget rate limiting (respect API limits)
❌ **Don't** skip type hints (use Pydantic throughout)

---

## Conclusion

By combining the best patterns from mcp-fred (core infrastructure), alpha-vantage (tool management), and snowflake (production features), mcp-finnhub will be:

- **Well-structured** - Clean separation of concerns
- **Type-safe** - Pydantic validation throughout
- **Performant** - Async, streaming, token-aware
- **Flexible** - Configurable tools, multiple output modes
- **Reliable** - Rate limiting, error handling, background jobs
- **Open-source ready** - Extensible, documented, tested

Next steps: Begin implementation following these proven patterns.
