# MCP-Finnhub Architecture

## Overview

MCP server for Finnhub API providing comprehensive financial market data access with premium features. Built for flexibility, performance, and open-source extensibility.

**Key Features:**
- 23 MCP tools covering 108 Finnhub API endpoints
- Configurable tool enable/disable per user needs
- Premium features: Technical indicators, alternative data, filings
- Project-based storage with CSV/JSON exports
- Async job processing for large datasets
- Token estimation for smart output handling

---

## Design Principles

### 1. Modular Tool Architecture
- Each tool represents a logical grouping of related endpoints
- Tools can be individually enabled/disabled via configuration
- Reduces context window usage when tools are disabled
- Maintains clean separation of concerns

### 2. Configuration-First Design
- All tools configurable via `.env` file
- Default: All tools enabled (premium user)
- Users can disable unused asset classes (crypto, bonds, mutual funds)
- Open source users can customize for their workflows

### 3. mcp-fred Patterns
- Project-based storage with subdirectories
- Conservative token estimation (assume 75% context used)
- Async job processing for large datasets (>10K rows)
- Smart output handling (auto/screen/file modes)
- Type safety with Pydantic models

### 4. Premium Access Optimized
- Full API coverage (108 endpoints)
- Technical analysis tools (indicators, patterns, signals)
- Alternative data (ESG, sentiment, supply chain)
- Institutional/insider tracking
- SEC filings & transcripts

---

## Tool Architecture (23 Tools)

### **Core Trading & Analysis Tools** (8 Tools)

#### 1. `finnhub_technical_analysis` ⭐ MANDATORY
**Endpoints:** 4
- `/indicator` - 50+ technical indicators (RSI, MACD, SMA, EMA, etc.)
- `/scan/technical-indicator` - Aggregate buy/sell/hold signals
- `/scan/pattern` - Pattern recognition (H&S, triangles, candlesticks)
- `/scan/support-resistance` - Support/resistance levels

**Operations:** `get_indicator`, `aggregate_signals`, `scan_patterns`, `support_resistance`

**Premium:** Yes (all endpoints)

**Config:** `FINNHUB_ENABLE_TECHNICAL_ANALYSIS=true`

---

#### 2. `finnhub_stock_market_data` ⭐ MANDATORY
**Endpoints:** 8
- `/quote` - Real-time quote
- `/stock/candle` - OHLCV historical candles
- `/stock/tick` - Tick data
- `/stock/bbo` - Best bid/offer
- `/stock/bidask` - Bid/ask spread
- `/stock/symbol` - Symbol lookup
- `/stock/market-status` - Market status
- `/stock/market-holiday` - Market holidays

**Operations:** `quote`, `candle`, `tick`, `bbo`, `bidask`, `symbols`, `market_status`, `market_holiday`

**Premium:** Partial (tick, bbo, bidask require premium)

**Config:** `FINNHUB_ENABLE_STOCK_MARKET_DATA=true`

---

#### 3. `finnhub_stock_fundamentals`
**Endpoints:** 8+
- `/stock/profile`, `/stock/profile2` - Company profiles
- `/stock/financials`, `/stock/financials-reported` - Financial statements
- `/stock/metric`, `/stock/price-metric` - Key metrics
- `/stock/earnings` - Earnings data
- `/stock/earnings-quality-score` - Earnings quality
- `/stock/revenue-breakdown`, `/stock/revenue-breakdown2` - Revenue breakdown
- `/stock/dividend`, `/stock/dividend2`, `/stock/split` - Corporate actions

**Operations:** `profile`, `financials`, `metrics`, `earnings`, `dividend`, `split`, `revenue_breakdown`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_STOCK_FUNDAMENTALS=true`

---

#### 4. `finnhub_stock_estimates`
**Endpoints:** 7
- `/stock/revenue-estimate` - Revenue estimates
- `/stock/eps-estimate` - EPS estimates
- `/stock/ebit-estimate` - EBIT estimates
- `/stock/ebitda-estimate` - EBITDA estimates
- `/stock/price-target` - Analyst price targets
- `/stock/recommendation` - Analyst recommendations
- `/stock/upgrade-downgrade` - Rating changes

**Operations:** `revenue_estimate`, `eps_estimate`, `ebit_estimate`, `ebitda_estimate`, `price_target`, `recommendation`, `upgrade_downgrade`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_STOCK_ESTIMATES=true`

