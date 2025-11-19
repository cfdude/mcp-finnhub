"""Tests for finnhub_job_status tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from mcp_finnhub.config import AppConfig
from mcp_finnhub.jobs.models import JobStatus
from mcp_finnhub.server import ServerContext
from mcp_finnhub.tools.job_status import finnhub_job_status

if TYPE_CHECKING:
    from pathlib import Path


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


class TestJobStatus:
    """Test finnhub_job_status tool."""

    @pytest.fixture
    def context(self, test_config):
        """Create server context."""
        return ServerContext(test_config)

    @pytest.mark.asyncio
    async def test_get_job_status_success(self, context):
        """Test getting job status for existing job."""
        # Create a job
        job = context.job_manager.create_job(
            tool_name="test_tool",
            params={"operation": "test_operation", "test": "data"},
        )

        # Get job status
        result = await finnhub_job_status(context, "get", job_id=job.job_id)

        assert "error" not in result
        assert result["job_id"] == job.job_id
        assert result["status"] == JobStatus.PENDING.value
        assert result["progress"] == 0
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_get_completed_job_with_result(self, context):
        """Test getting status of completed job with result."""
        # Create and complete a job
        job = context.job_manager.create_job(
            tool_name="test_tool", params={"operation": "test_operation"}
        )
        context.job_manager.complete_job(job.job_id, result={"rows": 100, "file": "data.csv"})

        # Get job status
        result = await finnhub_job_status(context, "get", job_id=job.job_id)

        assert "error" not in result
        assert result["status"] == JobStatus.COMPLETED.value
        assert result["progress"] == 100
        assert result["result"] == {"rows": 100, "file": "data.csv"}

    @pytest.mark.asyncio
    async def test_get_failed_job_with_error(self, context):
        """Test getting status of failed job with error."""
        # Create and fail a job
        job = context.job_manager.create_job(
            tool_name="test_tool", params={"operation": "test_operation"}
        )
        context.job_manager.fail_job(job.job_id, error="Something went wrong")

        # Get job status
        result = await finnhub_job_status(context, "get", job_id=job.job_id)

        assert "error" in result
        assert result["status"] == JobStatus.FAILED.value
        assert result["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, context):
        """Test getting status for non-existent job."""
        result = await finnhub_job_status(context, "get", job_id="nonexistent")

        assert "error" in result
        assert result["error"]["code"] == "JOB_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_job_status_missing_parameter(self, context):
        """Test missing job_id parameter."""
        result = await finnhub_job_status(context, "get")

        assert "error" in result
        assert result["error"]["code"] == "MISSING_PARAMETER"

    @pytest.mark.asyncio
    async def test_get_job_status_unknown_operation(self, context):
        """Test unknown operation."""
        result = await finnhub_job_status(context, "delete", job_id="test")

        assert "error" in result
        assert result["error"]["code"] == "UNKNOWN_OPERATION"
