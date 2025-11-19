"""Tests for ServerContext and dependency injection."""

from __future__ import annotations

import pytest

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.jobs.manager import JobManager
from mcp_finnhub.jobs.worker import BackgroundWorker
from mcp_finnhub.server import ServerContext, build_server_context
from mcp_finnhub.utils.file_writer import FileWriter
from mcp_finnhub.utils.json_to_csv import JSONToCSVConverter
from mcp_finnhub.utils.output_handler import ResultOutputHandler
from mcp_finnhub.utils.path_resolver import PathResolver
from mcp_finnhub.utils.token_estimator import TokenEstimator


class TestServerContext:
    """Test ServerContext initialization and lifecycle."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration."""
        return AppConfig(
            finnhub_api_key="test_api_key",
            storage_directory=tmp_path,
        )

    @pytest.fixture
    async def context(self, config):
        """Create test server context."""
        ctx = ServerContext(config)
        yield ctx
        await ctx.aclose()

    def test_initialization(self, config):
        """Test ServerContext initialization with all components."""
        context = ServerContext(config)

        # Verify config is stored
        assert context.config == config

        # Verify client is initialized
        assert isinstance(context.client, FinnhubClient)

        # Verify utilities are initialized
        assert isinstance(context.token_estimator, TokenEstimator)
        assert isinstance(context.csv_converter, JSONToCSVConverter)
        assert isinstance(context.path_resolver, PathResolver)
        assert isinstance(context.file_writer, FileWriter)
        assert isinstance(context.job_manager, JobManager)
        assert isinstance(context.background_worker, BackgroundWorker)
        assert isinstance(context.output_handler, ResultOutputHandler)

    def test_client_configuration(self, config):
        """Test client is configured from AppConfig."""
        context = ServerContext(config)

        # Client receives the full config
        assert context.client.config == config

    def test_path_resolver_configuration(self, config, tmp_path):
        """Test path resolver is configured from AppConfig."""
        context = ServerContext(config)

        assert context.path_resolver.storage_dir == tmp_path

    def test_output_handler_has_all_dependencies(self, config):
        """Test output handler receives all required dependencies."""
        context = ServerContext(config)

        # Output handler should have references to all utilities
        assert context.output_handler.config == config
        assert context.output_handler.token_estimator == context.token_estimator
        assert context.output_handler.csv_converter == context.csv_converter
        assert context.output_handler.path_resolver == context.path_resolver
        assert context.output_handler.file_writer == context.file_writer
        assert context.output_handler.job_manager == context.job_manager

    @pytest.mark.asyncio
    async def test_aclose(self, config):
        """Test graceful shutdown closes client."""
        context = ServerContext(config)

        # Client should start open
        assert not context.client.is_closed

        # After aclose, client should be closed
        await context.aclose()
        assert context.client.is_closed

    @pytest.mark.asyncio
    async def test_context_manager_support(self, config):
        """Test ServerContext can be used with context cleanup."""
        context = ServerContext(config)

        assert not context.client.is_closed

        await context.aclose()

        assert context.client.is_closed


class TestBuildServerContext:
    """Test build_server_context factory function."""

    def test_builds_with_env_config(self, monkeypatch, tmp_path):
        """Test building context from environment variables."""
        monkeypatch.setenv("FINNHUB_API_KEY", "env_api_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path))

        context = build_server_context()

        assert context.config.finnhub_api_key == "env_api_key"
        assert context.config.storage_directory == tmp_path

    def test_builds_with_overrides(self, monkeypatch, tmp_path):
        """Test building context with configuration overrides."""
        monkeypatch.setenv("FINNHUB_API_KEY", "env_api_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path))

        context = build_server_context(finnhub_api_key="override_key")

        assert context.config.finnhub_api_key == "override_key"

    def test_returns_server_context_instance(self, monkeypatch, tmp_path):
        """Test factory returns ServerContext instance."""
        monkeypatch.setenv("FINNHUB_API_KEY", "test_key")
        monkeypatch.setenv("FINNHUB_STORAGE_DIR", str(tmp_path))

        context = build_server_context()

        assert isinstance(context, ServerContext)
        assert isinstance(context.config, AppConfig)
