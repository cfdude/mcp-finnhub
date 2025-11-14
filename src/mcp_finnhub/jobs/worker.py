"""Background worker for executing jobs asynchronously."""

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from mcp_finnhub.jobs.manager import JobManager
from mcp_finnhub.jobs.models import Job, JobStatus

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """Execute background jobs asynchronously with concurrency limits."""

    def __init__(
        self,
        job_manager: JobManager,
        max_workers: int = 5,
        default_timeout: float = 300.0,
    ):
        """Initialize background worker.

        Args:
            job_manager: JobManager instance for job persistence
            max_workers: Maximum number of concurrent jobs
            default_timeout: Default job timeout in seconds
        """
        self.job_manager = job_manager
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self._semaphore = asyncio.Semaphore(max_workers)
        self._running_tasks: dict[str, asyncio.Task[Any]] = {}
        self._tool_handlers: dict[str, Callable[..., Awaitable[dict[str, Any]]]] = {}
        self._shutdown = False

    def register_tool(
        self,
        tool_name: str,
        handler: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Register a tool handler function.

        Args:
            tool_name: Name of the tool
            handler: Async function that executes the tool
        """
        self._tool_handlers[tool_name] = handler
        logger.debug(f"Registered tool handler for {tool_name}")

    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool handler.

        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self._tool_handlers:
            del self._tool_handlers[tool_name]
            logger.debug(f"Unregistered tool handler for {tool_name}")

    async def execute_job(
        self,
        job_id: str,
        *,
        timeout: float | None = None,
    ) -> Job:
        """Execute a specific job by ID.

        Args:
            job_id: Job ID to execute
            timeout: Optional timeout override in seconds

        Returns:
            Updated job after execution

        Raises:
            ValueError: If job not found or already running
            RuntimeError: If tool handler not registered
        """
        # Get job
        job = self.job_manager.get_job(job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        # Check job status
        if job.status == JobStatus.RUNNING:
            raise ValueError(f"Job {job_id} is already running")
        if job.is_terminal:
            raise ValueError(f"Job {job_id} is already in terminal state: {job.status}")

        # Check tool handler registered
        if job.tool_name not in self._tool_handlers:
            raise RuntimeError(
                f"No handler registered for tool {job.tool_name}. "
                f"Available tools: {list(self._tool_handlers.keys())}"
            )

        # Get handler and timeout
        handler = self._tool_handlers[job.tool_name]
        job_timeout = timeout or self.default_timeout

        # Mark job as running
        job.mark_running(f"Executing {job.tool_name}")
        self.job_manager.save_job(job)

        try:
            # Execute with timeout and semaphore
            async with self._semaphore:
                logger.info(
                    f"Executing job {job_id} for tool {job.tool_name} (timeout: {job_timeout}s)"
                )
                result = await asyncio.wait_for(
                    handler(**job.params),
                    timeout=job_timeout,
                )

            # Mark job as completed
            job.mark_completed(result, "Job completed successfully")
            self.job_manager.save_job(job)
            logger.info(f"Job {job_id} completed successfully")

        except TimeoutError:
            # Job timed out
            error_msg = f"Job timed out after {job_timeout} seconds"
            job.mark_failed(error_msg)
            self.job_manager.save_job(job)
            logger.error(f"Job {job_id} timed out")

        except asyncio.CancelledError:
            # Job was cancelled
            job.mark_cancelled("Job was cancelled")
            self.job_manager.save_job(job)
            logger.warning(f"Job {job_id} was cancelled")
            raise

        except Exception as exc:
            # Job failed with error
            error_msg = f"{type(exc).__name__}: {exc}"
            job.mark_failed(error_msg)
            self.job_manager.save_job(job)
            logger.exception(f"Job {job_id} failed with error")

        return job

    async def submit_job(
        self,
        job_id: str,
        *,
        timeout: float | None = None,
    ) -> asyncio.Task[Job]:
        """Submit a job for background execution.

        Args:
            job_id: Job ID to execute
            timeout: Optional timeout override in seconds

        Returns:
            Asyncio task for the job execution

        Raises:
            ValueError: If job is already running
        """
        if job_id in self._running_tasks:
            raise ValueError(f"Job {job_id} is already running")

        # Create task for job execution
        task = asyncio.create_task(
            self.execute_job(job_id, timeout=timeout),
            name=f"job-{job_id}",
        )

        # Track running task
        self._running_tasks[job_id] = task

        # Remove from tracking when done
        def _on_done(t: asyncio.Task[Job]) -> None:
            if job_id in self._running_tasks:
                del self._running_tasks[job_id]

        task.add_done_callback(_on_done)

        logger.debug(f"Submitted job {job_id} for background execution")
        return task

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if job was cancelled, False if not running
        """
        if job_id not in self._running_tasks:
            logger.warning(f"Cannot cancel job {job_id}: not running")
            return False

        task = self._running_tasks[job_id]
        task.cancel()
        logger.info(f"Cancelled job {job_id}")

        with contextlib.suppress(asyncio.CancelledError):
            await task

        return True

    async def wait_for_job(self, job_id: str, *, timeout: float | None = None) -> Job:
        """Wait for a running job to complete.

        Args:
            job_id: Job ID to wait for
            timeout: Optional timeout in seconds

        Returns:
            Completed job

        Raises:
            ValueError: If job not running
            asyncio.TimeoutError: If wait times out
        """
        if job_id not in self._running_tasks:
            # Job not running, return current state
            job = self.job_manager.get_job(job_id)
            if job is None:
                raise ValueError(f"Job {job_id} not found")
            return job

        task = self._running_tasks[job_id]

        if timeout is not None:
            return await asyncio.wait_for(task, timeout=timeout)
        else:
            return await task

    async def shutdown(self, *, cancel_running: bool = False) -> None:
        """Shutdown the worker.

        Args:
            cancel_running: If True, cancel all running jobs
        """
        self._shutdown = True
        logger.info(f"Shutting down worker (running jobs: {len(self._running_tasks)})")

        if cancel_running:
            # Cancel all running tasks
            for job_id in list(self._running_tasks.keys()):
                await self.cancel_job(job_id)
        else:
            # Wait for all running tasks to complete
            if self._running_tasks:
                logger.info(f"Waiting for {len(self._running_tasks)} jobs to complete")
                await asyncio.gather(
                    *self._running_tasks.values(),
                    return_exceptions=True,
                )

        logger.info("Worker shutdown complete")

    @property
    def running_count(self) -> int:
        """Get count of currently running jobs."""
        return len(self._running_tasks)

    @property
    def available_slots(self) -> int:
        """Get count of available worker slots."""
        return self.max_workers - self.running_count

    def is_running(self, job_id: str) -> bool:
        """Check if a job is currently running.

        Args:
            job_id: Job ID to check

        Returns:
            True if job is running
        """
        return job_id in self._running_tasks
