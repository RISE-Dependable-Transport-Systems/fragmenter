"""Tests for extractors.py module."""

from llama_index.core.llms import MockLLM

from fragmenter.rag.extractors import get_metadata_extractors


class TestGetMetadataExtractors:
    """Tests for get_metadata_extractors function."""

    def test_extractors_disabled_by_default(self):
        """Test that extractors are disabled by default."""
        llm = MockLLM()
        extractors = get_metadata_extractors(llm)

        assert extractors == []

    def test_extractors_disabled_explicitly(self):
        """Test explicitly disabling extractors."""
        llm = MockLLM()
        extractors = get_metadata_extractors(llm, enable_extractors=False)

        assert extractors == []

    def test_extractors_enabled(self):
        """Test enabling extractors."""
        llm = MockLLM()
        extractors = get_metadata_extractors(llm, enable_extractors=True)

        assert len(extractors) == 1
        # KeywordExtractor should be returned
        assert extractors[0].__class__.__name__ == "KeywordExtractor"

    def test_extractors_custom_keywords(self):
        """Test custom keyword count."""
        llm = MockLLM()
        extractors = get_metadata_extractors(llm, enable_extractors=True, keywords=10)

        assert len(extractors) == 1
        # Should have configured keyword count
        extractor = extractors[0]
        assert extractor.keywords == 10

    def test_extractors_default_keywords(self):
        """Test default keyword count."""
        llm = MockLLM()
        extractors = get_metadata_extractors(llm, enable_extractors=True)

        extractor = extractors[0]
        assert extractor.keywords == 5  # Default value

    def test_extractors_requires_llm(self):
        """Test that extractors work with provided LLM."""
        llm = MockLLM()

        extractors = get_metadata_extractors(llm, enable_extractors=True)

        # Should create extractor without error
        assert len(extractors) == 1
