# mcp-finnhub

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io)

Model Context Protocol (MCP) server providing comprehensive access to [Finnhub](https://finnhub.io) financial market data API. Built for AI assistants like Claude Desktop to seamlessly access real-time market data, technical indicators, fundamentals, and alternative data.

## Features

- **15 MCP Tools** covering 100+ Finnhub API endpoints
- **Real-time market data**: Quotes, candles, tick data, BBO
- **Technical analysis**: 50+ indicators, patterns, support/resistance
- **Fundamentals**: Financials, earnings, dividends, metrics
- **Alternative data**: ESG scores, social sentiment, supply chain
- **Multi-asset support**: Stocks, crypto, forex, ETFs, bonds
- **Project-based storage** with automatic CSV/JSON exports
- **Background job processing** for large datasets
- **Smart output handling** with token estimation
- **Configurable tools** - enable only what you need
- **AI-friendly errors** - Structured error responses with guidance
- **Built-in help** - Every tool supports `operation="help"` for discovery

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [Finnhub API key](https://finnhub.io/register) (free tier available)
- [Claude Desktop](https://claude.ai/download) or compatible MCP client

### Installation

#### Option 1: Install from PyPI (coming soon)

```bash
pip install mcp-finnhub
```

#### Option 2: Install from source

```bash
git clone https://github.com/cfdude/mcp-finnhub.git
cd mcp-finnhub
pip install -e .
```

### Configuration

1. Create a `.env` file in your project root:

```bash
# Required
FINNHUB_API_KEY=your_api_key_here
FINNHUB_STORAGE_DIR=/path/to/storage

# Optional - Tool configuration
FINNHUB_ENABLE_TECHNICAL_ANALYSIS=true
FINNHUB_ENABLE_STOCK_MARKET_DATA=true
FINNHUB_ENABLE_NEWS_SENTIMENT=true
# ... enable/disable other tools as needed

# Optional - Performance tuning
FINNHUB_RATE_LIMIT_RPM=300  # Requests per minute (30 free, 300 premium)
FINNHUB_REQUEST_TIMEOUT=30  # Request timeout in seconds
FINNHUB_SAFE_TOKEN_LIMIT=75000  # Conservative token limit
```

2. Configure Claude Desktop to use mcp-finnhub by adding to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "finnhub": {
      "command": "mcp-finnhub",
      "env": {
        "FINNHUB_API_KEY": "your_api_key_here",
        "FINNHUB_STORAGE_DIR": "/Users/yourname/finnhub-data"
      }
    }
  }
}
```

3. Restart Claude Desktop

### First Query

Ask Claude:

> "Get me the latest quote for AAPL"

Claude will use the `finnhub_stock_market_data` tool with the `get_quote` operation to fetch Apple's real-time stock quote.

## Available Tools

### Core Trading & Analysis (3 tools)

- **`finnhub_stock_market_data`** - Quotes, candles, tick data, BBO, market status
- **`finnhub_technical_analysis`** - 50+ indicators (RSI, MACD, SMA), patterns, signals
- **`finnhub_news_sentiment`** - Company news, market news, sentiment scores

### Fundamentals & Analysis (5 tools)

- **`finnhub_stock_fundamentals`** - Financials, earnings, dividends, metrics
- **`finnhub_stock_estimates`** - Revenue/EPS estimates, price targets
- **`finnhub_stock_ownership`** - Insider trades, institutional holdings
- **`finnhub_alternative_data`** - ESG scores, social sentiment, supply chain
- **`finnhub_sec_filings`** - SEC filings, earnings transcripts

### Multi-Asset Data (4 tools)

- **`finnhub_crypto_data`** - Crypto exchanges, symbols, profiles, candles
- **`finnhub_forex_data`** - Forex rates, candles, exchanges
- **`finnhub_calendar_data`** - IPO calendar, earnings calendar, economic events
- **`finnhub_market_events`** - Market holidays, analyst upgrades/downgrades

### Management Tools (3 tools)

- **`finnhub_project_create`** - Create project workspaces
- **`finnhub_project_list`** - List all projects with statistics
- **`finnhub_job_status`** - Check background job status

## Example Workflows

### Technical Analysis Workflow

```
User: "Analyze TSLA using RSI and MACD indicators"

Claude uses:
1. finnhub_technical_analysis → get_indicator (operation=get_indicator, symbol=TSLA, indicator=rsi)
2. finnhub_technical_analysis → get_indicator (operation=get_indicator, symbol=TSLA, indicator=macd)
3. Analyzes both indicators and provides trading insights
```

### Fundamental Research Workflow

```
User: "Research MSFT - get financials, earnings, and analyst estimates"

Claude uses:
1. finnhub_stock_fundamentals → get_basic_financials (operation=get_basic_financials, symbol=MSFT)
2. finnhub_stock_fundamentals → get_earnings (operation=get_earnings, symbol=MSFT)
3. finnhub_stock_estimates → get_earnings_estimates (operation=get_earnings_estimates, symbol=MSFT)
4. Summarizes financial health and analyst outlook
```

### Multi-Asset Portfolio Workflow

```
User: "Create a project called 'my-portfolio', get quotes for AAPL, BTC-USD, and EUR/USD"

Claude uses:
1. finnhub_project_create → create (operation=create, project=my-portfolio)
2. finnhub_stock_market_data → get_quote (operation=get_quote, symbol=AAPL, project=my-portfolio)
3. finnhub_crypto_data → get_crypto_profile (operation=get_crypto_profile, symbol=BINANCE:BTCUSDT)
4. finnhub_forex_data → get_forex_rates (operation=get_forex_rates, base=EUR, project=my-portfolio)
5. All data saved to /storage/my-portfolio/ with CSV exports
```

## Tool Configuration

Control which tools are available to reduce context window usage:

```bash
# Disable tools you don't need
FINNHUB_ENABLE_CRYPTO=false
FINNHUB_ENABLE_FOREX=false
FINNHUB_ENABLE_ALTERNATIVE_DATA=false

# Core tools (always recommended)
FINNHUB_ENABLE_STOCK_MARKET_DATA=true
FINNHUB_ENABLE_TECHNICAL_ANALYSIS=true
FINNHUB_ENABLE_NEWS_SENTIMENT=true
```

## Rate Limits

- **Free tier**: 60 requests/minute
- **Basic tier**: 150 requests/minute ($49.99/month)
- **Premium tier**: 300 requests/minute
- **Enterprise tier**: Custom limits

mcp-finnhub automatically handles rate limiting with exponential backoff and retry logic.

## AI Agent Features

### Help/Discovery

Every tool supports `operation="help"` to discover available operations:

```python
finnhub_stock_fundamentals(operation="help")
# Returns all operations with required/optional params and examples
```

### Structured Errors

Errors return actionable JSON instead of stack traces:

```json
{
  "error": "invalid_operation",
  "message": "Operation 'get_data' not found",
  "valid_operations": ["get_basic_financials", "get_dividends", ...],
  "tool": "finnhub_stock_fundamentals"
}
```

## Storage Structure

Projects are stored in subdirectories:

```
FINNHUB_STORAGE_DIR/
├── my-portfolio/
│   ├── .project.json         # Project metadata
│   ├── candles/              # Historical price data
│   ├── quotes/               # Real-time quotes
│   ├── news/                 # News articles
│   ├── fundamentals/         # Financial data
│   ├── technical/            # Technical indicators
│   └── jobs/                 # Background job results
└── research-tech/
    └── ...
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/cfdude/mcp-finnhub.git
cd mcp-finnhub

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest --cov=mcp_finnhub --cov-report=term-missing

# Lint and format
ruff check --fix .
ruff format .
```

### Running Locally

```bash
# Set environment variables
export FINNHUB_API_KEY=your_api_key
export FINNHUB_STORAGE_DIR=/tmp/finnhub-data

# Run the MCP server
mcp-finnhub
```

The server will listen on stdin/stdout for JSON-RPC requests following the MCP protocol.

### Testing with MCP Inspector

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector mcp-finnhub
```

## Architecture

- **ServerContext**: Dependency injection container managing client and utilities
- **Tool Registry**: Dynamic tool registration with enable/disable support
- **STDIO Transport**: JSON-RPC over stdin/stdout implementing MCP 2024-11-05
- **Async Job Processing**: Background workers for large dataset operations
- **Type Safety**: Pydantic models for all API requests/responses

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## API Reference

See [API.md](docs/API.md) for complete tool documentation with examples.

## Troubleshooting

### "Authentication failed" error
- Verify your `FINNHUB_API_KEY` is correct
- Check if your API key has expired
- Ensure you haven't exceeded rate limits

### "Tool not found" error
- Check that the tool is enabled in your configuration
- Verify tool names match exactly (case-sensitive)

### Storage permission errors
- Ensure `FINNHUB_STORAGE_DIR` exists and is writable
- Check filesystem permissions

### Rate limit errors
- Reduce `FINNHUB_RATE_LIMIT_RPM` in your configuration
- Upgrade to premium tier for higher limits

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io)
- Powered by [Finnhub API](https://finnhub.io)
- Inspired by [mcp-fred](https://github.com/robsherman/mcp-fred) patterns

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-finnhub/issues)
- **Documentation**: [docs/](docs/)
- **Finnhub API Docs**: [finnhub.io/docs/api](https://finnhub.io/docs/api)

---

**Made with ❤️ for the AI assistant ecosystem**
