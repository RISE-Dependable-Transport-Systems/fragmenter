"""Base configuration for the fragmenter RAG tool."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    """Base settings for RAG system with LLM and embedding configuration.

    All settings can be overridden via environment variables.
    No prefix by default - use standard names like LLM_PROVIDER, LLM_MODEL, etc.

    Example .env file:
        OPENAI_API_KEY=sk-...
        LLM_PROVIDER=openai
        LLM_MODEL=gpt-4o-mini
        EMBED_PROVIDER=openai
        EMBED_MODEL=text-embedding-3-small
    """

    # LLM Configuration
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 512
    LLM_TIMEOUT: float = 600.0  # Request timeout in seconds (10 minutes default)
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Embedding Configuration
    EMBED_PROVIDER: str = "openai"
    EMBED_MODEL: str = "text-embedding-3-small"

    # Metadata Configuration
    RELATIVE_PATHS: bool = True
    INCLUDE_FILE_CATEGORIZATION: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow subclasses to add fields
    )

    def configure_llm_settings(self):
        """Configure LlamaIndex global Settings based on environment variables.

        This method should be called before using any LlamaIndex functionality
        to ensure the correct LLM and embedding models are configured.
        """
        from llama_index.core import Settings as LlamaSettings

        # Configure LLM
        if self.LLM_PROVIDER == "openai":
            try:
                from llama_index.llms.openai import OpenAI
            except ImportError:
                raise ImportError(
                    "OpenAI provider requires the 'openai' extra. "
                    "Install with: uv pip install 'fragmenter[openai]'"
                )

            LlamaSettings.llm = OpenAI(
                model=self.LLM_MODEL,
                temperature=self.LLM_TEMPERATURE,
                max_tokens=self.LLM_MAX_TOKENS,
                api_key=os.getenv("OPENAI_API_KEY"),
                timeout=self.LLM_TIMEOUT,
            )
        elif self.LLM_PROVIDER == "anthropic":
            try:
                from llama_index.llms.anthropic import Anthropic
            except ImportError:
                raise ImportError(
                    "Anthropic provider requires the 'anthropic' extra. "
                    "Install with: uv pip install 'fragmenter[anthropic]'"
                )

            LlamaSettings.llm = Anthropic(
                model=self.LLM_MODEL,
                temperature=self.LLM_TEMPERATURE,
                max_tokens=self.LLM_MAX_TOKENS,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif self.LLM_PROVIDER == "ollama":
            try:
                from llama_index.llms.ollama import Ollama
            except ImportError:
                raise ImportError(
                    "Ollama provider requires the 'ollama' extra. "
                    "Install with: uv pip install 'fragmenter[ollama]'"
                )

            LlamaSettings.llm = Ollama(
                model=self.LLM_MODEL,
                base_url=self.OLLAMA_BASE_URL,
                temperature=self.LLM_TEMPERATURE,
            )
        elif self.LLM_PROVIDER == "huggingface":
            try:
                from llama_index.llms.huggingface import HuggingFaceInferenceAPI
            except ImportError:
                raise ImportError(
                    "HuggingFace provider requires the 'huggingface' extra. "
                    "Install with: uv pip install 'fragmenter[huggingface]'"
                )

            LlamaSettings.llm = HuggingFaceInferenceAPI(
                model_name=self.LLM_MODEL,
                token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            )

        # Configure Embeddings
        if self.EMBED_PROVIDER == "openai":
            try:
                from llama_index.embeddings.openai import OpenAIEmbedding
            except ImportError:
                raise ImportError(
                    "OpenAI embeddings require the 'openai' extra. "
                    "Install with: uv pip install 'fragmenter[openai]'"
                )

            LlamaSettings.embed_model = OpenAIEmbedding(
                model=self.EMBED_MODEL,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif self.EMBED_PROVIDER == "huggingface":
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            except ImportError:
                raise ImportError(
                    "HuggingFace embeddings require the 'huggingface' extra. "
                    "Install with: uv pip install 'fragmenter[huggingface]'"
                )

            LlamaSettings.embed_model = HuggingFaceEmbedding(
                model_name=self.EMBED_MODEL
            )
        elif self.EMBED_PROVIDER == "ollama":
            try:
                from llama_index.embeddings.ollama import OllamaEmbedding
            except ImportError:
                raise ImportError(
                    "Ollama embeddings require the 'ollama' extra. "
                    "Install with: uv pip install 'fragmenter[ollama]'"
                )

            LlamaSettings.embed_model = OllamaEmbedding(
                model_name=self.EMBED_MODEL, base_url=self.OLLAMA_BASE_URL
            )


# Global settings instance that can be imported by library tools
settings = RAGSettings()