---

#### 5. `finnhub_stock_ownership`
**Endpoints:** 8
- `/stock/insider-transactions` - Insider trades
- `/stock/insider-sentiment` - Insider sentiment
- `/stock/congressional-trading` - Congressional trades
- `/stock/ownership` - Major shareholders
- `/stock/fund-ownership` - Fund ownership
- `/institutional/ownership` - Institutional ownership
- `/institutional/portfolio` - Institutional portfolios
- `/institutional/profile` - Institutional profiles

**Operations:** `insider_transactions`, `insider_sentiment`, `congressional_trading`, `ownership`, `fund_ownership`, `institutional_ownership`, `institutional_portfolio`, `institutional_profile`

**Premium:** Yes

**Config:** `FINNHUB_ENABLE_STOCK_OWNERSHIP=true`

---

#### 6. `finnhub_stock_alternative_data`
**Endpoints:** 10+
- `/stock/social-sentiment` - Social media sentiment
- `/stock/esg`, `/stock/historical-esg` - ESG scores
- `/stock/supply-chain` - Supply chain relationships
- `/stock/similarity-index` - Similar companies
- `/stock/investment-theme` - Investment themes
- `/stock/lobbying` - Lobbying activity
- `/stock/uspto-patent` - Patent filings
- `/stock/usa-spending` - Government contracts
- `/stock/visa-application` - H1B visa applications
- `/stock/historical-market-cap`, `/stock/historical-employee-count`

**Operations:** `social_sentiment`, `esg`, `supply_chain`, `similarity`, `themes`, `lobbying`, `patents`, `government_spending`, `visa_data`, `historical`

**Premium:** Yes

**Config:** `FINNHUB_ENABLE_STOCK_ALTERNATIVE_DATA=true`

---

#### 7. `finnhub_stock_filings`
**Endpoints:** 9+
- `/stock/filings` - SEC filings
- `/stock/filings-sentiment` - Filing sentiment analysis
- `/stock/international-filings` - International filings
- `/global-filings/search` - Search global filings
- `/global-filings/filter` - Filter filings
- `/global-filings/search-in-filing` - Search within filing
- `/global-filings/download` - Download filings
- `/stock/transcripts/list`, `/stock/transcripts` - Earnings transcripts
- `/stock/earnings-call-live` - Live earnings calls
- `/stock/presentation` - Investor presentations

**Operations:** `filings`, `filing_sentiment`, `international_filings`, `global_filings_search`, `global_filings_filter`, `global_filings_download`, `transcripts`, `live_calls`, `presentations`

**Premium:** Yes

**Config:** `FINNHUB_ENABLE_STOCK_FILINGS=true`

---

#### 8. `finnhub_news_sentiment` ⭐ MANDATORY
**Endpoints:** 4
- `/news` - General market news
- `/company-news` - Company-specific news
- `/press-releases` - Press releases
- `/news-sentiment` - News sentiment scores

**Operations:** `market_news`, `company_news`, `press_releases`, `sentiment`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_NEWS_SENTIMENT=true`

---

### **Multi-Asset Market Data Tools** (6 Tools)

#### 9. `finnhub_forex`
**Endpoints:** 4
- `/forex/exchange` - FX exchanges
- `/forex/symbol` - FX symbols
- `/forex/candle` - FX candles
- `/forex/rates` - Exchange rates

**Operations:** `exchanges`, `symbols`, `candle`, `rates`

**Premium:** No

**Config:** `FINNHUB_ENABLE_FOREX=true`

---

#### 10. `finnhub_crypto`
**Endpoints:** 4
- `/crypto/exchange` - Crypto exchanges
- `/crypto/symbol` - Crypto symbols
- `/crypto/profile` - Crypto profiles
- `/crypto/candle` - Crypto candles

**Operations:** `exchanges`, `symbols`, `profile`, `candle`

**Premium:** No

**Config:** `FINNHUB_ENABLE_CRYPTO=true`

---

#### 11. `finnhub_etf`
**Endpoints:** 4
- `/etf/profile` - ETF profiles
- `/etf/holdings` - ETF holdings
- `/etf/sector` - ETF sector exposure
- `/etf/country` - ETF country exposure

**Operations:** `profile`, `holdings`, `sector_exposure`, `country_exposure`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_ETF=true`

