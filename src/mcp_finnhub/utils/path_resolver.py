"""Path resolution utilities for project and file management.

Provides secure path handling for project directories, exports, and job files
with protection against directory traversal attacks.
"""

from __future__ import annotations

from pathlib import Path


class PathResolver:
    """Resolve and manage paths for projects, exports, and jobs.

    All paths are resolved relative to a storage directory root, with
    validation to prevent directory traversal attacks.

    Example:
        >>> resolver = PathResolver(Path("/data/finnhub"))
        >>> project_path = resolver.get_project_path("my_project")
        >>> export_path = resolver.get_export_path("my_project", "quotes.csv")
    """

    def __init__(self, storage_dir: Path):
        """Initialize PathResolver with storage directory.

        Args:
            storage_dir: Root directory for all data storage

        Raises:
            ValueError: If storage_dir is not absolute
        """
        if not storage_dir.is_absolute():
            raise ValueError(f"Storage directory must be absolute: {storage_dir}")

        self.storage_dir = storage_dir.resolve()

    def get_project_path(self, project_name: str) -> Path:
        """Get the directory path for a project.

        Args:
            project_name: Name of the project

        Returns:
            Absolute path to project directory

        Raises:
            ValueError: If project_name contains path traversal attempts

        Example:
            >>> resolver = PathResolver(Path("/data"))
            >>> resolver.get_project_path("stocks")
            PosixPath('/data/stocks')
        """
        self._validate_name(project_name, "Project name")
        return self.storage_dir / project_name

    def get_export_path(self, project_name: str, filename: str) -> Path:
        """Get the path for an export file within a project.

        Args:
            project_name: Name of the project
            filename: Name of the export file

        Returns:
            Absolute path to export file

        Raises:
            ValueError: If project_name or filename contains path traversal attempts

        Example:
            >>> resolver = PathResolver(Path("/data"))
            >>> resolver.get_export_path("stocks", "quotes.csv")
            PosixPath('/data/stocks/exports/quotes.csv')
        """
        self._validate_name(project_name, "Project name")
        self._validate_name(filename, "Filename")

        project_path = self.get_project_path(project_name)
        exports_dir = project_path / "exports"
        return exports_dir / filename

    def get_job_path(self, project_name: str, job_id: str) -> Path:
        """Get the directory path for a background job.

        Args:
            project_name: Name of the project
            job_id: Unique job identifier

        Returns:
            Absolute path to job directory

        Raises:
            ValueError: If project_name or job_id contains path traversal attempts

        Example:
            >>> resolver = PathResolver(Path("/data"))
            >>> resolver.get_job_path("stocks", "job_123")
            PosixPath('/data/stocks/jobs/job_123')
        """
        self._validate_name(project_name, "Project name")
        self._validate_name(job_id, "Job ID")

        project_path = self.get_project_path(project_name)
        jobs_dir = project_path / "jobs"
        return jobs_dir / job_id

    def ensure_project_dir(self, project_name: str) -> Path:
        """Ensure project directory exists, creating if necessary.

        Creates the project directory and standard subdirectories:
        - exports/
        - jobs/

        Args:
            project_name: Name of the project

        Returns:
            Absolute path to project directory

        Raises:
            ValueError: If project_name contains path traversal attempts

        Example:
            >>> resolver = PathResolver(Path("/data"))
            >>> project_path = resolver.ensure_project_dir("stocks")
            >>> project_path.exists()
            True
        """
        project_path = self.get_project_path(project_name)

        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories
        (project_path / "exports").mkdir(exist_ok=True)
        (project_path / "jobs").mkdir(exist_ok=True)

        return project_path

    def list_projects(self) -> list[str]:
        """List all project names in the storage directory.

        Returns:
            List of project names (directory names in storage_dir)

        Example:
            >>> resolver = PathResolver(Path("/data"))
            >>> resolver.list_projects()
            ['stocks', 'crypto', 'forex']
        """
        if not self.storage_dir.exists():
            return []

        return [
            item.name
            for item in self.storage_dir.iterdir()
            if item.is_dir() and not item.name.startswith(".")
        ]

    def _validate_name(self, name: str, field_name: str) -> None:
        """Validate that a name doesn't contain path traversal attempts.

        Args:
            name: Name to validate
            field_name: Name of the field for error messages

        Raises:
            ValueError: If name contains invalid characters or path traversal
        """
        if not name:
            raise ValueError(f"{field_name} cannot be empty")

        # Check for path traversal attempts
        if ".." in name:
            raise ValueError(
                f"{field_name} cannot contain '..': {name}"
            )

        # Check for absolute paths
        if name.startswith("/") or name.startswith("\\"):
            raise ValueError(
                f"{field_name} cannot be an absolute path: {name}"
            )

        # Check for null bytes
        if "\x00" in name:
            raise ValueError(
                f"{field_name} cannot contain null bytes"
            )

        # Ensure the resolved path stays within storage_dir
        try:
            test_path = (self.storage_dir / name).resolve()
            if not str(test_path).startswith(str(self.storage_dir)):
                raise ValueError(
                    f"{field_name} would escape storage directory: {name}"
                )
        except (ValueError, OSError) as e:
            raise ValueError(
                f"{field_name} contains invalid characters: {name}"
            ) from e


__all__ = ["PathResolver"]
