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


def create_query_engine(index: BaseIndex, top_k: int = 5, llm=None):
    """Create a cached query engine from the index with top-k retrieval.

    Args:
        index: The index to create query engine from
        top_k: Number of top results to retrieve from vector store
        llm: Optional LLM instance to use (uses global config if not provided)

    Returns:
        Query engine ready for queries
    """
    logger.debug(f"Creating query engine with top_k={top_k}")
    kwargs = {"similarity_top_k": top_k}
    if llm:
        kwargs["llm"] = llm
        logger.debug("Using provided LLM instance for query engine")
    return index.as_query_engine(**kwargs)


def retrieve_top_chunks(index: BaseIndex, query_text: str, top_k: int = 5) -> str:
    """Retrieve top-k raw chunks from the index without synthesis.

    Args:
        index: The index to query
        query_text: The query text
        top_k: Number of top chunks to retrieve

    Returns:
        Formatted string of top chunks
    """
    query_preview = query_text if len(query_text) <= 100 else query_text[:100] + "..."
    logger.debug(f"Retrieving top {top_k} chunks for: {query_preview}")

    # Get retriever and retrieve nodes
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query_text)

    if not nodes:
        logger.debug("No chunks retrieved")
        return ""

    logger.debug(f"Retrieved {len(nodes)} chunks")

    # Format chunks
    formatted_chunks = []
    for i, node in enumerate(nodes, 1):
        chunk_text = node.get_content()
        # Get source info if available
        metadata = node.metadata if hasattr(node, "metadata") else {}
        file_ref = metadata.get("file_path", "unknown source")

        formatted_chunk = f"[{i}] {file_ref}\n{chunk_text}"
        formatted_chunks.append(formatted_chunk)

    chunks_str = "\n\n---\n\n".join(formatted_chunks)
    logger.debug(f"Formatted {len(nodes)} chunks ({len(chunks_str)} chars total)")
    return chunks_str


def query_with_engine(query_engine, query_text: str):
    """Query using a pre-created query engine (efficient for repeated queries).

    Args:
        query_engine: Pre-created query engine from create_query_engine()
        query_text: The query text

    Returns:
        The synthesized response text
    """
    query_preview = query_text if len(query_text) <= 100 else query_text[:100] + "..."
    logger.info(f"Querying database with: {query_preview}")

    response = query_engine.query(query_text)

    # Extract response text from Response object
    # Standard LlamaIndex Response has a .response attribute
    if hasattr(response, "response"):
        response_str = str(response.response)
    else:
        response_str = str(response)

    # Extract source nodes info for debugging
    source_info = ""
    if hasattr(response, "source_nodes") and response.source_nodes:
        logger.debug(f"Retrieved {len(response.source_nodes)} source nodes")
        source_info = f" [from {len(response.source_nodes)} nodes]"

    response_preview = (
        response_str if len(response_str) <= 200 else response_str[:200] + "..."
    )
    logger.info(f"Response{source_info}: {response_preview}")
    return response_str


def query_index(index: BaseIndex, query_text: str, llm=None):
    """Query the database with optional custom LLM (creates new engine each time).

    For efficiency with repeated queries, use create_query_engine() + query_with_engine().

    Args:
        index: The index to query
        query_text: The query text
        llm: Optional LLM instance to use (uses global config if not provided)

    Returns:
        The synthesized response text
    """
    query_engine = create_query_engine(index, llm=llm)
    return query_with_engine(query_engine, query_text)


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
        if language.lower() == "git":
            # For git, we match both ```git and ```diff blocks as they are common for patches
            # We use a non-greedy match to handle multiple blocks
            pattern = r"```(?:git|diff)[\s\w]*\n(.*?)\n```"
        else:
            pattern = rf"```{language}[\s\w]*\n(.*?)\n```"
    else:
        # Match ```optional-language\n...\n``` or ```\n...\n```
        pattern = r"```(?:\w+)?\s*\n(.*?)\n```"

    matches = re.findall(pattern, text, re.DOTALL)

    # Clean matches: remove nested markdown code block markers if any
    cleaned_matches = []
    for match in matches:
        # Remove any leading/trailing backticks or language markers that might have been captured
        # (happens with nested blocks)
        cleaned = re.sub(r"^```\w*\s*\n", "", match)
        cleaned = re.sub(r"\n\s*```$", "", cleaned)
        cleaned_matches.append(cleaned.strip())

    return cleaned_matches


def query_and_save(
    index: BaseIndex,
    query_text: str,
    output_file: Path,
    code_only: bool = False,
    language: str | None = None,
    llm=None,
) -> str:
    """Query RAG and save response to file.

    Args:
        index: The RAG index to query
        query_text: The query/question to ask
        output_file: Path where to save the response
        code_only: If True, extract and save only code blocks from response
        language: Optional language filter for code extraction (e.g., 'cpp', 'python')
        llm: Optional LLM instance to use (uses global config if not provided)

    Returns:
        The response text
    """
    query_engine = create_query_engine(index, llm=llm)
    response_text = query_with_engine(query_engine, query_text)

    # Prepare content to save
    if code_only:
        code_blocks = extract_code_blocks(response_text, language=language)
        if code_blocks:
            content = "\n\n".join(code_blocks)
            logger.info(f"Extracted {len(code_blocks)} code block(s)")

            # If language is git, ensure it's saved with .patch extension if not already specified
            if language and language.lower() == "git":
                if output_file.suffix != ".patch":
                    output_file = output_file.with_suffix(".patch")
                    logger.info(
                        f"Language is git, changing output file extension to {output_file.suffix}"
                    )

                # Sanity check for bare @@ headers
                if "@@" in content and not re.search(
                    r"@@ -\d+,\d+ \+\d+,\d+ @@", content
                ):
                    logger.warning(
                        "Extracted patch contains bare '@@' headers. This will likely fail with 'git apply'."
                    )
                    logger.warning(
                        "Try regenerating with more explicit instructions or checking the prompt."
                    )
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
