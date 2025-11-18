"""Tests for finnhub_project_list tool."""

from __future__ import annotations

import pytest

from mcp_finnhub.server import ServerContext
from mcp_finnhub.tools.project_create import finnhub_project_create
from mcp_finnhub.tools.project_list import finnhub_project_list


class TestProjectList:
    """Test finnhub_project_list tool."""

    @pytest.fixture
    def context(self, test_config):
        """Create server context."""
        return ServerContext(test_config)

    @pytest.mark.asyncio
    async def test_list_empty_projects(self, context):
        """Test listing projects when none exist."""
        result = await finnhub_project_list(context, "list")

        assert "error" not in result
        assert result["projects"] == []
        assert result["total_projects"] == 0

    @pytest.mark.asyncio
    async def test_list_single_project(self, context):
        """Test listing projects with one project."""
        # Create a project
        await finnhub_project_create(context, "create", project="test-project")

        # List projects
        result = await finnhub_project_list(context, "list")

        assert "error" not in result
        assert result["total_projects"] == 1
        assert len(result["projects"]) == 1

        project = result["projects"][0]
        assert project["name"] == "test-project"
        assert "path" in project
        assert "created_at" in project
        assert project["subdirectories"] == [
            "candles",
            "quotes",
            "news",
            "fundamentals",
            "technical",
            "jobs",
        ]
        assert "file_counts" in project
        assert "total_files" in project
        assert "total_size" in project

    @pytest.mark.asyncio
    async def test_list_multiple_projects(self, context):
        """Test listing multiple projects."""
        # Create multiple projects
        await finnhub_project_create(context, "create", project="project-1")
        await finnhub_project_create(context, "create", project="project-2")
        await finnhub_project_create(context, "create", project="project-3")

        # List projects
        result = await finnhub_project_list(context, "list")

        assert "error" not in result
        assert result["total_projects"] == 3
        assert len(result["projects"]) == 3

        # Verify all projects are listed
        project_names = {p["name"] for p in result["projects"]}
        assert project_names == {"project-1", "project-2", "project-3"}

    @pytest.mark.asyncio
    async def test_list_projects_sorted_by_date(self, context):
        """Test projects are sorted by creation date (newest first)."""
        # Create projects in sequence
        await finnhub_project_create(context, "create", project="oldest")
        await finnhub_project_create(context, "create", project="middle")
        await finnhub_project_create(context, "create", project="newest")

        # List projects
        result = await finnhub_project_list(context, "list")

        # Should be sorted newest first
        project_names = [p["name"] for p in result["projects"]]
        assert project_names == ["newest", "middle", "oldest"]

    @pytest.mark.asyncio
    async def test_list_projects_unknown_operation(self, context):
        """Test unknown operation."""
        result = await finnhub_project_list(context, "delete")

        assert "error" in result
        assert result["error"]["code"] == "UNKNOWN_OPERATION"

    @pytest.mark.asyncio
    async def test_list_projects_file_counts(self, context, tmp_path):
        """Test file counts are accurate."""
        # Create a project
        await finnhub_project_create(context, "create", project="test-project")

        # Add some files to subdirectories
        project_dir = tmp_path / "test-project"
        (project_dir / "candles" / "data1.csv").write_text("test")
        (project_dir / "candles" / "data2.csv").write_text("test")
        (project_dir / "quotes" / "data1.csv").write_text("test")

        # List projects
        result = await finnhub_project_list(context, "list")

        project = result["projects"][0]
        assert project["file_counts"]["candles"] == 2
        assert project["file_counts"]["quotes"] == 1
        assert project["total_files"] == 3
