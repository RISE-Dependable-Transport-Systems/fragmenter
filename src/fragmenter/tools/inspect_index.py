import sys
from pathlib import Path

import typer
from llama_index.core import Settings, VectorStoreIndex
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fragmenter.rag.utils import MockEmbedding
from fragmenter.rag.vector_stores import create_chroma_vector_store
from fragmenter.utils.logging import setup_logging

console = Console()

app = typer.Typer(help="Inspect the contents and statistics of a RAG index.")


@app.command()
def main(
    storage_dir: Path = typer.Option(
        "vector_store",
        "--storage-dir",
        "-s",
        help="Directory containing the index.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    logs_dir: Path | None = typer.Option(
        None,
        "--logs-dir",
        "-l",
        help="Directory for logs (optional).",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Inspect the RAG index and display statistics.

    Shows:
    - Number of documents/nodes
    - Chunk statistics (length distribution)
    - Node types
    - Source directories
    - Example file paths
    """
    # Setup logging with appropriate level
    log_level = "DEBUG" if debug else "INFO"
    if logs_dir:
        setup_logging(logs_dir=logs_dir, level=log_level)
    else:
        setup_logging(level=log_level)

    # Configure settings to avoid OpenAI requirement
    # Suppress the MockLLM message by temporarily redirecting stdout
    old_stdout = sys.stdout
    sys.stdout = open("/dev/null", "w")
    Settings.embed_model = MockEmbedding(embed_batch_size=10)
    Settings.llm = None
    sys.stdout.close()
    sys.stdout = old_stdout

    logger.info(f"Loading index from {storage_dir}...")
    try:
        # Load Chroma vector store
        vector_store, storage_context = create_chroma_vector_store(
            persist_path=storage_dir,
            collection_name="documents",
        )

        # Check vector store status
        collection_count = vector_store._collection.count()
        docstore_count = len(storage_context.docstore.docs)

        logger.info(f"Vector store contains {collection_count} vectors")
        logger.info(f"Docstore contains {docstore_count} documents")

        if collection_count == 0 and docstore_count == 0:
            console.print(
                "\n[red]Error: Index is empty. Please build the index first.[/red]\n"
            )
            raise typer.Exit(code=1)

        if collection_count == 0 and docstore_count > 0:
            console.print(
                "\n[yellow]Warning: Vector store is empty but docstore has entries. "
                "Index may be corrupted.[/yellow]\n"
            )

        # Reconstruct index from vector store (not used, but validates the setup)
        VectorStoreIndex.from_vector_store(
            vector_store=vector_store, storage_context=storage_context
        )
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        raise typer.Exit(code=1)

    logger.info("Index loaded successfully")
    logger.info("Analyzing index contents...\n")

    # Get data from Chroma collection directly (ChromaDB stores the actual content)
    chroma_collection = vector_store._collection
    chroma_data = chroma_collection.get(include=["metadatas", "documents"])

    # Use Chroma data as primary source since it has the actual stored content
    docs = {}
    if chroma_data and chroma_data["ids"]:
        for i, doc_id in enumerate(chroma_data["ids"]):
            # Get the text content
            text_content = (
                chroma_data["documents"][i] if chroma_data["documents"] else ""
            )
            metadata = chroma_data["metadatas"][i] if chroma_data["metadatas"] else {}

            # Create a simple object to hold document data
            class SimpleDoc:
                def __init__(self, doc_id, text, metadata):
                    self.id_ = doc_id
                    self.text = text
                    self.metadata = metadata

                def get_content(self):
                    return self.text

            docs[doc_id] = SimpleDoc(doc_id, text_content, metadata)

    # Collect statistics
    file_paths = set()
    chunk_lengths = []
    node_types = {}
    metadata_keys = set()
    repositories = set()
    file_types = set()

    # Track min/max chunks
    min_chunk = {"length": float("inf"), "file": None, "content": None}
    max_chunk = {"length": 0, "file": None, "content": None}

    # New statistics
    code_chunks = 0
    doc_chunks = 0
    repo_stats = {}  # repo -> chunk count
    depth_distribution = {}  # depth -> count
    empty_chunks = []  # Track problematically small chunks

    for doc_id, doc in docs.items():
        # Initialize file_path to avoid unbound variable issues
        file_path = None

        # doc is likely a BaseNode or Document
        if hasattr(doc, "metadata"):
            # Collect all metadata keys to understand what's available
            metadata_keys.update(doc.metadata.keys())

            # Try multiple possible keys for file path
            file_path = (
                doc.metadata.get("relative_path")
                or doc.metadata.get("file_path")
                or doc.metadata.get("file_name")
            )
            if file_path:
                file_paths.add(file_path)

            # Collect repository info
            repo = doc.metadata.get("repository")
            if repo:
                repositories.add(repo)

            # Collect file types
            file_type = doc.metadata.get("file_type")
            if file_type:
                file_types.add(file_type)

            # Track content type distribution
            if doc.metadata.get("is_code"):
                code_chunks += 1
            if doc.metadata.get("is_documentation"):
                doc_chunks += 1

            # Track repository statistics
            if repo:
                repo_stats[repo] = repo_stats.get(repo, 0) + 1

            # Track depth distribution
            depth = doc.metadata.get("depth")
            if depth is not None:
                depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

        # Analyze content length and track min/max
        content = None
        if hasattr(doc, "get_content"):
            content = doc.get_content()
            length = len(content)
        elif hasattr(doc, "text"):
            content = getattr(doc, "text")
            length = len(content)
        else:
            continue

        chunk_lengths.append(length)

        # Track very small chunks (potential quality issues)
        if length < 50:  # Less than 50 characters is suspiciously small
            empty_chunks.append(
                {
                    "file": file_path or "Unknown",
                    "length": length,
                    "content": content[:100] if content else "",
                }
            )

        # Update min chunk
        if length < min_chunk["length"]:
            min_chunk["length"] = length
            min_chunk["file"] = file_path or "Unknown"
            min_chunk["content"] = content[:200] if content else ""

        # Update max chunk
        if length > max_chunk["length"]:
            max_chunk["length"] = length
            max_chunk["file"] = file_path or "Unknown"
            max_chunk["content"] = content[:200] if content else ""

        # Analyze node type if available (class name)
        type_name = type(doc).__name__
        node_types[type_name] = node_types.get(type_name, 0) + 1

    # Display report using Rich
    console.print()
    console.print(
        Panel(
            "[bold cyan]INDEX INSPECTION REPORT[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    # Overview section
    overview = Table.grid(padding=(0, 2))
    overview.add_column(style="bold")
    overview.add_column()
    overview.add_row("Total Chunks:", f"[green]{len(docs):,}[/green]")
    overview.add_row("Unique Files:", f"[green]{len(file_paths):,}[/green]")
    if repositories:
        repos_str = ", ".join(sorted(repositories))
        overview.add_row("Repositories:", f"[yellow]{repos_str}[/yellow]")

    # Add node type info to overview (all are Document in current implementation)
    if len(node_types) == 1:
        type_name = list(node_types.keys())[0]
        overview.add_row("Node Type:", f"[dim]{type_name}[/dim]")

    console.print(Panel(overview, title="📊 Overview", border_style="blue"))

    # Chunk statistics
    if chunk_lengths:
        avg_len = sum(chunk_lengths) / len(chunk_lengths)

        stats_table = Table.grid(padding=(0, 2))
        stats_table.add_column(style="bold")
        stats_table.add_column(justify="right", style="green")
        stats_table.add_row("Count:", f"{len(chunk_lengths):,}")
        stats_table.add_row("Average Length:", f"{avg_len:,.0f}")
        stats_table.add_row("Min Length:", f"[red]{min(chunk_lengths):,}[/red]")
        stats_table.add_row("Max Length:", f"[yellow]{max(chunk_lengths):,}[/yellow]")

        console.print(
            Panel(
                stats_table,
                title="📏 Chunk Statistics (Characters)",
                border_style="blue",
            )
        )

        # Min/Max chunk details
        if min_chunk["file"]:
            min_content = Text(min_chunk["content"], overflow="fold")
            min_info = (
                f"[bold]File:[/bold] [cyan]{min_chunk['file']}[/cyan]\n"
                f"[bold]Length:[/bold] [red]{min_chunk['length']:,}[/red] "
                "characters\n\n"
                f"[bold]Content Preview:[/bold]\n"
            )
            console.print(
                Panel(
                    min_info + min_content.plain,
                    title="🔽 Smallest Chunk",
                    border_style="red",
                )
            )

        if max_chunk["file"]:
            max_content = Text(max_chunk["content"] + "...", overflow="fold")
            max_info = (
                f"[bold]File:[/bold] [cyan]{max_chunk['file']}[/cyan]\n"
                f"[bold]Length:[/bold] [yellow]{max_chunk['length']:,}[/yellow] "
                "characters\n\n"
                f"[bold]Content Preview:[/bold]\n"
            )
            console.print(
                Panel(
                    max_info + max_content.plain,
                    title="🔼 Largest Chunk",
                    border_style="yellow",
                )
            )

        # Distribution histogram
        hist_table = Table.grid()
        hist_table.add_column(style="cyan", width=12)
        hist_table.add_column(justify="right", style="green", width=8)
        hist_table.add_column()

        buckets = [0, 500, 1000, 1500, 2000, 3000, 5000]
        for i in range(len(buckets)):
            lower = buckets[i]
            upper = buckets[i + 1] if i + 1 < len(buckets) else float("inf")
            count = sum(1 for length in chunk_lengths if lower <= length < upper)
            label = (
                f"{lower:>5}-{upper:<5}" if upper != float("inf") else f"{lower:>5}+"
            )
            bar_width = int((count / len(chunk_lengths)) * 40)
            bar = "█" * bar_width
            hist_table.add_row(label, f"{count:,}", bar)

        console.print(
            Panel(hist_table, title="📊 Length Distribution", border_style="blue")
        )

    # Content type distribution
    if code_chunks or doc_chunks:
        content_table = Table.grid(padding=(0, 2))
        content_table.add_column(style="bold")
        content_table.add_column(justify="right", style="green")
        content_table.add_column(style="dim")

        total = len(chunk_lengths)
        content_table.add_row(
            "Code Chunks:", f"{code_chunks:,}", f"({code_chunks / total * 100:.1f}%)"
        )
        content_table.add_row(
            "Documentation Chunks:",
            f"{doc_chunks:,}",
            f"({doc_chunks / total * 100:.1f}%)",
        )
        other = total - code_chunks - doc_chunks
        if other > 0:
            content_table.add_row(
                "Other:", f"{other:,}", f"({other / total * 100:.1f}%)"
            )

        console.print(
            Panel(
                content_table,
                title="📝 Content Type Distribution",
                border_style="blue",
            )
        )

    # Repository breakdown
    if repo_stats:
        repo_table = Table.grid(padding=(0, 2))
        repo_table.add_column(style="bold cyan")
        repo_table.add_column(justify="right", style="green")
        repo_table.add_column(style="dim")

        total = sum(repo_stats.values())
        for repo, count in sorted(repo_stats.items(), key=lambda x: x[1], reverse=True):
            repo_table.add_row(repo, f"{count:,}", f"({count / total * 100:.1f}%)")

        console.print(
            Panel(repo_table, title="📚 Chunks per Repository", border_style="blue")
        )

    # Depth distribution
    if depth_distribution:
        depth_table = Table.grid(padding=(0, 2))
        depth_table.add_column(style="bold")
        depth_table.add_column(justify="right", style="green")
        depth_table.add_column()

        max_depth_count = max(depth_distribution.values())
        for depth in sorted(depth_distribution.keys()):
            count = depth_distribution[depth]
            bar_width = int((count / max_depth_count) * 30)
            bar = "█" * bar_width
            depth_table.add_row(f"Level {depth}:", f"{count:,}", bar)

        console.print(
            Panel(
                depth_table,
                title="📊 Directory Depth Distribution",
                border_style="blue",
            )
        )

    # Quality warnings
    if empty_chunks:
        warning_text = (
            f"[yellow]⚠️  Found {len(empty_chunks)} chunks"
            " with < 50 characters[/yellow]\n\n"
        )
        warning_text += "[dim]These may indicate parsing issues or noise:\n"
        for chunk in empty_chunks[:5]:  # Show first 5
            preview = chunk["content"][:30]
            warning_text += (
                f'  • {chunk["file"]} ({chunk["length"]} chars): "{preview}..."\n'
            )
        if len(empty_chunks) > 5:
            warning_text += f"  ... and {len(empty_chunks) - 5} more[/dim]"

        console.print(
            Panel(warning_text, title="⚠️  Quality Warnings", border_style="yellow")
        )

    # File types
    if file_types:
        file_types_text = ", ".join(sorted(file_types))
        console.print(
            Panel(file_types_text, title="📁 File Types", border_style="blue")
        )

    # Metadata keys
    if metadata_keys:
        metadata_text = ", ".join(sorted(metadata_keys))
        console.print(
            Panel(metadata_text, title="🏷️  Metadata Keys", border_style="blue")
        )

    # Sample directories (show top-level only for brevity)
    dirs = set()
    for fp in file_paths:
        parent = Path(fp).parent
        # Get top-level directory
        if parent != Path("."):
            top_level = str(parent).split("/")[0]
            dirs.add(top_level)
        else:
            dirs.add(".")

    if dirs:
        # Create a table with columns for directories
        dir_table = Table.grid(padding=(0, 2))
        for _ in range(4):  # 4 columns
            dir_table.add_column()

        sorted_dirs = sorted(dirs)
        for i in range(0, len(sorted_dirs), 4):
            row = sorted_dirs[i : i + 4]
            # Pad with empty strings if needed
            while len(row) < 4:
                row.append("")
            dir_table.add_row(*row)

        console.print(
            Panel(
                dir_table,
                title="📂 Source Directories (Top-level)",
                border_style="blue",
            )
        )

    # Sample file paths
    if file_paths:
        sample_paths = "\n".join(sorted(file_paths)[:10])
        console.print(
            Panel(
                sample_paths,
                title="📄 Sample File Paths (First 10)",
                border_style="blue",
            )
        )

    console.print()


if __name__ == "__main__":
    app()
