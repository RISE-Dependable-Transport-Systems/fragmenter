"""File-type-specific document readers and parsers.

This module provides custom document readers that apply appropriate parsers
based on file types (code, markdown, text, PDFs) and ensure minimum chunk sizes
through intelligent merging.
"""

from pathlib import Path

from llama_index.core import Document
from llama_index.core.node_parser import (
    CodeSplitter,
    MarkdownNodeParser,
    SentenceSplitter,
)
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import TextNode
from llama_index.readers.file import PDFReader
from loguru import logger

# Minimum chunk size thresholds per file type (in characters)
# Optimized for C++ code - enough context for functions, classes, meaningful blocks
# Increased from 150/100/50 to prevent tiny fragments and improve retrieval quality
# Code files: C++, Python, etc. (enough for small function + context)
MIN_CHUNK_SIZE_CODE = 250
# Documentation: Markdown, text, PDFs (complete paragraph)
MIN_CHUNK_SIZE_DOCS = 150
# Config files: YAML, JSON, etc. (complete key-value pairs)
MIN_CHUNK_SIZE_CONFIG = 75


class TypedDocumentReader(BaseReader):
    """Reader that applies file-type-specific parsing during document loading."""

    def __init__(
        self,
        min_chunk_size_code: int = MIN_CHUNK_SIZE_CODE,
        min_chunk_size_docs: int = MIN_CHUNK_SIZE_DOCS,
        min_chunk_size_config: int = MIN_CHUNK_SIZE_CONFIG,
    ):
        """Initialize parsers for different file types.

        Args:
            min_chunk_size_code: Minimum characters for code chunks (default: 150)
            min_chunk_size_docs: Minimum characters for doc chunks (default: 100)
            min_chunk_size_config: Minimum characters for config chunks (default: 50)
        """
        self.min_chunk_size_code = min_chunk_size_code
        self.min_chunk_size_docs = min_chunk_size_docs
        self.min_chunk_size_config = min_chunk_size_config

        self.md_parser = MarkdownNodeParser()
        self.py_splitter = CodeSplitter(
            language="python", chunk_lines=80, chunk_lines_overlap=20, max_chars=2000
        )
        self.cpp_splitter = CodeSplitter(
            language="cpp", chunk_lines=80, chunk_lines_overlap=20, max_chars=2000
        )
        self.xml_splitter = CodeSplitter(
            language="xml", chunk_lines=60, chunk_lines_overlap=15, max_chars=1800
        )
        self.yaml_splitter = CodeSplitter(
            language="yaml", chunk_lines=60, chunk_lines_overlap=15, max_chars=1800
        )
        self.text_splitter = SentenceSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            paragraph_separator="\n\n",
        )
        self.pdf_reader = PDFReader()

    def load_data(self, file: Path, extra_info: dict | None = None) -> list[TextNode]:
        """Load and parse document based on file type.

        Uses file-type-specific parsers (CodeSplitter for code,
        MarkdownNodeParser for markdown) and returns TextNode objects
        ready for the IngestionPipeline. This prevents the pipeline
        from applying its default splitter and re-chunking our carefully
        merged chunks.

        Filters chunks by file-type-specific minimum sizes:
        - Code files (C++, Python, etc.): min_chunk_size_code (default 150)
        - Documentation (Markdown, PDF, etc.): min_chunk_size_docs (default 100)
        - Config files (YAML, JSON, etc.): min_chunk_size_config (default 50)

        **No code is lost**: Small chunks are merged with adjacent chunks
        rather than discarded. If entire file < min size, keeps whole file.

        Args:
            file: Path to file to load
            extra_info: Additional metadata

        Returns:
            List of TextNode objects (already chunked with preserved metadata)
        """
        extra_info = extra_info or {}
        file_str = str(file)
        file_name = file.name
        content = ""  # Initialize early to avoid scope issues

        # Handle PDFs with dedicated reader
        if file_str.endswith(".pdf"):
            try:
                # PDFReader returns Document objects directly
                pdf_docs = self.pdf_reader.load_data(file, extra_info=extra_info)
                # Apply text splitter to PDF content
                nodes = self.text_splitter.get_nodes_from_documents(pdf_docs)
            except Exception as e:
                logger.warning(f"Failed to read PDF {file}: {e}. Skipping.")
                return []
        else:
            # Read text-based files with binary detection
            try:
                with open(file, encoding="utf-8", errors="strict") as f:
                    content = f.read()
            except UnicodeDecodeError:
                logger.warning(f"Skipping binary/non-UTF8 file: {file}")
                return []
            except Exception as e:
                logger.warning(f"Failed to read file {file}: {e}. Skipping.")
                return []

            # Create base document
            doc = Document(text=content, metadata=extra_info)

            # Select appropriate parser and return chunked documents
            if file_str.endswith(".md") or file_name == "README":
                nodes = self.md_parser.get_nodes_from_documents([doc])
                # Markdown parser creates large sections based on headings,
                # so post-process chunks larger than chunk_size
                processed_nodes = []
                for node in nodes:
                    if len(node.get_content()) > self.text_splitter.chunk_size:
                        # Split large markdown chunks with text splitter
                        large_doc = Document(
                            text=node.get_content(), metadata=node.metadata
                        )
                        split_nodes = self.text_splitter.get_nodes_from_documents(
                            [large_doc]
                        )
                        processed_nodes.extend(split_nodes)
                    else:
                        processed_nodes.append(node)
                nodes = processed_nodes
            elif file_str.endswith(".py"):
                nodes = self.py_splitter.get_nodes_from_documents([doc])
            elif file_str.endswith((".cpp", ".h", ".hpp", ".cc", ".c", ".dts")):
                nodes = self.cpp_splitter.get_nodes_from_documents([doc])
            elif file_str.endswith((".xml", ".ui")):
                nodes = self.xml_splitter.get_nodes_from_documents([doc])
            elif file_str.endswith((".yml", ".yaml", ".json", ".cff")):
                nodes = self.yaml_splitter.get_nodes_from_documents([doc])
            else:
                # Catch-all for text files
                nodes = self.text_splitter.get_nodes_from_documents([doc])

        # Determine minimum chunk size based on file type
        is_code = extra_info.get("is_code", False)
        is_doc = extra_info.get("is_documentation", False)

        if is_code:
            min_size = self.min_chunk_size_code
        elif is_doc:
            min_size = self.min_chunk_size_docs
        else:
            min_size = self.min_chunk_size_config

        # Special case: If entire file is smaller than min_size, keep it whole
        # (don't discard small but complete files like short config files)
        if len(content) < min_size and len(nodes) > 0:
            # Return whole file as single TextNode, but only if it has content
            if content.strip():
                return [
                    TextNode(
                        text=content,
                        metadata=extra_info,
                    )
                ]
            else:
                # Empty file - skip it
                logger.debug(f"Skipping empty file: {file}")
                return []

        # Merge small chunks with adjacent chunks to avoid losing code
        # Strategy: Merge small chunks forward, but if it's the last chunk
        # and still too small, merge it backward with the previous chunk
        merged_nodes = []
        i = 0
        while i < len(nodes):
            node = nodes[i]
            content_text = node.get_content()

            # Skip empty nodes
            if not content_text or not content_text.strip():
                i += 1
                continue

            # If chunk is large enough, keep it as-is
            if len(content_text.strip()) >= min_size:
                merged_nodes.append(node)
                i += 1
            else:
                # Chunk is too small - try to merge with next chunk(s)
                merged_content = content_text
                merged_metadata = {**node.metadata}
                j = i + 1

                # Keep merging with next chunks until we reach min_size
                # or run out of chunks
                while j < len(nodes) and len(merged_content.strip()) < min_size:
                    next_node = nodes[j]
                    next_content = next_node.get_content()
                    if next_content and next_content.strip():
                        merged_content += "\n" + next_content
                        # Merge metadata (later chunks take precedence)
                        merged_metadata.update(next_node.metadata)
                    j += 1

                # If still too small and this is the last chunk, merge with previous
                if len(merged_content.strip()) < min_size and merged_nodes:
                    # Merge with the last node in merged_nodes
                    last_node = merged_nodes[-1]
                    merged_nodes[-1] = TextNode(
                        text=last_node.text + "\n" + merged_content,
                        metadata={**last_node.metadata, **merged_metadata},
                        excluded_embed_metadata_keys=last_node.excluded_embed_metadata_keys,
                        excluded_llm_metadata_keys=last_node.excluded_llm_metadata_keys,
                    )
                    # Don't add a new node, just updated the previous one
                else:
                    # Create merged node (or keep the small one if it's the only chunk)
                    merged_node = TextNode(
                        text=merged_content,
                        metadata=merged_metadata,
                        excluded_embed_metadata_keys=node.excluded_embed_metadata_keys,
                        excluded_llm_metadata_keys=node.excluded_llm_metadata_keys,
                    )
                    merged_nodes.append(merged_node)

                # Skip all the chunks we just merged
                i = j

        # Return TextNodes directly (already properly chunked and merged).
        # All metadata from file-type-specific parsers (is_code,
        # file_type, etc.) is preserved.
        return [
            TextNode(
                text=node.get_content(),
                metadata={**extra_info, **node.metadata},
                excluded_embed_metadata_keys=node.excluded_embed_metadata_keys,
                excluded_llm_metadata_keys=node.excluded_llm_metadata_keys,
            )
            for node in merged_nodes
            if node.get_content() and node.get_content().strip()
        ]
