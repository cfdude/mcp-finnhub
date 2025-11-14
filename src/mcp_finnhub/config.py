"""Configuration management for mcp-finnhub.

Provides Pydantic-based configuration for the Finnhub MCP server with environment
variable loading and tool enable/disable functionality.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator


class ToolConfig(BaseModel):
    """Tool enable/disable configuration.

    Controls which of the 18 data tools are registered with the MCP server.
    Management tools (project_create, project_list, job_status, job_list, job_cancel)
    are always enabled and cannot be disabled.

    Environment variables use the prefix FINNHUB_ENABLE_:
        FINNHUB_ENABLE_TECHNICAL_ANALYSIS=true
        FINNHUB_ENABLE_STOCK_MARKET_DATA=true
        etc.

    All tools default to enabled (True) for premium users.
    """

    # Core Trading & Analysis Tools (3 mandatory)
    technical_analysis: bool = Field(
        default=True,
        description="Technical indicators, patterns, signals, support/resistance (MANDATORY)",
    )
    stock_market_data: bool = Field(
        default=True,
        description="Quote, candles, tick, BBO, symbols, market status (MANDATORY)",
    )
    news_sentiment: bool = Field(
        default=True, description="Market news, company news, sentiment scores (MANDATORY)"
    )

    # Core Trading & Analysis Tools (5 optional)
    stock_fundamentals: bool = Field(
        default=True,
        description="Company profiles, financials, metrics, earnings, dividends",
    )
    stock_estimates: bool = Field(
        default=True,
        description="Revenue/EPS estimates, price targets, analyst recommendations",
    )
    stock_ownership: bool = Field(
        default=True,
        description="Insider trades, institutional ownership, congressional trades",
    )
    stock_alternative_data: bool = Field(
        default=True, description="ESG scores, social sentiment, supply chain, patents"
    )
    stock_filings: bool = Field(
        default=True, description="SEC filings, earnings transcripts, presentations"
    )

    # Multi-Asset Market Data Tools (6 tools)
    forex: bool = Field(default=True, description="Foreign exchange rates and candles")
    crypto: bool = Field(default=True, description="Cryptocurrency prices and candles")
    etf: bool = Field(default=True, description="ETF profiles, holdings, sector exposure")
    mutual_fund: bool = Field(default=True, description="Mutual fund profiles, holdings, NAV")
    bond: bool = Field(default=True, description="Bond profiles and tick data")
    index: bool = Field(default=True, description="Index constituents and historical data")

    # Discovery & Screening Tools (2 tools)
    screening: bool = Field(default=True, description="Stock screeners by market cap, volume")
    calendar: bool = Field(default=True, description="IPO, earnings, economic event calendars")

    # Economic & Specialized Data Tools (2 tools)
    economic: bool = Field(default=True, description="Economic indicators and calendars")
    specialized: bool = Field(
        default=True, description="Merger arbitrage, SPAC data, aggregated indicators"
    )

    @property
    def enabled_tools(self) -> list[str]:
        """Return list of enabled tool names."""
        return [name for name, value in self.model_dump().items() if value is True]

    @property
    def disabled_tools(self) -> list[str]:
        """Return list of disabled tool names."""
        return [name for name, value in self.model_dump().items() if value is False]

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled.

        Args:
            tool_name: Name of the tool (e.g., "technical_analysis")

        Returns:
            True if tool is enabled, False if disabled or not found
        """
        return getattr(self, tool_name, False)


