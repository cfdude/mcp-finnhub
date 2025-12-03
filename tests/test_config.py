"""Unit tests for configuration management.

Tests AppConfig, ToolConfig, and load_config functionality with comprehensive
coverage of environment variable loading, validation, and edge cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from mcp_finnhub.config import AppConfig, ToolConfig, load_config

if TYPE_CHECKING:
    from pathlib import Path


class TestToolConfig:
    """Tests for ToolConfig class."""

    def test_all_tools_enabled_by_default(self):
        """Test that all 18 tools are enabled by default."""
        config = ToolConfig()

        # Check all 18 tools are enabled
        assert config.technical_analysis is True
        assert config.stock_market_data is True
        assert config.news_sentiment is True
        assert config.stock_fundamentals is True
        assert config.stock_estimates is True
        assert config.stock_ownership is True
        assert config.stock_alternative_data is True
        assert config.stock_filings is True
        assert config.forex is True
        assert config.crypto is True
        assert config.etf is True
        assert config.mutual_fund is True
        assert config.bond is True
        assert config.index is True
        assert config.screening is True
        assert config.calendar is True
        assert config.economic is True
        assert config.specialized is True

        # Check enabled_tools property
        assert len(config.enabled_tools) == 18

    def test_disable_specific_tools(self):
        """Test disabling specific tools."""
        config = ToolConfig(
            forex=False,
            crypto=False,
            mutual_fund=False,
            bond=False,
        )

        # Disabled tools
        assert config.forex is False
        assert config.crypto is False
        assert config.mutual_fund is False
        assert config.bond is False

        # Enabled tools
        assert config.technical_analysis is True
        assert config.stock_market_data is True

        # Check counts
        assert len(config.enabled_tools) == 14
        assert len(config.disabled_tools) == 4

    def test_enabled_tools_property(self):
        """Test enabled_tools property returns correct list."""
        config = ToolConfig(
            forex=False,
            crypto=False,
            bond=False,
        )

        enabled = config.enabled_tools
        disabled = config.disabled_tools

        # Check enabled list
        assert "technical_analysis" in enabled
        assert "stock_market_data" in enabled
        assert "news_sentiment" in enabled
        assert "forex" not in enabled
        assert "crypto" not in enabled
        assert "bond" not in enabled

        # Check disabled list
        assert "forex" in disabled
        assert "crypto" in disabled
        assert "bond" in disabled
        assert len(disabled) == 3

    def test_is_tool_enabled_method(self):
        """Test is_tool_enabled method."""
        config = ToolConfig(
            forex=False,
            crypto=False,
        )

        # Enabled tools
        assert config.is_tool_enabled("technical_analysis") is True
        assert config.is_tool_enabled("stock_market_data") is True

        # Disabled tools
        assert config.is_tool_enabled("forex") is False
        assert config.is_tool_enabled("crypto") is False

        # Non-existent tool
        assert config.is_tool_enabled("nonexistent_tool") is False

    def test_mandatory_tools(self):
        """Test that mandatory tools can be disabled (not enforced in ToolConfig)."""
        # ToolConfig doesn't enforce mandatory status, just tracks state
        config = ToolConfig(
            technical_analysis=False,
            stock_market_data=False,
            news_sentiment=False,
        )

        assert config.technical_analysis is False
        assert config.stock_market_data is False
        assert config.news_sentiment is False


class TestAppConfig:
    """Tests for AppConfig class."""

    def test_create_with_required_fields(self, tmp_path: Path):
        """Test creating AppConfig with only required fields."""
        config = AppConfig(
            finnhub_api_key="test_api_key_123",
            storage_directory=tmp_path / "finnhub-data",
        )

        assert config.finnhub_api_key == "test_api_key_123"
        assert config.storage_directory == tmp_path / "finnhub-data"

        # Check defaults
        assert config.safe_token_limit == 75_000
        assert config.rate_limit_rpm == 300
        assert config.request_timeout == 30
        assert config.enable_cache is True
        assert config.cache_ttl == 300
        assert config.max_concurrent_jobs == 5
        assert config.job_timeout == 3600
        assert config.job_cleanup_after == 86400
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.debug is False
        assert config.mock_responses is False

        # Check ToolConfig defaults
        assert isinstance(config.tools, ToolConfig)
        assert len(config.tools.enabled_tools) == 18

    def test_create_with_all_fields(self, tmp_path: Path):
        """Test creating AppConfig with all fields specified."""
        log_file = tmp_path / "logs" / "finnhub.log"

        config = AppConfig(
            finnhub_api_key="test_key",
            storage_directory=tmp_path / "data",
            safe_token_limit=50_000,
            rate_limit_rpm=60,
            request_timeout=60,
            enable_cache=False,
            cache_ttl=600,
            max_concurrent_jobs=10,
            job_timeout=7200,
            job_cleanup_after=172800,
            log_level="DEBUG",
            log_file=log_file,
            debug=True,
            mock_responses=True,
            tools=ToolConfig(forex=False, crypto=False),
        )

        assert config.finnhub_api_key == "test_key"
        assert config.safe_token_limit == 50_000
        assert config.rate_limit_rpm == 60
        assert config.request_timeout == 60
        assert config.enable_cache is False
        assert config.cache_ttl == 600
        assert config.max_concurrent_jobs == 10
        assert config.job_timeout == 7200
        assert config.job_cleanup_after == 172800
        assert config.log_level == "DEBUG"
        assert config.log_file == log_file
        assert config.debug is True
        assert config.mock_responses is True
        assert config.tools.forex is False
        assert config.tools.crypto is False

    def test_storage_directory_creation(self, tmp_path: Path):
        """Test that storage directory is created if it doesn't exist."""
        storage_dir = tmp_path / "new_directory" / "subfolder"
        assert not storage_dir.exists()

        config = AppConfig(
            finnhub_api_key="test_key",
            storage_directory=storage_dir,
        )

        # Directory should be created
        assert config.storage_directory.exists()
        assert config.storage_directory.is_dir()

    def test_log_directory_creation(self, tmp_path: Path):
        """Test that log file directory is created if it doesn't exist."""
        log_file = tmp_path / "new_logs" / "subfolder" / "app.log"
        assert not log_file.parent.exists()

        config = AppConfig(
            finnhub_api_key="test_key",
            storage_directory=tmp_path / "data",
            log_file=log_file,
        )

        # Log directory should be created
        assert config.log_file.parent.exists()
        assert config.log_file.parent.is_dir()

    def test_empty_api_key_raises_error(self, tmp_path: Path):
        """Test that empty API key raises ValidationError."""
        with pytest.raises(ValidationError, match="FINNHUB_API_KEY cannot be empty"):
            AppConfig(
                finnhub_api_key="",
                storage_directory=tmp_path / "data",
            )

    def test_whitespace_api_key_raises_error(self, tmp_path: Path):
        """Test that whitespace-only API key raises ValidationError."""
        with pytest.raises(ValidationError, match="FINNHUB_API_KEY cannot be empty"):
            AppConfig(
                finnhub_api_key="   ",
                storage_directory=tmp_path / "data",
            )

    def test_api_key_trimmed(self, tmp_path: Path):
        """Test that API key is trimmed of whitespace."""
        config = AppConfig(
            finnhub_api_key="  test_key_with_spaces  ",
            storage_directory=tmp_path / "data",
        )

        assert config.finnhub_api_key == "test_key_with_spaces"

    def test_invalid_log_level_raises_error(self, tmp_path: Path):
        """Test that invalid log level raises ValidationError."""
        with pytest.raises(ValidationError, match="Log level must be one of"):
            AppConfig(
                finnhub_api_key="test_key",
                storage_directory=tmp_path / "data",
                log_level="INVALID",
            )

    def test_log_level_case_insensitive(self, tmp_path: Path):
        """Test that log level is case-insensitive and uppercased."""
        config = AppConfig(
            finnhub_api_key="test_key",
            storage_directory=tmp_path / "data",
            log_level="debug",
        )

        assert config.log_level == "DEBUG"

    def test_negative_rate_limit_raises_error(self, tmp_path: Path):
        """Test that negative rate limit raises ValidationError."""
        with pytest.raises(ValidationError):
            AppConfig(
                finnhub_api_key="test_key",
                storage_directory=tmp_path / "data",
                rate_limit_rpm=-1,
            )

    def test_negative_timeout_raises_error(self, tmp_path: Path):
        """Test that negative timeout raises ValidationError."""
        with pytest.raises(ValidationError):
            AppConfig(
                finnhub_api_key="test_key",
                storage_directory=tmp_path / "data",
                request_timeout=-1,
            )

    def test_token_limit_minimum(self, tmp_path: Path):
        """Test that token limit has minimum value."""
        with pytest.raises(ValidationError):
            AppConfig(
                finnhub_api_key="test_key",
                storage_directory=tmp_path / "data",
                safe_token_limit=100,  # Below minimum of 1000
            )


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_from_environment(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test loading configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("FINNHUB_API_KEY", "env_api_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "env_data"))
        monkeypatch.setenv("FINNHUB_SAFE_TOKEN_LIMIT", "50000")
        monkeypatch.setenv("FINNHUB_RATE_LIMIT_RPM", "60")
        monkeypatch.setenv("FINNHUB_REQUEST_TIMEOUT", "60")
        monkeypatch.setenv("FINNHUB_ENABLE_CACHE", "false")
        monkeypatch.setenv("FINNHUB_CACHE_TTL", "600")
        monkeypatch.setenv("FINNHUB_LOG_LEVEL", "WARNING")
        monkeypatch.setenv("FINNHUB_DEBUG", "true")
        monkeypatch.setenv("FINNHUB_MOCK_RESPONSES", "yes")

        config = load_config()

        assert config.finnhub_api_key == "env_api_key"
        assert config.storage_directory == tmp_path / "env_data"
        assert config.safe_token_limit == 50000
        assert config.rate_limit_rpm == 60
        assert config.request_timeout == 60
        assert config.enable_cache is False
        assert config.cache_ttl == 600
        assert config.log_level == "WARNING"
        assert config.debug is True
        assert config.mock_responses is True

    def test_load_tool_config_from_environment(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test loading tool configuration from environment variables."""
        monkeypatch.setenv("FINNHUB_API_KEY", "test_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "data"))
        monkeypatch.setenv("FINNHUB_ENABLE_FOREX", "false")
        monkeypatch.setenv("FINNHUB_ENABLE_CRYPTO", "false")
        monkeypatch.setenv("FINNHUB_ENABLE_MUTUAL_FUND", "0")
        monkeypatch.setenv("FINNHUB_ENABLE_BOND", "false")

        config = load_config()

        assert config.tools.forex is False
        assert config.tools.crypto is False
        assert config.tools.mutual_fund is False
        assert config.tools.bond is False
        assert config.tools.technical_analysis is True  # Not disabled
        assert len(config.tools.disabled_tools) == 4

    def test_boolean_parsing_variations(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that boolean values are parsed correctly."""
        monkeypatch.setenv("FINNHUB_API_KEY", "test_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "data"))
        monkeypatch.setenv("FINNHUB_ENABLE_CACHE", "1")
        monkeypatch.setenv("FINNHUB_DEBUG", "yes")
        monkeypatch.setenv("FINNHUB_MOCK_RESPONSES", "TRUE")

        config = load_config()

        assert config.enable_cache is True
        assert config.debug is True
        assert config.mock_responses is True

    def test_overrides_take_precedence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that function overrides take precedence over environment."""
        monkeypatch.setenv("FINNHUB_API_KEY", "env_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "env_data"))
        monkeypatch.setenv("FINNHUB_SAFE_TOKEN_LIMIT", "50000")

        config = load_config(
            finnhub_api_key="override_key",
            safe_token_limit=30000,
        )

        assert config.finnhub_api_key == "override_key"
        assert config.safe_token_limit == 30000
        # Storage dir from env should still be used
        assert config.storage_directory == tmp_path / "env_data"

    def test_invalid_integer_ignored(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that invalid integer values are ignored and defaults used."""
        monkeypatch.setenv("FINNHUB_API_KEY", "test_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "data"))
        monkeypatch.setenv("FINNHUB_SAFE_TOKEN_LIMIT", "not_a_number")
        monkeypatch.setenv("FINNHUB_RATE_LIMIT_RPM", "invalid")

        config = load_config()

        # Should use defaults when parsing fails
        assert config.safe_token_limit == 75_000
        assert config.rate_limit_rpm == 300

    def test_missing_required_fields_raises_error(self, monkeypatch: pytest.MonkeyPatch):
        """Test that missing required fields raises ValidationError."""
        # Clear any existing env vars
        monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
        monkeypatch.delenv("FINNHUB_STORAGE_DIR", raising=False)

        # Prevent load_dotenv from loading .env file
        monkeypatch.setattr("mcp_finnhub.config.load_dotenv", lambda: None)

        with pytest.raises(ValidationError):
            load_config()

    def test_load_with_log_file_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test loading configuration with log file path."""
        log_path = tmp_path / "logs" / "app.log"

        monkeypatch.setenv("FINNHUB_API_KEY", "test_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path / "data"))
        monkeypatch.setenv("FINNHUB_LOG_FILE", str(log_path))

        config = load_config()

        assert config.log_file == log_path
        assert config.log_file.parent.exists()
