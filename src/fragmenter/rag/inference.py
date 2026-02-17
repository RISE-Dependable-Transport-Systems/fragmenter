import re
from pathlib import Path

from llama_index.core import VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from loguru import logger

from fragmenter.rag.vector_stores import create_chroma_vector_store


def load_index(persist_dir: str) -> BaseIndex:
    """Load the index from Chroma vector store.

    Args:
        persist_dir: Directory containing the Chroma vector store

    Returns:
        VectorStoreIndex loaded from persistent storage
    """
    logger.info(f"Loading index from Chroma storage: {persist_dir}")

    # Load Chroma vector store
    vector_store, storage_context = create_chroma_vector_store(
        persist_path=Path(persist_dir)
    )

    # Reconstruct index from vector store
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, storage_context=storage_context
    )

    logger.success("Loaded index from Chroma storage")
    return index


def query_index(index: BaseIndex, query_text: str):
    """Query the database."""
    query_preview = query_text if len(query_text) <= 100 else query_text[:100] + "..."
    logger.info(f"Querying database with: {query_preview}")
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    response_str = str(response)
    response_preview = (
        response_str if len(response_str) <= 200 else response_str[:200] + "..."
    )
    logger.info(f"Response: {response_preview}")
    return response


def extract_code_blocks(text: str, language: str | None = None) -> list[str]:
    """Extract code blocks from markdown text.

    Args:
        text: Markdown text containing code blocks
        language: Optional language filter (e.g., 'python', 'cpp')

    Returns:
        List of code block contents
    """
    if language:
        # Match ```language\n...\n```
        pattern = rf"```{language}\n(.*?)```"
    else:
        # Match ```optional-language\n...\n``` or ```\n...\n```
        pattern = r"```(?:\w+)?\n(.*?)```"

    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def query_and_save(
    index: BaseIndex,
    query_text: str,
    output_file: Path,
    code_only: bool = False,
    language: str | None = None,
) -> str:
    """Query RAG and save response to file.

    Args:
        index: The RAG index to query
        query_text: The query/question to ask
        output_file: Path where to save the response
        code_only: If True, extract and save only code blocks from response
        language: Optional language filter for code extraction (e.g., 'cpp', 'python')

    Returns:
        The response text
    """
    query_preview = query_text if len(query_text) <= 100 else query_text[:100] + "..."
    logger.info(f"Querying database with: {query_preview}")
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)

    response_text = str(response)
    response_preview = (
        response_text if len(response_text) <= 200 else response_text[:200] + "..."
    )
    logger.info(f"Response: {response_preview}")

    # Prepare content to save
    if code_only:
        code_blocks = extract_code_blocks(response_text, language=language)
        if code_blocks:
            content = "\n\n".join(code_blocks)
            logger.info(f"Extracted {len(code_blocks)} code block(s)")
        else:
            logger.warning("No code blocks found, saving full response")
            content = response_text
    else:
        content = response_text

    # Save to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")
    logger.success(f"Saved response to: {output_file}")

    return response_text
