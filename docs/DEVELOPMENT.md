# Development Guide - mcp-finnhub

## Technology Stack

### Core
- **Python 3.11+** - Modern Python with type hints
- **MCP SDK** - Model Context Protocol implementation
- **httpx** - Async HTTP client for Finnhub API
- **Pydantic** - Data validation and settings management
- **python-dotenv** - Environment variable management
- **tiktoken** - Token estimation for output sizing

### Code Quality & Testing

#### Ruff (All-in-One Tool) ✅
**Ruff handles BOTH linting AND formatting** - no need for separate Black installation.

- **Linting**: Replaces Flake8, isort, pyupgrade, and more
- **Formatting**: Black-compatible formatter built-in
- **Speed**: 10-100x faster than traditional tools
- **Configuration**: Single `[tool.ruff]` section in pyproject.toml

**Benefits:**
- One tool instead of multiple (Flake8 + Black + isort + pyupgrade)
- Faster CI/CD pipelines
- Consistent style enforcement
- Auto-fix capabilities

#### PyTest Testing Suite ✅
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **respx** - HTTP request mocking
- **Minimum Coverage: 80%** - Enforced via pytest-cov

---

## Development Setup

### 1. Prerequisites

```bash
# Python 3.11 or higher
python --version  # Should be 3.11+

# uv (recommended) or pip
brew install uv
```

### 2. Clone and Setup

```bash
cd /Users/robsherman/Servers/mcp-finnhub
git checkout dev

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
# OR with pip:
pip install -e ".[dev]"
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API key
vim .env
# Add: FINNHUB_API_KEY=your_key_here
```

---

## Code Quality Tools

### Ruff - Linting & Formatting

#### Run Linter

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific files
ruff check src/mcp_finnhub/tools/
```

#### Run Formatter

```bash
# Check formatting (dry-run)
ruff format --check .

# Format code
ruff format .

# Format specific files
ruff format src/mcp_finnhub/
```

#### Ruff Configuration (pyproject.toml)

```toml
[tool.ruff]
# Python version
target-version = "py311"

# Line length (Black-compatible)
line-length = 100

# Exclude directories
exclude = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "*.egg-info",
]

[tool.ruff.lint]
# Enable rule sets
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "Q",     # flake8-quotes
    "RUF",   # Ruff-specific rules
]

# Disable specific rules
ignore = [
    "E501",   # Line too long (handled by formatter)
    "B008",   # Function call in argument defaults (FastAPI pattern)
    "UP007",  # Use X | Y syntax (prefer Optional for clarity)
]

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

# Allow unused variables when underscore-prefixed
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[tool.ruff.lint.per-file-ignores]
# Tests can use magic values, assertions, etc.
"tests/**/*.py" = [
    "S101",    # Use of assert
    "PLR2004", # Magic value used in comparison
]

[tool.ruff.lint.isort]
known-first-party = ["mcp_finnhub"]
combine-as-imports = true

[tool.ruff.format]
# Use double quotes for strings
quote-style = "double"

# Indent with spaces
indent-style = "space"

# Respect magic trailing comma
skip-magic-trailing-comma = false

# Line endings (auto-detect)
line-ending = "auto"
```

---

## Testing

### PyTest Configuration

#### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_finnhub --cov-report=html

# Run specific test file
pytest tests/test_tools/test_quote.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_tools/test_quote.py::test_quote_success

# Run tests matching pattern
pytest -k "test_quote"

# Run tests in parallel (with pytest-xdist)
pytest -n auto
```

#### Coverage Reports

```bash
# Terminal report with missing lines
pytest --cov=mcp_finnhub --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=mcp_finnhub --cov-report=html
open htmlcov/index.html

# Fail if coverage below 80%
pytest --cov=mcp_finnhub --cov-fail-under=80
```

#### PyTest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
# Test discovery patterns
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Options
addopts = [
    "-v",                           # Verbose output
    "--strict-markers",             # Raise error on unknown markers
    "--tb=short",                   # Shorter traceback format
    "--cov=mcp_finnhub",           # Coverage for mcp_finnhub package
    "--cov-report=term-missing",   # Show missing lines in terminal
    "--cov-report=html",           # Generate HTML coverage report
    "--cov-fail-under=80",         # Fail if coverage below 80%
]

# Async test support
asyncio_mode = "auto"

# Markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src/mcp_finnhub"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api/
│   ├── test_client.py       # HTTP client tests
│   └── test_endpoints/
│       ├── test_technical_analysis.py
│       ├── test_market_data.py
│       └── ...
├── test_tools/
│   ├── test_technical_analysis.py
│   ├── test_stock_market_data.py
│   ├── test_news.py
│   └── ...
└── test_utils/
    ├── test_token_estimator.py
    ├── test_output_handler.py
    ├── test_job_manager.py
    └── ...
