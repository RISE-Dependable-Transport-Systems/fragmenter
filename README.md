# 🧩🔎 `fragmenter`

[![uv][uv-badge]][uv]
[![PyPI][pypi-badge]][pypi]
[![Python Version][python-badge]][pypi]
[![Tests][tests-badge]][tests]
[![License][license-badge]][license]
[![Code style: ruff][ruff-badge]][ruff]
[![Conventional Commits][cc-badge]][cc]

[uv]: https://github.com/astral-sh/uv
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[pypi-badge]: https://img.shields.io/pypi/v/fragmenter
[pypi]: https://pypi.org/project/fragmenter/
[python-badge]: https://img.shields.io/pypi/pyversions/fragmenter
[tests-badge]: https://github.com/RISE-Dependable-Transport-Systems/fragmenter/actions/workflows/test.yaml/badge.svg
[tests]: https://github.com/RISE-Dependable-Transport-Systems/fragmenter/actions/workflows/test.yaml
[license-badge]: https://img.shields.io/github/license/RISE-Dependable-Transport-Systems/fragmenter
[license]: ./LICENSE
[ruff]: https://github.com/astral-sh/ruff
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[cc-badge]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg
[cc]: https://www.conventionalcommits.org/en/v1.1.0/

Build powerful RAG (Retrieval-Augmented Generation) systems with multiple LLM providers and zero configuration hassle.

---

## ✨ Features

- 🤖 **Multiple LLM Providers**: OpenAI, Anthropic, Ollama, and HuggingFace support out-of-the-box
- 🔄 **Smart Incremental Updates**: Only processes changed files — no wasted computation
- 📄 **Intelligent Parsing**: Automatic file-type detection for Markdown, Code, PDF, and more
- 🎨 **Beautiful CLI**: Rich formatting with colors and progress indicators
- 🌐 **Web Scraping**: Built-in scraper to ingest content from websites
- 💾 **Vector Store Persistence**: Save and reload indexes efficiently
- 🔍 **Code Extraction**: Automatically extract code blocks from LLM responses
- ⚙️ **Environment-Based Config**: Simple `.env` file configuration
- 🚀 **Zero-Code Usage**: CLI tools for complete workflows without writing code
- 📦 **Library Mode**: Full programmatic API for custom integrations

---

## 📦 Installation

### Install as a CLI tool (recommended)

```bash
# Install globally as a tool
uv tool install 'fragmenter[openai]'

# Or run instantly without installing
uvx fragmenter init
```

### Add as a project dependency

Install the core package **plus the provider(s) you need**:

```bash
# Pick one (or more) LLM provider extras:
uv add 'fragmenter[openai]'        # OpenAI  (default provider)
uv add 'fragmenter[anthropic]'      # Anthropic
uv add 'fragmenter[ollama]'         # Ollama  (local models)
uv add 'fragmenter[huggingface]'    # HuggingFace

# Or combine several:
uv add 'fragmenter[openai,ollama]'

# Or install everything:
uv add 'fragmenter[all-providers]'
```

### Traditional pip install

```bash
pip install 'fragmenter[openai]'
```

> [!NOTE]
> LLM provider packages are **not** included in the base install to keep downloads small.
> If you see an `ImportError` mentioning a missing extra, install the matching provider extra shown in the error message.

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python**: 3.12 or higher ✅
- **API Keys**: For your chosen LLM provider (OpenAI, Anthropic, etc.) 🔑

### 1. Initialize your project

```bash
# Create .env template
fragmenter init
```

Edit the generated `.env` file with your API credentials:

```bash
# .env
OPENAI_API_KEY=sk-your-actual-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBED_PROVIDER=openai
EMBED_MODEL=text-embedding-3-small
```

