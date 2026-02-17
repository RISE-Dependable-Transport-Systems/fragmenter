from pathlib import Path

import typer
from loguru import logger

from fragmenter.utils.logging import setup_logging

app = typer.Typer(help="Collect and display all unique file extensions in a directory.")


@app.command()
def main(
    directory: Path = typer.Argument(
        "data/code",
        help="Directory to scan for file extensions.",
        exists=True,
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
    exclude_git: bool = typer.Option(
        True,
        "--exclude-git/--include-git",
        help="Exclude .git directories from scan.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Scan a directory and list all unique file extensions.

    This is useful for discovering what file types exist in your data
    directory before configuring the RAG ingestion pipeline.
    """
    # Setup logging with appropriate level
    log_level = "DEBUG" if debug else "INFO"
    if logs_dir:
        setup_logging(logs_dir=logs_dir, level=log_level)
    else:
        setup_logging(level=log_level)

    extensions = set()
    logger.info(f"Scanning directory: {directory}")

    for path in directory.rglob("*"):
        # Skip .git directories if requested
        if exclude_git and ".git" in path.parts:
            continue

        if path.is_file():
            ext = path.suffix
            if ext:
                extensions.add(ext)
            else:
                # Files without extensions (e.g., Makefile, README)
                extensions.add(path.name)

    logger.info(f"Found {len(extensions)} unique file extensions/names:")
    for ext in sorted(extensions):
        logger.info(f"  {ext}")


if __name__ == "__main__":
    app()
