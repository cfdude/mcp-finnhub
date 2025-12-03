# Contributing to mcp-finnhub

Thank you for your interest in contributing to mcp-finnhub! This document provides guidelines and information for contributors.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- [Finnhub API key](https://finnhub.io/register)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/cfdude/mcp-finnhub.git
   cd mcp-finnhub
   ```

2. **Install dependencies**
   ```bash
   uv sync --all-extras
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your FINNHUB_API_KEY
   ```

4. **Run tests**
   ```bash
   uv run pytest --cov=mcp_finnhub
   ```

## Development Workflow

### Branching

- `main` - Production-ready code
- `dev` - Development branch (PR target)
- Feature branches from `dev`

### Making Changes

1. Create a feature branch from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Add tests for new functionality

4. Run the test suite:
   ```bash
   uv run pytest --cov=mcp_finnhub --cov-fail-under=80
   ```

5. Run linting and formatting:
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```

6. Commit your changes:
   ```bash
   git commit -m "feat(scope): description of change"
   ```

7. Push and create a pull request to `dev`

## Code Style

### Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance tasks
- `perf` - Performance improvement

Examples:
```
feat(tools): add congressional trades to stock ownership
fix(api): handle rate limit errors with exponential backoff
docs: update README with new AI features
test(models): add validation tests for CandleResponse
```

### Type Hints

All functions must have type hints:

```python
async def get_quote(self, symbol: str) -> dict[str, Any]:
    """Get real-time quote for a symbol.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Quote data with price, volume, etc.
    """
    ...
```

### Docstrings

Use Google-style docstrings for all public functions and classes.

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=mcp_finnhub --cov-report=term-missing

# Specific test file
uv run pytest tests/test_tools/test_stock_market_data.py

# Specific test
uv run pytest tests/test_tools/test_stock_market_data.py::test_get_quote
```

### Writing Tests

- Use `pytest` and `pytest-asyncio`
- Mock external API calls with `respx`
- Aim for 90%+ coverage on new code
- Test both success and error cases

Example test:
```python
@pytest.mark.asyncio
async def test_get_quote_success(mock_client):
    tool = StockMarketDataTool(mock_client)
    result = await tool.get_quote("AAPL")

    assert result["symbol"] == "AAPL"
    assert "c" in result  # current price
    assert "h" in result  # high
    assert "l" in result  # low
```

### Coverage Requirements

- Overall: 80% minimum
- Tools: 90% minimum
- New code: 90% recommended

## Adding New Features

### Adding a New Tool

1. Create endpoint functions in `src/mcp_finnhub/api/endpoints/`
2. Create Pydantic models in `src/mcp_finnhub/api/models/`
3. Create tool class in `src/mcp_finnhub/tools/`
4. Register in `src/mcp_finnhub/tools/__init__.py`
5. Add examples to `_get_operation_examples()`
6. Add tests in `tests/test_tools/`

### Adding a New Operation

1. Add endpoint function
2. Add Pydantic model (if needed)
3. Add method to tool class
4. Add to `VALID_OPERATIONS`
5. Add example to `_get_operation_examples()`
6. Add tests

## Pull Request Process

1. **Before submitting:**
   - All tests pass
   - Coverage meets requirements
   - No linting errors
   - Documentation updated
   - CHANGELOG updated

2. **PR description should include:**
   - Summary of changes
   - Related issue (if any)
   - Testing performed
   - Screenshots (if UI-related)

3. **Review process:**
   - At least one approval required
   - All CI checks must pass
   - Address review feedback promptly

## Reporting Issues

### Bug Reports

Include:
- Python version
- mcp-finnhub version
- Finnhub subscription tier
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered

## Questions?

- Open an issue for questions
- Check existing issues first
- Be specific and provide context

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to mcp-finnhub!
