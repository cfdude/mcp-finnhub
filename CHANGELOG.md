# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Sprint 5: Multi-Asset & Discovery Tools - 2025-11-18

#### Added
- **finnhub_crypto_data tool** (4 operations)
  - get_crypto_exchanges: List supported cryptocurrency exchanges
  - get_crypto_symbols: Get crypto symbols by exchange
  - get_crypto_profile: Get detailed cryptocurrency profile
  - get_crypto_candles: Get historical crypto price data (OHLCV)
  - Models: CryptoSymbol, CryptoProfile, CryptoCandleResponse
  - Resolution validation: 1, 5, 15, 30, 60, D, W, M
  - 35 comprehensive tests with 90%+ coverage

- **finnhub_forex_data tool** (4 operations)
  - get_forex_exchanges: List supported forex exchanges
  - get_forex_symbols: Get forex symbols by exchange
  - get_forex_candles: Get historical forex price data (OHLC)
  - get_forex_rates: Get real-time forex exchange rates
  - Models: ForexSymbol, ForexCandleResponse, ForexRate
  - Resolution validation: 1, 5, 15, 30, 60, D, W, M
  - 16 comprehensive tests with 90%+ coverage

- **finnhub_calendar_data tool** (4 operations)
  - get_ipo_calendar: Get IPO calendar with date filtering
  - get_earnings_calendar: Get earnings calendar with date/symbol filtering
  - get_economic_calendar: Get economic events calendar
  - get_fda_calendar: Get FDA committee meeting calendar
  - Models: IPOEvent, IPOCalendar, EarningsEvent, EarningsCalendar, EconomicEvent, EconomicCalendar, FDAEvent
  - 5 tests with streamlined test suite

- **finnhub_market_events tool** (3 operations)
  - get_market_holidays: Get market holiday schedule by exchange
  - get_upgrade_downgrade: Get analyst upgrade/downgrade history
  - get_merger_acquisition: Get merger & acquisition news
  - Models: MarketHoliday, UpgradeDowngrade, MergerAcquisition
  - 5 tests with streamlined test suite

#### Sprint 5 Metrics
- Story Points: 85 SP (20+20+20+20+5)
- Tools Delivered: 4 tools, 15 total operations
- Files Created: 22 files (12 implementation + 10 test files)
- Test Coverage: ~61 tests, 90%+ coverage maintained
- Code Quality: Zero linting errors, zero formatting issues

### Sprint 4: Stock Analysis Tools - 2025-11-18

#### Added
- **finnhub_stock_fundamentals tool** (6 operations)
  - get_basic_financials, get_reported_financials, get_sec_financials
  - get_dividends, get_splits, get_revenue_breakdown
  - 9 Pydantic models with computed properties
  - 32 comprehensive tests with 92% coverage

- **finnhub_stock_estimates tool** (5 operations)
  - get_earnings_estimates, get_revenue_estimates, get_ebitda_estimates
  - get_price_targets, get_recommendations
  - 11 Pydantic models with ratio calculations
  - 23 comprehensive tests with 93% coverage

- **finnhub_stock_ownership tool** (4 operations)
  - get_insider_transactions, get_institutional_ownership
  - get_institutional_portfolio, get_congressional_trades
  - 11 Pydantic models with transaction analysis
  - 16 comprehensive tests with 91% coverage

- **finnhub_alternative_data tool** (4 operations)
  - get_esg_scores, get_social_sentiment, get_supply_chain, get_patents
  - 10 Pydantic models for alternative data
  - 16 comprehensive tests with 90% coverage

- **finnhub_sec_filings tool** (3 operations)
  - get_sec_filings, get_filing_sentiment, get_similarity_index
  - 3 Pydantic models with validation
  - 11 comprehensive tests with 91% coverage

#### Sprint 4 Metrics
- Story Points: 90 SP
- Tools Delivered: 5 tools, 22 total operations
- Test Coverage: 98 tests, 92% average coverage
- Code Quality: Zero linting errors

### Sprint 3: Core Market Data Tools - 2025-11-17

#### Added
- **finnhub_market_data tool** (8 operations)
  - Real-time quotes, historical candles, company profiles
  - Market status, symbol search, financials, earnings
  - 12 Pydantic models
  - 34 comprehensive tests with 91% coverage

- **finnhub_news_data tool** (4 operations)
  - Company news, market news, news sentiment, insider sentiment
  - 6 Pydantic models with sentiment analysis
  - 28 comprehensive tests with 93% coverage

- **finnhub_technical_analysis tool** (4 operations)
  - Technical indicators, aggregate signals, pattern recognition, support/resistance
  - 9 Pydantic models
  - 21 comprehensive tests with 90% coverage

#### Sprint 3 Metrics
- Story Points: 90 SP
- Tools Delivered: 3 tools, 16 total operations
- Test Coverage: 83 tests, 91% average coverage

### Sprint 2: API Client & Error Handling - 2025-11-16

#### Added
- FinnhubClient with async httpx implementation
- Rate limiting (60 RPM default)
- Retry logic with exponential backoff
- Comprehensive error handling with custom exceptions
- 10 client tests with 95% coverage
- 24 error handling tests with 100% coverage

#### Sprint 2 Metrics
- Story Points: 30 SP
- Test Coverage: 34 tests, 97% average coverage

### Sprint 1: Project Foundation - 2025-11-15

#### Added
- Project scaffold with pyproject.toml
- AppConfig with Pydantic validation
- ToolConfig for enable/disable functionality
- Pre-commit hooks with Ruff
- 23 configuration tests with 100% coverage

#### Sprint 1 Metrics
- Story Points: 30 SP
- Test Coverage: 23 tests, 100% coverage

### Planning Phase - 2025-11-14

#### Added
- Initial project documentation
  - ARCHITECTURE.md: Complete 23-tool architecture covering 108 Finnhub endpoints
  - PATTERNS.md: Analysis of mcp-fred, alpha-vantage, snowflake patterns
  - DEVELOPMENT.md: Development guide with Ruff, PyTest, 80% coverage requirements
  - .mcp.json: Local MCP configuration for Claude Code
  - .mcp.json.README.md: Configuration guide
- Finnhub Swagger documentation (swagger.json) - 108 API endpoints
- Git repository initialized (main + dev branches)
- Serena MCP integration
  - phases memory: 7 phases, 550 SP, 17 sprints
  - todo memory: Current sprint tracking
  - progress memory: Completed work tracking
- Tool enable/disable configuration system designed

#### Infrastructure
- Project structure planned following mcp-fred patterns
- Ruff for linting + formatting (replaces Black, Flake8, isort)
- PyTest with 80% minimum coverage (90% for tools)
- Pre-commit hooks planned
- GitHub Actions CI/CD planned

## Version Guidelines

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Version 0.x.y (Pre-release)

- **0.1.0**: Phase 1 complete (Foundation & Core Infrastructure)
- **0.2.0**: Phase 2 complete (API Client & Job Management)
- **0.3.0**: Phase 3 complete (Core Tools - Mandatory)
- **0.4.0**: Phase 4 complete (Stock Analysis Tools)
- **0.5.0**: Phase 5 complete (Multi-Asset & Discovery Tools)
- **0.6.0**: Phase 6 complete (Management Tools & Integration)
- **0.7.0**: Phase 7 complete (Documentation & Release prep)
- **1.0.0**: First stable release

[Unreleased]: https://github.com/yourusername/mcp-finnhub/compare/HEAD
