# Architecture

## Module Overview

```text
fragmenter/
├── cli.py                          # Typer CLI — single entry point, 6 subcommands
├── config.py                       # RAGSettings (pydantic-settings) — LLM/embed config
│
├── rag/                            # Core RAG pipeline
│   ├── ingestion.py                # Orchestrator: load_documents() + build_index()
│   ├── parsers.py                  # TypedDocumentReader — file-type-specific chunking
│   ├── metadata.py                 # Git-aware metadata extraction
│   ├── extractors.py               # Optional LLM-based KeywordExtractor wrapper
│   ├── pipeline.py                 # IngestionPipeline factory (UPSERTS_AND_DELETE)
│   ├── vector_stores.py            # ChromaDB persistent vector store factory
│   ├── inference.py                # Query engine: load_index(), query_index()
│   └── utils.py                    # MockEmbedding (for inspection without API keys)
│
├── tools/                          # CLI subcommand implementations
│   ├── init.py                     # fragmenter init — copies .env.example → .env
│   ├── scrape.py                   # fragmenter scrape — web scraping
│   ├── rebuild_index.py            # fragmenter rebuild-index — env setup + build_index()
│   ├── query_index.py              # fragmenter query — env setup + Rich output
│   ├── inspect_index.py            # fragmenter inspect-index — Rich stats dashboard
│   └── collect_extensions.py       # fragmenter collect-extensions — file scanner
│
├── scraping/
│   └── scraper.py                  # trafilatura + BeautifulSoup crawl-and-extract
│
├── evaluation/                     # RAG evaluation (RAGAS-based)
│   ├── evaluator.py                # Async RAGAS experiment runner (4 metrics)
│   ├── data_loader.py              # JSON → RAGAS Dataset loader
│   └── index_analysis.py           # UMAP embedding visualization + chunk stats
│
└── utils/
    └── logging.py                  # Loguru setup (console + rotating file handler)
```

## Design Decisions

1. **TextNode Returns (Not Documents)**: `parsers.py` returns `TextNode[]` instead of `Document[]`. This is critical — LlamaIndex's `IngestionPipeline` applies its default `SentenceSplitter` to `Document` nodes but passes `TextNode` objects through without re-chunking. This preserves file-type-specific chunking.

2. **UPSERTS_AND_DELETE Strategy**: The pipeline uses hash-based change detection. Unchanged nodes skip embedding, modified files get upserted, and removed files are automatically purged.

3. **Provider System via Optional Dependencies**: LLM/embedding providers are optional extras (`fragmenter[openai]`, `fragmenter[anthropic]`, etc.) with lazy imports and actionable error messages.

4. **Configuration Hierarchy**: CLI args > env vars > `.env` file > defaults in `RAGSettings`.

5. **Git-Aware Metadata**: `metadata.py` walks up the directory tree to find `.git`, enabling repo-relative paths and repository name tagging.

6. **Graceful Error Recovery**: If `pipeline.run()` fails on a batch, it falls back to node-by-node processing, logging exactly which file/chunk failed.

7. **MockEmbedding for Inspection**: `rag/utils.py` provides a no-op embedding model for loading and analyzing indexes without API keys.

## Data Flow: Ingestion

```text
CLI: fragmenter rebuild-index --data-dir ./data --storage-dir ./vector_store
         │
         ▼
tools/rebuild_index.py::main()
  1. load_dotenv()
  2. setup_logging()
  3. RAGSettings().configure_llm_settings() → sets LlamaIndex globals
         │
         ▼
rag/ingestion.py::build_index()
         │
         ├──► load_documents(input_dir, project_root, min_chunk_sizes)
         │     │
         │     ├──► metadata.py::create_metadata_extractor()
         │     │     Returns closure: detects git repos, computes relative paths,
         │     │     categorizes files (is_code, is_documentation, file_type)
         │     │
         │     ├──► parsers.py::TypedDocumentReader
         │     │     Pre-configured splitters per file type:
         │     │     • MarkdownNodeParser → .md, README
         │     │     • CodeSplitter(python) → .py
         │     │     • CodeSplitter(cpp) → .cpp, .h, .hpp, .cc, .c, .dts
         │     │     • CodeSplitter(xml) → .xml, .ui
         │     │     • CodeSplitter(yaml) → .yml, .yaml, .json, .cff
         │     │     • SentenceSplitter → .txt, .sh, .dcf, .eds, fallback
         │     │     • PDFReader → .pdf
         │     │
         │     └──► For each file: parse → merge small chunks → TextNode[]
         │
         ├──► vector_stores.py::create_chroma_vector_store()
         │     ChromaDB PersistentClient + load existing docstore.json
         │
         ├──► pipeline.py::create_ingestion_pipeline()
         │     Transformations: [extractors...] + [embed_model]
         │     Strategy: UPSERTS_AND_DELETE
         │
         ├──► pipeline.run(nodes) → hash-based dedup, embed, upsert/delete
         │
         └──► Persist pipeline state + docstore.json
```

## Data Flow: Query

```text
CLI: fragmenter query -s ./vector_store -q "How does X work?"
         │
         ▼
tools/query_index.py::main()
  1. load_dotenv()
  2. RAGSettings() + CLI overrides → configure_llm_settings()
         │
         ▼
rag/inference.py::load_index(persist_dir)
  → create_chroma_vector_store() → VectorStoreIndex.from_vector_store()
         │
         ▼
rag/inference.py::query_index(index, query_text)
  → index.as_query_engine() → query_engine.query()
         │
         ├──► Optional: extract_code_blocks(response, language)
         └──► Display via Rich (syntax highlighting for code blocks)
```

## Configuration Hierarchy

```text
Priority (highest → lowest):
┌─────────────────────────────────┐
│ 1. CLI arguments                │  --llm-provider, --llm-model, --temperature
├─────────────────────────────────┤
│ 2. Environment variables        │  LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY
├─────────────────────────────────┤
│ 3. .env file                    │  Loaded by python-dotenv + pydantic-settings
├─────────────────────────────────┤
│ 4. Defaults in RAGSettings      │  LLM_PROVIDER="openai", LLM_MODEL="gpt-4o-mini"
└─────────────────────────────────┘
```

`RAGSettings` uses pydantic-settings with `model_config = SettingsConfigDict(env_file=".env")`. The `configure_llm_settings()` method reads settings and sets **LlamaIndex global singletons** (`Settings.llm` and `Settings.embed_model`).

## Storage Layout

```text
vector_store/
├── chroma_db/          # ChromaDB persistent storage (embeddings + metadata)
├── docstore.json       # LlamaIndex SimpleDocumentStore (hash-based dedup)
└── pipeline/           # IngestionPipeline state (node hashes for incremental)
```

## Provider System

```text
config.py::RAGSettings.configure_llm_settings()
  │
  ├── LLM Provider:
  │   ├── openai      → llama_index.llms.openai.OpenAI
  │   ├── anthropic   → llama_index.llms.anthropic.Anthropic
  │   ├── ollama      → llama_index.llms.ollama.Ollama
  │   └── huggingface → llama_index.llms.huggingface.HuggingFaceInferenceAPI
  │
  └── Embedding Provider:
      ├── openai      → llama_index.embeddings.openai.OpenAIEmbedding
      ├── huggingface → llama_index.embeddings.huggingface.HuggingFaceEmbedding
      └── ollama      → llama_index.embeddings.ollama.OllamaEmbedding
```

- LLM and embeddings are independently configurable
- API keys come from `os.getenv()`, not settings fields
- Each provider is wrapped in `try/except ImportError` with actionable messages
- CLI can override at runtime via `--llm-provider` / `--llm-model` flags
