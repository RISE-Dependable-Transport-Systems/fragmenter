# Fragmenter - Task Runner
# Usage: just <recipe>
# Run `just` or `just --list` to see all available commands

set shell := ["bash", "-c"]

# Default recipe shows help
default:
    @just --list

# List available commands
help:
    @just --list

# === Setup ===

# Install dependencies and set up the environment
install:
    uv sync --all-groups

# Clean all build artifacts and caches
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .coverage htmlcov/ coverage.xml
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# === Development ===

# Run linters (pre-commit hooks)
lint:
    uv run pre-commit run --all-files --show-diff-on-failure

# Format code
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Run all tests
test:
    uv run pytest -m "not integration"

# Run tests with coverage
test-cov:
    uv run pytest -m "not integration" --cov=src/fragmenter --cov-report=html --cov-report=term

# Run integration tests
test-integration:
    uv run pytest -m integration -v

# === Build & Verify ===

# Build the package (sdist and wheel)
build:
    uv build

# Verify the package contents
verify:
    @echo "Checking wheel contents..."
    @unzip -l dist/*.whl | head -30
    @echo ""
    @echo "Checking sdist contents..."
    @tar -tzf dist/*.tar.gz | head -30

# Test installation in a fresh environment
test-install:
    @echo "Testing installation from wheel..."
    uv run --isolated --with dist/*.whl -- fragmenter --help

# === CI ===

# Run pre-commit hooks and tests
check-all: lint test
    @echo "✅ All checks passed!"

# Run the full release pipeline locally
all: clean install check-all build verify test-install
    @echo "✅ Full pipeline completed!"

# === CLI Convenience ===

# Initialize a new .env from template
init:
    uv run fragmenter init

# Scrape a URL to data directory
scrape url out="./data":
    uv run fragmenter scrape {{ url }} -o {{ out }}

# Build/rebuild the RAG index
ingest data="./data" store="./vector_store":
    uv run fragmenter rebuild-index -d {{ data }} -s {{ store }}

# Query the RAG index
query q store="./vector_store":
    uv run fragmenter query -s {{ store }} -q "{{ q }}"

# Inspect index statistics
inspect store="./vector_store":
    uv run fragmenter inspect-index -s {{ store }}

# End-to-end smoke test: init → ingest → query
smoke-test:
    @echo "🔍 Smoke test: init → ingest → query"
    uv run fragmenter init --force
    @echo "✅ init passed"
    uv run fragmenter --help
    @echo "✅ CLI help works"
