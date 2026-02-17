from pathlib import Path

from examples.waywise.config import settings

from fragmenter.evaluation.index_analysis import analyze_index_structure
from fragmenter.utils.logging import setup_logging


def main():
    setup_logging(logs_dir=settings.absolute_logs_dir)
    plots_dir = Path(__file__).parent / "plots"
    analyze_index_structure(
        storage_dir=settings.absolute_storage_dir, output_dir=plots_dir
    )


if __name__ == "__main__":
    main()
