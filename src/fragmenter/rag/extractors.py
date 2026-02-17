"""Metadata extractors for optional LLM-based metadata enrichment.

This module provides utilities for configuring LlamaIndex metadata extractors
that use LLMs to extract keywords, summaries, and other metadata from chunks.
"""

from llama_index.core.extractors import BaseExtractor, KeywordExtractor
from llama_index.core.llms.llm import LLM
from loguru import logger


def get_metadata_extractors(
    llm: LLM | None = None,
    enable_extractors: bool = False,
    keywords: int = 5,
) -> list[BaseExtractor]:
    """Get metadata extractors for ingestion pipeline.

    Metadata extractors use LLMs to enrich chunks with additional metadata.
    WARNING: Each extractor makes one LLM call per chunk, which can be expensive
    for large document sets (1000 chunks = 1000 LLM calls).

    Args:
        llm: LLM instance to use for extraction (required if enable_extractors=True)
        enable_extractors: Whether to enable metadata extraction (default: False)
        keywords: Number of keywords to extract per chunk (default: 5)

    Returns:
        List of metadata extractors (empty if disabled or no LLM available)
    """
    if not enable_extractors:
        logger.info("Metadata extractors disabled")
        return []

    if llm is None:
        logger.warning(
            "Metadata extractors enabled but no LLM configured. Skipping extraction."
        )
        return []

    extractors: list[BaseExtractor] = [
        KeywordExtractor(
            llm=llm,
            keywords=keywords,
        ),
    ]

    logger.info(f"Enabled metadata extractors: KeywordExtractor (keywords={keywords})")
    logger.warning(
        f"Metadata extraction will make ~{keywords} LLM calls per chunk. "
        "This can be expensive for large document sets."
    )

    return extractors
