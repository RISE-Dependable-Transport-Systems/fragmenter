import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from examples.waywise.config import settings
from loguru import logger
from openai import AsyncOpenAI

# Ragas imports
from ragas.embeddings import OpenAIEmbeddings
from ragas.llms import llm_factory

from fragmenter.evaluation.data_loader import prepare_ragas_dataset
from fragmenter.evaluation.evaluator import create_evaluation_task
from fragmenter.rag.inference import load_index
from fragmenter.utils.logging import setup_logging

load_dotenv()


async def main():
    # 1. Setup
    setup_logging(logs_dir=settings.absolute_logs_dir)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    # 2. Load Resources
    try:
        logger.info("Loading LlamaIndex...")
        index = load_index(str(settings.absolute_storage_dir))

        # Prepare Dataset
        dataset = prepare_ragas_dataset(
            source_path=Path(__file__).parent / "dataset.json",
            storage_dir=Path(__file__).parent / "ragas_data",
        )

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

    # 3. Run Evaluation
    results = None
    try:
        logger.info(f"Starting evaluation on {len(dataset)} samples...")
        async with AsyncOpenAI(api_key=api_key) as client:
            # Initialize resources
            llm = llm_factory("gpt-4o-mini", client=client)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=client)

            # Create evaluation task with dependencies
            evaluate_row = create_evaluation_task(index, llm, embeddings)

            # Run experiment
            results = await evaluate_row.arun(dataset)
            logger.info("Batch evaluation completed. Closing client...")

            # Add delay for graceful shutdown
            await asyncio.sleep(0.25)

    except Exception as e:
        if results:
            logger.warning(f"Evaluation finished, but cleanup failed: {e}")
        else:
            logger.error(f"Evaluation process failed: {e}")
        # Continue to save whatever results we have

    # 4. Log Results Location
    # Ragas automatically saves results to the configured dataset storage directory
    # with a random run name (e.g., 'adoring_tarjan.csv')
    try:
        # results is an Experiment object which typically has a 'name' attribute
        run_name = getattr(results, "name", "unknown_run")
        # We need to reconstruct the path since we moved the dir logic to data_loader
        dataset_storage_dir = Path(__file__).parent / "ragas_data"
        csv_path = dataset_storage_dir / "experiments" / f"{run_name}.csv"

        logger.success("Evaluation completed.")
        logger.info(f"Ragas automatically saved results to: {csv_path}")

    except Exception as e:
        logger.error(f"Failed to locate automatic results: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) != "Event loop is closed":
            raise
