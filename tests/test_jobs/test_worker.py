"""Tests for BackgroundWorker."""

import asyncio
from pathlib import Path

import pytest

from mcp_finnhub.jobs.manager import JobManager
from mcp_finnhub.jobs.models import JobStatus
from mcp_finnhub.jobs.worker import BackgroundWorker


class TestBackgroundWorker:
    """Test BackgroundWorker functionality."""

    @pytest.fixture
    def job_manager(self, tmp_path: Path) -> JobManager:
        """Create a temporary job manager."""
        return JobManager(tmp_path / "jobs")

    @pytest.fixture
    def worker(self, job_manager: JobManager) -> BackgroundWorker:
        """Create a background worker."""
        return BackgroundWorker(job_manager, max_workers=3, default_timeout=5.0)

    async def test_register_tool(self, worker: BackgroundWorker):
        """Test registering a tool handler."""

        async def test_handler(**params):
            return {"result": "success"}

        worker.register_tool("test_tool", test_handler)
        assert "test_tool" in worker._tool_handlers

    async def test_unregister_tool(self, worker: BackgroundWorker):
        """Test unregistering a tool handler."""

        async def test_handler(**params):
            return {"result": "success"}

        worker.register_tool("test_tool", test_handler)
        worker.unregister_tool("test_tool")
        assert "test_tool" not in worker._tool_handlers

    async def test_execute_job_success(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test successful job execution."""

        async def test_handler(value: int):
            await asyncio.sleep(0.1)
            return {"result": value * 2}

        worker.register_tool("test_tool", test_handler)

        # Create job
        job = job_manager.create_job("test_tool", {"value": 42})
        assert job.status == JobStatus.PENDING

        # Execute job
        result_job = await worker.execute_job(job.job_id)

        # Verify job completed
        assert result_job.status == JobStatus.COMPLETED
        assert result_job.result == {"result": 84}
        assert result_job.started_at is not None
        assert result_job.completed_at is not None

    async def test_execute_job_not_found(self, worker: BackgroundWorker):
        """Test executing non-existent job."""
        with pytest.raises(ValueError, match="not found"):
            await worker.execute_job("nonexistent")

    async def test_execute_job_no_handler(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test executing job without registered handler."""
        job = job_manager.create_job("unregistered_tool", {})

        with pytest.raises(RuntimeError, match="No handler registered"):
            await worker.execute_job(job.job_id)

    async def test_execute_job_already_running(
        self, worker: BackgroundWorker, job_manager: JobManager
    ):
        """Test executing job that's already running."""
        job = job_manager.create_job("test_tool", {})
        job.mark_running()
        job_manager.save_job(job)

        with pytest.raises(ValueError, match="already running"):
            await worker.execute_job(job.job_id)

    async def test_execute_job_terminal_state(
        self, worker: BackgroundWorker, job_manager: JobManager
    ):
        """Test executing job in terminal state."""
        job = job_manager.create_job("test_tool", {})
        job.mark_completed({"result": "done"})
        job_manager.save_job(job)

        with pytest.raises(ValueError, match="terminal state"):
            await worker.execute_job(job.job_id)

    async def test_execute_job_timeout(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test job execution timeout."""

        async def slow_handler():
            await asyncio.sleep(10)
            return {"result": "too slow"}

        worker.register_tool("slow_tool", slow_handler)

        # Create job
        job = job_manager.create_job("slow_tool", {})

        # Execute with short timeout
        result_job = await worker.execute_job(job.job_id, timeout=0.1)

        # Verify job failed with timeout
        assert result_job.status == JobStatus.FAILED
        assert "timed out" in result_job.error.lower()

    async def test_execute_job_error(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test job execution with error."""

        async def failing_handler():
            raise ValueError("Something went wrong")

        worker.register_tool("failing_tool", failing_handler)

        # Create job
        job = job_manager.create_job("failing_tool", {})

        # Execute job
        result_job = await worker.execute_job(job.job_id)

        # Verify job failed
        assert result_job.status == JobStatus.FAILED
        assert "ValueError" in result_job.error
        assert "Something went wrong" in result_job.error

    async def test_submit_job(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test submitting a job for background execution."""

        async def test_handler(value: int):
            await asyncio.sleep(0.1)
            return {"result": value * 2}

        worker.register_tool("test_tool", test_handler)

        # Create job
        job = job_manager.create_job("test_tool", {"value": 42})

        # Submit job
        task = await worker.submit_job(job.job_id)

        # Verify task is running
        assert worker.is_running(job.job_id)
        assert worker.running_count == 1
        assert worker.available_slots == 2

        # Wait for completion
        result_job = await task

        # Verify job completed
        assert result_job.status == JobStatus.COMPLETED
        assert result_job.result == {"result": 84}
        assert not worker.is_running(job.job_id)
        assert worker.running_count == 0

    async def test_submit_job_already_running(
        self, worker: BackgroundWorker, job_manager: JobManager
    ):
        """Test submitting job that's already running."""

        async def slow_handler():
            await asyncio.sleep(1)
            return {"result": "done"}

        worker.register_tool("slow_tool", slow_handler)

        # Create and submit job
        job = job_manager.create_job("slow_tool", {})
        task1 = await worker.submit_job(job.job_id)

        # Try to submit again
        with pytest.raises(ValueError, match="already running"):
            await worker.submit_job(job.job_id)

        # Clean up
        await task1

    async def test_cancel_job(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test cancelling a running job."""

        async def slow_handler():
            await asyncio.sleep(10)
            return {"result": "done"}

        worker.register_tool("slow_tool", slow_handler)

        # Create and submit job
        job = job_manager.create_job("slow_tool", {})
        task = await worker.submit_job(job.job_id)

        # Cancel job
        await asyncio.sleep(0.1)  # Let it start
        cancelled = await worker.cancel_job(job.job_id)

        assert cancelled is True
        assert not worker.is_running(job.job_id)

        # Verify job was marked as cancelled
        updated_job = job_manager.get_job(job.job_id)
        assert updated_job.status == JobStatus.CANCELLED

        # Task should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_cancel_job_not_running(self, worker: BackgroundWorker):
        """Test cancelling job that's not running."""
        cancelled = await worker.cancel_job("nonexistent")
        assert cancelled is False

    async def test_wait_for_job(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test waiting for a running job."""

        async def test_handler():
            await asyncio.sleep(0.1)
            return {"result": "done"}

        worker.register_tool("test_tool", test_handler)

        # Create and submit job
        job = job_manager.create_job("test_tool", {})
        await worker.submit_job(job.job_id)

        # Wait for job
        result_job = await worker.wait_for_job(job.job_id)

        assert result_job.status == JobStatus.COMPLETED
        assert result_job.result == {"result": "done"}

    async def test_wait_for_job_not_running(
        self, worker: BackgroundWorker, job_manager: JobManager
    ):
        """Test waiting for job that's not running."""
        job = job_manager.create_job("test_tool", {})

        # Wait should return current state
        result_job = await worker.wait_for_job(job.job_id)
        assert result_job.status == JobStatus.PENDING

    async def test_wait_for_job_timeout(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test waiting for job with timeout."""

        async def slow_handler():
            await asyncio.sleep(10)
            return {"result": "done"}

        worker.register_tool("slow_tool", slow_handler)

        # Create and submit job
        job = job_manager.create_job("slow_tool", {})
        await worker.submit_job(job.job_id)

        # Wait with short timeout
        with pytest.raises(asyncio.TimeoutError):
            await worker.wait_for_job(job.job_id, timeout=0.1)

        # Clean up
        await worker.cancel_job(job.job_id)

    async def test_concurrency_limit(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test that worker respects max_workers limit."""

        async def test_handler():
            await asyncio.sleep(0.2)
            return {"result": "done"}

        worker.register_tool("test_tool", test_handler)

        # Submit max_workers jobs
        jobs = []
        for _ in range(worker.max_workers):
            job = job_manager.create_job("test_tool", {})
            task = await worker.submit_job(job.job_id)
            jobs.append((job.job_id, task))

        # All should be running
        assert worker.running_count == worker.max_workers
        assert worker.available_slots == 0

        # Submit one more - should wait for slot
        extra_job = job_manager.create_job("test_tool", {})
        extra_task = await worker.submit_job(extra_job.job_id)

        # Worker is at capacity
        assert worker.running_count == worker.max_workers + 1  # +1 waiting
        assert worker.available_slots < 0 or worker.running_count <= worker.max_workers

        # Wait for all to complete
        await asyncio.gather(*[task for _, task in jobs], extra_task)

        # All should be done
        assert worker.running_count == 0
        assert worker.available_slots == worker.max_workers

    async def test_shutdown_wait(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test shutdown waiting for jobs to complete."""

        async def test_handler():
            await asyncio.sleep(0.2)
            return {"result": "done"}

        worker.register_tool("test_tool", test_handler)

        # Submit jobs
        jobs = []
        for _ in range(3):
            job = job_manager.create_job("test_tool", {})
            await worker.submit_job(job.job_id)
            jobs.append(job)

        # Shutdown without cancelling
        await worker.shutdown(cancel_running=False)

        # All jobs should be completed
        for job in jobs:
            updated = job_manager.get_job(job.job_id)
            assert updated.status == JobStatus.COMPLETED

        assert worker.running_count == 0

    async def test_shutdown_cancel(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test shutdown cancelling running jobs."""

        async def slow_handler():
            await asyncio.sleep(10)
            return {"result": "done"}

        worker.register_tool("slow_tool", slow_handler)

        # Submit jobs
        jobs = []
        for _ in range(3):
            job = job_manager.create_job("slow_tool", {})
            await worker.submit_job(job.job_id)
            jobs.append(job)

        await asyncio.sleep(0.1)  # Let them start

        # Shutdown with cancelling
        await worker.shutdown(cancel_running=True)

        # All jobs should be cancelled
        for job in jobs:
            updated = job_manager.get_job(job.job_id)
            assert updated.status == JobStatus.CANCELLED

        assert worker.running_count == 0

    async def test_properties(self, worker: BackgroundWorker, job_manager: JobManager):
        """Test worker properties."""
        assert worker.running_count == 0
        assert worker.available_slots == worker.max_workers

        async def test_handler():
            await asyncio.sleep(0.2)
            return {"result": "done"}

        worker.register_tool("test_tool", test_handler)

        # Submit one job
        job = job_manager.create_job("test_tool", {})
        task = await worker.submit_job(job.job_id)

        assert worker.running_count == 1
        assert worker.available_slots == worker.max_workers - 1
        assert worker.is_running(job.job_id)
        assert not worker.is_running("nonexistent")

        await task
