# mcp-finnhub Current Sprint

## Sprint 2 - API Client & Job Management (85 SP)
**Status:** 🔄 IN PROGRESS (0/85 SP complete)  
**Target Velocity:** 70-90 SP  
**Goal:** Build HTTP client for Finnhub API with rate limiting, retry logic, and background job management

---

## Stories

### Story 2.1 (20 SP): Implement FinnhubClient with httpx
**Status:** 📋 NOT STARTED  
**Priority:** HIGH  
**File:** `src/mcp_finnhub/api/client.py`

**Tasks:**
- [ ] Import httpx, asyncio, time for async HTTP client
- [ ] Create FinnhubClient class with __init__(api_key, base_url, config)
- [ ] Implement async __aenter__ and __aexit__ for context manager
- [ ] Implement rate limiting using token bucket algorithm
  - [ ] Track requests per minute based on config.rate_limit_rpm
  - [ ] Add _rate_limiter() method with async sleep
  - [ ] Maintain request timestamps in deque
- [ ] Implement retry logic with exponential backoff
  - [ ] Use config.max_retries, retry_backoff_factor, retry_jitter
  - [ ] Retry on 429 (rate limit), 500-504 (server errors)
  - [ ] Don't retry on 401 (auth), 400 (bad request), 404 (not found)
- [ ] Implement _request() method with rate limiting + retry
- [ ] Implement get() method for API requests
- [ ] Add request/response logging
- [ ] Add comprehensive docstrings with examples

**Acceptance Criteria:**
- FinnhubClient works as async context manager
- Rate limiting prevents exceeding config.rate_limit_rpm
- Retry logic handles transient errors
- All HTTP methods properly handle auth headers
- Type hints complete

---

### Story 2.2 (15 SP): Implement FinnhubAPIError and error handling
**Status:** 📋 NOT STARTED  
**Priority:** HIGH  
**File:** `src/mcp_finnhub/api/errors.py` (new file)

**Tasks:**
- [ ] Create FinnhubAPIError exception class extending Exception
- [ ] Add attributes: status_code, message, response_data, request_url
- [ ] Add __init__ method with all error details
- [ ] Add __str__ method for readable error messages
- [ ] Create error handler function: handle_api_error(response)
- [ ] Map status codes to specific error types:
  - [ ] 401: AuthenticationError
  - [ ] 403: PermissionError  
  - [ ] 404: NotFoundError
  - [ ] 429: RateLimitError
  - [ ] 500-504: ServerError
- [ ] Add comprehensive docstrings
- [ ] Integrate error handling into FinnhubClient._request()

**Acceptance Criteria:**
- All API errors wrapped in FinnhubAPIError
- Error messages include status code, URL, response data
- Type hints complete
- Proper error inheritance hierarchy

---

### Story 2.3 (15 SP): Create Pydantic response models
**Status:** 📋 NOT STARTED  
**Priority:** MEDIUM  
**File:** `src/mcp_finnhub/api/models/__init__.py` and response models

**Tasks:**
- [ ] Create BaseResponse model with common fields
- [ ] Create QuoteResponse model:
  - [ ] c: float (current price)
  - [ ] h: float (high)
  - [ ] l: float (low)
  - [ ] o: float (open)
  - [ ] pc: float (previous close)
  - [ ] t: int (timestamp)
- [ ] Create CandleResponse model:
  - [ ] c: list[float] (close prices)
  - [ ] h: list[float] (high prices)
  - [ ] l: list[float] (low prices)
  - [ ] o: list[float] (open prices)
  - [ ] v: list[int] (volumes)
  - [ ] t: list[int] (timestamps)
  - [ ] s: str (status: ok/no_data)
- [ ] Create NewsArticle model for news responses
- [ ] Create CompanyProfile model
- [ ] Add field validators where needed
- [ ] Add comprehensive docstrings
- [ ] Export all models from __init__.py

**Acceptance Criteria:**
- All response models use Pydantic BaseModel
- Field types match Finnhub API documentation
- Validators handle edge cases
- Type hints complete

---

### Story 2.4 (15 SP): Implement JobManager
**Status:** 📋 NOT STARTED  
**Priority:** MEDIUM  
**File:** `src/mcp_finnhub/utils/job_manager.py` (new file)

**Tasks:**
- [ ] Create Job dataclass with fields:
  - [ ] job_id: str
  - [ ] project_name: str
  - [ ] status: JobStatus (pending/running/completed/failed)
  - [ ] created_at: datetime
  - [ ] started_at: datetime | None
  - [ ] completed_at: datetime | None
  - [ ] result_path: Path | None
  - [ ] error: str | None
