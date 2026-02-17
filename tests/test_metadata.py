"""Tests for metadata.py module."""

from llama_index.core import Document

from fragmenter.rag.metadata import create_metadata_extractor, find_git_root


class TestFindGitRoot:
    """Tests for find_git_root function."""

    def test_find_git_root_from_repo(self, git_repo):
        """Test finding git root from inside repository."""
        # Test from root
        assert find_git_root(git_repo) == git_repo

        # Test from subdirectory
        src_dir = git_repo / "src"
        assert find_git_root(src_dir) == git_repo

    def test_find_git_root_no_repo(self, temp_dir):
        """Test behavior when no git repo is found."""
        result = find_git_root(temp_dir)
        assert result is None

    def test_find_git_root_with_file(self, git_repo):
        """Test finding git root starting from a file."""
        file_path = git_repo / "src" / "main.py"
        assert find_git_root(file_path) == git_repo


class TestCreateMetadataExtractor:
    """Tests for create_metadata_extractor function."""

    def test_metadata_extractor_with_git_repo(self, git_repo):
        """Test metadata extraction inside git repository."""
        extractor = create_metadata_extractor(project_root=git_repo)

        # Create a document
        file_path = git_repo / "src" / "main.py"
        doc = Document(text="print('hello')", metadata={"file_path": str(file_path)})

        # Extract metadata
        result = extractor(doc)

        # Verify metadata was added
        assert "repository_path" in result.metadata
        assert "relative_path" in result.metadata
        assert "is_code" in result.metadata
        assert "is_documentation" in result.metadata
        assert result.metadata["is_code"] is True
        assert result.metadata["relative_path"] == "src/main.py"

    def test_metadata_extractor_without_git_repo(self, temp_dir):
        """Test metadata extraction outside git repository."""
        # Create a file without git repo
        file_path = temp_dir / "test.py"
        file_path.write_text("print('test')")

        extractor = create_metadata_extractor(project_root=temp_dir)

        doc = Document(text="print('test')", metadata={"file_path": str(file_path)})

        result = extractor(doc)

        # Should still have metadata but no repository_path
        assert "repository_path" not in result.metadata
        assert "relative_path" in result.metadata
        assert "is_code" in result.metadata

    def test_metadata_extractor_file_type_detection(self, temp_dir):
        """Test file type categorization."""
        extractor = create_metadata_extractor(project_root=temp_dir)

        # Test code file
        code_doc = Document(
            text="code", metadata={"file_path": str(temp_dir / "test.cpp")}
        )
        result = extractor(code_doc)
        assert result.metadata["is_code"] is True
        assert result.metadata["is_documentation"] is False

        # Test documentation file
        doc_doc = Document(
            text="docs", metadata={"file_path": str(temp_dir / "README.md")}
        )
        result = extractor(doc_doc)
        assert result.metadata["is_documentation"] is True

        # Test config file
        config_doc = Document(
            text="config", metadata={"file_path": str(temp_dir / "config.yaml")}
        )
        result = extractor(config_doc)
        assert result.metadata["is_code"] is False
        assert result.metadata["is_documentation"] is False

    def test_metadata_extractor_no_file_path(self, temp_dir):
        """Test behavior when document has no file_path metadata."""
        extractor = create_metadata_extractor(project_root=temp_dir)

        doc = Document(text="test content")
        result = extractor(doc)

        # Should return document unchanged
        assert result == doc
