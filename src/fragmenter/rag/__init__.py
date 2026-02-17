"""RAG (Retrieval Augmented Generation) ingestion and querying.

This package provides modular components for building and querying RAG indexes:
- ingestion: High-level orchestration for document loading and index building
- parsers: File-type-specific document readers (TypedDocumentReader)
- metadata: Metadata extraction and git repository detection
- extractors: Optional LLM-based metadata enrichment
- vector_stores: Vector store initialization (Chroma)
- pipeline: Ingestion pipeline configuration
- inference: Query interface for RAG indexes
"""

from fragmenter.rag.ingestion import build_index, load_documents
from fragmenter.rag.parsers import TypedDocumentReader

__all__ = ["build_index", "load_documents", "TypedDocumentReader"]
