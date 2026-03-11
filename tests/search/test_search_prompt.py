import pytest
from unittest.mock import MagicMock, patch

import search as search_module


def _make_search_results(content="relevant content", score=0.9):
    doc = MagicMock()
    doc.page_content = content
    return [(doc, score)]


class TestSearchPromptEnvValidation:
    @pytest.mark.parametrize(
        "missing_key",
        [
            "DATABASE_URL",
            "PG_VECTOR_COLLECTION_NAME",
            "GOOGLE_API_KEY",
            "GOOGLE_EMBEDDING_MODEL",
        ],
    )
    def test_raises_runtime_error_when_env_var_missing(
        self, env_vars, monkeypatch, missing_key
    ):
        monkeypatch.delenv(missing_key)
        with pytest.raises(RuntimeError, match=missing_key):
            search_module.search_prompt("test question")


class TestSearchPromptExecution:
    def test_returns_chain_invocation_result(self, env_vars):
        expected = MagicMock()
        expected.content = "response text"

        with (
            patch("search.GoogleGenerativeAIEmbeddings"),
            patch("search.PGVector") as mock_store,
            patch("search.ChatGoogleGenerativeAI"),
            patch("search.PromptTemplate") as mock_template,
        ):
            mock_store.return_value.similarity_search_with_score.return_value = (
                _make_search_results()
            )
            mock_template.return_value.__or__ = MagicMock(
                return_value=MagicMock(invoke=MagicMock(return_value=expected))
            )

            result = search_module.search_prompt("qual o tema?")

        assert result is expected

    def test_similarity_search_called_with_question(self, env_vars):
        with (
            patch("search.GoogleGenerativeAIEmbeddings"),
            patch("search.PGVector") as mock_store,
            patch("search.ChatGoogleGenerativeAI"),
            patch("search.PromptTemplate"),
        ):
            mock_store.return_value.similarity_search_with_score.return_value = (
                _make_search_results()
            )

            search_module.search_prompt("minha pergunta")

            search_mock = mock_store.return_value.similarity_search_with_score
            search_mock.assert_called_once_with("minha pergunta", k=10)

    def test_pgvector_store_uses_correct_collection(self, env_vars):
        with (
            patch("search.GoogleGenerativeAIEmbeddings"),
            patch("search.PGVector") as mock_store,
            patch("search.ChatGoogleGenerativeAI"),
            patch("search.PromptTemplate"),
        ):
            mock_store.return_value.similarity_search_with_score.return_value = (
                _make_search_results()
            )

            search_module.search_prompt("pergunta")

            _, kwargs = mock_store.call_args
            assert kwargs["collection_name"] == "test_collection"
            assert kwargs["connection"] == (
                "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
            )

    def test_context_built_from_all_search_results(self, env_vars):
        results = [
            (MagicMock(page_content="parte 1"), 0.9),
            (MagicMock(page_content="parte 2"), 0.8),
        ]
        captured_invoke_args = {}

        def fake_invoke(payload):
            captured_invoke_args.update(payload)
            return MagicMock()

        with (
            patch("search.GoogleGenerativeAIEmbeddings"),
            patch("search.PGVector") as mock_store,
            patch("search.ChatGoogleGenerativeAI"),
            patch("search.PromptTemplate") as mock_template,
        ):
            mock_store.return_value.similarity_search_with_score.return_value = results
            chain_mock = MagicMock(invoke=fake_invoke)
            mock_template.return_value.__or__ = MagicMock(return_value=chain_mock)

            search_module.search_prompt("pergunta")

        assert "parte 1" in captured_invoke_args.get("context", "")
        assert "parte 2" in captured_invoke_args.get("context", "")
