# CLAUDE.md - AI Agent Operational Guide

**Project:** mcp-finnhub - Finnhub MCP Server
**Language:** Python 3.11+
**MCP Server:** Serena
**Project Name in Serena:** mcp-finnhub

---

## 🚀 Quick Start for New Sessions

If you're starting a new session or lost context, follow these steps:

### 1. Activate Serena MCP for this project

```
Use Serena MCP tool: activate_project
Project path: /Users/robsherman/Servers/mcp-finnhub
```

### 2. Read the current state

```
Read Serena memory: todo       # What you're currently working on
Read Serena memory: progress   # What's been completed
Read Serena memory: phases     # Overall project roadmap
```

### 3. Check the CHANGELOG

```
Read: CHANGELOG.md             # Git commits and version history
```

### 4. Review planning documents (if needed)

```
Read: docs/ARCHITECTURE.md     # Complete architecture
Read: docs/PATTERNS.md         # MCP server patterns learned
Read: docs/DEVELOPMENT.md      # Dev workflow, testing, tools
```

---

## 📂 Project Structure

```
mcp-finnhub/
├── CLAUDE.md                  # ← YOU ARE HERE - Operational guide
├── CHANGELOG.md               # Version history with semantic versioning
├── README.md                  # User-facing documentation (TBD)
├── .mcp.json                  # Local MCP server configuration
├── .mcp.json.README.md        # Configuration guide
│
├── docs/                      # 📚 PLANNING DOCUMENTATION
│   ├── ARCHITECTURE.md        # Complete 23-tool architecture
│   ├── PATTERNS.md            # Learned patterns from mcp-fred, alpha-vantage, snowflake
│   └── DEVELOPMENT.md         # Dev workflow, Ruff, PyTest, 80% coverage
│
├── .serena/                   # 🧠 SERENA MCP OPERATIONAL STATE
│   ├── project.yml            # Serena project config
│   └── memories/
│       ├── phases.md          # 7 phases, 550 SP, 17 sprints
│       ├── todo.md            # Current sprint tasks
│       └── progress.md        # Completed work history
│
├── src/mcp_finnhub/           # Source code (to be built)
├── tests/                     # Test suite (to be built)
├── pyproject.toml             # Python project config (to be built)
└── .env.example               # Environment variables template (to be built)
```

---

## 🧠 Serena Memory Guide

### **phases** - Project Roadmap

**Purpose:** High-level project plan broken into 7 phases

**Read with:** `Read Serena memory: phases`

**Contains:**
- Phase 1: Foundation & Core Infrastructure (90 SP)
- Phase 2: API Client & Job Management (90 SP)
- Phase 3: Core Tools - Mandatory (100 SP)
- Phase 4: Stock Analysis Tools (90 SP)
- Phase 5: Multi-Asset & Discovery Tools (90 SP)
- Phase 6: Management Tools & Integration (50 SP)
- Phase 7: Documentation & Release (40 SP)

**Total:** 550 story points, 17 sprints

**When to read:** When you need to understand the overall roadmap or plan the next phase

---

### **todo** - Current Sprint

**Purpose:** Active sprint tasks with story breakdown

**Read with:** `Read Serena memory: todo`

**Contains:**
- Current sprint number and story points
- All stories in the sprint with tasks
- Task checkboxes for tracking completion
- Definition of done for each story
- Sprint completion criteria
- Next sprint preview

**When to read:**
- ⭐ **START OF EVERY SESSION** - This tells you what you're working on
- When resuming work after interruption
- To check what's left in current sprint

**Example structure:**
```
Sprint 1.1 - Project Scaffold (30 SP)

Story 1.1.1 (8 SP): Create project structure
- [ ] Task 1
- [ ] Task 2
Status: Not Started

Story 1.1.2 (8 SP): Setup pyproject.toml
- [ ] Task 1
Status: Not Started
```

---

### **progress** - Completed Work

**Purpose:** History of what's been completed

**Read with:** `Read Serena memory: progress`

**Contains:**
- Completed phases and sprints
- Key milestones achieved
- Git commits summary
- Important decisions made
- Current phase/sprint status
- Velocity tracking

**When to read:**
- When you need to understand what's already done
- Before starting a new phase
- To avoid duplicating work
- To understand project history

**Update frequency:** After each sprint completion

---

## 📋 Development Workflow

### Starting a Sprint

1. **Read current state:**
   ```
   Read Serena memory: todo
   Read Serena memory: progress
   ```

2. **Execute sprint:**
   - Work through all stories in order
   - No mid-sprint updates to user
   - Update task checkboxes in `todo` memory as you complete them
   - Make git commits with semantic versioning

