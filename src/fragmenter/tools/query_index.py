"""Query a RAG index with questions and save responses to files."""

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from fragmenter.config import RAGSettings
from fragmenter.rag.inference import load_index, query_and_save, query_index
from fragmenter.utils.logging import setup_logging

app = typer.Typer(
    help="Query a RAG index with natural language questions",
    no_args_is_help=True,
)
console = Console()


@app.command()
def main(
    # Query input
    query: str = typer.Option(
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
        "-d",
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
        "-l",
        help="Language filter for code extraction (e.g., cpp, python)",
    ),
    # LLM configuration (overrides env vars)
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
    logs_dir: Path = typer.Option(
        None,
        "--logs-dir",
        help="Logs directory",
    ),
    env_file: Path = typer.Option(
        None,
        "--env-file",
        help="Path to .env file (default: search parent directories)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
):
    """Query a RAG index with a question and optionally save the response."""
    # Load environment variables
    if env_file and env_file.exists():
        load_dotenv(env_file)
        console.print(f"[dim]Loaded environment from {env_file}[/dim]")
    else:
        load_dotenv()

    # Setup logging with appropriate level
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(logs_dir=logs_dir, level=log_level)

    # Validate input
    if not query and not file:
        console.print(
            "[red]Error:[/red] Must provide either --query or --file", style="bold red"
        )
        raise typer.Exit(1)
    if query and file:
        console.print(
            "[red]Error:[/red] Cannot use both --query and --file", style="bold red"
        )
        raise typer.Exit(1)

    # Read query from file if needed
    if file:
        query = file.read_text(encoding="utf-8").strip()
        console.print(f"[dim]Read query from {file}[/dim]")

    # Create settings instance with CLI overrides
    settings = RAGSettings()

    # Override from CLI args if provided
    if llm_provider is not None:
        settings.LLM_PROVIDER = llm_provider
    if llm_model is not None:
        settings.LLM_MODEL = llm_model
    if llm_temperature is not None:
        settings.LLM_TEMPERATURE = llm_temperature
    if llm_max_tokens is not None:
        settings.LLM_MAX_TOKENS = llm_max_tokens
    if llm_timeout is not None:
        settings.LLM_TIMEOUT = llm_timeout
    if ollama_base_url is not None:
        settings.OLLAMA_BASE_URL = ollama_base_url
    if embed_provider is not None:
        settings.EMBED_PROVIDER = embed_provider
    if embed_model is not None:
        settings.EMBED_MODEL = embed_model

    # Configure LLM and embeddings
    console.print("\n[bold cyan]Configuring RAG System[/bold cyan]")
    console.print(f"LLM: {settings.LLM_PROVIDER}/{settings.LLM_MODEL}")
    console.print(f"Embeddings: {settings.EMBED_PROVIDER}/{settings.EMBED_MODEL}")

    settings.configure_llm_settings()

    # Load index
    console.print("\n[bold cyan]Loading Index[/bold cyan]")
    console.print(f"Storage: {storage_dir}")
    index = load_index(str(storage_dir))

    # Display query (truncated if too long)
    console.print("\n[bold cyan]Query[/bold cyan]")
    if len(query) <= 500:
        query_preview = query
    else:
        truncation_msg = f"\n\n... (truncated, total length: {len(query)} chars)"
        query_preview = query[:500] + truncation_msg
    console.print(Panel(Text(query_preview, no_wrap=False), border_style="cyan"))

    # Query the index
    if output:
        # Resolve output path
        if not output.is_absolute():
            output = output_dir / output

        with console.status("[bold green]Generating response...", spinner="dots"):
            response_text = query_and_save(
                index, query, output, code_only=code_only, language=language
            )

        console.print(f"\n[green]✓[/green] Response saved to: {output}")

        # Display preview
        console.print("\n[bold cyan]Response Preview[/bold cyan]")
        preview = response_text[:500] + ("..." if len(response_text) > 500 else "")
        console.print(Panel(preview, border_style="green"))
    else:
        with console.status("[bold green]Generating response...", spinner="dots"):
            response = query_index(index, query)
        response_text = str(response)

        console.print("\n[bold cyan]Response[/bold cyan]")

        # Try to detect and syntax highlight code
        if "```" in response_text:
            console.print(response_text)
        else:
            console.print(Panel(response_text, border_style="green"))


if __name__ == "__main__":
    app()
