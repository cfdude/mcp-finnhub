# mcp-finnhub API Reference

Complete reference for all 15 MCP tools provided by mcp-finnhub.

## Table of Contents

- [Core Trading & Analysis Tools](#core-trading--analysis-tools)
  - [finnhub_stock_market_data](#finnhub_stock_market_data)
  - [finnhub_technical_analysis](#finnhub_technical_analysis)
  - [finnhub_news_sentiment](#finnhub_news_sentiment)
- [Fundamentals & Analysis Tools](#fundamentals--analysis-tools)
  - [finnhub_stock_fundamentals](#finnhub_stock_fundamentals)
  - [finnhub_stock_estimates](#finnhub_stock_estimates)
  - [finnhub_stock_ownership](#finnhub_stock_ownership)
  - [finnhub_alternative_data](#finnhub_alternative_data)
  - [finnhub_sec_filings](#finnhub_sec_filings)
- [Multi-Asset Data Tools](#multi-asset-data-tools)
  - [finnhub_crypto_data](#finnhub_crypto_data)
  - [finnhub_forex_data](#finnhub_forex_data)
  - [finnhub_calendar_data](#finnhub_calendar_data)
  - [finnhub_market_events](#finnhub_market_events)
- [Management Tools](#management-tools)
  - [finnhub_project_create](#finnhub_project_create)
  - [finnhub_project_list](#finnhub_project_list)
  - [finnhub_job_status](#finnhub_job_status)

---

## Core Trading & Analysis Tools

### finnhub_stock_market_data

Real-time quotes, historical candles, and company profiles.

**Config Key**: `FINNHUB_ENABLE_STOCK_MARKET_DATA`

#### Operations

##### get_quote

Get real-time quote for a symbol.

**Parameters:**
- `symbol` (required): Stock symbol (e.g., "AAPL", "TSLA")

**Example:**
```json
{
  "operation": "get_quote",
  "symbol": "AAPL"
}
```

**Response:**
```json
{
  "c": 182.52,
  "h": 183.12,
  "l": 180.34,
  "o": 181.50,
  "pc": 180.95,
  "t": 1699296000
}
```

##### get_candles

Get historical OHLCV candle data.

**Parameters:**
- `symbol` (required): Stock symbol
- `resolution` (required): Candle resolution (1, 5, 15, 30, 60, D, W, M)
- `from_date` (required): Start date (YYYY-MM-DD or Unix timestamp)
- `to_date` (required): End date (YYYY-MM-DD or Unix timestamp)

**Example:**
```json
{
  "operation": "get_candles",
  "symbol": "MSFT",
  "resolution": "D",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

##### get_company_profile

Get comprehensive company profile.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_company_profile",
  "symbol": "GOOGL"
}
```

##### get_market_status

Get current market status.

**Parameters:**
- `exchange` (required): Exchange code (US, UK, EU, etc.)

**Example:**
```json
{
  "operation": "get_market_status",
  "exchange": "US"
}
```

##### get_symbols

Get list of symbols for an exchange.

**Parameters:**
- `exchange` (required): Exchange code

**Example:**
```json
{
  "operation": "get_symbols",
  "exchange": "US"
}
```

##### search_symbols

Search for symbols by query.

**Parameters:**
- `query` (required): Search query

**Example:**
```json
{
  "operation": "search_symbols",
  "query": "Apple"
}
```

##### get_financials

Get basic financials.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_financials",
  "symbol": "NFLX"
}
```

##### get_earnings

Get earnings history.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_earnings",
  "symbol": "AMZN"
}
```

---

### finnhub_technical_analysis

Technical indicators, patterns, and signals.

**Config Key**: `FINNHUB_ENABLE_TECHNICAL_ANALYSIS`

#### Operations

##### get_indicator

Calculate technical indicator.

**Parameters:**
- `symbol` (required): Stock symbol
- `resolution` (required): Resolution (1, 5, 15, 30, 60, D, W, M)
- `from_date` (required): Start date
- `to_date` (required): End date
- `indicator` (required): Indicator name (rsi, macd, ema, sma, etc.)
- Additional indicator-specific parameters

**Example:**
```json
{
  "operation": "get_indicator",
  "symbol": "AAPL",
  "resolution": "D",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31",
  "indicator": "rsi",
  "timeperiod": 14
}
```

##### aggregate_signals

Get aggregate buy/sell/hold signals.

**Parameters:**
- `symbol` (required): Stock symbol
- `resolution` (required): Resolution

**Example:**
```json
{
  "operation": "aggregate_signals",
  "symbol": "TSLA",
  "resolution": "D"
}
```

##### scan_patterns

Scan for chart patterns.

**Parameters:**
- `symbol` (required): Stock symbol
- `resolution` (required): Resolution

**Example:**
```json
{
  "operation": "scan_patterns",
  "symbol": "NVDA",
  "resolution": "D"
}
```

##### support_resistance

Get support and resistance levels.

**Parameters:**
- `symbol` (required): Stock symbol
- `resolution` (required): Resolution

**Example:**
```json
{
  "operation": "support_resistance",
  "symbol": "META",
  "resolution": "D"
}
```

---

### finnhub_news_sentiment

Company news, market news, and sentiment analysis.

**Config Key**: `FINNHUB_ENABLE_NEWS_SENTIMENT`

#### Operations

##### get_company_news

Get company-specific news.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (required): Start date (YYYY-MM-DD)
- `to_date` (required): End date (YYYY-MM-DD)

**Example:**
```json
{
  "operation": "get_company_news",
  "symbol": "AAPL",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

##### get_market_news

Get general market news.

**Parameters:**
- `category` (required): News category (general, forex, crypto, merger)

**Example:**
```json
{
  "operation": "get_market_news",
  "category": "general"
}
```

##### get_news_sentiment

Get sentiment analysis for a symbol.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_news_sentiment",
  "symbol": "TSLA"
}
```

##### get_insider_sentiment

Get insider trading sentiment.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_insider_sentiment",
  "symbol": "MSFT",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

---

## Fundamentals & Analysis Tools

### finnhub_stock_fundamentals

Financial statements, earnings, dividends, and metrics.

**Config Key**: `FINNHUB_ENABLE_STOCK_FUNDAMENTALS`

#### Operations

##### get_basic_financials

Get basic financial metrics.

**Parameters:**
- `symbol` (required): Stock symbol
- `metric` (optional): Specific metric category

**Example:**
```json
{
  "operation": "get_basic_financials",
  "symbol": "AAPL",
  "metric": "all"
}
```

##### get_reported_financials

Get reported financial statements.

**Parameters:**
- `symbol` (required): Stock symbol
- `freq` (required): Frequency (annual, quarterly)

**Example:**
```json
{
  "operation": "get_reported_financials",
  "symbol": "MSFT",
  "freq": "annual"
}
```

##### get_sec_financials

Get SEC standardized financials.

**Parameters:**
- `symbol` (required): Stock symbol
- `statement` (required): Statement type (bs, ic, cf)
- `freq` (required): Frequency (annual, quarterly)

**Example:**
```json
{
  "operation": "get_sec_financials",
  "symbol": "GOOGL",
  "statement": "ic",
  "freq": "quarterly"
}
```

##### get_dividends

Get dividend history.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_dividends",
  "symbol": "JNJ",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

##### get_splits

Get stock split history.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_splits",
  "symbol": "TSLA",
  "from_date": "2020-01-01",
  "to_date": "2024-12-31"
}
```

##### get_revenue_breakdown

Get revenue breakdown by product/geography.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_revenue_breakdown",
  "symbol": "AAPL"
}
```

---

### finnhub_stock_estimates

Earnings estimates, revenue estimates, and price targets.

**Config Key**: `FINNHUB_ENABLE_STOCK_ESTIMATES`

#### Operations

##### get_earnings_estimates

Get earnings estimates from analysts.

**Parameters:**
- `symbol` (required): Stock symbol
- `freq` (optional): Frequency (annual, quarterly)

**Example:**
```json
{
  "operation": "get_earnings_estimates",
  "symbol": "NVDA",
  "freq": "quarterly"
}
```

##### get_revenue_estimates

Get revenue estimates.

**Parameters:**
- `symbol` (required): Stock symbol
- `freq` (optional): Frequency

**Example:**
```json
{
  "operation": "get_revenue_estimates",
  "symbol": "AMZN"
}
```

##### get_ebitda_estimates

Get EBITDA estimates.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_ebitda_estimates",
  "symbol": "META"
}
```

##### get_price_targets

Get analyst price targets.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_price_targets",
  "symbol": "TSLA"
}
```

##### get_recommendations

Get analyst buy/sell/hold recommendations.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_recommendations",
  "symbol": "AAPL"
}
```

---

### finnhub_stock_ownership

Insider trades, institutional ownership, and congressional trading.

**Config Key**: `FINNHUB_ENABLE_STOCK_OWNERSHIP`

#### Operations

##### get_insider_transactions

Get insider trading transactions.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_insider_transactions",
  "symbol": "MSFT"
}
```

##### get_institutional_ownership

Get institutional ownership data.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_institutional_ownership",
  "symbol": "GOOGL"
}
```

##### get_institutional_portfolio

Get institutional fund portfolio holdings.

**Parameters:**
- `cik` (required): Fund CIK number

**Example:**
```json
{
  "operation": "get_institutional_portfolio",
  "cik": "0001067983"
}
```

##### get_congressional_trades

Get congressional trading activity.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_congressional_trades",
  "symbol": "NVDA"
}
```

---

### finnhub_alternative_data

ESG scores, social sentiment, supply chain, and patents.

**Config Key**: `FINNHUB_ENABLE_ALTERNATIVE_DATA`

#### Operations

##### get_esg_scores

Get ESG (Environmental, Social, Governance) scores.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_esg_scores",
  "symbol": "TSLA"
}
```

##### get_social_sentiment

Get social media sentiment.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (optional): Start date
- `to_date` (optional): End date

**Example:**
```json
{
  "operation": "get_social_sentiment",
  "symbol": "GME",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

##### get_supply_chain

Get supply chain relationships.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_supply_chain",
  "symbol": "AAPL"
}
```

##### get_patents

Get USPTO patent data.

**Parameters:**
- `symbol` (required): Stock symbol

**Example:**
```json
{
  "operation": "get_patents",
  "symbol": "IBM"
}
```

---

### finnhub_sec_filings

SEC filings, earnings transcripts, and similarity analysis.

**Config Key**: `FINNHUB_ENABLE_SEC_FILINGS`

#### Operations

##### get_sec_filings

Get SEC filings.

**Parameters:**
- `symbol` (required): Stock symbol
- `from_date` (optional): Start date
- `to_date` (optional): End date

**Example:**
```json
{
  "operation": "get_sec_filings",
  "symbol": "AAPL",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

##### get_filing_sentiment

Get sentiment analysis of SEC filings.

**Parameters:**
- `access_number` (required): SEC filing access number

**Example:**
```json
{
  "operation": "get_filing_sentiment",
  "access_number": "0000320193-24-000010"
}
```

##### get_similarity_index

Get similarity analysis between company filings.

**Parameters:**
- `symbol` (optional): Stock symbol
- `cik` (optional): Company CIK
- `freq` (optional): Frequency

**Example:**
```json
{
  "operation": "get_similarity_index",
  "symbol": "AAPL"
}
```

---

## Multi-Asset Data Tools

### finnhub_crypto_data

Cryptocurrency exchanges, symbols, profiles, and candles.

**Config Key**: `FINNHUB_ENABLE_CRYPTO`

#### Operations

##### get_crypto_exchanges

List supported cryptocurrency exchanges.

**Example:**
```json
{
  "operation": "get_crypto_exchanges"
}
```

##### get_crypto_symbols

Get crypto symbols for an exchange.

**Parameters:**
- `exchange` (required): Exchange name (e.g., "BINANCE")

**Example:**
```json
{
  "operation": "get_crypto_symbols",
  "exchange": "BINANCE"
}
```

##### get_crypto_profile

Get cryptocurrency profile.

**Parameters:**
- `symbol` (required): Crypto symbol (e.g., "BINANCE:BTCUSDT")

**Example:**
```json
{
  "operation": "get_crypto_profile",
  "symbol": "BINANCE:BTCUSDT"
}
```

##### get_crypto_candles

Get historical crypto OHLCV data.

**Parameters:**
- `symbol` (required): Crypto symbol
- `resolution` (required): Resolution (1, 5, 15, 30, 60, D, W, M)
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_crypto_candles",
  "symbol": "BINANCE:BTCUSDT",
  "resolution": "60",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

---

### finnhub_forex_data

Foreign exchange rates and candles.

**Config Key**: `FINNHUB_ENABLE_FOREX`

#### Operations

##### get_forex_exchanges

List supported forex exchanges.

**Example:**
```json
{
  "operation": "get_forex_exchanges"
}
```

##### get_forex_symbols

Get forex symbols for an exchange.

**Parameters:**
- `exchange` (required): Exchange name

**Example:**
```json
{
  "operation": "get_forex_symbols",
  "exchange": "OANDA"
}
```

##### get_forex_candles

Get historical forex OHLC data.

**Parameters:**
- `symbol` (required): Forex symbol (e.g., "OANDA:EUR_USD")
- `resolution` (required): Resolution
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_forex_candles",
  "symbol": "OANDA:EUR_USD",
  "resolution": "D",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

##### get_forex_rates

Get real-time forex exchange rates.

**Parameters:**
- `base` (required): Base currency (e.g., "USD")

**Example:**
```json
{
  "operation": "get_forex_rates",
  "base": "USD"
}
```

---

### finnhub_calendar_data

IPO calendar, earnings calendar, and economic events.

**Config Key**: `FINNHUB_ENABLE_CALENDAR`

#### Operations

##### get_ipo_calendar

Get IPO calendar.

**Parameters:**
- `from_date` (required): Start date
- `to_date` (required): End date

**Example:**
```json
{
  "operation": "get_ipo_calendar",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

##### get_earnings_calendar

Get earnings calendar.

**Parameters:**
- `from_date` (optional): Start date
- `to_date` (optional): End date
- `symbol` (optional): Filter by symbol

**Example:**
```json
{
  "operation": "get_earnings_calendar",
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

##### get_economic_calendar

Get economic events calendar.

**Example:**
```json
{
  "operation": "get_economic_calendar"
}
```

##### get_fda_calendar

Get FDA committee meeting calendar.

**Example:**
```json
{
  "operation": "get_fda_calendar"
}
```

---

### finnhub_market_events

Market holidays and analyst upgrades/downgrades.

**Config Key**: `FINNHUB_ENABLE_MARKET_EVENTS`

#### Operations

##### get_market_holidays

Get market holiday schedule.

**Parameters:**
- `exchange` (required): Exchange code

**Example:**
```json
{
  "operation": "get_market_holidays",
  "exchange": "US"
}
```

##### get_upgrade_downgrade

Get analyst upgrade/downgrade history.

**Parameters:**
- `symbol` (optional): Stock symbol

**Example:**
```json
{
  "operation": "get_upgrade_downgrade",
  "symbol": "TSLA"
}
```

##### get_merger_acquisition

Get merger & acquisition news.

**Parameters:**
- `from_date` (optional): Start date
- `to_date` (optional): End date

**Example:**
```json
{
  "operation": "get_merger_acquisition",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

---

## Management Tools

### finnhub_project_create

Create project workspaces for organizing data.

**Always enabled** (cannot be disabled)

#### Operations

##### create

Create a new project workspace.

**Parameters:**
- `project` (required): Project name (alphanumeric, hyphens, underscores only)

**Example:**
```json
{
  "operation": "create",
  "project": "tech-stocks-2024"
}
```

**Response:**
```json
{
  "project": "tech-stocks-2024",
  "path": "/storage/tech-stocks-2024",
  "metadata_file": "/storage/tech-stocks-2024/.project.json",
  "subdirectories": ["candles", "quotes", "news", "fundamentals", "technical", "jobs"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### finnhub_project_list

List all project workspaces with statistics.

**Always enabled** (cannot be disabled)

#### Operations

##### list

List all projects.

**Example:**
```json
{
  "operation": "list"
}
```

**Response:**
```json
{
  "projects": [
    {
      "name": "tech-stocks-2024",
      "path": "/storage/tech-stocks-2024",
      "created_at": "2024-01-15T10:30:00Z",
      "subdirectories": ["candles", "quotes", "news", "fundamentals", "technical", "jobs"],
      "file_counts": {
        "candles": 42,
        "quotes": 128,
        "news": 76,
        "fundamentals": 15,
        "technical": 38,
        "jobs": 3
      },
      "total_files": 302,
      "total_size": "12.5 MB"
    }
  ],
  "total_projects": 1
}
```

---

### finnhub_job_status

Check status of background jobs.

**Always enabled** (cannot be disabled)

#### Operations

##### get

Get job status.

**Parameters:**
- `job_id` (required): Job ID returned when job was created

**Example:**
```json
{
  "operation": "get",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "result": {
    "file_path": "/storage/my-project/candles/AAPL_2024.csv",
    "rows": 252
  }
}
```

---

## Error Handling

All tools return errors in a consistent format:

```json
{
  "error": {
    "code": "INVALID_OPERATION",
    "message": "Invalid operation: invalid_op. Valid operations: get_quote, get_candles, ...",
    "details": {
      "operation": "invalid_op",
      "valid_operations": ["get_quote", "get_candles", "..."]
    }
  }
}
```

Common error codes:
- `INVALID_OPERATION`: Unknown operation for the tool
- `MISSING_PARAMETER`: Required parameter not provided
- `INVALID_PARAMETER`: Parameter value is invalid
- `API_ERROR`: Finnhub API returned an error
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `AUTHENTICATION_FAILED`: Invalid API key

---

## Best Practices

1. **Always specify projects** for data operations to keep organized
2. **Use date ranges** to limit result sizes
3. **Check rate limits** before batch operations
4. **Validate symbols** using search_symbols before querying
5. **Store results** to avoid repeated API calls
6. **Use background jobs** for large datasets (>10K rows)

---

## Rate Limiting

mcp-finnhub automatically handles rate limiting:
- Tracks requests per minute
- Implements exponential backoff
- Retries on 429 errors
- Respects `FINNHUB_RATE_LIMIT_RPM` configuration

---

## See Also

- [README.md](../README.md) - Getting started guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [Finnhub API Documentation](https://finnhub.io/docs/api) - Official API docs