---

#### 12. `finnhub_mutual_fund`
**Endpoints:** 6
- `/mutual-fund/profile` - Fund profiles
- `/mutual-fund/holdings` - Fund holdings
- `/mutual-fund/sector` - Sector exposure
- `/mutual-fund/country` - Country exposure
- `/mutual-fund/eet` - EET data
- `/mutual-fund/eet-pai` - EET PAI data

**Operations:** `profile`, `holdings`, `sector_exposure`, `country_exposure`, `eet_data`

**Premium:** Yes

**Config:** `FINNHUB_ENABLE_MUTUAL_FUND=true`

---

#### 13. `finnhub_bond`
**Endpoints:** 4
- `/bond/profile` - Bond profiles
- `/bond/price` - Bond prices
- `/bond/tick` - Bond tick data
- `/bond/yield-curve` - Yield curves

**Operations:** `profile`, `price`, `tick`, `yield_curve`

**Premium:** Yes

**Config:** `FINNHUB_ENABLE_BOND=true`

---

#### 14. `finnhub_index`
**Endpoints:** 2
- `/index/constituents` - Current index constituents
- `/index/historical-constituents` - Historical constituents

**Operations:** `constituents`, `historical_constituents`

**Premium:** No

**Config:** `FINNHUB_ENABLE_INDEX=true`

---

### **Discovery & Calendar Tools** (2 Tools)

#### 15. `finnhub_screening`
**Endpoints:** 3
- `/search` - Symbol search
- `/sector/metrics` - Sector metrics
- `/stock/peers` - Peer companies

**Operations:** `search`, `sector_metrics`, `peers`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_SCREENING=true`

---

#### 16. `finnhub_calendar`
**Endpoints:** 4
- `/calendar/earnings` - Earnings calendar
- `/calendar/ipo` - IPO calendar
- `/calendar/economic` - Economic calendar
- `/fda-advisory-committee-calendar` - FDA calendar

**Operations:** `earnings`, `ipo`, `economic`, `fda`

**Premium:** Partial

**Config:** `FINNHUB_ENABLE_CALENDAR=true`

---

### **Economic & Specialized Tools** (2 Tools)

#### 17. `finnhub_economic`
**Endpoints:** 3
- `/economic` - Economic indicators
- `/economic/code` - Economic codes
- `/country` - Country metadata

**Operations:** `indicators`, `codes`, `country`

**Premium:** No

**Config:** `FINNHUB_ENABLE_ECONOMIC=true`

---

#### 18. `finnhub_specialized`
**Endpoints:** 7+
- `/stock/executive` - Executive profiles
- `/ca/symbol-change` - Symbol changes
- `/ca/isin-change` - ISIN changes
- `/covid19/us` - COVID-19 data
- `/bank-branch` - Bank branch data
- `/airline/price-index` - Airline pricing
- `/ai-chat` - AI chat

**Operations:** Various specialized operations

**Premium:** Mixed

**Config:** `FINNHUB_ENABLE_SPECIALIZED=true`

---

### **Management Tools** (5 Tools - Always Enabled)

#### 19. `finnhub_project_create`
Create new project directories with subdirectories

**Operations:** `create`

---

#### 20. `finnhub_project_list`
List all projects with metadata

**Operations:** `list`

---

#### 21. `finnhub_job_status`
Check background job status

**Operations:** `get`

---

#### 22. `finnhub_job_list`
List all background jobs

**Operations:** `list`

---

#### 23. `finnhub_job_cancel`
Cancel running background job

**Operations:** `cancel`

---

## Configuration System

### Environment Variables

```bash
# =========================
# REQUIRED
# =========================
FINNHUB_API_KEY=your_api_key_here

