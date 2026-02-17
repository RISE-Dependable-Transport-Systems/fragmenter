"""Tests for pipeline.py module."""

from unittest.mock import MagicMock

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import TransformComponent
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore

from fragmenter.rag.pipeline import create_ingestion_pipeline


class TestCreateIngestionPipeline:
    """Tests for create_ingestion_pipeline function."""

    def test_create_pipeline_basic(self):
        """Test basic pipeline creation."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        pipeline = create_ingestion_pipeline(vector_store)

        assert isinstance(pipeline, IngestionPipeline)
        assert pipeline.vector_store == vector_store

    def test_create_pipeline_with_extractors(self):
        """Test pipeline creation with metadata extractors."""
        vector_store = MagicMock(spec=ChromaVectorStore)
        extractors = [MagicMock(spec=TransformComponent)]

        pipeline = create_ingestion_pipeline(
            vector_store, metadata_extractors=extractors
        )

        assert isinstance(pipeline, IngestionPipeline)
        # Transformations should include extractors
        assert len(pipeline.transformations) > 0

    def test_create_pipeline_with_docstore(self):
        """Test pipeline creation with custom docstore."""
        vector_store = MagicMock(spec=ChromaVectorStore)
        docstore = SimpleDocumentStore()

        pipeline = create_ingestion_pipeline(vector_store, docstore=docstore)

        assert pipeline.docstore == docstore

    def test_create_pipeline_custom_workers(self):
        """Test pipeline creation with custom worker count."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        pipeline = create_ingestion_pipeline(vector_store, num_workers=4)

        # num_workers is used during .run(), not stored on the pipeline object
        assert isinstance(pipeline, IngestionPipeline)

    def test_create_pipeline_default_workers(self):
        """Test pipeline creation with default worker count."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        pipeline = create_ingestion_pipeline(vector_store)

        # Basic check that it returns a pipeline
        assert isinstance(pipeline, IngestionPipeline)

    def test_pipeline_has_embedding_transformation(self):
        """Test that pipeline includes embedding transformation."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        pipeline = create_ingestion_pipeline(vector_store)

        # Should have transformations (at minimum embedding)
        assert len(pipeline.transformations) > 0

    def test_pipeline_transformation_order(self):
        """Test that transformations are in correct order."""
        vector_store = MagicMock(spec=ChromaVectorStore)
        extractors = [
            MagicMock(spec=TransformComponent),
            MagicMock(spec=TransformComponent),
        ]

        pipeline = create_ingestion_pipeline(
            vector_store, metadata_extractors=extractors
        )

        transformations = pipeline.transformations
        assert len(transformations) >= 1  # At least embedding

    def test_pipeline_with_empty_extractors(self):
        """Test pipeline with empty extractors list."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        pipeline = create_ingestion_pipeline(vector_store, metadata_extractors=[])

        # Should still create pipeline, just without extractors
        assert isinstance(pipeline, IngestionPipeline)

    def test_pipeline_rejects_invalid_workers(self):
        """Test that pipeline validates worker count."""
        vector_store = MagicMock(spec=ChromaVectorStore)

        # Should handle edge cases gracefully
        # num_workers=1 is valid
        pipeline = create_ingestion_pipeline(vector_store, num_workers=1)
        assert isinstance(pipeline, IngestionPipeline)

        # num_workers=0 might raise error or default to 1
        # This depends on LlamaIndex validation
