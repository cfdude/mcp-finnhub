"""Job manager for background task lifecycle management.

Manages job persistence, status tracking, and cleanup with JSON file storage.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from mcp_finnhub.jobs.models import Job, JobStatus

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class JobManager:
    """Manage background job lifecycle with file persistence.

    Jobs are stored as JSON files in a dedicated directory with atomic writes
    to prevent corruption. Supports job creation, status updates, result storage,
    and automatic cleanup of old completed jobs.

    Example:
        >>> manager = JobManager(Path("/data/jobs"))
        >>> job = manager.create_job("fetch_data", {"symbol": "AAPL"})
        >>> manager.update_job(job.job_id, status=JobStatus.RUNNING)
        >>> manager.complete_job(job.job_id, {"data": [...]})
    """

    def __init__(self, jobs_dir: Path):
        """Initialize job manager.

        Args:
            jobs_dir: Directory for storing job files
        """
        self.jobs_dir = jobs_dir
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def _job_file(self, job_id: str) -> Path:
        """Get path to job file."""
        return self.jobs_dir / f"{job_id}.json"

    def _load_job(self, job_id: str) -> Job | None:
        """Load job from disk.

        Args:
            job_id: Job identifier

        Returns:
            Job instance or None if not found
        """
        job_file = self._job_file(job_id)
        if not job_file.exists():
            return None

        try:
            with job_file.open() as f:
                data = json.load(f)
            return Job(**data)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error(f"Failed to load job {job_id}: {exc}")
            return None

    def _save_job(self, job: Job) -> None:
        """Save job to disk atomically.

        Args:
            job: Job to save
        """
        job_file = self._job_file(job.job_id)
        temp_file = job_file.with_suffix(".tmp")

        try:
            # Write to temp file first
            with temp_file.open("w") as f:
                json.dump(job.model_dump(mode="json"), f, indent=2)

            # Atomic rename
            temp_file.replace(job_file)
        except Exception as exc:
            logger.error(f"Failed to save job {job.job_id}: {exc}")
            if temp_file.exists():
                temp_file.unlink()
            raise

    def save_job(self, job: Job) -> None:
        """Save a job object to disk.

        This is useful when you've modified a job object in-place
        (e.g., via mark_running(), mark_completed()) and want to persist it.

        Args:
            job: Job object to save
        """
        self._save_job(job)

    def create_job(
        self,
        tool_name: str,
        params: dict[str, Any] | None = None,
    ) -> Job:
        """Create a new job.

        Args:
            tool_name: Name of tool to execute
            params: Tool parameters

        Returns:
            Created job instance

        Example:
            >>> job = manager.create_job("fetch_candles", {"symbol": "AAPL"})
        """
        job = Job(
            job_id=str(uuid.uuid4()),
            tool_name=tool_name,
            params=params or {},
            status=JobStatus.PENDING,
        )
        self._save_job(job)
        logger.info(f"Created job {job.job_id} for tool {tool_name}")
        return job

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job instance or None if not found
        """
        return self._load_job(job_id)

    def update_job(
        self,
        job_id: str,
        *,
        status: JobStatus | None = None,
        progress: int | None = None,
        message: str | None = None,
    ) -> Job | None:
        """Update job status and metadata.

        Args:
            job_id: Job identifier
            status: New status (if provided)
            progress: Progress percentage (if provided)
            message: Status message (if provided)

        Returns:
            Updated job or None if not found

        Example:
            >>> manager.update_job(job_id, progress=50, message="Processing...")
        """
        job = self._load_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found for update")
            return None

        if status is not None:
            job.status = status
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.utcnow()
            elif (
                status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}
                and not job.completed_at
            ):
                job.completed_at = datetime.utcnow()

        if progress is not None:
            job.progress = max(0, min(100, progress))

        if message is not None:
            job.message = message

        self._save_job(job)
        return job

    def complete_job(
        self,
        job_id: str,
        result: dict[str, Any],
        message: str = "",
    ) -> Job | None:
        """Mark job as completed with result.

        Args:
            job_id: Job identifier
            result: Job result data
            message: Optional completion message

        Returns:
            Updated job or None if not found
        """
        job = self._load_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found for completion")
            return None

        job.mark_completed(result, message)
        self._save_job(job)
        logger.info(f"Completed job {job_id}")
        return job

    def fail_job(
        self,
        job_id: str,
        error: str,
        message: str = "",
    ) -> Job | None:
        """Mark job as failed with error.

        Args:
            job_id: Job identifier
            error: Error message/details
            message: Optional failure message

        Returns:
            Updated job or None if not found
        """
        job = self._load_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found for failure")
            return None

        job.mark_failed(error, message)
        self._save_job(job)
        logger.error(f"Failed job {job_id}: {error}")
        return job

    def cancel_job(
        self,
        job_id: str,
        message: str = "",
    ) -> Job | None:
        """Cancel a job.

        Args:
            job_id: Job identifier
            message: Optional cancellation message

        Returns:
            Updated job or None if not found
        """
        job = self._load_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found for cancellation")
            return None

        if job.is_terminal:
            logger.warning(f"Cannot cancel job {job_id} in terminal state {job.status}")
            return job

        job.mark_cancelled(message)
        self._save_job(job)
        logger.info(f"Cancelled job {job_id}")
        return job

    def list_jobs(
        self,
        status: JobStatus | None = None,
        limit: int | None = None,
    ) -> list[Job]:
        """List jobs, optionally filtered by status.

        Args:
            status: Filter by status (if provided)
            limit: Maximum number of jobs to return (if provided)

        Returns:
            List of jobs, sorted by creation time (newest first)

        Example:
            >>> running_jobs = manager.list_jobs(status=JobStatus.RUNNING)
            >>> recent_jobs = manager.list_jobs(limit=10)
        """
        jobs: list[Job] = []

        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with job_file.open() as f:
                    data = json.load(f)
                job = Job(**data)

                if status is None or job.status == status:
                    jobs.append(job)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning(f"Failed to load job from {job_file}: {exc}")
                continue

        # Sort by creation time, newest first
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        if limit is not None:
            jobs = jobs[:limit]

        return jobs

    def delete_job(self, job_id: str) -> bool:
        """Delete a job.

        Args:
            job_id: Job identifier

        Returns:
            True if job was deleted, False if not found
        """
        job_file = self._job_file(job_id)
        if not job_file.exists():
            return False

        try:
            job_file.unlink()
            logger.info(f"Deleted job {job_id}")
            return True
        except OSError as exc:
            logger.error(f"Failed to delete job {job_id}: {exc}")
            return False

    def cleanup_old_jobs(self, older_than: timedelta) -> int:
        """Clean up old completed jobs.

        Args:
            older_than: Delete jobs completed before this duration ago

        Returns:
            Number of jobs deleted

        Example:
            >>> # Delete jobs completed more than 24 hours ago
            >>> deleted = manager.cleanup_old_jobs(timedelta(hours=24))
        """
        cutoff = datetime.utcnow() - older_than
        deleted = 0

        for job in self.list_jobs():
            if (
                job.is_terminal
                and job.completed_at is not None
                and job.completed_at < cutoff
                and self.delete_job(job.job_id)
            ):
                deleted += 1

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old jobs")

        return deleted


__all__ = ["JobManager"]