# =========================
# Storage Configuration
# =========================
FINNHUB_STORAGE_DIR=./finnhub-data
FINNHUB_PROJECT_NAME=default

# =========================
# Output Configuration
# =========================
FINNHUB_OUTPUT_FORMAT=csv              # csv or json
FINNHUB_OUTPUT_MODE=auto               # auto, screen, file
FINNHUB_SAFE_TOKEN_LIMIT=50000
FINNHUB_ASSUME_CONTEXT_USED=0.75

# =========================
# Job Configuration
# =========================
FINNHUB_JOB_RETENTION_HOURS=24
FINNHUB_JOB_MIN_ROWS=10000

# =========================
# Rate Limiting
# =========================
FINNHUB_RATE_LIMIT_PER_MINUTE=60       # Free: 60, Premium: 300-600

# =========================
# TOOL ENABLE/DISABLE
# =========================

# Core Trading (Mandatory - Always Keep Enabled)
FINNHUB_ENABLE_TECHNICAL_ANALYSIS=true    # Indicators, patterns, signals
FINNHUB_ENABLE_STOCK_MARKET_DATA=true     # Quote, candle, tick
FINNHUB_ENABLE_NEWS_SENTIMENT=true        # Company news

# Stock Analysis (Highly Recommended)
FINNHUB_ENABLE_STOCK_FUNDAMENTALS=true    # Financials, earnings
FINNHUB_ENABLE_STOCK_ESTIMATES=true       # Analyst estimates
FINNHUB_ENABLE_STOCK_OWNERSHIP=true       # Insider/institutional
FINNHUB_ENABLE_STOCK_ALTERNATIVE_DATA=true # ESG, sentiment, supply chain
FINNHUB_ENABLE_STOCK_FILINGS=true         # SEC filings, transcripts

# Multi-Asset (Optional - Disable if not trading these assets)
FINNHUB_ENABLE_FOREX=false                # Foreign exchange
FINNHUB_ENABLE_CRYPTO=false               # Cryptocurrency
FINNHUB_ENABLE_ETF=true                   # ETFs
FINNHUB_ENABLE_MUTUAL_FUND=false          # Mutual funds
FINNHUB_ENABLE_BOND=false                 # Bonds
FINNHUB_ENABLE_INDEX=true                 # Market indices

# Discovery & Events (Recommended)
FINNHUB_ENABLE_SCREENING=true             # Search, peers, sectors
FINNHUB_ENABLE_CALENDAR=true              # Earnings, IPO, economic calendars

# Economic & Specialized (Optional)
FINNHUB_ENABLE_ECONOMIC=true              # Economic indicators
FINNHUB_ENABLE_SPECIALIZED=false          # Misc endpoints
```

### Configuration Loading Logic

```python
# src/mcp_finnhub/config.py

