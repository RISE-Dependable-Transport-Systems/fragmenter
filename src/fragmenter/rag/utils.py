from llama_index.core.embeddings import BaseEmbedding


class MockEmbedding(BaseEmbedding):
    """Mock embedding model to avoid API calls during inspection/testing."""

    def _get_query_embedding(self, query: str) -> list[float]:
        return []

    def _get_text_embedding(self, text: str) -> list[float]:
        return []

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return []

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return []
