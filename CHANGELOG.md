# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
