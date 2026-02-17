# Ingestion Pipeline

## Overview

The ingestion pipeline transforms raw files into embedded, searchable vector data. The entry point is `rag/ingestion.py::build_index()`.

## Key Concepts

### File-Type-Specific Parsing

`rag/parsers.py::TypedDocumentReader` selects the appropriate parser per file extension:

| Extensions | Parser | Notes |
|-----------|--------|-------|
| `.md`, `README` | `MarkdownNodeParser` | Respects heading structure |
| `.py` | `CodeSplitter(python)` | AST-aware splitting |
| `.cpp`, `.h`, `.hpp`, `.cc`, `.c`, `.dts` | `CodeSplitter(cpp)` | Function/class boundaries |
| `.xml`, `.ui` | `CodeSplitter(xml)` | Tag-aware |
| `.yml`, `.yaml`, `.json`, `.cff` | `CodeSplitter(yaml)` | Key-level splitting |
| `.txt`, `.sh`, `.dcf`, `.eds` | `SentenceSplitter` | Sentence boundaries |
| `.pdf` | `PDFReader` → `SentenceSplitter` | Extract text first, then split |
| Everything else | `SentenceSplitter` | Fallback |

### Intelligent Chunk Merging

Small chunks are **never discarded**. The merging strategy in `parsers.py`:

1. **Forward-merge**: Combine small chunk with subsequent chunks until `min_chunk_size` is reached
2. **Backward-merge**: If still too small at end, merge into previous chunk
3. **Whole-file preservation**: If entire file < `min_chunk_size`, keep as single chunk

Default thresholds per file type:
- Code: 250 characters
- Docs: 150 characters
- Config: 75 characters

### Incremental Updates

Three cooperating mechanisms enable incremental rebuilds:

1. **Docstore hash tracking** (`docstore.json`): LlamaIndex's `SimpleDocumentStore` stores a content hash per node. Unchanged hashes skip embedding entirely.

2. **Pipeline state persistence** (`pipeline/` directory): The `IngestionPipeline` persists its internal state. On reload via `pipeline.load()`, it knows what's been processed.

3. **UPSERTS_AND_DELETE strategy**: `DocstoreStrategy.UPSERTS_AND_DELETE` means:
   - New nodes → embedded and inserted
   - Changed nodes (different hash) → re-embedded and upserted
   - Removed nodes (not in current input) → deleted from Chroma + docstore
   - Unchanged nodes → completely skipped (zero API calls)

4. **Mismatch detection**: `build_index()` checks if Chroma is empty but docstore has entries (e.g., Chroma was manually deleted). Clears docstore to force full rebuild.

### Git-Aware Metadata

`rag/metadata.py::create_metadata_extractor()` returns a closure that:
- Walks up from each file to find `.git` (bounded by `data_dir`)
- Computes repo-relative paths for files inside git repos
- Falls back to data-dir-relative paths for non-repo files
- Tags each node with: `file_path`, `file_name`, `file_type`, `is_code`, `is_documentation`, `repository_name`, `relative_depth`

### Vector Store

`rag/vector_stores.py::create_chroma_vector_store()`:
- Creates `chromadb.PersistentClient` at `persist_path/chroma_db/`
- Uses `get_or_create_collection("documents")`
- Loads existing `docstore.json` if present for hash-based dedup
- Returns `(ChromaVectorStore, StorageContext)`

### Pipeline Assembly

`rag/pipeline.py::create_ingestion_pipeline()`:
- Transformations: `[metadata_extractors...] + [embed_model]`
- Strategy: `DocstoreStrategy.UPSERTS_AND_DELETE`
- `num_workers` controls parallel embedding (defaults to 2)
- Pipeline state is persisted/loaded from `persist_path/pipeline/`

## Error Recovery

If `pipeline.run()` fails on a batch, `build_index()` falls back to **node-by-node processing**:
- Each node is run individually through the pipeline
- Failures are logged with chunk preview (first 200 chars) and error details
- Processing continues with remaining nodes
- This prevents a single bad file from blocking the entire index build

## Adding New File Types

1. Add the extension to `SUPPORTED_EXTENSIONS` in `parsers.py`
2. Create or select a parser in `TypedDocumentReader.__init__()`
3. Map the extension in `TypedDocumentReader.load_data()`
4. Set an appropriate `min_chunk_size` threshold
