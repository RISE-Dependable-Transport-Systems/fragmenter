"""Tests for parsers.py module."""

from fragmenter.rag.parsers import (
    MIN_CHUNK_SIZE_CODE,
    MIN_CHUNK_SIZE_CONFIG,
    MIN_CHUNK_SIZE_DOCS,
    TypedDocumentReader,
)


class TestTypedDocumentReader:
    """Tests for TypedDocumentReader class."""

    def test_initialization_defaults(self):
        """Test initialization with default parameters."""
        reader = TypedDocumentReader()

        assert reader.min_chunk_size_code == MIN_CHUNK_SIZE_CODE
        assert reader.min_chunk_size_docs == MIN_CHUNK_SIZE_DOCS
        assert reader.min_chunk_size_config == MIN_CHUNK_SIZE_CONFIG

    def test_initialization_custom_sizes(self):
        """Test initialization with custom chunk sizes."""
        reader = TypedDocumentReader(
            min_chunk_size_code=200,
            min_chunk_size_docs=150,
            min_chunk_size_config=75,
        )

        assert reader.min_chunk_size_code == 200
        assert reader.min_chunk_size_docs == 150
        assert reader.min_chunk_size_config == 75

    def test_load_data_empty_file(self, temp_dir):
        """Test loading from empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")
        reader = TypedDocumentReader()
        documents = reader.load_data(test_file)

        assert isinstance(documents, list)
        assert len(documents) == 0

    def test_load_data_with_files(self, temp_dir):
        """Test loading from files of different types."""
        # Create test files
        py_file = temp_dir / "test.py"
        py_file.write_text("def hello():\n    print('hello')\n\n" * 20)

        md_file = temp_dir / "README.md"
        md_file.write_text("# Test\n\n" + "Content block 1.\n\nContent block 2. " * 50)

        reader = TypedDocumentReader()

        # Test Python file
        docs = reader.load_data(py_file, extra_info={"is_code": True})
        assert len(docs) > 0
        for doc in docs:
            assert doc.metadata["is_code"] is True

        # Test Markdown file (README is treated as docs)
        docs = reader.load_data(md_file, extra_info={"is_documentation": True})
        assert len(docs) > 0
        for doc in docs:
            assert doc.metadata["is_documentation"] is True

    def test_chunk_merging_logic(self, temp_dir):
        """Test that small chunks are merged into larger ones."""
        # Create a file with many small lines
        small_file = temp_dir / "small_lines.txt"
        small_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        # Set a min chunk size that is larger than one line but smaller than whole file
        reader = TypedDocumentReader(min_chunk_size_docs=50)

        # Process as generic text file
        docs = reader.load_data(small_file, extra_info={"is_documentation": True})

        if docs:
            # Chunks should be at least 50 chars unless it's the only chunk
            for doc in docs:
                if len(docs) > 1:
                    assert len(doc.get_content()) >= 50
                else:
                    # If it's the only chunk, it might be smaller if the file is smaller
                    assert len(doc.get_content()) <= 50
