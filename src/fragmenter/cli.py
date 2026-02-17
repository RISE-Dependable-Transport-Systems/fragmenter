"""Unified CLI entry point for Fragmenter.

This module provides a single command-line interface with subcommands for all
RAG system operations: initialization, scraping, indexing, querying, and inspection.
"""

from pathlib import Path

import typer

# Create main app
app = typer.Typer(
    name="fragmenter",
    help="Fragmenter - RAG indexing and querying for code and docs",
    no_args_is_help=True,
)


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing .env file"
    ),
) -> None:
    """Initialize a new RAG project by creating a .env file from template.

    Example:
        fragmenter init
        fragmenter init --force
    """
    from fragmenter.tools.init import main as init_main

    init_main(force=force)


@app.command()
def scrape(
    url: str = typer.Argument(..., help="Base URL to scrape"),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Directory to save scraped content",
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format: markdown or html",
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Scrape content from websites and save as markdown or HTML files.

    Example:
        fragmenter scrape https://docs.example.com --output-dir ./data/docs
        fragmenter scrape https://example.com -o ./data --format html
    """
    from fragmenter.tools.scrape import main as scrape_main

    scrape_main(
        url=url,
        output_dir=output_dir,
        format=format,
        logs_dir=logs_dir,
        debug=debug,
    )


@app.command("rebuild-index")
def rebuild_index(
    data_dir: Path = typer.Option(
        ...,
        "--data-dir",
        "-d",
        help="Directory containing source documents",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    storage_dir: Path = typer.Option(
        ...,
        "--storage-dir",
        "-s",
        help="Directory to store the index",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional)",
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
        help="Enable debug logging",
    ),
    min_chunk_size_code: int = typer.Option(
        150,
        "--min-chunk-code",
        help="Minimum chunk size for code files (C++, Python, etc.).",
    ),
    min_chunk_size_docs: int = typer.Option(
        100,
        "--min-chunk-docs",
        help="Minimum chunk size for docs (Markdown, PDF, etc.).",
    ),
    min_chunk_size_config: int = typer.Option(
        50,
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

    Uses hash-based change detection to only process modified files and
    automatically removes stale documents from the index.

    Example:
           fragmenter rebuild-index --data-dir ./data --storage-dir ./vector_store
           fragmenter rebuild-index -d ./data -s ./index --debug
    """
    from fragmenter.tools.rebuild_index import main as rebuild_main

    rebuild_main(
        data_dir=data_dir,
        storage_dir=storage_dir,
        logs_dir=logs_dir,
        env_file=env_file,
        debug=debug,
        min_chunk_size_code=min_chunk_size_code,
        min_chunk_size_docs=min_chunk_size_docs,
        min_chunk_size_config=min_chunk_size_config,
        enable_extractors=enable_extractors,
        num_workers=num_workers,
    )


@app.command()
def query(
    # Query input
    query_text: str = typer.Option(
        None,
        "--query",
        "-q",
        help="Question to ask (use this OR --file, not both)",
    ),
    file: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="File containing the question",
        exists=True,
        dir_okay=False,
    ),
    # Paths
    storage_dir: Path = typer.Option(
        ...,
        "--storage-dir",
        "-s",
        help="Index storage directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    # Output
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Save response to file (relative to --output-dir if not absolute)",
    ),
    output_dir: Path = typer.Option(
        Path.cwd(),
        "--output-dir",
        help="Output directory for saved files",
    ),
    code_only: bool = typer.Option(
        False,
        "--code-only",
        help="Extract and save only code blocks from response",
    ),
    language: str = typer.Option(
        None,
        "--language",
        help="Language filter for code extraction (e.g., cpp, python)",
    ),
    # LLM configuration
    llm_provider: str = typer.Option(
        None,
        "--llm-provider",
        help="LLM provider: openai, ollama, anthropic, huggingface",
    ),
    llm_model: str = typer.Option(
        None,
        "--llm-model",
        help="LLM model name",
    ),
    llm_temperature: float = typer.Option(
        None,
        "--temperature",
        help="LLM temperature (0.0-1.0)",
    ),
    llm_max_tokens: int = typer.Option(
        None,
        "--max-tokens",
        help="Maximum response tokens",
    ),
    llm_timeout: float = typer.Option(
        None,
        "--timeout",
        help="LLM request timeout in seconds (default: 600)",
    ),
    # Embedding configuration
    embed_provider: str = typer.Option(
        None,
        "--embed-provider",
        help="Embedding provider: openai, huggingface, ollama",
    ),
    embed_model: str = typer.Option(
        None,
        "--embed-model",
        help="Embedding model name",
    ),
    # Other
    ollama_base_url: str = typer.Option(
        None,
        "--ollama-url",
        help="Ollama base URL (default: http://localhost:11434)",
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional)",
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
        help="Enable debug logging",
    ),
) -> None:
    """Query the RAG index with natural language questions.

    Example:
           fragmenter query --storage-dir ./index --query "How does the system work?"
           fragmenter query -s ./index -q "Explain the code" -o response.md
           fragmenter query -s ./index --file question.txt --code-only --language cpp
    """
    from fragmenter.tools.query_index import main as query_main

    query_main(
        query=query_text,
        file=file,
        storage_dir=storage_dir,
        output=output,
        output_dir=output_dir,
        code_only=code_only,
        language=language,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        llm_timeout=llm_timeout,
        embed_provider=embed_provider,
        embed_model=embed_model,
        ollama_base_url=ollama_base_url,
        logs_dir=logs_dir,
        env_file=env_file,
        debug=debug,
    )


@app.command("inspect-index")
def inspect_index(
    storage_dir: Path = typer.Option(
        "vector_store",
        "--storage-dir",
        "-s",
        help="Directory containing the index",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Inspect the RAG index and display statistics.

    Shows document counts, chunk statistics, node types, source directories,
    and example file paths.

    Example:
           fragmenter inspect-index
           fragmenter inspect-index --storage-dir ./custom_index --debug
    """
    from fragmenter.tools.inspect_index import main as inspect_main

    inspect_main(storage_dir=storage_dir, logs_dir=logs_dir, debug=debug)


@app.command("collect-extensions")
def collect_extensions(
    directory: Path = typer.Argument(
        "data/code",
        help="Directory to scan for file extensions",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    exclude_git: bool = typer.Option(
        True,
        "--exclude-git/--include-git",
        help="Exclude .git directories from scan",
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Scan a directory and list all unique file extensions.

    Useful for discovering what file types exist in your data directory
    before configuring the RAG ingestion pipeline.

    Example:
           fragmenter collect-extensions
           fragmenter collect-extensions ./my-project
           fragmenter collect-extensions ./data --include-git
    """
    from fragmenter.tools.collect_extensions import main as collect_main

    collect_main(
        directory=directory,
        logs_dir=logs_dir,
        exclude_git=exclude_git,
        debug=debug,
    )


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
