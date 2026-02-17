import asyncio
from typing import Any

from loguru import logger
from pydantic import BaseModel
from ragas import experiment
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from fragmenter.rag.inference import query_index


class ExperimentResult(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_recall: float
    context_precision: float
    response: str
    retrieved_contexts: list[str]


async def get_rag_response(index: Any, query: str) -> Any:
    """
    Run the blocking RAG query in a thread executor to avoid blocking the event loop.
    """
    loop = asyncio.get_running_loop()
    # Run the synchronous query_index function in a separate thread
    return await loop.run_in_executor(None, query_index, index, query)


def create_evaluation_task(index: Any, llm: Any, embeddings: Any):
    # Initialize metrics once
    metric_faithfulness = Faithfulness(llm=llm)
    metric_relevancy = AnswerRelevancy(llm=llm, embeddings=embeddings)
    metric_recall = ContextRecall(llm=llm)
    metric_precision = ContextPrecision(llm=llm)

    @experiment(ExperimentResult)
    async def evaluate_row(row: dict[str, Any]):
        user_input = row["user_input"]
        reference = row["reference"]

        # 1. Query RAG System
        try:
            response_obj = await get_rag_response(index, user_input)
            response_text = response_obj.response
            retrieved_contexts = [
                node.node.get_content() for node in response_obj.source_nodes
            ]
        except Exception as e:
            logger.error(f"RAG query failed for '{user_input}': {e}")
            # Return empty/zero result on failure
            return ExperimentResult(
                faithfulness=0.0,
                answer_relevancy=0.0,
                context_recall=0.0,
                context_precision=0.0,
                response="Error during generation",
                retrieved_contexts=[],
            )

        # 2. Calculate Metrics
        faith_score = relevancy_score = recall_score = precision_score = None
        error_msg = None

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
            ):
                with attempt:
                    (
                        faith_score,
                        relevancy_score,
                        recall_score,
                        precision_score,
                    ) = await asyncio.gather(
                        metric_faithfulness.ascore(
                            user_input=user_input,
                            response=response_text,
                            retrieved_contexts=retrieved_contexts,
                        ),
                        metric_relevancy.ascore(
                            user_input=user_input, response=response_text
                        ),
                        metric_recall.ascore(
                            user_input=user_input,
                            retrieved_contexts=retrieved_contexts,
                            reference=reference,
                        ),
                        metric_precision.ascore(
                            user_input=user_input,
                            retrieved_contexts=retrieved_contexts,
                            reference=reference,
                        ),
                    )
        except Exception as e:
            error_msg = (
                f"Metrics calculation failed for '{user_input}' after retries: {e}"
            )

        if not error_msg and (
            faith_score is None
            or relevancy_score is None
            or recall_score is None
            or precision_score is None
        ):
            error_msg = f"Metrics calculation incomplete for '{user_input}'"

        if error_msg:
            logger.error(error_msg)
            return ExperimentResult(
                faithfulness=0.0,
                answer_relevancy=0.0,
                context_recall=0.0,
                context_precision=0.0,
                response=response_text,
                retrieved_contexts=retrieved_contexts,
            )

        # Ensure metrics are not None for type checker
        assert faith_score is not None
        assert relevancy_score is not None
        assert recall_score is not None
        assert precision_score is not None

        return ExperimentResult(
            faithfulness=faith_score.value,
            answer_relevancy=relevancy_score.value,
            context_recall=recall_score.value,
            context_precision=precision_score.value,
            response=response_text,
            retrieved_contexts=retrieved_contexts,
        )

    return evaluate_row
