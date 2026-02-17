import json
import uuid
from pathlib import Path

from loguru import logger
from ragas import Dataset


def load_raw_dataset(file_path: Path) -> list[dict[str, str]]:
    """Load the dataset from a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with open(file_path) as f:
        dataset = json.load(f)

    logger.info(f"Loaded {len(dataset)} samples from {file_path}")
    return dataset


def prepare_ragas_dataset(source_path: Path, storage_dir: Path) -> Dataset:
    """
    Loads raw data and initializes a Ragas Dataset with local storage.
    """
    raw_dataset = load_raw_dataset(source_path)

    # Ragas 0.4.0 requires a name and backend. We use a local directory for storage.
    storage_dir.mkdir(exist_ok=True, parents=True)

    dataset = Dataset(
        name="evaluation_dataset",
        backend="local/csv",
        root_dir=str(storage_dir),
    )

    # Append items to the dataset
    for row in raw_dataset:
        # Ensure each row has an ID
        if "id" not in row:
            row["id"] = str(uuid.uuid4())
        dataset.append(row)

    return dataset
