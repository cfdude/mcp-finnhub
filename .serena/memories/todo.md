# Sprint 3 - Core Tools (Mandatory) - 90 SP

**Goal:** Implement the 3 mandatory MCP tools with comprehensive endpoint coverage, following mcp-fred patterns

**Sprint Duration:** 1 sprint  
**Velocity Target:** 90 SP  
**Quality Standards:** 
- Zero linting errors/warnings
- 90%+ test coverage for tools
- All tests passing before completion
- Follow mcp-fred ServerContext patterns

---

## Story 3.1 (30 SP): Implement finnhub_technical_analysis Tool

**Goal:** Create MCP tool for technical analysis with 4 operations covering indicators, signals, patterns, and support/resistance levels

### Tasks:

#### API Endpoint Modules (8 SP)
- [ ] Create `src/mcp_finnhub/api/endpoints/technical.py`
  - [ ] `get_indicator(symbol, resolution, from, to, indicator, **params)` → `/indicator`
  - [ ] `aggregate_signals(symbol, resolution)` → `/scan/technical-indicator`
  - [ ] `scan_patterns(symbol, resolution)` → `/scan/pattern`
  - [ ] `support_resistance(symbol, resolution)` → `/scan/support-resistance`
  - [ ] All methods async with proper error handling
  - [ ] Return raw API responses (dict)

#### Pydantic Response Models (8 SP)
- [ ] Create `src/mcp_finnhub/api/models/technical.py`
  - [ ] `IndicatorResponse` model (varies by indicator type)
  - [ ] `TechnicalSignal` model (buy/sell/hold with metadata)
  - [ ] `PatternRecognition` model (pattern type, confidence, etc.)
  - [ ] `SupportResistanceLevel` model
  - [ ] Field validators for all models
  - [ ] Properties for convenient data access

#### MCP Tool Implementation (10 SP)
- [ ] Create `src/mcp_finnhub/tools/technical_analysis.py`
  - [ ] Tool registration with `@mcp.tool()` decorator
  - [ ] `get_indicator` operation with input validation
  - [ ] `aggregate_signals` operation
  - [ ] `scan_patterns` operation
  - [ ] `support_resistance` operation
  - [ ] Smart output handling (auto/screen/file modes)
  - [ ] Token estimation integration
  - [ ] Job creation for large datasets (>10K rows)
  - [ ] CSV/JSON export support

#### Tests (4 SP)
- [ ] Create `tests/test_api/test_endpoints_technical.py` (unit tests for endpoints)
- [ ] Create `tests/test_api/test_models_technical.py` (model validation tests)
- [ ] Create `tests/test_tools/test_technical_analysis.py` (tool integration tests)
- [ ] Achieve 90%+ coverage

**Definition of Done:**
- ✅ All 4 operations implemented and working
- ✅ Pydantic models with 100% validation coverage
- ✅ 90%+ test coverage
- ✅ Zero linting errors/warnings
- ✅ Integration with ServerContext
- ✅ Smart output handling working

---

## Story 3.2 (30 SP): Implement finnhub_stock_market_data Tool

**Goal:** Create MCP tool for stock market data with 8 operations covering quotes, candles, ticks, and market status

### Tasks:

#### API Endpoint Modules (8 SP)
- [ ] Create `src/mcp_finnhub/api/endpoints/market.py`
  - [ ] `quote(symbol)` → `/quote` (already have model from Sprint 2)
  - [ ] `candle(symbol, resolution, from, to)` → `/stock/candle` (already have model from Sprint 2)
  - [ ] `tick(symbol, date, limit, skip)` → `/stock/tick`
  - [ ] `bbo(symbol)` → `/stock/bbo`
  - [ ] `bidask(symbol, from, to)` → `/stock/bidask`
  - [ ] `symbols(exchange, mic, security_type, currency)` → `/stock/symbol`
  - [ ] `market_status(exchange)` → `/stock/market-status` (already have model from Sprint 2)
  - [ ] `market_holiday(exchange)` → `/stock/market-holiday`
  - [ ] All methods async with proper error handling

#### Pydantic Response Models (8 SP)
- [ ] Update `src/mcp_finnhub/api/models/common.py` or create `market.py`
  - [ ] Reuse: `QuoteResponse`, `CandleResponse`, `MarketStatusResponse` from Sprint 2
  - [ ] `TickData` model (time, price, volume, conditions)
  - [ ] `BBO` model (best bid/offer with exchange info)
  - [ ] `BidAsk` model (bid/ask spread with timestamps)
  - [ ] `SymbolInfo` model (from SymbolLookupResult or create new)
  - [ ] `MarketHoliday` model (date, exchange, name)
  - [ ] Field validators for all new models

