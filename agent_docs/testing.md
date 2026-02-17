# Testing

## Running Tests

```bash
just test              # Unit tests only (excludes integration)
just test-cov          # Unit tests with coverage report
just test-integration  # Integration tests (requires API keys)
```

## Test Organization

```text
tests/
├── conftest.py           # Shared fixtures (tmp dirs, mock settings)
├── test_extractors.py    # KeywordExtractor enable/disable/config
├── test_integration.py   # End-to-end: load_documents → build_index
├── test_metadata.py      # Git detection, relative paths, file categorization
├── test_parsers.py       # TypedDocumentReader chunking and merging
├── test_pipeline.py      # IngestionPipeline factory configuration
└── test_vector_stores.py # ChromaDB store creation and persistence
```

## Test Strategy

### Unit Tests (`-m "not integration"`)

All unit tests run without external dependencies (no API keys, no network):

- **Mock LlamaIndex internals** — `MockEmbedding` from `rag/utils.py` replaces real embedding models
- **Temporary directories** — `tmp_path` fixtures for ChromaDB and docstore
- **No subprocess calls** — Everything is in-process

### Integration Tests (`-m integration`)

Marked with `@pytest.mark.integration`. Require:

- Valid API keys in `.env` (or environment variables)
- Network access for embedding/LLM calls
- More time (LLM latency)

### Key Patterns

1. **Fixtures in `conftest.py`**: Shared temp directories and mock configurations
2. **`TextNode` assertions**: Verify nodes have correct metadata, chunk sizes, and content
3. **Pipeline config tests**: Verify transformations, strategy, and worker settings without running the pipeline
4. **ChromaDB isolation**: Each test gets its own temp directory for the vector store

## Mocking Guide

### Mock Embedding Model

```python
from fragmenter.rag.utils import MockEmbedding
# Returns zero vectors of dimension 1536 — no API calls
```

### Mock Settings

```python
from unittest.mock import patch
with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test"}):
    settings = RAGSettings()
```

## Adding Tests

1. Place test files in `tests/` with `test_` prefix
2. Use `@pytest.mark.integration` for tests that need API keys
3. Use `tmp_path` for any filesystem operations
4. Prefer testing at module boundaries (public function inputs/outputs)
5. Run `just test` to verify before committing
