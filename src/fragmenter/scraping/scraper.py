import random
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
from trafilatura.settings import use_config

UA = UserAgent()


def create_output_directory(directory: str | Path) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)


def fetch_page(url: str) -> str | None:
    # Sleep for a random interval between 2 and 5 seconds
    time.sleep(random.uniform(2.0, 5.0))

    # Configure a random User-Agent
    config = use_config()
    config.set("DEFAULT", "USER_AGENTS", UA.random)

    return trafilatura.fetch_url(url, config=config)


def extract_links(html_content: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html_content, "html.parser")
    links = {base_url}
    for a in soup.find_all("a", href=True):
        full_url: str = urljoin(base_url, str(a["href"])).split("#")[0]
        if full_url.startswith(base_url):
            links.add(full_url)
    return links


def get_filepath(url: str, output_dir: str | Path, format: str) -> Path:
    filename = urlparse(url).path.strip("/").replace("/", "_") or "index"
    extension = "md" if format == "markdown" else "html"
    return Path(output_dir) / f"{filename}.{extension}"


def save_content(url: str, text: str, output_dir: str | Path, format: str) -> None:
    filepath = get_filepath(url, output_dir, format)

    if format == "markdown":
        filepath.write_text(f"# Source: {url}\n\n{text}", encoding="utf-8")
    else:  # html
        filepath.write_text(text, encoding="utf-8")


def process_page(url: str, output_dir: str | Path, format: str) -> None:
    filepath = get_filepath(url, output_dir, format)
    if filepath.exists():
        logger.info(f"Skipping {url} (already exists)")
        return

    logger.info(f"Processing {url}...")
    downloaded = fetch_page(url)
    if not downloaded:
        logger.warning(f"Failed to download {url}")
        return

    if format == "markdown":
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="markdown",
        )
    else:  # html
        text = downloaded

    if text:
        save_content(url, text, output_dir, format)


def scrape_site(
    base_url: str, output_dir: str | Path, format: str = "markdown"
) -> None:
    create_output_directory(output_dir)

    # 1. Fetch main page to discover links
    logger.info(f"Fetching index: {base_url}")
    index_html = fetch_page(base_url)
    if not index_html:
        logger.error("Failed to fetch index.")
        return

    # 2. Extract all links from the main page
    links = extract_links(index_html, base_url)
    logger.info(f"Found {len(links)} pages to process.")

    # 3. Process each link
    for link in links:
        process_page(link, output_dir, format)
