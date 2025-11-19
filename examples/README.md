# mcp-finnhub Examples

Example workflows demonstrating common use cases with mcp-finnhub.

## Quick Examples

### Example 1: Technical Analysis

```
User: "Analyze AAPL using RSI and MACD indicators for the last 30 days"

Claude workflow:
1. Calculate date range (today - 30 days)
2. Call finnhub_technical_analysis:
   - operation: get_indicator
   - symbol: AAPL
   - resolution: D
   - indicator: rsi
   - timeperiod: 14
3. Call finnhub_technical_analysis:
   - operation: get_indicator
   - symbol: AAPL
   - resolution: D
   - indicator: macd
4. Analyze both indicators and provide trading insights
```

**Expected Output:**
- RSI values showing overbought/oversold conditions
- MACD signal line crossovers
- Buy/sell/hold recommendation based on indicators

---

### Example 2: Fundamental Research

```
User: "Research MSFT - get financials, earnings history, and analyst estimates"

Claude workflow:
1. Call finnhub_stock_fundamentals:
   - operation: get_basic_financials
   - symbol: MSFT
2. Call finnhub_stock_fundamentals:
   - operation: get_reported_financials
   - symbol: MSFT
   - freq: quarterly
3. Call finnhub_stock_estimates:
   - operation: get_earnings_estimates
   - symbol: MSFT
4. Call finnhub_stock_estimates:
   - operation: get_price_targets
   - symbol: MSFT
5. Synthesize all data into comprehensive analysis
```

**Expected Output:**
- Key financial metrics (P/E, EPS, revenue, margins)
- Quarterly earnings trends
- Analyst consensus estimates
- Price target range and recommendations

---

### Example 3: News Sentiment Analysis

```
User: "Get news sentiment for TSLA over the last 7 days"

Claude workflow:
1. Calculate date range (today - 7 days)
2. Call finnhub_news_sentiment:
   - operation: get_company_news
   - symbol: TSLA
   - from_date: (calculated)
   - to_date: today
3. Call finnhub_news_sentiment:
   - operation: get_news_sentiment
   - symbol: TSLA
4. Call finnhub_alternative_data:
   - operation: get_social_sentiment
   - symbol: TSLA
5. Analyze sentiment scores and news articles
```

**Expected Output:**
- List of recent news articles with headlines
- Overall sentiment score (bullish/bearish)
- Social media sentiment trends
- Key themes and topics in news coverage

---

### Example 4: Multi-Asset Portfolio

```
User: "Create a portfolio project and track AAPL, BTC, and EUR/USD"

Claude workflow:
1. Call finnhub_project_create:
   - operation: create
   - project: my-portfolio
2. Call finnhub_stock_market_data:
   - operation: get_quote
   - symbol: AAPL
   - project: my-portfolio
3. Call finnhub_crypto_data:
   - operation: get_crypto_profile
   - symbol: BINANCE:BTCUSDT
   - project: my-portfolio
4. Call finnhub_forex_data:
   - operation: get_forex_rates
   - base: EUR
   - project: my-portfolio
5. Call finnhub_project_list:
   - operation: list
```

**Expected Output:**
- Project created at /storage/my-portfolio/
- Current quotes for all three assets
- Data saved to appropriate subdirectories
- Project summary with file counts

---

### Example 5: Earnings Calendar Monitoring

```
User: "Show me all earnings announcements for tech stocks this week"

Claude workflow:
1. Calculate this week's date range
2. Call finnhub_calendar_data:
   - operation: get_earnings_calendar
   - from_date: monday
   - to_date: friday
3. Filter results for technology sector
4. For each tech stock:
   - Call finnhub_stock_estimates:
     - operation: get_earnings_estimates
     - symbol: (stock)
5. Present calendar with consensus estimates
```

**Expected Output:**
- List of tech companies reporting this week
- Earnings date and time for each
- Consensus EPS estimates
- Expected vs. actual (if already reported)

---

### Example 6: Insider Trading Analysis

```
User: "Show me recent insider trading for NVDA"

Claude workflow:
1. Call finnhub_stock_ownership:
   - operation: get_insider_transactions
   - symbol: NVDA
2. Call finnhub_news_sentiment:
   - operation: get_insider_sentiment
   - symbol: NVDA
   - (calculate last 90 days)
3. Analyze transaction patterns
```

**Expected Output:**
- List of recent insider transactions (buy/sell)
- Transaction amounts and dates
- Net insider sentiment score
- Analysis of insider confidence

---

### Example 7: ESG Analysis

```
User: "Compare ESG scores for TSLA and GM"

Claude workflow:
1. Call finnhub_alternative_data:
   - operation: get_esg_scores
   - symbol: TSLA
2. Call finnhub_alternative_data:
   - operation: get_esg_scores
   - symbol: GM
3. Compare scores across E, S, G categories
```

