"""Tests for vector_stores.py module."""

from llama_index.vector_stores.chroma import ChromaVectorStore

from fragmenter.rag.vector_stores import create_chroma_vector_store


class TestCreateChromaVectorStore:
    """Tests for create_chroma_vector_store function."""

    def test_create_new_vector_store(self, temp_dir):
        """Test creating a new Chroma vector store."""
        vector_store, storage_context = create_chroma_vector_store(
            persist_path=temp_dir
        )

        # Check that vector store was created
        assert isinstance(vector_store, ChromaVectorStore)
        assert storage_context is not None

        # Check that storage directories were created
        chroma_path = temp_dir / "chroma_db"
        assert chroma_path.exists()
        assert chroma_path.is_dir()

    def test_create_with_custom_collection_name(self, temp_dir):
        """Test creating vector store with custom collection name."""
        vector_store, storage_context = create_chroma_vector_store(
            persist_path=temp_dir, collection_name="custom_collection"
        )

        assert isinstance(vector_store, ChromaVectorStore)
        # The collection should be created with custom name
        assert vector_store._collection.name == "custom_collection"

    def test_load_existing_vector_store(self, temp_dir):
        """Test loading an existing Chroma vector store."""
        # Create initial vector store
        vector_store1, _ = create_chroma_vector_store(persist_path=temp_dir)

        # Load the same vector store again
        vector_store2, _ = create_chroma_vector_store(persist_path=temp_dir)

        # Both should access the same collection
        assert vector_store1._collection.name == vector_store2._collection.name

    def test_persist_path_creation(self, temp_dir):
        """Test that persist path is created if it doesn't exist."""
        new_path = temp_dir / "new_vector_store"
        assert not new_path.exists()

        vector_store, _ = create_chroma_vector_store(persist_path=new_path)

        # Directory should now exist
        assert new_path.exists()
        assert (new_path / "chroma_db").exists()

    def test_storage_context_has_vector_store(self, temp_dir):
        """Test that storage context contains the vector store."""
        vector_store, storage_context = create_chroma_vector_store(
            persist_path=temp_dir
        )

        # Storage context should have the vector store set
        assert storage_context.vector_store == vector_store

    def test_docstore_creation(self, temp_dir):
        """Test that docstore is created in storage context."""
        vector_store, storage_context = create_chroma_vector_store(
            persist_path=temp_dir
        )

        # Storage context should have a docstore
        assert storage_context.docstore is not None

        # Docstore might not exist until documents are added
        # but the storage context should have it configured
        assert storage_context.docstore is not None
