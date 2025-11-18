# Sprint 5 Plan - Multi-Asset & Discovery Tools

**Phase:** 5 - Multi-Asset & Discovery Tools
**Sprint:** 5
**Story Points:** 85 SP
**Duration:** 1 sprint
**Goal:** Implement multi-asset data tools (crypto, forex) and market discovery tools (calendars, events)

---

## 🎯 Sprint Goal

Deliver 4 high-quality tools covering cryptocurrency data, forex data, economic/IPO calendars, and market events with 90%+ test coverage, enabling users to access multi-asset market data and track important market events.

---

## 📋 Stories

### **Story 5.1: Implement finnhub_crypto_data tool (20 SP)**

**Description:** Create a tool for accessing cryptocurrency market data including exchanges, symbols, profiles, and price candles.

**Operations (4):**
1. `get_crypto_exchanges` - List all crypto exchanges
2. `get_crypto_symbols` - Get crypto symbols by exchange
3. `get_crypto_profile` - Get detailed crypto profile
4. `get_crypto_candles` - Get historical crypto price data

**Tasks:**
- [ ] Create `src/mcp_finnhub/api/endpoints/crypto.py` with 4 async endpoint functions
- [ ] Create `src/mcp_finnhub/api/models/crypto.py` with Pydantic models:
  - CryptoExchange
  - CryptoSymbol
  - CryptoProfile
  - CryptoCandleResponse
- [ ] Create `src/mcp_finnhub/tools/crypto_data.py` with:
  - CryptoDataTool class
  - VALID_OPERATIONS ClassVar
  - 4 operation methods
  - validate_operation method
  - execute routing method
- [ ] Create `tests/test_api/test_endpoints_crypto.py` (5 tests)
- [ ] Create `tests/test_api/test_models_crypto.py` (15 tests)
- [ ] Create `tests/test_tools/test_crypto_data.py` (12 tests)
- [ ] Update `src/mcp_finnhub/api/endpoints/__init__.py`
- [ ] Update `src/mcp_finnhub/api/models/__init__.py`

**Acceptance Criteria:**
- All 4 crypto operations working correctly
- 90%+ test coverage on crypto tool, endpoints, and models
- Proper handling of exchange parameter validation
- Support for resolution parameter in candles (1, 5, 15, 30, 60, D, W, M)
- All tests passing, zero linting errors

**Estimated Effort:** 20 SP

---

### **Story 5.2: Implement finnhub_forex_data tool (20 SP)**

**Description:** Create a tool for accessing foreign exchange (forex) market data including exchanges, symbols, candles, and real-time rates.

**Operations (4):**
1. `get_forex_exchanges` - List all forex exchanges
2. `get_forex_symbols` - Get forex symbols by exchange
3. `get_forex_candles` - Get historical forex price data
4. `get_forex_rates` - Get real-time forex exchange rates

**Tasks:**
- [ ] Create `src/mcp_finnhub/api/endpoints/forex.py` with 4 async endpoint functions
- [ ] Create `src/mcp_finnhub/api/models/forex.py` with Pydantic models:
  - ForexExchange
  - ForexSymbol
  - ForexCandleResponse
  - ForexRate
- [ ] Create `src/mcp_finnhub/tools/forex_data.py` with:
  - ForexDataTool class
  - VALID_OPERATIONS ClassVar
  - 4 operation methods
  - validate_operation method
  - execute routing method
- [ ] Create `tests/test_api/test_endpoints_forex.py` (5 tests)
- [ ] Create `tests/test_api/test_models_forex.py` (15 tests)
- [ ] Create `tests/test_tools/test_forex_data.py` (12 tests)
- [ ] Update `src/mcp_finnhub/api/endpoints/__init__.py`
- [ ] Update `src/mcp_finnhub/api/models/__init__.py`

