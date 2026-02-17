from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from llama_index.core import Settings, StorageContext, load_index_from_storage
from loguru import logger
from umap import UMAP

from fragmenter.rag.utils import MockEmbedding


def analyze_index_structure(storage_dir: Path, output_dir: Path) -> None:
    """
    Loads a vector index and generates structural analysis plots.

    Args:
        storage_dir: Path to the persisted vector store.
        output_dir: Path where plots will be saved.
    """
    # Configure settings to avoid OpenAI requirement for loading
    Settings.embed_model = MockEmbedding()
    Settings.llm = None

    logger.info(f"Loading index from {storage_dir}...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context)
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return

    logger.info("Index loaded. Extracting nodes...")

    docstore = index.docstore
    nodes = docstore.docs.values()

    # Try to get embeddings from vector store if not in nodes
    vector_store = index.vector_store
    logger.info(f"Vector store type: {type(vector_store)}")

    # For SimpleVectorStore, embeddings are in data.embedding_dict
    embedding_dict = {}
    if hasattr(vector_store, "data") and hasattr(vector_store.data, "embedding_dict"):
        embedding_dict = vector_store.data.embedding_dict
        logger.info(f"Found {len(embedding_dict)} embeddings in vector store.")

    data: list[dict[str, Any]] = []
    embeddings = []

    for node in nodes:
        # Skip if not a BaseNode (e.g. if it's a Document)
        if not hasattr(node, "get_content"):
            continue

        content = node.get_content()
        metadata = node.metadata or {}
        file_path = metadata.get("file_path", "unknown")
        file_type = Path(file_path).suffix if file_path != "unknown" else "unknown"

        # Check for embedding in node or vector store
        emb = node.embedding
        if emb is None and node.node_id in embedding_dict:
            emb = embedding_dict[node.node_id]

        node_data = {
            "id": node.node_id,
            "length": len(content),
            "file_path": file_path,
            "file_type": file_type,
            "has_embedding": emb is not None,
        }
        data.append(node_data)

        if emb:
            embeddings.append(emb)

    df = pd.DataFrame(data)
    logger.info(f"Extracted {len(df)} nodes.")

    # Create plots directory
    output_dir.mkdir(exist_ok=True, parents=True)

    # 1. Chunk Size Distribution
    logger.info("Generating chunk size distribution plot...")
    plt.figure(figsize=(10, 6))
    plt.hist(df["length"], bins=50, alpha=0.7, color="blue", edgecolor="black")
    plt.title("Chunk Size Distribution (Characters)")
    plt.xlabel("Length")
    plt.ylabel("Count")
    plt.grid(axis="y", alpha=0.5)
    plt.savefig(output_dir / "chunk_size_distribution.png")
    plt.close()

    logger.info(f"Chunk size stats:\n{df['length'].describe()}")

    # 2. Embedding Visualization (UMAP)
    if embeddings:
        logger.info(f"Reducing {len(embeddings)} embeddings with UMAP...")
        reducer = UMAP(random_state=42)
        embedding_matrix = np.array(embeddings)

        # Check if we have enough data for UMAP
        if len(embeddings) > 5:
            try:
                reduced_embeddings = reducer.fit_transform(embedding_matrix)

                # Add reduced coords to dataframe (only for nodes with embeddings)
                df_with_emb = df[df["has_embedding"]].copy()
                df_with_emb["x"] = reduced_embeddings[:, 0]
                df_with_emb["y"] = reduced_embeddings[:, 1]

                plt.figure(figsize=(12, 8))

                # Color by file type
                file_types = df_with_emb["file_type"].unique()
                for ft in file_types:
                    subset = df_with_emb[df_with_emb["file_type"] == ft]
                    plt.scatter(subset["x"], subset["y"], label=ft, alpha=0.6, s=10)

                plt.title("Embedding Space (UMAP)")
                plt.legend()
                plt.savefig(output_dir / "embedding_clusters.png")
                plt.close()
                logger.info(f"Embedding plot saved to {output_dir}")
            except Exception as e:
                logger.error(f"Error during UMAP reduction: {e}")
        else:
            logger.warning("Not enough embeddings for UMAP.")
    else:
        logger.warning("No embeddings found in nodes.")