```

### Example Test

```python
# tests/conftest.py
import pytest
from mcp_finnhub.config import AppConfig, ToolConfig
from mcp_finnhub.server import ServerContext

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return AppConfig(
        finnhub_api_key="test_key",
        storage_directory="/tmp/finnhub-test",
        safe_token_limit=50000,
        tools=ToolConfig(
            technical_analysis=True,
            stock_market_data=True,
            news_sentiment=True,
        )
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
from mcp_finnhub.tools.stock_market_data import finnhub_stock_market_data

@pytest.mark.asyncio
async def test_quote_success(server_context):
    """Test successful quote retrieval."""

    # Mock API response
    with respx.mock:
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=Response(
                200,
                json={
                    "c": 150.25,  # Current price
                    "h": 151.00,  # High
                    "l": 149.50,  # Low
                    "o": 150.00,  # Open
                    "pc": 149.75, # Previous close
                    "t": 1699999999
                }
            )
        )

        # Call tool
        result = await finnhub_stock_market_data(
            server_context,
            operation="quote",
            symbol="AAPL"
        )

        # Assert
        assert "error" not in result
        assert result["data"]["c"] == 150.25
        assert result["data"]["symbol"] == "AAPL"

@pytest.mark.asyncio
async def test_quote_missing_symbol(server_context):
    """Test quote with missing symbol parameter."""

    result = await finnhub_stock_market_data(
        server_context,
        operation="quote"
        # Missing symbol
    )

    # Assert error
    assert "error" in result
    assert result["error"]["code"] == "MISSING_PARAMETER"
    assert "symbol" in result["error"]["message"]

@pytest.mark.asyncio
async def test_quote_api_error(server_context):
    """Test quote with API error."""

    with respx.mock:
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=Response(
                401,
                json={"error": "Invalid API key"}
            )
        )

        result = await finnhub_stock_market_data(
            server_context,
            operation="quote",
            symbol="AAPL"
        )

        assert "error" in result
        assert result["error"]["status_code"] == 401
```

---

## Pre-commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### Configuration (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      # Run linter
      - id: ruff
        args: [--fix]
      # Run formatter
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml

  - repo: local
    hooks:
      # Run tests before commit
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### Manual Run

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files
```

---

## CI/CD with GitHub Actions

### Workflow (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"

      - name: Run Ruff linter
        run: ruff check .

      - name: Run Ruff formatter
        run: ruff format --check .

      - name: Run tests with coverage
        run: |
          pytest --cov=mcp_finnhub --cov-report=xml --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/add-indicators-tool
```

### 2. Write Code

```bash
# Edit files
vim src/mcp_finnhub/tools/technical_analysis.py

# Format code
ruff format .

# Check linting
ruff check --fix .
```

### 3. Write Tests

```bash
# Create test file
vim tests/test_tools/test_technical_analysis.py

# Run tests
pytest tests/test_tools/test_technical_analysis.py

# Check coverage
pytest --cov=mcp_finnhub --cov-report=term-missing
```

### 4. Commit Changes

```bash
# Pre-commit hooks run automatically
git add .
git commit -m "feat(tools): add technical analysis tool with 4 operations"

# Hooks will run:
# - Ruff linting (with auto-fix)
# - Ruff formatting
# - PyTest (with 80% coverage check)
```

### 5. Push and PR

```bash
git push origin feature/add-indicators-tool

# Create PR on GitHub
# CI will run full test suite
```

---

## Code Quality Standards

### Required Checks

✅ **Ruff linting** - No errors allowed
✅ **Ruff formatting** - Must pass format check
✅ **PyTest** - All tests must pass
✅ **Coverage** - Minimum 80% code coverage
✅ **Type hints** - All functions must have type hints
✅ **Docstrings** - All public functions must have docstrings

### Coverage Targets by Module

| Module | Target | Priority |
|--------|--------|----------|
| tools/ | 90%+ | High |
| api/ | 85%+ | High |
| utils/ | 85%+ | High |
| config.py | 80%+ | Medium |
| server.py | 80%+ | Medium |

### Type Checking (Optional but Recommended)

```bash
# Install mypy
pip install mypy

# Run type checking
mypy src/mcp_finnhub
```

Add to pyproject.toml:

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## Troubleshooting

### Ruff Issues

```bash
# Clear cache
ruff clean

# Regenerate cache
ruff check --fix .
```

### Test Issues

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Clear coverage data
rm -rf .coverage htmlcov/

# Reinstall package
pip install -e ".[dev]"
```

### Coverage Below 80%

```bash
# Identify untested code
pytest --cov=mcp_finnhub --cov-report=term-missing

# Focus on specific module
pytest tests/test_tools/ --cov=mcp_finnhub.tools --cov-report=term-missing
```

---

## Summary

### Single Command for All Checks

```bash
# Run before every commit
ruff check --fix . && ruff format . && pytest --cov=mcp_finnhub --cov-fail-under=80
```

### Tools Used

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Linting + Formatting | `[tool.ruff]` in pyproject.toml |
| **PyTest** | Testing | `[tool.pytest.ini_options]` in pyproject.toml |
| **pytest-cov** | Coverage | `[tool.coverage.*]` in pyproject.toml |
| **pre-commit** | Git hooks | `.pre-commit-config.yaml` |

### Why Ruff Only (No Black)?

✅ Ruff includes a Black-compatible formatter
✅ Faster than Black (10-100x)
✅ Single tool for linting + formatting
✅ Active development and great performance
✅ Used by major projects (Pandas, FastAPI, Pydantic)

---

## Next Steps

1. ✅ Install dependencies: `uv pip install -e ".[dev]"`
2. ✅ Setup pre-commit: `pre-commit install`
3. ✅ Run initial checks: `ruff check . && ruff format . && pytest`
4. ✅ Start coding!
