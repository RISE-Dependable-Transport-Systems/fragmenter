"""
Programmatic example - demonstrates using the RAG framework in Python code.

This example shows how to use the library programmatically, though you can also
use the CLI tools directly without writing any Python:

    # Build index
    uv run python -m fragmenter.tools.rebuild_index \\
        -d ./data -s ./vector_store

    # Query
    uv run python -m fragmenter.tools.query_index \\
        -s ./vector_store \\
        -q "Your question"
"""

from pathlib import Path

from dotenv import load_dotenv

from fragmenter.config import RAGSettings
from fragmenter.rag.inference import load_index, query_index
from fragmenter.rag.ingestion import build_index
from fragmenter.utils.logging import setup_logging

# Example paths (adjust these to point to your data)
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"  # Your source data directory
STORAGE_DIR = BASE_DIR / "vector_store"  # Where the index will be stored
LOGS_DIR = BASE_DIR / "logs"  # Log output directory

# Example query
QUERY = "How does the system architecture work?"


def main():
    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging(logs_dir=LOGS_DIR)

    # Configure LLM/embedding from .env
    settings = RAGSettings()
    settings.configure_llm_settings()

    # Build index if it doesn't exist
    if not STORAGE_DIR.exists():
        build_index(DATA_DIR, STORAGE_DIR)

    # Load and query index
    index = load_index(str(STORAGE_DIR))
    query_index(index, QUERY)


if __name__ == "__main__":
    main()
