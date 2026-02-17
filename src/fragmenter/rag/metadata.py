"""Metadata extraction utilities for RAG ingestion.

This module provides utilities for extracting enhanced metadata from source files,
including repository detection, path normalization, and file categorization.
"""

from pathlib import Path

from llama_index.core import Document
from loguru import logger

# File type categorization constants
CODE_EXTENSIONS = {
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".c",
    ".cc",
    ".java",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".scala",
    ".rb",
    ".php",
    ".cs",
    ".dts",
    ".sh",
    ".bash",
    ".xml",
    ".ui",
}
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".pdf"}


def find_git_root(file_path: Path, stop_at: Path | None = None) -> Path | None:
    """Find the git repository root for a given file.

    Args:
        file_path: Path to a file or directory
        stop_at: Optional path to stop searching at (e.g., data directory).
                 Won't search beyond this directory.

    Returns:
        Path to git repository root, or None if not in a git repo
    """
    current = file_path if file_path.is_dir() else file_path.parent

    # Walk up the directory tree looking for .git
    for parent in [current, *current.parents]:
        # Check for .git before applying stop conditions
        # This allows detecting .git in the stop_at directory itself
        if (parent / ".git").exists():
            return parent

        # Stop if we've reached or passed the boundary
        if stop_at and parent == stop_at:
            break
        if stop_at and not parent.is_relative_to(stop_at):
            break

    return None


def create_metadata_extractor(project_root: Path):
    """Create a metadata extractor function for SimpleDirectoryReader.

    Args:
        project_root: Project root directory for calculating relative paths

    Returns:
        A metadata extraction function compatible with SimpleDirectoryReader
    """

    def metadata_extractor(file_path_or_doc: str | Document) -> dict | Document:
        """Extract enhanced metadata including relative paths and categorization.

        For files in git repositories:
            - Uses repo root as project_root
            - Paths are relative to repo (e.g., "main.cpp", "WayWise/autopilot/...")

        For files outside repositories (docs, papers, etc.):
            - Uses data_dir as project_root
            - Paths are relative to data_dir (e.g., "docs/file.md", "library/paper.pdf")
        """
        is_document = hasattr(file_path_or_doc, "metadata")
        if is_document:
            file_path = file_path_or_doc.metadata.get("file_path")
            if not file_path:
                return file_path_or_doc
        else:
            file_path = file_path_or_doc

        file_path_abs = Path(file_path).resolve()

        # Detect if file is in a git repository (but don't search beyond data dir)
        git_root = find_git_root(file_path_abs, stop_at=project_root)

        if git_root:
            # File is in a repo - use repo root as project root
            effective_project_root = git_root
            repo_name = git_root.name
        else:
            # File is not in a repo - use data_dir as project root
            effective_project_root = project_root
            repo_name = None

        # Calculate relative path from the effective project root
        try:
            relative_path = file_path_abs.relative_to(effective_project_root)
        except ValueError:
            # File is outside both repo and data_dir (shouldn't happen)
            relative_path = file_path_abs
            logger.warning(
                f"File {file_path_abs} is outside project root {effective_project_root}"
            )

        # Extract file type and categorization
        suffix = file_path_abs.suffix.lower()
        file_name = file_path_abs.name
        is_code = suffix in CODE_EXTENSIONS
        is_doc = suffix in DOC_EXTENSIONS or file_name in ("README", "LICENSE")

        # Calculate directory depth
        depth = len(relative_path.parts) - 1

        metadata = {
            # Only store relative paths - no absolute paths
            "file_path": str(file_path_abs),
            "file_name": file_name,
            "relative_path": str(relative_path),
            "relative_directory": str(relative_path.parent),
            "depth": depth,
            "file_type": suffix,
            "is_code": is_code,
            "is_documentation": is_doc,
        }

        # Add repo information if applicable
        if repo_name:
            metadata["repository_path"] = str(git_root)
            metadata["repository"] = repo_name
            metadata["in_repository"] = True
        else:
            metadata["in_repository"] = False

        if is_document:
            file_path_or_doc.metadata.update(metadata)
            return file_path_or_doc

        return metadata

    return metadata_extractor