> [!NOTE]
> See the [Configuration](#️-configuration) section for all available providers and models.

### 2. Prepare your data

```bash
# Create data directory
mkdir data

# Add your documents (markdown, code, PDFs, etc.)
cp /path/to/your/docs/* ./data/
```

### 3. Build the index

```bash
fragmenter rebuild-index \
    --data-dir ./data \
    --storage-dir ./vector_store
```

**What happens next?** 🎬

1. 📁 Scans your data directory
2. 🔍 Detects file types and applies appropriate parsers
3. ✂️ Chunks documents intelligently
4. 🧮 Generates embeddings
5. 💾 Stores vectors for fast retrieval

### 4. Query your data

```bash
# Ask a question
fragmenter query \
    --storage-dir ./vector_store \
    --query "What is this data about?"
```

> [!TIP]
> Save responses to files with `--output` and extract code with `--code-only`:
>
> ```bash
> fragmenter query \
>     -s ./vector_store \
>     -q "Write a Python example" \
>     -o output.py \
>     --code-only \
>     --language python
> ```

---

## 🛠️ CLI Tools

### `init`

Create a `.env` template file in your project.

```bash
fragmenter init
```

### `scrape`

Scrape content from websites and save as markdown or HTML.

```bash
# Scrape as markdown (default)
fragmenter scrape \
    https://example.com \
    -o ./data

# Scrape as HTML
fragmenter scrape \
    https://example.com \
    -o ./data \
    --format html
```

### `rebuild_index`

Build or update the RAG index with automatic incremental updates.

```bash
fragmenter rebuild-index \
    --data-dir ./data \
    --storage-dir ./vector_store
```

> [!NOTE]
> Incremental updates mean only new or modified files are processed, saving time and compute resources.

### `query_index`

Query the index with natural language.

```bash
# Basic query
fragmenter query \
    -s ./vector_store \
    -q "Your question here"

# Query from file
fragmenter query \
    -s ./vector_store \
    -f question.txt

# Save output
fragmenter query \
    -s ./vector_store \
    -q "Generate code" \
    -o output.cpp \
    --code-only \
    --language cpp

# Use different provider
fragmenter query \
    -s ./vector_store \
    -q "Explain this" \
    --llm-provider anthropic \
    --llm-model claude-3-5-sonnet-20241022
```

### `inspect_index`

View index statistics and contents.

```bash
fragmenter inspect-index \
    -s ./vector_store
```

---

## ⚙️ Configuration

All settings can be configured via environment variables. Create a `.env` file or set them in your shell.

### LLM Providers

| Provider        | Extra          | Configuration                                                              |
| --------------- | -------------- | -------------------------------------------------------------------------- |
| **OpenAI**      | `[openai]`     | `LLM_PROVIDER=openai`<br>`LLM_MODEL=gpt-4o-mini`                           |
| **Anthropic**   | `[anthropic]`  | `LLM_PROVIDER=anthropic`<br>`LLM_MODEL=claude-3-5-sonnet-20241022`         |
| **Ollama**      | `[ollama]`     | `LLM_PROVIDER=ollama`<br>`LLM_MODEL=llama3.2`                              |
| **HuggingFace** | `[huggingface]`| `LLM_PROVIDER=huggingface`<br>`LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct` |

### Embedding Providers

| Provider        | Configuration                                                        |
| --------------- | -------------------------------------------------------------------- |
| **OpenAI**      | `EMBED_PROVIDER=openai`<br>`EMBED_MODEL=text-embedding-3-small`      |
| **HuggingFace** | `EMBED_PROVIDER=huggingface`<br>`EMBED_MODEL=BAAI/bge-small-en-v1.5` |
| **Ollama**      | `EMBED_PROVIDER=ollama`<br>`EMBED_MODEL=nomic-embed-text`            |

### Complete .env Example

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Embedding Configuration
EMBED_PROVIDER=openai
EMBED_MODEL=text-embedding-3-small

# Optional: Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: HuggingFace
HUGGINGFACE_TOKEN=hf_your-token-here
```

> [!CAUTION]
> Never commit your `.env` file to version control! Add it to `.gitignore` to protect your API keys.

---

## 💻 Using as a Library

If you need custom logic or want to integrate into your own application:

```python
from dotenv import load_dotenv
from fragmenter.config import RAGSettings
from fragmenter.rag.ingestion import build_index
from fragmenter.rag.inference import load_index, query_index

# Load configuration
load_dotenv()
settings = RAGSettings()
settings.configure_llm_settings()

# Build index
build_index(input_dir="./data", persist_dir="./vector_store")

# Query
index = load_index("./vector_store")
response = query_index(index, "Your question")
print(response)
```

---

## 🌱 Usage Examples

### Example 1: Documentation RAG

Build a RAG system for your project documentation:

```bash
# 1. Scrape your docs site
fragmenter scrape \
    https://docs.example.com \
    -o ./data/docs

# 2. Build the index
fragmenter rebuild-index \
    -d ./data \
    -s ./vector_store

# 3. Query
fragmenter query \
    -s ./vector_store \
    -q "How do I configure authentication?"
```

### Example 2: Code Analysis

Analyze a codebase and generate examples:

```bash
# 1. Copy code files to data directory
cp -r /path/to/project/src ./data/

# 2. Build index
fragmenter rebuild-index -d ./data -s ./vector_store

# 3. Generate code examples
fragmenter query \
    -s ./vector_store \
    -q "Show me how to use the authentication module" \
    -o example.py \
    --code-only \
    --language python
```

### Example 3: Research Assistant

Build a research assistant for papers and articles:

```bash
# 1. Add PDFs and markdown files to data/
# 2. Build index
fragmenter rebuild-index -d ./data -s ./vector_store

# 3. Query with different providers
fragmenter query \
    -s ./vector_store \
    -q "Summarize the key findings about neural networks" \
    --llm-provider anthropic \
    --llm-model claude-3-5-sonnet-20241022
```

> [!TIP]
> See [examples/waywise](https://github.com/RISE-Dependable-Transport-Systems/fragmenter/tree/main/examples/waywise) for a complete real-world example with custom configuration.

---

## 🔧 Troubleshooting

### � Missing Provider Errors

> [!WARNING]
> If you see an `ImportError` like _"…requires the 'openai' extra"_:
>
> ```bash
> uv add 'fragmenter[openai]'   # install the provider you need
> ```
>
> See the [LLM Providers](#llm-providers) table for all available extras.

### �🔐 Authentication Errors

> [!WARNING]
> If you encounter authentication errors:
>
> - ✅ Verify your API key is correct and not expired
> - ✅ Check that you've set the correct provider name (`openai`, not `OpenAI`)
> - ✅ Ensure API key environment variable names match your provider
> - ✅ Run `fragmenter init` to generate a fresh `.env` template

### 📁 File Parsing Issues

> [!NOTE]
> If certain files aren't being indexed:
>
> - Check file extensions are supported (`.md`, `.py`, `.pdf`, `.txt`, etc.)
> - Verify files are in the `--data-dir` path
> - Use `--log-level DEBUG` to see detailed parsing information
> - Check file permissions (files must be readable)

### 💾 Vector Store Errors

> [!TIP]
> If you see vector store errors:
>
> - Delete the `./vector_store` directory and rebuild from scratch
> - Ensure you have write permissions in the storage directory
> - Check available disk space
> - Verify embedding model is properly configured

### 🌐 Provider-Specific Issues

**Ollama:**

```bash
# Ensure Ollama is running
ollama serve

# Pull the model first
ollama pull llama3.2
```

**HuggingFace:**

- Set `HUGGINGFACE_TOKEN` for private models
- Some models require acceptance of terms on HuggingFace website

---

## 🛠️ Development

### Setup

```bash
git clone https://github.com/RISE-Dependable-Transport-Systems/fragmenter.git
cd fragmenter
uv sync --all-groups
```

### Common Tasks

```bash
just lint              # Run all linters via pre-commit
just fmt               # Auto-format code
just test              # Run unit tests
just test-cov          # Run tests with coverage
just build             # Build sdist and wheel
just check-all         # Lint + test
just all               # Full pipeline: clean → install → lint → test → build → verify → install-test
```

---

## 📖 Examples

- **Complete Real-World Example**: See [examples/waywise](https://github.com/RISE-Dependable-Transport-Systems/fragmenter/tree/main/examples/waywise) for a full setup with custom data, configuration, and evaluation scripts.
- **Developer Example**: See [examples/dev_examples/main.py](https://github.com/RISE-Dependable-Transport-Systems/fragmenter/blob/main/examples/dev_examples/main.py) for a programmatic usage demonstration of the RAG framework.

---

## 🙌 Contributing

Contributions welcome! Please ensure:

- ✅ Code is formatted (`just fmt`)
- ✅ All linters pass (`just lint`)
- ✅ Tests pass (`just test`)
- ✅ New features include tests and documentation
- 🔒 No API keys or secrets in commits

---

## 📄 License

[MIT License](./LICENSE) — see LICENSE file for details.
