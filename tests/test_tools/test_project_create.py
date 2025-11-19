"""Tests for finnhub_project_create tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from mcp_finnhub.config import AppConfig
from mcp_finnhub.server import ServerContext
from mcp_finnhub.tools.project_create import finnhub_project_create

if TYPE_CHECKING:
    pass


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
    """Create test configuration."""
    return AppConfig(
        finnhub_api_key="test_api_key",
        storage_directory=tmp_path / "data",
        rate_limit_rpm=60,
        request_timeout=5,
        max_retries=2,
        retry_backoff_factor=1.5,
        retry_jitter=0.1,
    )


class TestProjectCreate:
    """Test finnhub_project_create tool."""

    @pytest.fixture
    def context(self, test_config):
        """Create server context."""
        return ServerContext(test_config)

    @pytest.mark.asyncio
    async def test_create_project_success(self, context, tmp_path):
        """Test creating a new project."""
        result = await finnhub_project_create(context, "create", project="test-project")

        assert "error" not in result
        assert result["project"] == "test-project"
        assert "path" in result
        assert "metadata_file" in result
        assert result["subdirectories"] == [
            "candles",
            "quotes",
            "news",
            "fundamentals",
            "technical",
            "jobs",
        ]

        # Verify directory was created
        project_dir = Path(result["path"])
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Verify subdirectories were created
        for subdir in result["subdirectories"]:
            assert (project_dir / subdir).exists()

        # Verify metadata file was created
        metadata_path = Path(result["metadata_file"])
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text())
        assert metadata["project"] == "test-project"
        assert "created_at" in metadata

    @pytest.mark.asyncio
    async def test_create_project_invalid_name(self, context):
        """Test creating project with invalid name."""
        result = await finnhub_project_create(context, "create", project="test project!")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_PROJECT_NAME"

    @pytest.mark.asyncio
    async def test_create_project_already_exists(self, context, tmp_path):
        """Test creating project that already exists."""
        # Create project first time
        await finnhub_project_create(context, "create", project="existing")

        # Try to create again
        result = await finnhub_project_create(context, "create", project="existing")

        assert "error" in result
        assert result["error"]["code"] == "PROJECT_EXISTS"

    @pytest.mark.asyncio
    async def test_create_project_missing_parameter(self, context):
        """Test creating project without project parameter."""
        result = await finnhub_project_create(context, "create")

        assert "error" in result
        assert result["error"]["code"] == "MISSING_PARAMETER"

    @pytest.mark.asyncio
    async def test_create_project_unknown_operation(self, context):
        """Test unknown operation."""
        result = await finnhub_project_create(context, "delete", project="test")

        assert "error" in result
        assert result["error"]["code"] == "UNKNOWN_OPERATION"

    @pytest.mark.asyncio
    async def test_create_project_empty_name(self, context):
        """Test creating project with empty name."""
        result = await finnhub_project_create(context, "create", project="")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_PROJECT_NAME"

    @pytest.mark.asyncio
    async def test_create_project_with_hyphens(self, context):
        """Test creating project with hyphens in name."""
        result = await finnhub_project_create(context, "create", project="my-test-project")

        assert "error" not in result
        assert result["project"] == "my-test-project"

    @pytest.mark.asyncio
    async def test_create_project_with_underscores(self, context):
        """Test creating project with underscores in name."""
        result = await finnhub_project_create(context, "create", project="my_test_project")

        assert "error" not in result
        assert result["project"] == "my_test_project"
