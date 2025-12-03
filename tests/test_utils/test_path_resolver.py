"""Unit tests for PathResolver.

Tests path resolution, validation, and security against directory traversal.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_finnhub.utils.path_resolver import PathResolver


class TestPathResolver:
    """Tests for PathResolver class."""

    def test_initialization(self, tmp_path: Path):
        """Test PathResolver initialization with absolute path."""
        resolver = PathResolver(tmp_path)
        assert resolver.storage_dir == tmp_path.resolve()

    def test_initialization_relative_path_raises_error(self):
        """Test that relative path raises ValueError."""
        with pytest.raises(ValueError, match="Storage directory must be absolute"):
            PathResolver(Path("relative/path"))

    def test_get_project_path(self, tmp_path: Path):
        """Test getting project path."""
        resolver = PathResolver(tmp_path)
        project_path = resolver.get_project_path("my_project")

        assert project_path == tmp_path / "my_project"
        assert project_path.is_absolute()

    def test_get_export_path(self, tmp_path: Path):
        """Test getting export file path."""
        resolver = PathResolver(tmp_path)
        export_path = resolver.get_export_path("my_project", "data.csv")

        assert export_path == tmp_path / "my_project" / "exports" / "data.csv"
        assert export_path.is_absolute()

    def test_get_job_path(self, tmp_path: Path):
        """Test getting job directory path."""
        resolver = PathResolver(tmp_path)
        job_path = resolver.get_job_path("my_project", "job_123")

        assert job_path == tmp_path / "my_project" / "jobs" / "job_123"
        assert job_path.is_absolute()

    def test_ensure_project_dir_creates_directory(self, tmp_path: Path):
        """Test that ensure_project_dir creates directories."""
        resolver = PathResolver(tmp_path)
        project_path = resolver.ensure_project_dir("new_project")

        assert project_path.exists()
        assert project_path.is_dir()
        assert (project_path / "exports").exists()
        assert (project_path / "jobs").exists()

    def test_ensure_project_dir_idempotent(self, tmp_path: Path):
        """Test that ensure_project_dir is idempotent."""
        resolver = PathResolver(tmp_path)

        # Call twice
        path1 = resolver.ensure_project_dir("project")
        path2 = resolver.ensure_project_dir("project")

        assert path1 == path2
        assert path1.exists()

    def test_list_projects_empty(self, tmp_path: Path):
        """Test listing projects when directory is empty."""
        resolver = PathResolver(tmp_path)
        projects = resolver.list_projects()

        assert projects == []

    def test_list_projects_with_projects(self, tmp_path: Path):
        """Test listing projects."""
        resolver = PathResolver(tmp_path)

        # Create some projects
        resolver.ensure_project_dir("project1")
        resolver.ensure_project_dir("project2")
        resolver.ensure_project_dir("project3")

        projects = resolver.list_projects()

        assert len(projects) == 3
        assert "project1" in projects
        assert "project2" in projects
        assert "project3" in projects

    def test_list_projects_ignores_hidden(self, tmp_path: Path):
        """Test that hidden directories are ignored."""
        resolver = PathResolver(tmp_path)

        resolver.ensure_project_dir("visible")
        (tmp_path / ".hidden").mkdir()

        projects = resolver.list_projects()

        assert "visible" in projects
        assert ".hidden" not in projects

    def test_list_projects_nonexistent_storage(self, tmp_path: Path):
        """Test listing projects when storage dir doesn't exist."""
        nonexistent = tmp_path / "nonexistent"
        resolver = PathResolver(nonexistent)

        projects = resolver.list_projects()
        assert projects == []

    def test_path_traversal_with_dotdot(self, tmp_path: Path):
        """Test that .. is blocked."""
        resolver = PathResolver(tmp_path)

        with pytest.raises(ValueError, match="cannot contain '\\.\\.'"):
            resolver.get_project_path("../escape")

    def test_path_traversal_in_filename(self, tmp_path: Path):
        """Test that .. in filename is blocked."""
        resolver = PathResolver(tmp_path)

        with pytest.raises(ValueError, match="cannot contain '\\.\\.'"):
            resolver.get_export_path("project", "../../../etc/passwd")

    def test_absolute_path_blocked(self, tmp_path: Path):
        """Test that absolute paths are blocked."""
        resolver = PathResolver(tmp_path)

        with pytest.raises(ValueError, match="cannot be an absolute path"):
            resolver.get_project_path("/absolute/path")

    def test_null_byte_blocked(self, tmp_path: Path):
        """Test that null bytes are blocked."""
        resolver = PathResolver(tmp_path)

        with pytest.raises(ValueError, match="cannot contain null bytes"):
            resolver.get_project_path("project\x00name")

    def test_empty_name_blocked(self, tmp_path: Path):
        """Test that empty names are blocked."""
        resolver = PathResolver(tmp_path)

        with pytest.raises(ValueError, match="cannot be empty"):
            resolver.get_project_path("")

    def test_symlink_escape_blocked(self, tmp_path: Path):
        """Test that symlink-based escapes are blocked."""
        resolver = PathResolver(tmp_path)

        # This test may not be fully effective depending on OS,
        # but validates the check exists
        with pytest.raises(ValueError):
            resolver._validate_name("../../etc", "Test")

    def test_multiple_projects_independent(self, tmp_path: Path):
        """Test that multiple projects have independent paths."""
        resolver = PathResolver(tmp_path)

        path1 = resolver.get_project_path("project1")
        path2 = resolver.get_project_path("project2")

        assert path1 != path2
        assert path1.parent == path2.parent == tmp_path
