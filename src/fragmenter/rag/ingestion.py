"""High-level orchestration for RAG document ingestion and index building.

This module provides the main entry points for loading documents and building
vector store indexes. It composes functionality from the specialized modules:
- parsers: File-type-specific document readers
- metadata: Metadata extraction and git repository detection
- extractors: Optional LLM-based metadata enrichment
- vector_stores: Chroma vector store initialization
- pipeline: Ingestion pipeline configuration

Example:
    >>> from fragmenter.rag.ingestion import build_index
    >>> index = build_index(
    ...     input_dir="./data",
    ...     persist_dir="./vector_store",
    ...     enable_extractors=False,
    ... )
"""

from pathlib import Path

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from llama_index.core.schema import TextNode
from loguru import logger

from fragmenter.rag.extractors import get_metadata_extractors
from fragmenter.rag.metadata import create_metadata_extractor
from fragmenter.rag.parsers import (
    MIN_CHUNK_SIZE_CODE,
    MIN_CHUNK_SIZE_CONFIG,
    MIN_CHUNK_SIZE_DOCS,
    TypedDocumentReader,
)
from fragmenter.rag.pipeline import create_ingestion_pipeline
from fragmenter.rag.vector_stores import create_chroma_vector_store


def load_documents(
    input_dir: str | Path,
    project_root: str | Path | None = None,
    min_chunk_size_code: int = MIN_CHUNK_SIZE_CODE,
    min_chunk_size_docs: int = MIN_CHUNK_SIZE_DOCS,
    min_chunk_size_config: int = MIN_CHUNK_SIZE_CONFIG,
) -> list[TextNode]:
    """Load documents from directory with file-type-specific parsing.

    Returns TextNode objects (not Documents) to prevent IngestionPipeline
    from applying its default splitter and re-chunking our carefully
    prepared chunks.

    Args:
        input_dir: Directory containing source documents
        project_root: Project root for calculating relative paths
            (defaults to input_dir)
        min_chunk_size_code: Minimum characters for code chunks (default: 250)
        min_chunk_size_docs: Minimum characters for doc chunks (default: 150)
        min_chunk_size_config: Minimum characters for config chunks (default: 75)

    Returns:
        List of TextNodes with enhanced metadata and proper chunking
    """
    logger.info(f"Starting indexing from path: {input_dir}")

    input_dir = Path(input_dir).resolve()
    project_root = Path(project_root).resolve() if project_root else input_dir

    logger.info(f"Project root for relative paths: {project_root}")

    # Create metadata extractor
    metadata_extractor = create_metadata_extractor(project_root)

    # Create custom reader for file-type-specific parsing
    reader = TypedDocumentReader(
        min_chunk_size_code=min_chunk_size_code,
        min_chunk_size_docs=min_chunk_size_docs,
        min_chunk_size_config=min_chunk_size_config,
    )

    # Define file extensions to process
    file_extensions = {
        ".md",
        ".py",
        ".cpp",
        ".h",
        ".hpp",
        ".cc",
        ".c",
        ".dts",
        ".xml",
        ".ui",
        ".yml",
        ".yaml",
        ".json",
        ".cff",
        ".txt",
        ".sh",
        ".dcf",
        ".eds",
        ".pdf",
    }
    special_files = {"Makefile", "Dockerfile", "README"}

    # Binary and noise file patterns to exclude
    exclude_patterns = {
        ".git",
        ".dtbo",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".gitmodules",
    }

    # Manually walk the directory and load files
    nodes = []
    for file_path in input_dir.rglob("*"):
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip excluded patterns
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue

        # Check if file should be processed
        should_process = (
            file_path.suffix in file_extensions or file_path.name in special_files
        )

        if should_process:
            # Extract metadata
            extra_info = metadata_extractor(str(file_path))

            # Load and chunk the file
            try:
                file_nodes = reader.load_data(file_path, extra_info=extra_info)
                nodes.extend(file_nodes)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

    logger.info(f"Loaded and chunked {len(nodes)} TextNode chunks")
    return nodes


