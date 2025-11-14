# mcp-finnhub - Current Sprint TODO

**Sprint:** 1.1 - Project Scaffold & Configuration  
**Story Points:** 30 SP  
**Phase:** 1 - Foundation & Core Infrastructure  
**Status:** Ready to start

---

## Sprint Goal
Establish complete project structure with pyproject.toml, dependencies, .env.example, and pre-commit hooks.

---

## Stories

### ✅ Story 1.1.1 (8 SP): Create complete project structure
**Status:** Not Started  
**Tasks:**
- [ ] Create src/mcp_finnhub/ directory structure
  - [ ] __init__.py
  - [ ] __main__.py
  - [ ] config.py (placeholder)
  - [ ] server.py (placeholder)
- [ ] Create api/ subdirectory
  - [ ] __init__.py
  - [ ] client.py (placeholder)
  - [ ] endpoints/__init__.py (placeholder)
  - [ ] models/__init__.py (placeholder)
- [ ] Create tools/ subdirectory
  - [ ] __init__.py
  - [ ] _common.py (placeholder)
- [ ] Create utils/ subdirectory
  - [ ] __init__.py
- [ ] Create transports/ subdirectory
  - [ ] __init__.py
  - [ ] stdio.py (placeholder)
- [ ] Create tests/ directory structure
  - [ ] conftest.py
  - [ ] test_api/
  - [ ] test_tools/
  - [ ] test_utils/
- [ ] Verify structure matches mcp-fred pattern

**Definition of Done:**
- All directories and __init__.py files created
- Structure matches ARCHITECTURE.md
- Placeholders for key modules in place

---

### ✅ Story 1.1.2 (8 SP): Setup pyproject.toml with all dependencies
**Status:** Not Started  
**Tasks:**
- [ ] Create pyproject.toml based on mcp-fred pattern
- [ ] Add project metadata (name, version, description, authors)
- [ ] Add core dependencies:
  - [ ] httpx (async HTTP client)
  - [ ] pydantic (validation)
  - [ ] python-dotenv (env loading)
  - [ ] tiktoken (token estimation)
  - [ ] mcp SDK
- [ ] Add dev dependencies:
  - [ ] ruff (linting + formatting)
  - [ ] pytest (testing)
  - [ ] pytest-asyncio (async tests)
  - [ ] pytest-cov (coverage)
  - [ ] respx (HTTP mocking)
- [ ] Configure [tool.ruff] section
- [ ] Configure [tool.pytest.ini_options] section
- [ ] Configure [tool.coverage.*] sections
- [ ] Add project.scripts entry point

**Definition of Done:**
- pyproject.toml complete and valid
- All dependencies specified with versions
- Ruff configuration matches DEVELOPMENT.md
- PyTest configuration with 80% coverage enforcement

---

### ✅ Story 1.1.3 (5 SP): Create .env.example with all configuration variables
**Status:** Not Started  
**Tasks:**
- [ ] Create .env.example based on ARCHITECTURE.md
- [ ] Add REQUIRED section:
  - [ ] FINNHUB_API_KEY
- [ ] Add STORAGE section:
  - [ ] FINNHUB_STORAGE_DIR
  - [ ] FINNHUB_PROJECT_NAME
- [ ] Add OUTPUT section:
  - [ ] FINNHUB_OUTPUT_FORMAT
  - [ ] FINNHUB_OUTPUT_MODE
  - [ ] FINNHUB_SAFE_TOKEN_LIMIT
  - [ ] FINNHUB_ASSUME_CONTEXT_USED
- [ ] Add JOB section:
  - [ ] FINNHUB_JOB_RETENTION_HOURS
  - [ ] FINNHUB_JOB_MIN_ROWS
- [ ] Add RATE LIMITING section:
  - [ ] FINNHUB_RATE_LIMIT_PER_MINUTE
- [ ] Add TOOL ENABLE/DISABLE section (all 18 tools)
- [ ] Add comments explaining each variable
- [ ] Add examples and defaults

**Definition of Done:**
- .env.example complete with all variables
- Comments explain each variable
- Matches .mcp.json configuration
- Includes tool enable/disable flags

---

### ✅ Story 1.1.4 (5 SP): Create .gitignore for Python/venv/IDE files
**Status:** Not Started  
**Tasks:**
- [ ] Copy .gitignore from mcp-fred as base
- [ ] Add Python-specific ignores:
  - [ ] __pycache__/
  - [ ] *.py[cod]
  - [ ] *$py.class
  - [ ] *.so
  - [ ] .Python
- [ ] Add virtual environment ignores:
  - [ ] .venv/
  - [ ] venv/
  - [ ] ENV/
- [ ] Add test/coverage ignores:
  - [ ] .pytest_cache/
  - [ ] .coverage
  - [ ] htmlcov/
- [ ] Add IDE ignores:
  - [ ] .vscode/
  - [ ] .idea/
  - [ ] *.swp
- [ ] Add build/dist ignores:
  - [ ] build/
  - [ ] dist/
  - [ ] *.egg-info/
- [ ] Add Ruff cache:
  - [ ] .ruff_cache/
- [ ] Add .env (but not .env.example)
- [ ] Add local data directory

**Definition of Done:**
- .gitignore comprehensive
- No sensitive files tracked
- IDE and build artifacts ignored

---

### ✅ Story 1.1.5 (4 SP): Setup pre-commit hooks
**Status:** Not Started  
**Tasks:**
- [ ] Create .pre-commit-config.yaml
- [ ] Add Ruff linting hook (with --fix)
- [ ] Add Ruff formatting hook
- [ ] Add pre-commit standard hooks:
  - [ ] trailing-whitespace
  - [ ] end-of-file-fixer
  - [ ] check-yaml
  - [ ] check-json
  - [ ] check-toml
  - [ ] check-added-large-files
- [ ] Add pytest hook (run tests before commit)
- [ ] Document in DEVELOPMENT.md
- [ ] Test pre-commit hooks work

**Definition of Done:**
- .pre-commit-config.yaml created
- All hooks configured
- Hooks run automatically on git commit
- Matches DEVELOPMENT.md specification

---

## Sprint Completion Criteria

- [ ] All 5 stories completed
- [ ] Project structure matches ARCHITECTURE.md
- [ ] All configuration files created
- [ ] Pre-commit hooks installed and working
- [ ] Git commit with semantic versioning
- [ ] CHANGELOG.md updated

---

## Next Sprint

**Sprint 1.2:** Configuration System (30 SP)
- Implement AppConfig with Pydantic
- Implement ToolConfig with enable/disable
- Configuration loading from environment
- Tests for configuration (80% coverage)
