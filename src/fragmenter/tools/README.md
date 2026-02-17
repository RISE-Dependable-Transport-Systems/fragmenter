# RAG Tools

CLI tools for managing and querying the RAG index.

## Unified CLI

All tools are available through the `fragmenter` command with subcommands:

```bash
# Main command
uv run fragmenter --help

# Subcommands (with hyphenated names)
uv run fragmenter init
uv run fragmenter scrape
uv run fragmenter rebuild-index
uv run fragmenter query
uv run fragmenter inspect-index
uv run fragmenter collect-extensions
```

### Global Options

These options are available for most subcommands:

- `--logs-dir`, `-l`: Directory for logs (optional)
- `--debug`: Enable debug logging
- `--env-file`: Path to .env file (for commands that need it)

## Tools

### init

Create a `.env` configuration template in your project directory.

**Usage:**

```bash
# Create .env file
uv run fragmenter init

# With uvx (no installation!)
uvx fragmenter init

# Force overwrite existing .env
uv run fragmenter init --force
```

This creates a `.env` file with all available configuration options documented.

### scrape

Scrape content from websites and save as markdown or HTML.

**Usage:**

```bash
# Scrape as markdown (default)
uv run fragmenter scrape https://example.com --output-dir ./data

# Scrape as HTML
uv run fragmenter scrape https://example.com -o ./data --format html

# With logs and debug
uv run fragmenter scrape https://deepwiki.com/YourOrg/YourProject \
    -o ./data/docs \
    --logs-dir ./logs \
    --debug
```

### query

Query a RAG index with natural language questions and save responses to files.

**Features:**

- Multiple LLM providers (OpenAI, Anthropic, Ollama, HuggingFace)
- File or string input for queries
- Save responses to files
- Extract code blocks only (with language filtering)
- Rich colored output with syntax highlighting
- Environment variable configuration with CLI overrides
- Works with any RAG index (not example-specific)

**Basic Usage:**

```bash
# Query with string
uv run fragmenter query \
    --storage-dir examples/waywise/vector_store \
    --query "How do I initialize a truck?"

# Query from file
uv run fragmenter query \
    -s examples/waywise/vector_store \
    -f my_question.txt

# Save response to file
uv run fragmenter query \
    -s examples/waywise/vector_store \
    -q "Write a basic main.cpp for WayWise" \
    -o generated_main.cpp

# Extract only code blocks
uv run fragmenter query \
    -s examples/waywise/vector_store \
    -q "Show me a C++ example" \
    -o output.cpp \
    --code-only \
    --language cpp
```

**Advanced Configuration:**

```bash
# Use Anthropic Claude
uv run fragmenter query \
    -s vector_store \
    -q "Explain the architecture" \
    --llm-provider anthropic \
    --llm-model claude-3-5-sonnet-20241022

# Use local Ollama
uv run fragmenter query \
    -s vector_store \
    -q "How does this work?" \
    --llm-provider ollama \
    --llm-model llama3.2 \
    --ollama-url http://localhost:11434

# Use HuggingFace embeddings
uv run fragmenter query \
    -s vector_store \
    -q "Tell me about the system" \
    --embed-provider huggingface \
    --embed-model BAAI/bge-small-en-v1.5
```

**Environment Variables:**

Create a `.env` file:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HUGGINGFACEHUB_API_TOKEN=hf-...

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=512

# Embedding Configuration
EMBED_PROVIDER=openai
EMBED_MODEL=text-embedding-3-small
```

CLI arguments override environment variables.

**Example: Overwrite main.cpp**

```bash
# Generate and overwrite main.cpp with code only
uv run fragmenter query \
    -s examples/waywise/vector_store \
    -q "Write a complete main.cpp file for initializing and running a truck in WayWise" \
    -o examples/waywise/data/code/precise-truck/main.cpp \
    --code-only \
    --language cpp
```

### rebuild-index

Build or update the RAG index with automatic incremental updates.

**Features:**

- Hash-based change detection (only processes changed files)
- Automatic deletion handling (removes stale documents)
- File-type-specific parsing (Markdown, Code, Text, PDF)

**Usage:**

```bash
# Using absolute paths
uv run fragmenter rebuild-index \
    --data-dir /path/to/data \
    --storage-dir /path/to/vector_store

# Using relative paths
uv run fragmenter rebuild-index \
    -d examples/waywise/data \
    -s examples/waywise/vector_store

# With logs and debug
uv run fragmenter rebuild-index \
    -d data \
    -s storage \
    --logs-dir logs \
    --debug
```

**With config.py:**

```python
# examples/waywise/rebuild.py
from config import settings
from fragmenter.cli import app

if __name__ == "__main__":
    import sys
    sys.argv = [
        "rebuild-index",
        "--data-dir", str(settings.absolute_data_dir),
        "--storage-dir", str(settings.absolute_storage_dir),
        "--logs-dir", str(settings.absolute_logs_dir),
    ]
    app()
```

### inspect-index

Inspect the contents and statistics of a RAG index.

**Shows:**

- Number of documents/nodes
- Chunk statistics (length distribution)
- Node types
- Source directories
- Example file paths

**Usage:**

```bash
# Default (looks for vector_store in current dir)
uv run fragmenter inspect-index

# Custom storage dir
uv run fragmenter inspect-index \
    -s examples/waywise/vector_store

# With logs and debug
uv run fragmenter inspect-index \
    -s vector_store \
    --logs-dir logs \
    --debug
```

### collect-extensions

Scan a directory and list all unique file extensions.

**Use case:** Discover what file types exist in your data directory before configuring the RAG ingestion pipeline.

**Usage:**

```bash
# Default (scans data/code)
uv run fragmenter collect-extensions

# Custom directory
uv run fragmenter collect-extensions examples/waywise/data

# Include .git directories
uv run fragmenter collect-extensions \
    data \
    --include-git

# With logs and debug
uv run fragmenter collect-extensions \
    data \
    --logs-dir logs \
    --debug
```

## Integration with config.py

Create wrapper scripts in your examples directory:

```python
# examples/waywise/tools.py
import sys
from config import settings
from fragmenter.cli import app

def rebuild():
    sys.argv = [
        "rebuild-index",
        "--data-dir", str(settings.absolute_data_dir),
        "--storage-dir", str(settings.absolute_storage_dir),
        "--logs-dir", str(settings.absolute_logs_dir),
    ]
    app()

def inspect():
    sys.argv = [
        "inspect-index",
        "--storage-dir", str(settings.absolute_storage_dir),
        "--logs-dir", str(settings.absolute_logs_dir),
    ]
    app()

if __name__ == "__main__":
    import typer
    cli = typer.Typer()
    cli.command()(rebuild)
    cli.command()(inspect)
    cli()
```

Then run:

```bash
cd examples/waywise
uv run python tools.py rebuild
uv run python tools.py inspect
```

## Legacy Usage (Direct Module Execution)

Note: The old `python -m fragmenter.tools.<tool>` invocation method is no longer supported.
Please use the unified `fragmenter` CLI instead.