#### MCP Tool Implementation (10 SP)
- [ ] Create `src/mcp_finnhub/tools/stock_market_data.py`
  - [ ] Tool registration with `@mcp.tool()` decorator
  - [ ] `quote` operation
  - [ ] `candle` operation with resolution validation
  - [ ] `tick` operation with pagination support
  - [ ] `bbo` operation
  - [ ] `bidask` operation
  - [ ] `symbols` operation with filtering
  - [ ] `market_status` operation
  - [ ] `market_holiday` operation
  - [ ] Smart output handling for large tick datasets
  - [ ] Background job support for tick data

#### Tests (4 SP)
- [ ] Create `tests/test_api/test_endpoints_market.py`
- [ ] Create `tests/test_api/test_models_market.py` (or update test_models.py)
- [ ] Create `tests/test_tools/test_stock_market_data.py`
- [ ] Achieve 90%+ coverage

**Definition of Done:**
- ✅ All 8 operations implemented and working
- ✅ Pydantic models for all endpoints
- ✅ 90%+ test coverage
- ✅ Zero linting errors/warnings
- ✅ Premium endpoint detection (tick, bbo, bidask)
- ✅ Background job support for tick data

---

## Story 3.3 (20 SP): Implement finnhub_news_sentiment Tool

**Goal:** Create MCP tool for news and sentiment with 4 operations

### Tasks:

#### API Endpoint Modules (6 SP)
- [ ] Create `src/mcp_finnhub/api/endpoints/news.py`
  - [ ] `market_news(category, min_id)` → `/news`
  - [ ] `company_news(symbol, from, to)` → `/company-news` (already have NewsArticle model from Sprint 2)
  - [ ] `press_releases(symbol, from, to)` → `/press-releases`
  - [ ] `sentiment(symbol)` → `/news-sentiment`
  - [ ] All methods async with proper error handling

#### Pydantic Response Models (5 SP)
- [ ] Update `src/mcp_finnhub/api/models/common.py` or create `news.py`
  - [ ] Reuse: `NewsArticle` model from Sprint 2
  - [ ] `PressRelease` model (similar to NewsArticle)
  - [ ] `SentimentScore` model (articlesInLastWeek, buzz, sentiment, companyNewsScore, sectorAverageBullishPercent, etc.)
  - [ ] Field validators for sentiment ranges

#### MCP Tool Implementation (7 SP)
- [ ] Create `src/mcp_finnhub/tools/news_sentiment.py`
  - [ ] Tool registration with `@mcp.tool()` decorator
  - [ ] `market_news` operation with category filter
  - [ ] `company_news` operation with date range
  - [ ] `press_releases` operation
  - [ ] `sentiment` operation with score interpretation
  - [ ] Smart output handling
  - [ ] CSV export for news articles

#### Tests (2 SP)
- [ ] Create `tests/test_api/test_endpoints_news.py`
- [ ] Create `tests/test_api/test_models_news.py` (or update test_models.py)
- [ ] Create `tests/test_tools/test_news_sentiment.py`
- [ ] Achieve 90%+ coverage

**Definition of Done:**
- ✅ All 4 operations implemented and working
- ✅ Pydantic models for all endpoints
- ✅ 90%+ test coverage
- ✅ Zero linting errors/warnings
- ✅ Sentiment score interpretation helpers
- ✅ CSV export working

---

## Story 3.4 (10 SP): Write Comprehensive Tests for All 3 Tools

**Goal:** Create integration tests and achieve 90%+ coverage across all Sprint 3 code

### Tasks:

#### Integration Tests (5 SP)
- [ ] Create `tests/test_integration/test_sprint3_integration.py`
  - [ ] Test technical_analysis tool with FinnhubClient integration
  - [ ] Test stock_market_data tool with job system integration
  - [ ] Test news_sentiment tool with output handling
  - [ ] Test all tools with ServerContext (when available)
  - [ ] Test error handling across all tools
  - [ ] Test background jobs for large datasets
  - [ ] Test CSV/JSON export for all tools

#### End-to-End Workflows (3 SP)
- [ ] Test complete workflow: API request → parse model → tool output → CSV export
- [ ] Test job creation for large datasets
- [ ] Test token estimation for all operations
- [ ] Test premium vs free endpoint behavior