class ToolConfig(BaseModel):
    """Tool enable/disable configuration."""

    # Core trading tools (mandatory - always enabled)
    technical_analysis: bool = True
    stock_market_data: bool = True
    news_sentiment: bool = True

    # Stock analysis tools
    stock_fundamentals: bool = True
    stock_estimates: bool = True
    stock_ownership: bool = True
    stock_alternative_data: bool = True
    stock_filings: bool = True

    # Multi-asset tools
    forex: bool = Field(default=False)
    crypto: bool = Field(default=False)
    etf: bool = Field(default=True)
    mutual_fund: bool = Field(default=False)
    bond: bool = Field(default=False)
    index: bool = Field(default=True)

    # Discovery & calendar tools
    screening: bool = True
    calendar: bool = True

    # Economic & specialized tools
    economic: bool = True
    specialized: bool = Field(default=False)

    @classmethod
    def from_env(cls) -> "ToolConfig":
        """Load tool configuration from environment variables."""
        return cls(
            technical_analysis=_get_bool_env("FINNHUB_ENABLE_TECHNICAL_ANALYSIS", True),
            stock_market_data=_get_bool_env("FINNHUB_ENABLE_STOCK_MARKET_DATA", True),
            news_sentiment=_get_bool_env("FINNHUB_ENABLE_NEWS_SENTIMENT", True),
            stock_fundamentals=_get_bool_env("FINNHUB_ENABLE_STOCK_FUNDAMENTALS", True),
            stock_estimates=_get_bool_env("FINNHUB_ENABLE_STOCK_ESTIMATES", True),
            stock_ownership=_get_bool_env("FINNHUB_ENABLE_STOCK_OWNERSHIP", True),
            stock_alternative_data=_get_bool_env("FINNHUB_ENABLE_STOCK_ALTERNATIVE_DATA", True),
            stock_filings=_get_bool_env("FINNHUB_ENABLE_STOCK_FILINGS", True),
            forex=_get_bool_env("FINNHUB_ENABLE_FOREX", False),
            crypto=_get_bool_env("FINNHUB_ENABLE_CRYPTO", False),
            etf=_get_bool_env("FINNHUB_ENABLE_ETF", True),
            mutual_fund=_get_bool_env("FINNHUB_ENABLE_MUTUAL_FUND", False),
            bond=_get_bool_env("FINNHUB_ENABLE_BOND", False),
            index=_get_bool_env("FINNHUB_ENABLE_INDEX", True),
            screening=_get_bool_env("FINNHUB_ENABLE_SCREENING", True),
            calendar=_get_bool_env("FINNHUB_ENABLE_CALENDAR", True),
            economic=_get_bool_env("FINNHUB_ENABLE_ECONOMIC", True),
            specialized=_get_bool_env("FINNHUB_ENABLE_SPECIALIZED", False),
        )
```

### Tool Registration

```python
# src/mcp_finnhub/server.py

def register_tools(server: Server, context: ServerContext) -> None:
    """Register MCP tools based on configuration."""
    config = context.config.tools

    # Core trading tools (mandatory)
    if config.technical_analysis:
        server.add_tool(technical_analysis_tool(context))

    if config.stock_market_data:
        server.add_tool(stock_market_data_tool(context))

    if config.news_sentiment:
        server.add_tool(news_sentiment_tool(context))

    # Stock analysis tools
    if config.stock_fundamentals:
        server.add_tool(stock_fundamentals_tool(context))

    if config.stock_estimates:
        server.add_tool(stock_estimates_tool(context))

    # ... etc for all tools

    # Management tools (always enabled)
    server.add_tool(project_create_tool(context))
    server.add_tool(project_list_tool(context))
    server.add_tool(job_status_tool(context))
    server.add_tool(job_list_tool(context))
    server.add_tool(job_cancel_tool(context))
```

---

## Storage Architecture

### Directory Structure

```
finnhub-data/
  my-project/
    technical/          # Technical analysis data
      indicators/       # Indicator calculations
      patterns/         # Pattern recognition results
      signals/          # Aggregate signals
      support/          # Support/resistance levels
    market-data/        # Market data (quotes, candles, ticks)
    fundamentals/       # Financial statements & metrics
    estimates/          # Analyst estimates
    ownership/          # Insider/institutional data
    alternative/        # ESG, sentiment, supply chain
    filings/            # SEC filings & transcripts
    news/               # News & sentiment
    forex/              # FX data
    crypto/             # Crypto data
    etf/                # ETF data
    mutual-fund/        # Mutual fund data
    bond/               # Bond data
    index/              # Index data
    calendar/           # Event calendars
    economic/           # Economic indicators
    .project.json       # Project metadata
```

### File Naming Convention

```
{symbol}_{operation}_{timestamp}.{format}

Examples:
AAPL_quote_20241114.csv
AAPL_candle_D_20241114.csv
AAPL_indicator_rsi_20241114.csv
AAPL_company_news_20241114.csv
```

---

## API Client Architecture

### HTTP Client

Based on mcp-fred pattern:
- `httpx.AsyncClient` for async requests
- Automatic retry with exponential backoff
- Rate limiting (60 req/min free, 300-600 req/min premium)
- Request/response logging
- Error handling with FinnhubAPIError

### Endpoint Modules

```python
# src/mcp_finnhub/api/endpoints/technical_analysis.py

