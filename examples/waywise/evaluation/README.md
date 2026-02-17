# RAG Evaluation Tools

This directory contains tools for evaluating the RAG index.

## Prerequisites

Install the required dependencies:

```bash
uv add --dev pandas matplotlib scikit-learn umap-learn ragas
```

## Scripts

### 1. `analyze_structure.py`

Analyzes the structural properties of the index.

- **Does not require API keys.**
- Generates plots in `tools/evaluation/plots/`:
  - `chunk_size_distribution.png`: Histogram of chunk lengths.
  - `embedding_clusters.png`: UMAP visualization of embedding space.
- Prints statistics about chunk sizes.

Usage:

```bash
uv run tools/evaluation/analyze_structure.py
```

### 2. `evaluate_with_ragas.py`

Evaluates the RAG pipeline using the **Ragas** framework.

- **Requires `OPENAI_API_KEY`**.
- Generates synthetic questions from the index.
- Queries the RAG pipeline.
- Computes metrics:
  - **Faithfulness**: Is the answer derived from the context?
  - **Answer Relevancy**: Is the answer relevant to the question?
  - **Context Precision**: Is the relevant context ranked high?
  - **Context Recall**: Is the relevant context retrieved?
- Saves results to `tools/evaluation/results/ragas_metrics.csv`.

Usage:

```bash
export OPENAI_API_KEY=sk-...
uv run tools/evaluation/evaluate_with_ragas.py
```