3. **Complete sprint:**
   - Provide comprehensive summary to user
   - Update `progress` memory with sprint completion
   - Update `todo` memory with next sprint
   - Update CHANGELOG.md

### Making Changes

1. **Git commits:**
   ```
   Format: <type>(<scope>): <subject>
   Types: feat, fix, docs, style, refactor, test, chore, perf

   Examples:
   feat(tools): add technical analysis tool with 4 operations
   fix(api): handle rate limit errors correctly
   docs: update ARCHITECTURE.md with testing strategy
   test(utils): add tests for token estimator
   ```

2. **Update CHANGELOG.md:**
   - Add entry under [Unreleased] section
   - Use semantic versioning
   - Group by Added/Changed/Fixed/Removed

3. **Update Serena memories:**
   - Check off tasks in `todo` as completed
   - Add completed work to `progress`
   - Update phase status when phase completes

### Code Quality Standards

**Must pass before commit:**
- ✅ Ruff linting: `ruff check --fix .`
- ✅ Ruff formatting: `ruff format .`
- ✅ PyTest: `pytest --cov=mcp_finnhub --cov-fail-under=80`

**Pre-commit hooks handle this automatically**

---

## 📊 Sprint Tracking

### Story Points

- **Small (3-5 SP):** Simple task, 1-2 hours
- **Medium (8-13 SP):** Moderate complexity, half day
- **Large (20-30 SP):** Complex task, 1-2 days

### Velocity Target

- **Minimum per sprint:** 90 story points
- **First sprint:** 30 SP (foundation work)
- **Regular sprints:** 90+ SP

### Sprint Completion

**DO NOT provide mid-sprint updates**

**At sprint end, provide:**
- Comprehensive summary of all completed stories
- Updated CHANGELOG.md
- Updated Serena `progress` memory
- Updated Serena `todo` memory with next sprint
- Git commits pushed

---

## 🗺️ Project Phases (Quick Reference)

| Phase | Name | Story Points | Status |
|-------|------|--------------|--------|
| 1 | Foundation & Core Infrastructure | 90 | 🔵 Current |
| 2 | API Client & Job Management | 90 | ⚪ Planned |
| 3 | Core Tools (Mandatory) | 100 | ⚪ Planned |
| 4 | Stock Analysis Tools | 90 | ⚪ Planned |
| 5 | Multi-Asset & Discovery | 90 | ⚪ Planned |
| 6 | Management Tools | 50 | ⚪ Planned |
| 7 | Documentation & Release | 40 | ⚪ Planned |

**Total:** 550 SP across 17 sprints

---

## 🎯 Current Status (As of last update)

**Phase:** 1 - Foundation & Core Infrastructure
**Sprint:** 1.1 - Project Scaffold & Configuration (30 SP)
**Status:** Ready to start
**Next Action:** Execute Sprint 1.1 (5 stories)

**To check current status:**
```
Read Serena memory: progress  # Check "Current Status" section
Read Serena memory: todo      # Check which tasks are checked off
```

---

## 📚 Documentation Hierarchy

### Planning Documents (Strategic)
Located in `docs/` directory - read when you need to understand architecture or patterns.

1. **ARCHITECTURE.md** - Complete system design
   - 23 tools covering 108 Finnhub endpoints
   - Tool enable/disable configuration
   - Storage structure, API design, data flow
   - Testing strategy (80% coverage)

2. **PATTERNS.md** - Learned patterns from existing MCP servers
   - mcp-fred patterns (primary reference)
   - alpha-vantage patterns (tool registry)
   - snowflake patterns (production features)
   - 11 proven patterns with code examples

3. **DEVELOPMENT.md** - Developer workflow
   - Ruff configuration (linting + formatting)
   - PyTest setup (80% minimum coverage)
   - Pre-commit hooks
   - CI/CD with GitHub Actions

### Operational Documents (Tactical)
Located in Serena memories and root directory - read every session.

1. **Serena `todo`** - Current sprint tasks ⭐ **READ FIRST**
2. **Serena `progress`** - Completed work history
3. **Serena `phases`** - Overall roadmap
4. **CHANGELOG.md** - Version history with commits
5. **CLAUDE.md** - This file (operational guide)

---

## 🔧 Tools & Technologies

### Core Stack
- **Python 3.11+** - Base language
- **MCP SDK** - Model Context Protocol
- **httpx** - Async HTTP client
- **Pydantic** - Validation
- **tiktoken** - Token estimation