**Acceptance Criteria:**
- All 4 forex operations working correctly
- 90%+ test coverage on forex tool, endpoints, and models
- Proper handling of exchange and base/quote currency parameters
- Support for resolution parameter in candles
- All tests passing, zero linting errors

**Estimated Effort:** 20 SP

---

### **Story 5.3: Implement finnhub_calendar_data tool (20 SP)**

**Description:** Create a tool for accessing various market calendars including IPO, earnings, economic events, and FDA committee meetings.

**Operations (4):**
1. `get_ipo_calendar` - Get upcoming and recent IPO calendar
2. `get_earnings_calendar` - Get earnings announcement calendar
3. `get_economic_calendar` - Get economic events calendar
4. `get_fda_calendar` - Get FDA committee meeting calendar

**Tasks:**
- [ ] Create `src/mcp_finnhub/api/endpoints/calendar.py` with 4 async endpoint functions
- [ ] Create `src/mcp_finnhub/api/models/calendar.py` with Pydantic models:
  - IPOEvent
  - EarningsEvent
  - EconomicEvent
  - FDAEvent
  - IPOCalendar
  - EarningsCalendar
  - EconomicCalendar
  - FDACalendar
- [ ] Create `src/mcp_finnhub/tools/calendar_data.py` with:
  - CalendarDataTool class
  - VALID_OPERATIONS ClassVar
  - 4 operation methods
  - validate_operation method
  - execute routing method
- [ ] Create `tests/test_api/test_endpoints_calendar.py` (6 tests)
- [ ] Create `tests/test_api/test_models_calendar.py` (20 tests)
- [ ] Create `tests/test_tools/test_calendar_data.py` (12 tests)
- [ ] Update `src/mcp_finnhub/api/endpoints/__init__.py`
- [ ] Update `src/mcp_finnhub/api/models/__init__.py`

**Acceptance Criteria:**
- All 4 calendar operations working correctly
- 90%+ test coverage on calendar tool, endpoints, and models
- Proper date range validation for calendar queries
- Support for symbol filtering in earnings calendar
- All tests passing, zero linting errors

**Estimated Effort:** 20 SP

---

### **Story 5.4: Implement finnhub_market_events tool (20 SP)**

**Description:** Create a tool for tracking important market events including market holidays, analyst upgrades/downgrades, and company-specific events.

**Operations (3):**
1. `get_market_holidays` - Get market holiday calendar
2. `get_upgrade_downgrade` - Get analyst upgrade/downgrade history
3. `get_merger_acquisition` - Get M&A news and announcements

**Tasks:**
- [ ] Create `src/mcp_finnhub/api/endpoints/events.py` with 3 async endpoint functions
- [ ] Create `src/mcp_finnhub/api/models/events.py` with Pydantic models:
  - MarketHoliday
  - UpgradeDowngrade
  - MergerAcquisition
  - MarketHolidayCalendar
  - UpgradeDowngradeHistory
  - MergerAcquisitionData
- [ ] Create `src/mcp_finnhub/tools/market_events.py` with:
  - MarketEventsTool class
  - VALID_OPERATIONS ClassVar
  - 3 operation methods
  - validate_operation method
  - execute routing method
- [ ] Create `tests/test_api/test_endpoints_events.py` (4 tests)
- [ ] Create `tests/test_api/test_models_events.py` (15 tests)
- [ ] Create `tests/test_tools/test_market_events.py` (10 tests)
- [ ] Update `src/mcp_finnhub/api/endpoints/__init__.py`
- [ ] Update `src/mcp_finnhub/api/models/__init__.py`

**Acceptance Criteria:**
- All 3 market event operations working correctly
- 90%+ test coverage on events tool, endpoints, and models
- Proper handling of exchange parameter for market holidays
- Date range filtering for upgrade/downgrade history
- All tests passing, zero linting errors

**Estimated Effort:** 20 SP

---

### **Story 5.5: Comprehensive Sprint 5 Testing (5 SP)**

