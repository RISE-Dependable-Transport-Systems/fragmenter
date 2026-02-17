from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger

from fragmenter.config import RAGSettings
from fragmenter.rag.ingestion import build_index
from fragmenter.utils.logging import setup_logging

app = typer.Typer(help="Rebuild or update the RAG index with incremental changes.")


@app.command()
def main(
    data_dir: Path = typer.Option(
        ...,
        "--data-dir",
        "-d",
        help="Directory containing source documents.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    storage_dir: Path = typer.Option(
        ...,
        "--storage-dir",
        "-s",
        help="Directory to store the index.",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional).",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    env_file: Path | None = typer.Option(
        None,
        "--env-file",
        help="Path to .env file (default: search parent directories)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging (shows full problematic chunks)",
    ),
    min_chunk_size_code: int = typer.Option(
        250,
        "--min-chunk-code",
        help="Minimum chunk size for code files (C++, Python, etc.).",
    ),
    min_chunk_size_docs: int = typer.Option(
        150,
        "--min-chunk-docs",
        help="Minimum chunk size for docs (Markdown, PDF, etc.).",
    ),
    min_chunk_size_config: int = typer.Option(
        75,
        "--min-chunk-config",
        help="Minimum chunk size for config files (YAML, JSON, etc.).",
    ),
    enable_extractors: bool = typer.Option(
        False,
        "--enable-extractors",
        help=(
            "Enable metadata extractors (KeywordExtractor). "
            "WARNING: Makes 1 LLM call per chunk."
        ),
    ),
    num_workers: int = typer.Option(
        2,
        "--num-workers",
        help="Number of parallel workers for ingestion pipeline.",
    ),
) -> None:
    """Build or update the RAG index with automatic change detection.

    Uses LlamaIndex IngestionPipeline with:
    - Hash-based change detection (only processes changed files)
    - Automatic deletion handling (removes stale documents)
    - File-type-specific parsing (Markdown, Code, Text, PDF)
    - Chroma persistent vector store with UPSERTS_AND_DELETE support
    - Optional metadata extraction (keywords)
    """
    # Load environment variables
    if env_file and env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        load_dotenv()

    # Setup logging with appropriate level
    log_level = "DEBUG" if debug else "INFO"
    if logs_dir:
        setup_logging(logs_dir=logs_dir, level=log_level)
    else:
        setup_logging(level=log_level)

    # Configure embeddings from environment
    settings = RAGSettings()
    logger.info(
        f"Configuring embeddings: {settings.EMBED_PROVIDER}/{settings.EMBED_MODEL}"
    )
    settings.configure_llm_settings()

    logger.info(f"Building/updating index from {data_dir} to {storage_dir}...")
    logger.info(
        f"Minimum chunk sizes: code={min_chunk_size_code}, "
        f"docs={min_chunk_size_docs}, config={min_chunk_size_config}"
    )
    logger.info(
        f"Ingestion config: enable_extractors={enable_extractors}, "
        f"num_workers={num_workers}"
    )

    # Use data_dir as project root for relative path calculations
    try:
        build_index(
            input_dir=data_dir,
            persist_dir=storage_dir,
            project_root=data_dir,
            min_chunk_size_code=min_chunk_size_code,
            min_chunk_size_docs=min_chunk_size_docs,
            min_chunk_size_config=min_chunk_size_config,
            enable_extractors=enable_extractors,
            num_workers=num_workers,
        )
        logger.success("Index build/update completed successfully!")
    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