def build_index(
    input_dir: str | Path,
    persist_dir: str | Path,
    project_root: str | Path | None = None,
    min_chunk_size_code: int = MIN_CHUNK_SIZE_CODE,
    min_chunk_size_docs: int = MIN_CHUNK_SIZE_DOCS,
    min_chunk_size_config: int = MIN_CHUNK_SIZE_CONFIG,
    enable_extractors: bool = False,
    num_workers: int = 2,
) -> BaseIndex:
    """Create or update index from documents using Chroma vector store.

    Uses LlamaIndex's IngestionPipeline with:
    - File-type-specific parsing (CodeSplitter, MarkdownNodeParser, SentenceSplitter)
    - Enhanced metadata (relative paths, categorization, depth)
    - Optional LLM-based metadata extractors (KeywordExtractor)
    - Chroma vector store for persistent storage
    - UPSERTS_AND_DELETE strategy for true upserts and automatic deletion
    - Configurable minimum chunk sizes with intelligent merging (no code lost)
    - Parallel processing with configurable workers

    Args:
        input_dir: Directory containing source documents
        persist_dir: Directory to store the index and Chroma database
        project_root: Project root for relative paths (defaults to input_dir)
        min_chunk_size_code: Minimum characters for code chunks (default: 250)
        min_chunk_size_docs: Minimum characters for doc chunks (default: 150)
        min_chunk_size_config: Minimum characters for config chunks (default: 75)
        enable_extractors: Enable LLM-based metadata extraction (default: False)
        num_workers: Number of parallel workers for pipeline (default: 2)

    Returns:
        VectorStoreIndex ready for querying
    """
    persist_path = Path(persist_dir)
    pipeline_storage = persist_path / "pipeline"

    # Load TextNodes with file-type-specific parsing and enhanced metadata
    nodes = load_documents(
        input_dir,
        project_root=project_root,
        min_chunk_size_code=min_chunk_size_code,
        min_chunk_size_docs=min_chunk_size_docs,
        min_chunk_size_config=min_chunk_size_config,
    )

    # Filter out empty nodes
    original_count = len(nodes)
    nodes = [node for node in nodes if node.text and node.text.strip()]
    if len(nodes) < original_count:
        logger.info(f"Filtered out {original_count - len(nodes)} empty nodes")

    # Initialize Chroma vector store
    vector_store, storage_context = create_chroma_vector_store(
        persist_path=persist_path,
        collection_name="documents",
    )

    # Check if vector store is empty but docstore has entries
    # This indicates a mismatch (e.g., Chroma was deleted but docstore remains)
    collection_count = vector_store._collection.count()
    docstore_count = len(storage_context.docstore.docs)

    if collection_count == 0 and docstore_count > 0:
        logger.warning(
            f"Vector store is empty but docstore has {docstore_count} entries. "
            "Clearing docstore to force full rebuild."
        )
        # Clear the docstore to force reprocessing
        storage_context.docstore.docs.clear()

    # Get optional metadata extractors
    metadata_extractors = get_metadata_extractors(
        llm=Settings.llm,
        enable_extractors=enable_extractors,
        keywords=5,
    )

    # Create ingestion pipeline
    pipeline = create_ingestion_pipeline(
        vector_store=vector_store,
        metadata_extractors=metadata_extractors,
        docstore=storage_context.docstore,
        num_workers=num_workers,
    )

    # Load existing pipeline state if available
    if pipeline_storage.exists():
        logger.info(f"Loading existing pipeline state from: {pipeline_storage}")
        try:
            pipeline.load(str(pipeline_storage))
        except Exception as e:
            logger.warning(f"Failed to load pipeline state: {e}. Starting fresh.")

    # Run ingestion pipeline
    logger.info(f"Running ingestion pipeline with {num_workers} workers...")
    try:
        processed_nodes = pipeline.run(
            nodes=nodes,
            num_workers=num_workers,
            show_progress=True,
        )
        logger.success(
            f"Processed {len(nodes)} TextNodes into "
            f"{len(processed_nodes)} embedded nodes"
        )

        # If no nodes were generated but we have input nodes,
        # it means everything was cached
        # This is expected for incremental updates, but warn the user
        if len(processed_nodes) == 0 and len(nodes) > 0:
            logger.warning(
                f"No new nodes created from {len(nodes)} nodes. "
                "All nodes already exist in docstore (based on hash). "
                "If migrating to new storage backend, delete the old "
                f"{persist_path} directory and rebuild from scratch."
            )
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        logger.info("Attempting to identify problematic node...")

        # Process nodes one by one to find the problematic one
        processed_nodes = []
        for i, node in enumerate(nodes):
            try:
                node_result = pipeline.run(
                    nodes=[node],
                    num_workers=1,
                    show_progress=False,
                )
                processed_nodes.extend(node_result)
            except Exception as node_error:
                file_name = node.metadata.get("file_name", "unknown")
                file_path = node.metadata.get("relative_path", "unknown")

                logger.error(
                    f"Failed to process node {i + 1}/{len(nodes)} "
                    f"from file: {file_name} (path: {file_path})"
                )
                logger.error(f"Error: {node_error}")
                logger.info(
                    f"Chunk preview: {node.text[:200]}..."
                    f" (total length: {len(node.text)} chars)"
                )
                logger.warning("Skipping this node and continuing...")

        if processed_nodes:
            logger.success(
                f"Processed {len(processed_nodes)} nodes from {len(nodes)} input nodes "
                f"(some nodes may have been skipped due to errors)"
            )

    # Persist pipeline state for future incremental updates
    logger.info(f"Persisting pipeline state to: {pipeline_storage}")
    pipeline.persist(str(pipeline_storage))

    # Persist docstore separately (for compatibility with index loading)
    docstore_path = persist_path / "docstore.json"
    logger.info(f"Persisting docstore to: {docstore_path}")
    storage_context.docstore.persist(persist_path=str(docstore_path))

    # Create index from Chroma vector store
    logger.info("Creating vector store index")
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )

    logger.success(
        f"Index created with {len(processed_nodes)} nodes in Chroma vector store"
    )

    return index
