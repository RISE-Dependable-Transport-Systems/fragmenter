"""Initialize a new RAG project by copying .env template."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Initialize a new RAG project", no_args_is_help=True)
console = Console()


@app.command()
def main(
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing .env file"
    ),
) -> None:
    """Create a .env file from template in the current directory.

    Example:
        uv run python -m fragmenter.tools.init
        uvx fragmenter init
    """
    env_file = Path(".env")

    if env_file.exists() and not force:
        console.print(
            f"[yellow]Warning:[/yellow] {env_file} already exists."
            " Use --force to overwrite.",
            style="bold yellow",
        )
        raise typer.Exit(1)

    # Find the .env.example file in the package
    # Logic to find it when running from package or source
    try:
        # Check standard location relative to this file
        template_path = Path(__file__).parent.parent.parent.parent / ".env.example"
        if not template_path.exists():
            # Fallback for installed package structure (site-packages)
            template_path = Path(__file__).parent.parent / ".env.example"
    except (NameError, AttributeError):
        # Fallback for environments where __file__ is not defined
        template_path = Path(".env.example")

    if not template_path.exists():
        console.print(
            f"[red]Error:[/red] Template file not found at {template_path.absolute()}",
            style="bold red",
        )
        raise typer.Exit(1)

    # Copy template to current directory
    template_content = template_path.read_text()
    env_file.write_text(template_content)

    # Success message with next steps
    console.print(
        Panel(
            f"[green]✓ Created {env_file}[/green]\n\n"
            f"[cyan]Next steps:[/cyan]\n"
            f"1. Edit {env_file} and add your API key(s)\n"
            f"2. Scrape documentation:\n"
            f"   [dim]uv run fragmenter scrape \\\n"
            f"     --url https://docs.example.com \\\n"
            f"     --output ./data/docs[/dim]\n"
            f"3. Build the index:\n"
            f"   [dim]uv run fragmenter rebuild-index \\\n"
            f"     --data-dir ./data \\\n"
            f"     --storage-dir ./vector_store[/dim]\n"
            f"4. Query the RAG system:\n"
            f"   [dim]uv run fragmenter query \\\n"
            f"     --storage-dir ./vector_store \\\n"
            f"     --query 'your question'[/dim]",
            title="Setup Complete",
            border_style="green",
        )
    )


if __name__ == "__main__":
    app()