- [ ] Create JobStatus enum (pending, running, completed, failed, cancelled)
- [ ] Create JobManager class with __init__(storage_dir, config)
- [ ] Implement create_job(project_name, operation) -> Job
- [ ] Implement update_job(job_id, **updates) -> Job
- [ ] Implement get_job(job_id) -> Job | None
- [ ] Implement list_jobs(project_name) -> list[Job]
- [ ] Implement complete_job(job_id, result_path)
- [ ] Implement fail_job(job_id, error)
- [ ] Implement cancel_job(job_id)
- [ ] Implement cleanup_old_jobs() based on config.job_cleanup_after
- [ ] Persist job metadata to JSON files
- [ ] Add comprehensive docstrings

**Acceptance Criteria:**
- Jobs persisted to disk with JSON metadata
- Job lifecycle managed correctly (pending→running→completed/failed)
- Cleanup removes old completed jobs
- Type hints complete

---

### Story 2.5 (10 SP): Implement BackgroundWorker
**Status:** 📋 NOT STARTED  
**Priority:** MEDIUM  
**File:** `src/mcp_finnhub/utils/background_worker.py` (new file)

**Tasks:**
- [ ] Create BackgroundWorker class with __init__(job_manager, max_concurrent)
- [ ] Implement submit_job(job_id, coro) -> None
- [ ] Implement _worker() coroutine for processing jobs
- [ ] Track running jobs count vs max_concurrent_jobs
- [ ] Implement job timeout based on config.job_timeout
- [ ] Handle job completion and failures
- [ ] Update JobManager on job status changes
- [ ] Add comprehensive docstrings
- [ ] Implement graceful shutdown

**Acceptance Criteria:**
- Background jobs execute asynchronously
- Respects max_concurrent_jobs limit
- Job timeouts enforced
- JobManager updated with results/errors
- Type hints complete

---

### Story 2.6 (10 SP): Write comprehensive tests
**Status:** 📋 NOT STARTED  
**Priority:** HIGH  
**Files:** `tests/test_api/`, `tests/test_utils/`

**Tasks:**
- [ ] Create tests/test_api/test_client.py:
  - [ ] Test FinnhubClient initialization
  - [ ] Test rate limiting prevents exceeding limit
  - [ ] Test retry logic on 429, 500-504
  - [ ] Test no retry on 401, 400, 404
  - [ ] Test successful requests
  - [ ] Test context manager usage
- [ ] Create tests/test_api/test_errors.py:
  - [ ] Test FinnhubAPIError creation
  - [ ] Test error message formatting
  - [ ] Test handle_api_error() for all status codes
- [ ] Create tests/test_api/test_models.py:
  - [ ] Test QuoteResponse parsing
  - [ ] Test CandleResponse parsing
  - [ ] Test field validation
- [ ] Create tests/test_utils/test_job_manager.py:
  - [ ] Test job creation, update, retrieval
  - [ ] Test job lifecycle (pending→completed)
  - [ ] Test job cleanup
  - [ ] Test persistence to disk
- [ ] Create tests/test_utils/test_background_worker.py:
  - [ ] Test job submission and execution
  - [ ] Test concurrent job limits
  - [ ] Test job timeouts
- [ ] Run pytest with coverage
- [ ] Achieve 85%+ coverage for Sprint 2 code

**Acceptance Criteria:**
- All tests pass
- Coverage >= 85% for API client and job system
- Tests use respx for HTTP mocking
- Tests use tmp_path for file operations
- Happy path and edge cases covered

---

## Sprint Goals
1. ✅ Complete async HTTP client with rate limiting and retry
2. ✅ Implement comprehensive error handling
3. ✅ Create Pydantic models for API responses
4. ✅ Build background job management system
5. ✅ Achieve 85%+ test coverage

## Definition of Done
- [ ] All 6 stories completed
- [ ] All tests passing
- [ ] Coverage >= 85% for Sprint 2 code
- [ ] Code formatted with ruff
- [ ] Pre-commit hooks passing
- [ ] Git commits following conventional format
- [ ] Progress memory updated
- [ ] Ready for Sprint 3 (Core Tools)

## Notes
- FinnhubClient will be used by all tools for API access
- JobManager will handle large dataset operations
- Focus on reliability and error handling
- Follow mcp-fred patterns for async client and rate limiting