**Expected Output:**
- ESG scores for both companies
- Breakdown by Environmental, Social, Governance
- Industry comparison
- Strengths and weaknesses analysis

---

### Example 8: Pattern Recognition

```
User: "Scan for bullish patterns in AAPL, MSFT, and GOOGL"

Claude workflow:
1. For each symbol:
   - Call finnhub_technical_analysis:
     - operation: scan_patterns
     - symbol: (stock)
     - resolution: D
2. Filter for bullish patterns
3. Rank by pattern strength
```

**Expected Output:**
- List of detected patterns (H&S, triangles, etc.)
- Pattern confidence scores
- Price targets based on patterns
- Ranked list of best opportunities

---

### Example 9: Historical Performance Analysis

```
User: "Get 1-year daily candles for SPY and calculate returns"

Claude workflow:
1. Calculate date range (today - 365 days)
2. Call finnhub_stock_market_data:
   - operation: get_candles
   - symbol: SPY
   - resolution: D
   - from_date: (1 year ago)
   - to_date: today
   - project: spy-analysis
3. Calculate returns, volatility, max drawdown
```

**Expected Output:**
- 252 trading days of OHLCV data
- Total return (%)
- Annualized volatility
- Max drawdown
- CSV file saved to project

---

### Example 10: Sector Analysis

```
User: "Analyze the technology sector - compare AAPL, MSFT, GOOGL, NVDA"

Claude workflow:
1. For each stock:
   - Call finnhub_stock_market_data → get_quote
   - Call finnhub_stock_fundamentals → get_basic_financials
   - Call finnhub_stock_estimates → get_price_targets
2. Call finnhub_project_create:
   - operation: create
   - project: tech-sector-2024
3. Save all data to project
4. Compare key metrics
```

**Expected Output:**
- Side-by-side comparison table
- Key metrics: P/E, EPS growth, revenue growth
- Analyst ratings and price targets
- Sector winner/loser analysis
- All data saved to tech-sector-2024 project

---

## Integration with Claude Desktop

### Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "finnhub": {
      "command": "mcp-finnhub",
      "env": {
        "FINNHUB_API_KEY": "your_key_here",
        "FINNHUB_STORAGE_DIR": "/Users/yourname/finnhub-data"
      }
    }
  }
}
```

### Conversation Starters

**For trading:**
- "What's the RSI for TSLA over the last month?"
- "Show me support and resistance levels for AAPL"
- "Get aggregate buy/sell signals for NVDA"

**For research:**
- "Research META - give me fundamentals, estimates, and news"
- "Compare P/E ratios for FAANG stocks"
- "What's the institutional ownership of MSFT?"

**For monitoring:**
- "Show me this week's earnings calendar"
- "Get recent insider trades for tech stocks"
- "What are the latest analyst upgrades?"

---

## Best Practices

1. **Create projects** for related analyses:
   ```
   "Create a project called 'earnings-season-2024' and track AAPL, MSFT, GOOGL earnings"
   ```

2. **Use date ranges** to limit data:
   ```
   "Get AAPL news from the last 7 days only"
   ```

3. **Combine tools** for comprehensive analysis:
   ```
   "Analyze TSLA using: price data, RSI indicator, news sentiment, and insider trades"
   ```

4. **Save results** to avoid re-fetching:
   ```
   "Get 5-year monthly candles for SPY and save to my-portfolio project"
   ```

5. **Check job status** for long-running operations:
   ```
   "Check the status of job abc-123-def"
   ```

---

## Troubleshooting Examples

### Rate Limit Hit
```
User: "I'm getting rate limit errors"

Solution:
1. Check current rate limit: FINNHUB_RATE_LIMIT_RPM
2. Free tier: 30 requests/minute
3. Premium tier: 300 requests/minute
4. Reduce requests or upgrade plan
```

### Symbol Not Found
```
User: "Quote for XYZ returns empty"

Solution:
1. Verify symbol exists:
   finnhub_stock_market_data → search_symbols (query: "XYZ")
2. Use correct exchange prefix for crypto/forex:
   - Crypto: "BINANCE:BTCUSDT"
   - Forex: "OANDA:EUR_USD"
```

### Large Dataset Timeout
```
User: "Getting 10 years of daily data times out"

Solution:
1. Break into smaller date ranges
2. Use background jobs for >10K rows
3. Check job status with finnhub_job_status
4. Retrieve results when job completes
```

---

## See Also

- [API.md](../docs/API.md) - Complete API reference
- [README.md](../README.md) - Getting started guide
- [Finnhub API Docs](https://finnhub.io/docs/api) - Official API documentation