class AppConfig(BaseModel):
    """Main application configuration with sensible defaults.

    Environment variables:
        FINNHUB_API_KEY: Required - Your Finnhub API key
        FINNHUB_STORAGE_DIR: Required - Root directory for data storage
        FINNHUB_SAFE_TOKEN_LIMIT: Optional - Safe token limit (default: 75000)
        FINNHUB_RATE_LIMIT_RPM: Optional - Requests per minute (default: 300 for premium)
        FINNHUB_REQUEST_TIMEOUT: Optional - Request timeout in seconds (default: 30)
        FINNHUB_ENABLE_CACHE: Optional - Enable request caching (default: true)
        FINNHUB_CACHE_TTL: Optional - Cache TTL in seconds (default: 300)
        FINNHUB_MAX_CONCURRENT_JOBS: Optional - Max background jobs (default: 5)
        FINNHUB_JOB_TIMEOUT: Optional - Job timeout in seconds (default: 3600)
        FINNHUB_JOB_CLEANUP_AFTER: Optional - Cleanup after seconds (default: 86400)
        FINNHUB_LOG_LEVEL: Optional - Log level (default: INFO)
        FINNHUB_LOG_FILE: Optional - Log file path (default: None = console only)
        FINNHUB_DEBUG: Optional - Enable debug mode (default: false)
        FINNHUB_MOCK_RESPONSES: Optional - Mock API responses (default: false)

    Plus all FINNHUB_ENABLE_* variables for tool configuration (see ToolConfig).
    """

    # Required
    finnhub_api_key: str = Field(description="Finnhub API key")
    storage_directory: Path = Field(description="Root directory for data storage")

    # Tool configuration
    tools: ToolConfig = Field(default_factory=ToolConfig, description="Tool enable/disable config")

    # MCP Server Configuration
    safe_token_limit: int = Field(
        default=75_000,
        ge=1000,
        description="Conservative token limit (75% of 100k context window)",
    )
    rate_limit_rpm: int = Field(
        default=300,
        ge=1,
        description="Rate limit in requests per minute (30 free, 300 premium)",
    )
    request_timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Maximum number of retry attempts")
    retry_backoff_factor: float = Field(
        default=1.5, ge=1.0, description="Exponential backoff factor for retries"
    )
    retry_jitter: float = Field(
        default=0.25, ge=0.0, le=1.0, description="Fractional jitter for retry backoff"
    )
    enable_cache: bool = Field(default=True, description="Enable request caching")
    cache_ttl: int = Field(default=300, ge=1, description="Cache TTL in seconds")

    # Background Job Configuration
    max_concurrent_jobs: int = Field(
        default=5, ge=1, description="Maximum concurrent background jobs"
    )
    job_timeout: int = Field(default=3600, ge=1, description="Job timeout in seconds")
    job_cleanup_after: int = Field(
        default=86400, ge=1, description="Auto-cleanup completed jobs after seconds"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")
    log_file: Path | None = Field(default=None, description="Log file path (None = console only)")

    # Development Configuration
    debug: bool = Field(default=False, description="Enable debug mode")
    mock_responses: bool = Field(default=False, description="Mock API responses for testing")

    @field_validator("finnhub_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is not empty."""
        if not v or not v.strip():
            raise ValueError("FINNHUB_API_KEY cannot be empty")
        return v.strip()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the accepted values."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper

    @model_validator(mode="after")
    def ensure_storage_directory(self) -> AppConfig:
        """Ensure storage directory exists, create if missing."""
        self.storage_directory.mkdir(parents=True, exist_ok=True)
        return self

    @model_validator(mode="after")
    def ensure_log_directory(self) -> AppConfig:
        """Ensure log file directory exists if log_file is specified."""
        if self.log_file is not None:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        return self


def load_config(**overrides: Any) -> AppConfig:
    """Load configuration from environment variables with optional overrides.

    Loads .env file if present, reads environment variables with FINNHUB_ prefix,
    and applies any provided overrides.

    Args:
        **overrides: Optional configuration overrides (e.g., finnhub_api_key="test")

    Returns:
        AppConfig instance with loaded configuration

    Raises:
        ValueError: If required configuration is missing or invalid

    Example:
        >>> config = load_config()
        >>> print(config.finnhub_api_key)
        >>> print(config.tools.enabled_tools)

        >>> # With overrides for testing
        >>> config = load_config(finnhub_api_key="test_key", mock_responses=True)
    """
    load_dotenv()
    env_config: dict[str, Any] = {}

    # Required
    if api_key := os.getenv("FINNHUB_API_KEY"):
        env_config["finnhub_api_key"] = api_key

    if storage_dir := os.getenv("FINNHUB_STORAGE_DIR"):
        env_config["storage_directory"] = Path(storage_dir)

    # MCP Server Configuration
    if token_limit := os.getenv("FINNHUB_SAFE_TOKEN_LIMIT"):
        try:
            env_config["safe_token_limit"] = int(token_limit)
        except ValueError:
            pass

    if rate_limit := os.getenv("FINNHUB_RATE_LIMIT_RPM"):
        try:
            env_config["rate_limit_rpm"] = int(rate_limit)
        except ValueError:
            pass

    if timeout := os.getenv("FINNHUB_REQUEST_TIMEOUT"):
        try:
            env_config["request_timeout"] = int(timeout)
        except ValueError:
            pass

    if cache := os.getenv("FINNHUB_ENABLE_CACHE"):
        env_config["enable_cache"] = cache.lower() in ("true", "1", "yes")

    if cache_ttl := os.getenv("FINNHUB_CACHE_TTL"):
        try:
            env_config["cache_ttl"] = int(cache_ttl)
        except ValueError:
            pass

    # Background Job Configuration
    if max_jobs := os.getenv("FINNHUB_MAX_CONCURRENT_JOBS"):
        try:
            env_config["max_concurrent_jobs"] = int(max_jobs)
        except ValueError:
            pass

    if job_timeout := os.getenv("FINNHUB_JOB_TIMEOUT"):
        try:
            env_config["job_timeout"] = int(job_timeout)
        except ValueError:
            pass

    if cleanup := os.getenv("FINNHUB_JOB_CLEANUP_AFTER"):
        try:
            env_config["job_cleanup_after"] = int(cleanup)
        except ValueError:
            pass

    # Logging Configuration
    if log_level := os.getenv("FINNHUB_LOG_LEVEL"):
        env_config["log_level"] = log_level

    if log_file := os.getenv("FINNHUB_LOG_FILE"):
        env_config["log_file"] = Path(log_file)

    # Development Configuration
    if debug := os.getenv("FINNHUB_DEBUG"):
        env_config["debug"] = debug.lower() in ("true", "1", "yes")

    if mock := os.getenv("FINNHUB_MOCK_RESPONSES"):
        env_config["mock_responses"] = mock.lower() in ("true", "1", "yes")

    # Tool Configuration (load from FINNHUB_ENABLE_* variables)
    tool_config: dict[str, bool] = {}
    for tool_name in [
        "technical_analysis",
        "stock_market_data",
        "news_sentiment",
        "stock_fundamentals",
        "stock_estimates",
        "stock_ownership",
        "stock_alternative_data",
        "stock_filings",
        "forex",
        "crypto",
        "etf",
        "mutual_fund",
        "bond",
        "index",
        "screening",
        "calendar",
        "economic",
        "specialized",
    ]:
        env_var = f"FINNHUB_ENABLE_{tool_name.upper()}"
        if value := os.getenv(env_var):
            tool_config[tool_name] = value.lower() in ("true", "1", "yes")

    if tool_config:
        env_config["tools"] = ToolConfig(**tool_config)

    final_config: dict[str, Any] = {**env_config, **overrides}
    return AppConfig(**final_config)


__all__ = ["AppConfig", "ToolConfig", "load_config"]
