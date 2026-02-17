"""Vector store initialization and configuration.

This module provides utilities for creating and configuring vector stores
for the RAG ingestion pipeline. Currently supports ChromaDB for persistent storage.
"""

from pathlib import Path

import chromadb
from llama_index.core import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from loguru import logger


def create_chroma_vector_store(
    persist_path: Path,
    collection_name: str = "documents",
) -> tuple[ChromaVectorStore, StorageContext]:
    """Create a Chroma vector store with persistent storage.

    Args:
        persist_path: Directory to persist the Chroma database
        collection_name: Name of the Chroma collection (default: "documents")

    Returns:
        Tuple of (ChromaVectorStore, StorageContext)
    """
    chroma_db_path = persist_path / "chroma_db"
    chroma_db_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Initializing Chroma vector store at: {chroma_db_path}")

    # Create Chroma client with persistent storage
    chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))

    # Get or create collection
    chroma_collection = chroma_client.get_or_create_collection(name=collection_name)

    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Create storage context
    # Load existing docstore if available for hash-based change detection
    docstore_path = persist_path / "docstore.json"
    if docstore_path.exists():
        logger.info(f"Loading existing docstore from: {docstore_path}")
        docstore = SimpleDocumentStore.from_persist_path(str(docstore_path))
    else:
        docstore = SimpleDocumentStore()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore,
    )

    logger.success(
        f"Chroma vector store initialized with collection '{collection_name}'"
    )

    return vector_store, storage_context