**Description:** Run comprehensive integration and quality tests across all Sprint 5 tools to ensure consistency, quality, and proper integration.

**Tasks:**
- [ ] Run all Sprint 5 tests together (~160 expected tests)
- [ ] Verify 90%+ coverage on all Sprint 5 code
- [ ] Run full test suite (530 + 160 = 690 tests expected)
- [ ] Verify zero linting errors with `uv run ruff check --fix --unsafe-fixes .`
- [ ] Verify zero formatting violations with `uv run ruff format .`
- [ ] Run integration tests for cross-tool functionality
- [ ] Performance testing for API rate limits
- [ ] Generate coverage report
- [ ] Document any edge cases discovered

**Acceptance Criteria:**
- All Sprint 5 tests passing (160+ tests)
- 90%+ coverage on crypto, forex, calendar, and events tools
- Overall project coverage improved
- Zero linting errors
- Zero formatting violations
- All quality gates passed

**Estimated Effort:** 5 SP

---

## 📊 Sprint Metrics

**Total Story Points:** 85 SP
**Total Stories:** 5
**Total Operations:** 15 operations across 4 tools

**Expected Deliverables:**
- 4 new tools (crypto, forex, calendar, market events)
- 15 API operations
- ~160 tests
- 12 implementation files (endpoints + models + tools)
- 12 test files
- 90%+ test coverage

**Test Distribution:**
- Endpoint tests: ~20 tests
- Model validation tests: ~65 tests
- Tool integration tests: ~46 tests
- Execute routing tests: ~29 tests

---

## 🔧 Technical Approach

### Architecture Consistency

All Sprint 5 tools will follow the proven Sprint 4 patterns:

**Endpoint Pattern:**
```python
async def operation_name(
    client: FinnhubClient,
    symbol: str,
    param: str | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Operation description."""
    params: dict[str, Any] = {"symbol": symbol}
    if param is not None:
        params["param"] = param
    return await client.get("/endpoint", params=params)
```

**Model Pattern:**
```python
class ModelName(BaseModel):
    """Model description."""

    mixedCaseField: type | None = Field(default=None, description="...")  # noqa: N815
    normalField: type = Field(description="...")

    @property
    def computed_property(self) -> type:
        """Computed property description."""
        return calculation
```

**Tool Pattern:**
```python
class ToolNameTool:
    """Tool description.

    Provides N operations:
    - operation1: Description
    - operation2: Description
    """

    VALID_OPERATIONS: ClassVar[set[str]] = {
        "operation1",
        "operation2",
    }

    def __init__(self, client: FinnhubClient):
        """Initialize tool."""
        self.client = client

    def validate_operation(self, operation: str) -> None:
        """Validate operation."""
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(f"Invalid operation: {operation}...")

    async def operation1(self, **params) -> dict[str, Any]:
        """Execute operation1."""
        response = await endpoint.operation1(self.client, **params)
        model = Model(**response)
        return model.model_dump()

    async def execute(self, operation: str, **params: Any) -> dict[str, Any]:
        """Execute operation."""
        self.validate_operation(operation)
        if operation == "operation1":
            return await self.operation1(**params)
        ...
```

### Quality Standards

**Code Quality:**
- Ruff linting: zero errors
- Ruff formatting: Black-compatible
- PyTest: 90%+ coverage minimum
- Type hints: comprehensive coverage
- Docstrings: all public methods

**Testing Standards:**
- Endpoint tests: HTTP mocking with respx
- Model tests: validation and edge cases
- Tool tests: operation routing and error handling
- Integration tests: cross-component validation

---

## 📝 Commit Strategy

Following Sprint 4's successful pattern:

