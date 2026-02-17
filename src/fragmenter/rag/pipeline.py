"""Ingestion pipeline configuration and execution.

This module provides utilities for creating and configuring LlamaIndex
ingestion pipelines with transformations, metadata extractors, and vector stores.
"""

from llama_index.core import Settings
from llama_index.core.extractors import BaseExtractor
from llama_index.core.ingestion import DocstoreStrategy, IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from loguru import logger


def create_ingestion_pipeline(
    vector_store: ChromaVectorStore,
    metadata_extractors: list[BaseExtractor] | None = None,
    docstore: SimpleDocumentStore | None = None,
    num_workers: int = 2,
) -> IngestionPipeline:
    """Create an ingestion pipeline with Chroma vector store.

    Args:
        vector_store: Chroma vector store for persistent storage
        metadata_extractors: Optional list of metadata extractors
            (KeywordExtractor, etc.)
        docstore: Optional docstore for hash-based change detection
        num_workers: Number of parallel workers (default: 2)

    Returns:
        Configured IngestionPipeline ready to process documents
    """
    transformations: list = []

    # Add metadata extractors first (if enabled)
    if metadata_extractors:
        transformations.extend(metadata_extractors)
        logger.info(f"Added {len(metadata_extractors)} metadata extractors")

    # Add embedding model last (so metadata can influence embeddings)
    if Settings.embed_model is not None:
        transformations.append(Settings.embed_model)  # type: ignore[arg-type]
        logger.info(f"Added embedding model: {type(Settings.embed_model).__name__}")

    # Create docstore if not provided
    if docstore is None:
        docstore = SimpleDocumentStore()

    # Create pipeline with UPSERTS_AND_DELETE strategy
    # This enables true upserts and automatic deletion of stale documents
    pipeline = IngestionPipeline(
        transformations=transformations,
        vector_store=vector_store,
        docstore=docstore,
        docstore_strategy=DocstoreStrategy.UPSERTS_AND_DELETE,
    )

    logger.info(
        f"Ingestion pipeline created with {len(transformations)} transformations, "
        f"num_workers={num_workers}, strategy=UPSERTS_AND_DELETE"
    )

    return pipeline
