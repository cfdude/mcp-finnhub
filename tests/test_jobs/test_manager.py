"""Unit tests for JobManager."""

from __future__ import annotations

import time
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from mcp_finnhub.jobs.manager import JobManager
from mcp_finnhub.jobs.models import JobStatus

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def manager(tmp_path: Path) -> JobManager:
    """Create JobManager with temp directory."""
    return JobManager(tmp_path / "jobs")


class TestJobManager:
    """Tests for JobManager class."""

    def test_initialization(self, tmp_path: Path):
        """Test manager initialization creates directory."""
        jobs_dir = tmp_path / "jobs"
        assert not jobs_dir.exists()

        manager = JobManager(jobs_dir)
        assert jobs_dir.exists()
        assert manager.jobs_dir == jobs_dir

    def test_create_job(self, manager: JobManager):
        """Test creating a new job."""
        job = manager.create_job("fetch_data", {"symbol": "AAPL"})
        assert job.job_id is not None
        assert job.tool_name == "fetch_data"
        assert job.params == {"symbol": "AAPL"}
        assert job.status == JobStatus.PENDING

    def test_create_job_without_params(self, manager: JobManager):
        """Test creating job without parameters."""
        job = manager.create_job("list_symbols")
        assert job.params == {}

    def test_get_job(self, manager: JobManager):
        """Test getting job by ID."""
        created = manager.create_job("test", {"key": "value"})
        retrieved = manager.get_job(created.job_id)

        assert retrieved is not None
        assert retrieved.job_id == created.job_id
        assert retrieved.tool_name == created.tool_name
        assert retrieved.params == created.params

    def test_get_nonexistent_job(self, manager: JobManager):
        """Test getting job that doesn't exist."""
        job = manager.get_job("nonexistent-id")
        assert job is None

    def test_update_job_status(self, manager: JobManager):
        """Test updating job status."""
        job = manager.create_job("test")
        assert job.status == JobStatus.PENDING

        updated = manager.update_job(job.job_id, status=JobStatus.RUNNING)
        assert updated is not None
        assert updated.status == JobStatus.RUNNING
        assert updated.started_at is not None

    def test_update_job_progress(self, manager: JobManager):
        """Test updating job progress."""
        job = manager.create_job("test")

        updated = manager.update_job(job.job_id, progress=50, message="Processing...")
        assert updated is not None
        assert updated.progress == 50
        assert updated.message == "Processing..."

    def test_update_nonexistent_job(self, manager: JobManager):
        """Test updating job that doesn't exist."""
        updated = manager.update_job("nonexistent-id", progress=50)
        assert updated is None

    def test_complete_job(self, manager: JobManager):
        """Test completing a job."""
        job = manager.create_job("test")
        result = {"data": [1, 2, 3], "count": 3}

        completed = manager.complete_job(job.job_id, result, "Fetched 3 items")
        assert completed is not None
        assert completed.status == JobStatus.COMPLETED
        assert completed.result == result
        assert completed.completed_at is not None
        assert completed.progress == 100

    def test_fail_job(self, manager: JobManager):
        """Test failing a job."""
        job = manager.create_job("test")

        failed = manager.fail_job(job.job_id, "Connection timeout", "Network error")
        assert failed is not None
        assert failed.status == JobStatus.FAILED
        assert failed.error == "Connection timeout"
        assert failed.completed_at is not None

    def test_cancel_job(self, manager: JobManager):
        """Test cancelling a job."""
        job = manager.create_job("test")

        cancelled = manager.cancel_job(job.job_id, "User requested")
        assert cancelled is not None
        assert cancelled.status == JobStatus.CANCELLED
        assert cancelled.completed_at is not None

    def test_cancel_terminal_job(self, manager: JobManager):
        """Test cannot cancel job in terminal state."""
        job = manager.create_job("test")
        manager.complete_job(job.job_id, {"success": True})

        # Try to cancel completed job
        result = manager.cancel_job(job.job_id)
        assert result is not None
        assert result.status == JobStatus.COMPLETED  # Status unchanged

    def test_list_jobs_empty(self, manager: JobManager):
        """Test listing jobs when none exist."""
        jobs = manager.list_jobs()
        assert jobs == []

    def test_list_jobs_all(self, manager: JobManager):
        """Test listing all jobs."""
        job1 = manager.create_job("test1")
        time.sleep(0.01)  # Ensure different timestamps on Windows
        job2 = manager.create_job("test2")
        time.sleep(0.01)
        job3 = manager.create_job("test3")

        jobs = manager.list_jobs()
        assert len(jobs) == 3
        # Should be sorted by creation time, newest first
        assert jobs[0].job_id == job3.job_id
        assert jobs[1].job_id == job2.job_id
        assert jobs[2].job_id == job1.job_id

    def test_list_jobs_by_status(self, manager: JobManager):
        """Test listing jobs filtered by status."""
        job1 = manager.create_job("test1")
        job2 = manager.create_job("test2")
        job3 = manager.create_job("test3")

        manager.update_job(job1.job_id, status=JobStatus.RUNNING)
        manager.complete_job(job2.job_id, {"success": True})
        # job3 remains PENDING

        pending = manager.list_jobs(status=JobStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].job_id == job3.job_id

        running = manager.list_jobs(status=JobStatus.RUNNING)
        assert len(running) == 1
        assert running[0].job_id == job1.job_id

        completed = manager.list_jobs(status=JobStatus.COMPLETED)
        assert len(completed) == 1
        assert completed[0].job_id == job2.job_id

    def test_list_jobs_with_limit(self, manager: JobManager):
        """Test listing jobs with limit."""
        for i in range(5):
            manager.create_job(f"test{i}")

        jobs = manager.list_jobs(limit=3)
        assert len(jobs) == 3

    def test_delete_job(self, manager: JobManager):
        """Test deleting a job."""
        job = manager.create_job("test")

        # Verify job exists
        assert manager.get_job(job.job_id) is not None

        # Delete job
        deleted = manager.delete_job(job.job_id)
        assert deleted is True

        # Verify job is gone
        assert manager.get_job(job.job_id) is None

    def test_delete_nonexistent_job(self, manager: JobManager):
        """Test deleting job that doesn't exist."""
        deleted = manager.delete_job("nonexistent-id")
        assert deleted is False

    def test_cleanup_old_jobs(self, manager: JobManager):
        """Test cleaning up old completed jobs."""
        # Create some jobs
        job1 = manager.create_job("test1")
        job2 = manager.create_job("test2")
        job3 = manager.create_job("test3")

        # Complete jobs
        manager.complete_job(job1.job_id, {"success": True})
        manager.fail_job(job2.job_id, "Error")
        # job3 remains pending

        # Manually set completion times to be old
        j1 = manager.get_job(job1.job_id)
        j2 = manager.get_job(job2.job_id)
        if j1:
            from datetime import datetime

            j1.completed_at = datetime.utcnow() - timedelta(days=2)
            manager._save_job(j1)
        if j2:
            from datetime import datetime

            j2.completed_at = datetime.utcnow() - timedelta(days=2)
            manager._save_job(j2)

        # Cleanup jobs older than 1 day
        deleted = manager.cleanup_old_jobs(timedelta(days=1))
        assert deleted == 2

        # Verify only pending job remains
        remaining = manager.list_jobs()
        assert len(remaining) == 1
        assert remaining[0].job_id == job3.job_id

    def test_cleanup_no_old_jobs(self, manager: JobManager):
        """Test cleanup when no jobs are old enough."""
        job = manager.create_job("test")
        manager.complete_job(job.job_id, {"success": True})

        # Try to cleanup jobs older than 1 day (but job was just completed)
        deleted = manager.cleanup_old_jobs(timedelta(days=1))
        assert deleted == 0

        # Job should still exist
        assert manager.get_job(job.job_id) is not None

    def test_persistence_across_instances(self, tmp_path: Path):
        """Test that jobs persist across manager instances."""
        jobs_dir = tmp_path / "jobs"

        # Create job with first manager
        manager1 = JobManager(jobs_dir)
        job = manager1.create_job("test", {"key": "value"})
        job_id = job.job_id

        # Create new manager instance
        manager2 = JobManager(jobs_dir)

        # Should be able to retrieve job
        retrieved = manager2.get_job(job_id)
        assert retrieved is not None
        assert retrieved.job_id == job_id
        assert retrieved.tool_name == "test"
        assert retrieved.params == {"key": "value"}
