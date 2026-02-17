"""Scrape content from websites and save as markdown or HTML."""

from pathlib import Path

import typer
from loguru import logger

from fragmenter.scraping.scraper import scrape_site
from fragmenter.utils.logging import setup_logging

app = typer.Typer(
    help="Scrape websites and save content as markdown or HTML",
    no_args_is_help=True,
)


@app.command()
def main(
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
    logs_dir: Path = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Logs directory (optional)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Scrape content from a website and save as markdown or HTML files."""
    # Setup logging with appropriate level
    log_level = "DEBUG" if debug else "INFO"
    if logs_dir:
        setup_logging(logs_dir=logs_dir, level=log_level)
    else:
        setup_logging(level=log_level)

    # Validate format
    if format not in ["markdown", "html"]:
        logger.error(f"Invalid format: {format}. Must be 'markdown' or 'html'")
        raise typer.Exit(code=1)

    logger.info(f"Scraping {url} to {output_dir} (format: {format})")

    try:
        scrape_site(url, output_dir, format=format)
        logger.success(f"Scraping completed! Content saved to {output_dir}")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
