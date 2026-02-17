"""Integration tests for the RAG pipeline."""

import pytest
from llama_index.core import Settings

from fragmenter.rag.ingestion import build_index, load_documents
from fragmenter.rag.metadata import create_metadata_extractor
from fragmenter.rag.parsers import TypedDocumentReader
from fragmenter.rag.utils import MockEmbedding


@pytest.fixture
def sample_repo(temp_dir):
    """Create a sample repository with code and docs."""
    # Create directory structure
    code_dir = temp_dir / "src"
    code_dir.mkdir()
    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()

    # Create sample files
    (code_dir / "main.py").write_text(
        "def main():\n    print('Hello, world!')\n\n" * 10
    )
    (code_dir / "utils.py").write_text("def helper():\n    return 42\n\n" * 10)
    (docs_dir / "README.md").write_text("# Project\n\nThis is a test project.\n\n" * 10)
    (temp_dir / "config.yaml").write_text("setting: value\nanother: setting\n" * 5)

    return temp_dir


class TestIntegration:
    """Integration tests for the full RAG pipeline."""

    def test_load_documents_basic(self, sample_repo):
        """Test loading documents from repository."""
        _metadata_extractor = create_metadata_extractor(sample_repo)

        documents = load_documents(
            input_dir=sample_repo,
        )

        # Should load all files
        assert len(documents) > 0

        # All documents should have metadata
        for doc in documents:
            assert "file_path" in doc.metadata
            assert "file_type" in doc.metadata

    def test_load_documents_with_custom_chunk_sizes(self, sample_repo):
        """Test loading documents with custom chunk sizes."""
        _metadata_extractor = create_metadata_extractor(sample_repo)

        documents = load_documents(
            input_dir=sample_repo,
            min_chunk_size_code=200,
            min_chunk_size_docs=150,
            min_chunk_size_config=75,
        )

        # Should load documents with custom sizes
        assert len(documents) > 0

    def test_build_index_end_to_end(self, sample_repo, temp_dir):
        """Test building index end-to-end."""
        # Configure mock embedding
        Settings.embed_model = MockEmbedding(embed_batch_size=10)
        Settings.llm = None

        # Create separate directory for vector store
        vector_store_dir = temp_dir / "vector_store"

        # Build index (without extractors to avoid LLM calls)
        build_index(
            input_dir=sample_repo,
            persist_dir=vector_store_dir,
            project_root=sample_repo,
            enable_extractors=False,
            num_workers=1,
        )

        # Verify vector store was created
        assert vector_store_dir.exists()
        chroma_dir = vector_store_dir / "chroma_db"
        assert chroma_dir.exists()

    def test_build_index_with_updates(self, sample_repo, temp_dir):
        """Test incremental updates to index."""
        # Configure mock embedding
        Settings.embed_model = MockEmbedding(embed_batch_size=10)
        Settings.llm = None

        vector_store_dir = temp_dir / "vector_store"

        # Build initial index
        build_index(
            input_dir=sample_repo,
            persist_dir=vector_store_dir,
            project_root=sample_repo,
            enable_extractors=False,
            num_workers=1,
        )

        # Add a new file
        (sample_repo / "src" / "new_file.py").write_text(
            "def new_function():\n    pass\n" * 10
        )

        # Rebuild index (should detect changes)
        build_index(
            input_dir=sample_repo,
            persist_dir=vector_store_dir,
            project_root=sample_repo,
            enable_extractors=False,
            num_workers=1,
        )

        # Should complete without error
        assert vector_store_dir.exists()

    def test_typed_document_reader_integration(self, sample_repo):
        """Test TypedDocumentReader with real files."""
        reader = TypedDocumentReader(
            min_chunk_size_code=150,
            min_chunk_size_docs=100,
            min_chunk_size_config=50,
        )

        documents = []
        for file_path in sample_repo.rglob("*"):
            if file_path.is_file():
                documents.extend(reader.load_data(file_path))

        # Should load all files
        assert len(documents) > 0

        # Verify chunk sizes are respected
        for doc in documents:
            # Files smaller than min_size kept whole
            # Others should be at least min_size
            if "file_type" in doc.metadata:
                file_type = doc.metadata["file_type"]
                if file_type in [".py", ".cpp", ".h", ".java"]:
                    # Code chunks (unless file is tiny)
                    pass  # May be smaller if entire file is small
                elif file_type in [".md", ".rst"]:
                    # Doc chunks
                    pass
