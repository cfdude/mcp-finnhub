"""Unit tests for FileWriter."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from mcp_finnhub.utils.file_writer import FileWriter

if TYPE_CHECKING:
    from pathlib import Path


class TestFileWriter:
    """Tests for FileWriter class."""

    def test_write_json(self, tmp_path: Path):
        """Test writing JSON file."""
        writer = FileWriter()
        data = {"key": "value", "number": 42}
        output_file = tmp_path / "output.json"

        writer.write_json(data, output_file)

        assert output_file.exists()
        with output_file.open() as f:
            loaded = json.load(f)
        assert loaded == data

    def test_write_json_creates_parent_dirs(self, tmp_path: Path):
        """Test that parent directories are created."""
        writer = FileWriter()
        output_file = tmp_path / "subdir" / "nested" / "output.json"

        writer.write_json({"test": "data"}, output_file)

        assert output_file.exists()

    def test_write_csv(self, tmp_path: Path):
        """Test writing CSV file."""
        writer = FileWriter()
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        output_file = tmp_path / "output.csv"

        writer.write_csv(data, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "a,b" in content
        assert "1,2" in content
        assert "3,4" in content

    def test_write_csv_empty_raises_error(self, tmp_path: Path):
        """Test that empty data raises ValueError."""
        writer = FileWriter()
        with pytest.raises(ValueError, match="Cannot write empty data"):
            writer.write_csv([], tmp_path / "output.csv")

    def test_append_csv(self, tmp_path: Path):
        """Test appending to CSV file."""
        writer = FileWriter()
        output_file = tmp_path / "output.csv"

        # Write initial data
        writer.write_csv([{"x": 1, "y": 2}], output_file)

        # Append more data
        writer.append_csv([{"x": 3, "y": 4}], output_file)

        content = output_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows

    def test_append_csv_empty_raises_error(self, tmp_path: Path):
        """Test that appending empty data raises ValueError."""
        writer = FileWriter()
        with pytest.raises(ValueError, match="Cannot append empty data"):
            writer.append_csv([], tmp_path / "output.csv")