**Commit 1:** Stories 5.1-5.2 (Crypto & Forex)
```
feat(tools): add crypto and forex data tools (Stories 5.1-5.2)

Story 5.1: Implement finnhub_crypto_data tool (4 operations)
- Add crypto exchanges, symbols, profile, candles endpoints
- Create Pydantic models for crypto data
- Implement CryptoDataTool with operation routing
- Add 32 comprehensive tests with 90%+ coverage

Story 5.2: Implement finnhub_forex_data tool (4 operations)
- Add forex exchanges, symbols, candles, rates endpoints
- Create Pydantic models for forex data
- Implement ForexDataTool with operation routing
- Add 32 comprehensive tests with 90%+ coverage
```

**Commit 2:** Stories 5.3-5.4 (Calendar & Events)
```
feat(tools): add calendar and market events tools (Stories 5.3-5.4)

Story 5.3: Implement finnhub_calendar_data tool (4 operations)
- Add IPO, earnings, economic, FDA calendar endpoints
- Create Pydantic models for calendar events
- Implement CalendarDataTool with operation routing
- Add 38 comprehensive tests with 90%+ coverage

Story 5.4: Implement finnhub_market_events tool (3 operations)
- Add market holidays, upgrades/downgrades, M&A endpoints
- Create Pydantic models for market events
- Implement MarketEventsTool with operation routing
- Add 29 comprehensive tests with 90%+ coverage
```

**Commit 3:** Story 5.5 (Testing & Quality)
```
test: comprehensive Sprint 5 testing and quality checks

- Run all Sprint 5 tests (160+ tests passing)
- Verify 90%+ coverage on all Sprint 5 code
- Zero linting errors, zero formatting violations
- Update CHANGELOG.md with Sprint 5 deliverables
```

---

## 🎯 Definition of Done

For each story:
- ✅ All operations implemented and tested
- ✅ 90%+ test coverage on tool, endpoints, models
- ✅ All tests passing (unit, integration, validation)
- ✅ Zero linting errors (Ruff)
- ✅ Zero formatting violations (Ruff)
- ✅ Pydantic models with proper validation
- ✅ Proper error handling and edge cases
- ✅ Type hints on all functions
- ✅ Docstrings on all public methods
- ✅ Module exports updated

For Sprint 5 completion:
- ✅ All 5 stories completed
- ✅ All 160+ tests passing
- ✅ 90%+ coverage on Sprint 5 code
- ✅ Git commits with semantic versioning
- ✅ CHANGELOG.md updated
- ✅ Zero technical debt introduced
- ✅ Comprehensive sprint summary provided

---

## 🚀 Sprint 5 Success Criteria

**Functional:**
- 4 tools implemented (crypto, forex, calendar, events)
- 15 operations fully functional
- All API endpoints properly integrated

**Quality:**
- 90%+ test coverage on all Sprint 5 code
- Zero linting errors
- Zero formatting violations
- 100% test pass rate

**Documentation:**
- All code properly documented
- CHANGELOG.md updated
- Sprint summary provided

---

## 📅 Next Steps After Sprint 5

**Sprint 6** will focus on Phase 6: Management Tools & Integration (50 SP):
- Tool registry and enable/disable functionality
- Job queue management
- Rate limit monitoring
- Storage management
- Integration testing across all tools

**Overall Progress After Sprint 5:**
- Phase 1: Foundation ✅ Complete
- Phase 2: API Client ✅ Complete
- Phase 3: Core Tools ✅ Complete
- Phase 4: Stock Analysis ✅ Complete (Sprint 4)
- **Phase 5: Multi-Asset & Discovery ✅ Complete (Sprint 5)**
- Phase 6: Management Tools ⏳ Next
- Phase 7: Documentation & Release ⏳ Planned

---

## 🎊 Sprint 5 Ready!

This sprint plan follows the proven Sprint 4 structure and maintains the high quality standards established in previous sprints. All patterns, testing approaches, and quality gates are consistent with the project's architectural vision.

**Ready to execute:** All stories clearly defined, acceptance criteria established, and technical approach documented. Let's build! 🚀
