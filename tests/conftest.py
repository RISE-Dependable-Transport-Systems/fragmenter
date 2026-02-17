"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path

import pytest
from llama_index.core import Document


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        Document(
            text="This is a test document with enough content to be meaningful.",
            metadata={
                "file_path": "test.py",
                "file_type": ".py",
                "is_code": True,
            },
        ),
        Document(
            text="# Header\n\nThis is markdown content with a header.",
            metadata={
                "file_path": "test.md",
                "file_type": ".md",
                "is_documentation": True,
            },
        ),
    ]


@pytest.fixture
def git_repo(temp_dir):
    """Create a mock git repository."""
    git_dir = temp_dir / ".git"
    git_dir.mkdir()

    # Create some files
    (temp_dir / "README.md").write_text("# Test Repo")
    code_dir = temp_dir / "src"
    code_dir.mkdir()
    (code_dir / "main.py").write_text("print('hello')")

    return temp_dir