class TechnicalAnalysisAPI:
    def __init__(self, client: FinnhubClient):
        self.client = client

    async def get_indicator(
        self,
        symbol: str,
        resolution: str,
        from_ts: int,
        to_ts: int,
        indicator: str,
        **indicator_fields
    ) -> IndicatorResponse:
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
            "indicator": indicator,
            **indicator_fields
        }
        return await self.client.get("/indicator", params=params)

    async def aggregate_signals(
        self,
        symbol: str,
        resolution: str
    ) -> AggregateSignalsResponse:
        params = {"symbol": symbol, "resolution": resolution}
        return await self.client.get("/scan/technical-indicator", params=params)
```

---

## Data Flow

### Request Flow

```
User Request
    ↓
MCP Tool (tools/technical_analysis.py)
    ↓
Validate Parameters
    ↓
API Endpoint (api/endpoints/technical_analysis.py)
    ↓
HTTP Client (api/client.py)
    ↓
Finnhub API
    ↓
Response Processing
    ↓
Token Estimation (utils/token_estimator.py)
    ↓
Output Handler (utils/output_handler.py)
    ├─→ Small Data: Return to screen
    ├─→ Large Data: Save to file
    └─→ Very Large: Background job
```

### Background Job Flow

```
Large Dataset Detected
    ↓
Create Job (utils/job_manager.py)
    ↓
Return Job ID to User
    ↓
Background Worker (utils/background_worker.py)
    ↓
Fetch Data from API
    ↓
Stream to CSV (utils/json_to_csv.py)
    ↓
Update Job Progress
    ↓
Complete Job with File Path
```

---

## Error Handling

### API Errors

```python
class FinnhubAPIError(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code
            }
        }
```

### Tool Errors

- `MISSING_PARAMETER` - Required parameter not provided
- `INVALID_PARAMETER` - Parameter validation failed
- `INVALID_OPERATION` - Unsupported operation
- `API_ERROR` - Finnhub API error
- `RATE_LIMIT_EXCEEDED` - Rate limit hit
- `PREMIUM_REQUIRED` - Endpoint requires premium access

---

## Testing Strategy

### Unit Tests (80% Coverage Target)

- Tool parameter validation
- API client error handling
- Token estimation accuracy
- File writer operations
- Job manager state transitions

### Integration Tests

- End-to-end tool execution
- API mocking with actual response structures
- File output validation
- Background job completion

### Test Fixtures

Mock Finnhub API responses for all endpoints

---

## Performance Considerations

### Token Estimation

Conservative approach from mcp-fred:
- Assume 75% of context already used
- Safe limits: 50K tokens for Claude Sonnet
- Auto-save to file when exceeding limit

### Rate Limiting

- Free tier: 60 calls/minute
- Premium tier: 300-600 calls/minute (configurable)
- Exponential backoff on rate limit errors
- Queue requests if needed

### Large Datasets

- Candles: Can return 10K+ datapoints
- Indicators: Similar size to candles
- Background jobs for >10K rows
- Streaming CSV writer for memory efficiency

---

## Open Source Considerations

### Flexible Configuration

Users can customize:
- Which tools to enable
- Storage directory location
- Output format preferences
- Token limits for their LLM
- Rate limits for their tier

### Documentation

- Comprehensive README
- API endpoint mapping
- Usage examples for each tool
- Configuration guide
- Contributing guidelines

### Extensibility

- Easy to add new tools
- Modular endpoint structure
- Clear patterns for new developers
- Type hints throughout

---

## Next Steps

1. ✅ Create DOCS folder
2. ✅ Document architecture
3. Analyze other Python MCP servers for patterns
4. Design configuration system implementation
5. Create project structure
6. Copy base files from mcp-fred
7. Implement core infrastructure
8. Implement tools (priority: technical_analysis → stock_market_data → news_sentiment)
9. Testing
10. Documentation

---

## References

- Finnhub API: https://finnhub.io/docs/api
- Finnhub Swagger: swagger.json (108 endpoints)
- MCP Specification: https://modelcontextprotocol.io
- mcp-fred: /Users/robsherman/Servers/mcp-fred