#### Coverage & Quality (2 SP)
- [ ] Run coverage report for all Sprint 3 code
- [ ] Ensure 90%+ coverage for:
  - [ ] `src/mcp_finnhub/api/endpoints/technical.py`
  - [ ] `src/mcp_finnhub/api/endpoints/market.py`
  - [ ] `src/mcp_finnhub/api/endpoints/news.py`
  - [ ] `src/mcp_finnhub/api/models/technical.py`
  - [ ] `src/mcp_finnhub/api/models/market.py` (or common.py updates)
  - [ ] `src/mcp_finnhub/api/models/news.py` (or common.py updates)
  - [ ] `src/mcp_finnhub/tools/technical_analysis.py`
  - [ ] `src/mcp_finnhub/tools/stock_market_data.py`
  - [ ] `src/mcp_finnhub/tools/news_sentiment.py`
- [ ] Fix all linting errors/warnings
- [ ] Format all code with ruff

**Definition of Done:**
- ✅ All integration tests passing
- ✅ 90%+ test coverage for Sprint 3 code
- ✅ Zero linting errors/warnings
- ✅ All edge cases covered
- ✅ Premium endpoint behavior tested

---

## Sprint 3 Success Criteria

### Functional Requirements
- ✅ 3 mandatory MCP tools fully implemented (16 total operations)
- ✅ All tools integrated with FinnhubClient
- ✅ Smart output handling (auto/screen/file modes)
- ✅ Background job support for large datasets
- ✅ CSV/JSON export working

### Quality Requirements
- ✅ 90%+ test coverage for all Sprint 3 code
- ✅ Zero linting errors/warnings
- ✅ All tests passing (unit + integration + end-to-end)
- ✅ Code formatted with ruff

### Technical Requirements
- ✅ Follow mcp-fred ServerContext patterns
- ✅ Pydantic models for all API responses
- ✅ Async/await throughout
- ✅ Comprehensive error handling
- ✅ Token estimation integration
- ✅ Job manager integration for large datasets

---

## Implementation Notes

### Tool Patterns to Follow (from mcp-fred)

1. **Tool Registration:**
```python
@mcp.tool()
async def finnhub_technical_analysis(
    operation: str,
    symbol: str,
    resolution: str = "D",
    # ... operation-specific params
) -> dict:
    """Technical analysis with 4 operations."""
    # Validate inputs
    # Route to operation handler
    # Return formatted response
```

2. **Operation Routing:**
```python
operations = {
    "get_indicator": _get_indicator,
    "aggregate_signals": _aggregate_signals,
    "scan_patterns": _scan_patterns,
    "support_resistance": _support_resistance,
}
handler = operations.get(operation)
if not handler:
    raise ValueError(f"Unknown operation: {operation}")
return await handler(symbol, resolution, **kwargs)
```

3. **Smart Output Handling:**
```python
# Estimate tokens
estimated_tokens = token_estimator.estimate(data)

# Choose output mode
if estimated_tokens > safe_limit:
    # Create background job
    job = job_manager.create_job("technical_analysis", params)
    return {"job_id": job.job_id, "status": "pending"}
elif output_mode == "file":
    # Write to file
    file_path = file_writer.write_csv(data, filename)
    return {"file": str(file_path), "rows": len(data)}
else:
    # Return data directly
    return {"data": data, "rows": len(data)}
```

4. **Error Handling:**
```python
try:
    response = await client.get_indicator(symbol, indicator, ...)
    model = IndicatorResponse(**response)
    return model.model_dump()
except AuthenticationError:
    raise ValueError("Invalid API key")
except RateLimitError:
    raise ValueError("Rate limit exceeded, try again later")
except ValidationError as e:
    raise ValueError(f"Invalid response from API: {e}")
```

### Testing Patterns

1. **API Endpoint Tests:**
```python
@respx.mock
async def test_get_indicator_success(test_config):
    respx.get("https://finnhub.io/api/v1/indicator").mock(
        return_value=httpx.Response(200, json={...})
    )
    async with FinnhubClient(test_config) as client:
        result = await client.get_indicator("AAPL", "sma", ...)
    assert result["symbol"] == "AAPL"
```

2. **Model Validation Tests:**
```python
def test_indicator_response_validation():
    data = {"symbol": "AAPL", "indicator": "sma", ...}
    model = IndicatorResponse(**data)
    assert model.symbol == "AAPL"
```

3. **Tool Integration Tests:**
```python
async def test_technical_analysis_tool(job_manager, worker):
    # Test full workflow with background jobs
    result = await finnhub_technical_analysis(
        operation="get_indicator",
        symbol="AAPL",
        indicator="rsi",
    )
    assert "data" in result or "job_id" in result
```

---

## Current Status

**Sprint:** 3 - Core Tools (Mandatory)  
**Story Points:** 0/90 complete  
**Status:** Planning complete, ready to start Story 3.1

**Next Action:** Implement Story 3.1 - finnhub_technical_analysis tool (30 SP)