### Development Tools
- **Ruff** - Linting + Formatting (replaces Black, Flake8, isort, pyupgrade)
- **PyTest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting (80% minimum)
- **respx** - HTTP mocking for tests
- **pre-commit** - Git hooks

### Commands
```bash
# Linting and formatting
ruff check --fix .
ruff format .

# Testing
pytest --cov=mcp_finnhub --cov-fail-under=80

# All checks (pre-commit does this automatically)
ruff check --fix . && ruff format . && pytest --cov=mcp_finnhub --cov-fail-under=80
```

---

## 🚨 Important Principles

### No Mid-Sprint Updates
**DO NOT** provide status updates during a sprint. Only provide a comprehensive summary at sprint completion.

### Serena Memory Updates
Update `todo` memory task checkboxes as you work, but only update `progress` memory at sprint completion.

### Code Quality
All code must pass:
- Ruff linting (no errors)
- Ruff formatting (Black-compatible)
- PyTest (80% minimum coverage, 90% for tools/)

### Documentation
- Update CHANGELOG.md with every commit
- Use semantic versioning
- Keep Serena memories current

### Git Workflow
- Work on `dev` branch
- Semantic commit messages
- Commits after each story completion

---

## 🔄 Session Checklist

### Starting New Session

- [ ] Read this file (CLAUDE.md)
- [ ] Activate Serena project: `/Users/robsherman/Servers/mcp-finnhub`
- [ ] Read Serena `todo` memory (see current sprint)
- [ ] Read Serena `progress` memory (see what's done)
- [ ] Check CHANGELOG.md (see recent commits)
- [ ] Review unchecked tasks in `todo`
- [ ] Continue from where you left off

### Ending Session (Sprint Complete)

- [ ] Provide comprehensive summary to user
- [ ] Update Serena `progress` memory
- [ ] Update Serena `todo` memory with next sprint
- [ ] Update CHANGELOG.md
- [ ] Git commit and push
- [ ] Confirm all tests pass

---

## 📞 Getting Help

### If Lost or Confused

1. **Read this file** (CLAUDE.md) - You are here!
2. **Read Serena `todo`** - What should you be working on?
3. **Read Serena `progress`** - What's already done?
4. **Read docs/ARCHITECTURE.md** - How is the system designed?
5. **Ask user for clarification** - User can provide context

### If Context Window Full

This CLAUDE.md file is designed to help you recover from context loss. Start with:
1. Read this file
2. Activate Serena
3. Read `todo` and `progress` memories
4. Continue work

---

## 🎓 Learning Resources

### Understanding the Project
1. Start: CLAUDE.md (this file)
2. Then: Serena memories (`todo`, `progress`, `phases`)
3. Deep dive: docs/ARCHITECTURE.md
4. Patterns: docs/PATTERNS.md
5. Development: docs/DEVELOPMENT.md

### Understanding Finnhub API
1. Read: swagger.json (108 endpoints)
2. Official docs: https://finnhub.io/docs/api

### Understanding MCP Patterns
1. Read: docs/PATTERNS.md
2. Study: /Users/robsherman/Servers/mcp-fred (primary reference)

---

## ✅ Success Criteria

### Sprint Success
- All stories completed
- All tests passing (80%+ coverage)
- Ruff checks passing
- Git commits made
- CHANGELOG.md updated
- Serena memories updated

### Phase Success
- All sprints in phase completed
- Phase deliverables met
- Version bumped in CHANGELOG.md
- User satisfied with deliverables

### Project Success
- All 7 phases completed (550 SP)
- 23 tools implemented
- 80%+ test coverage
- Documentation complete
- Open source ready
- v1.0.0 released

---

## 📝 Version History

- **Current:** Planning phase complete, Sprint 1.1 ready
- **Next:** v0.1.0-dev (Phase 1 completion)
- **Goal:** v1.0.0 (Stable release)

---

## 🤝 Working with User

### Communication Style
- Provide updates at sprint completion, not during sprint
- Be concise but comprehensive in summaries
- Ask for clarification when requirements unclear
- Present options for architectural decisions

### Velocity Expectations
- Target: 90+ story points per sprint
- Sprint 1.1: 30 SP (foundational work)
- Regular development sprints: 90 SP

### Quality Over Speed
- Code quality is mandatory (80% coverage, Ruff checks)
- Better to ask than assume
- Test as you go, not at the end

---

**This file is your guide. Read it at the start of every session. It will help you understand where you are, what needs to be done, and how to proceed.**

**Current action: Execute Sprint 1.1 (5 stories, 30 SP) - No mid-sprint updates - Comprehensive summary at completion**
