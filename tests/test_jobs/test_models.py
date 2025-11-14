"""Unit tests for job models."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from mcp_finnhub.jobs.models import Job, JobStatus


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_statuses(self):
        """Test all job status values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"


class TestJob:
    """Tests for Job model."""

    def test_create_basic_job(self):
        """Test creating a basic job."""
        job = Job(job_id="test-123", tool_name="fetch_data")
        assert job.job_id == "test-123"
        assert job.tool_name == "fetch_data"
        assert job.status == JobStatus.PENDING
        assert job.params == {}
        assert job.progress == 0

    def test_create_job_with_params(self):
        """Test creating job with parameters."""
        params = {"symbol": "AAPL", "resolution": "D"}
        job = Job(job_id="test-123", tool_name="fetch_candles", params=params)
        assert job.params == params

    def test_is_terminal(self):
        """Test is_terminal property."""
        job = Job(job_id="test-123", tool_name="test")

        job.status = JobStatus.PENDING
        assert not job.is_terminal

        job.status = JobStatus.RUNNING
        assert not job.is_terminal

        job.status = JobStatus.COMPLETED
        assert job.is_terminal

        job.status = JobStatus.FAILED
        assert job.is_terminal

        job.status = JobStatus.CANCELLED
        assert job.is_terminal

    def test_duration_seconds_not_started(self):
        """Test duration calculation for job not started."""
        job = Job(job_id="test-123", tool_name="test")
        assert job.duration_seconds is None

    def test_duration_seconds_running(self):
        """Test duration calculation for running job."""
        job = Job(job_id="test-123", tool_name="test")
        job.started_at = datetime.utcnow() - timedelta(seconds=30)
        duration = job.duration_seconds
        assert duration is not None
        assert 29 <= duration <= 31  # Allow small time variation

    def test_duration_seconds_completed(self):
        """Test duration calculation for completed job."""
        job = Job(job_id="test-123", tool_name="test")
        job.started_at = datetime.utcnow() - timedelta(seconds=60)
        job.completed_at = datetime.utcnow() - timedelta(seconds=30)
        duration = job.duration_seconds
        assert duration is not None
        assert 29 <= duration <= 31

    def test_mark_running(self):
        """Test marking job as running."""
        job = Job(job_id="test-123", tool_name="test")
        assert job.status == JobStatus.PENDING
        assert job.started_at is None

        job.mark_running("Processing data")
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
        assert job.message == "Processing data"

    def test_mark_running_default_message(self):
        """Test marking job as running with default message."""
        job = Job(job_id="test-123", tool_name="test")
        job.mark_running()
        assert job.message == "Job started"

    def test_mark_completed(self):
        """Test marking job as completed."""
        job = Job(job_id="test-123", tool_name="test")
        result = {"data": [1, 2, 3], "count": 3}

        job.mark_completed(result, "Fetched 3 items")
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.result == result
        assert job.progress == 100
        assert job.message == "Fetched 3 items"

    def test_mark_completed_default_message(self):
        """Test marking job as completed with default message."""
        job = Job(job_id="test-123", tool_name="test")
        job.mark_completed({"success": True})
        assert job.message == "Job completed successfully"

    def test_mark_failed(self):
        """Test marking job as failed."""
        job = Job(job_id="test-123", tool_name="test")
        error = "Connection timeout"

        job.mark_failed(error, "Network error occurred")
        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert job.error == error
        assert job.message == "Network error occurred"

    def test_mark_failed_default_message(self):
        """Test marking job as failed with default message."""
        job = Job(job_id="test-123", tool_name="test")
        job.mark_failed("Connection timeout")
        assert job.message == "Job failed: Connection timeout"

    def test_mark_cancelled(self):
        """Test marking job as cancelled."""
        job = Job(job_id="test-123", tool_name="test")

        job.mark_cancelled("User requested cancellation")
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
        assert job.message == "User requested cancellation"

    def test_mark_cancelled_default_message(self):
        """Test marking job as cancelled with default message."""
        job = Job(job_id="test-123", tool_name="test")
        job.mark_cancelled()
        assert job.message == "Job cancelled"

    def test_update_progress(self):
        """Test updating job progress."""
        job = Job(job_id="test-123", tool_name="test")
        assert job.progress == 0

        job.update_progress(50, "Halfway done")
        assert job.progress == 50
        assert job.message == "Halfway done"

    def test_update_progress_clamping(self):
        """Test progress clamping to 0-100 range."""
        job = Job(job_id="test-123", tool_name="test")

        job.update_progress(-10)
        assert job.progress == 0

        job.update_progress(150)
        assert job.progress == 100

    def test_update_progress_no_message(self):
        """Test updating progress without message."""
        job = Job(job_id="test-123", tool_name="test")
        job.message = "Original message"

        job.update_progress(75)
        assert job.progress == 75
        assert job.message == "Original message"  # Unchanged
