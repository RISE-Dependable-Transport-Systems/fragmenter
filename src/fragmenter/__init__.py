"""fragmenter — Local-first RAG indexer for repos, docs, and PDFs."""

__version__ = "0.1.1"

# Logging should be configured by applications, not by the library
# Import the setup function so it's available if needed
from fragmenter.utils.logging import setup_logging

__all__ = ["__version__", "setup_logging"]
