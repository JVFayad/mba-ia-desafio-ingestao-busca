import pytest
import runpy
from unittest.mock import patch

from langchain_core.documents import Document

import ingest as ingest_module


def _make_doc(content="test content", metadata=None):
    return Document(
        page_content=content,
        metadata=metadata if metadata is not None else {"source": "test.pdf"},
    )


class TestIngestPdfEnvValidation:
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
            ingest_module.ingest_pdf()


class TestIngestPdfDocumentProcessing:
    def test_raises_system_exit_when_no_documents_after_split(self, env_vars):
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
        ):
            mock_loader.return_value.load.return_value = [_make_doc()]
            mock_splitter.return_value.split_documents.return_value = []

            with pytest.raises(SystemExit):
                ingest_module.ingest_pdf()

    def test_metadata_empty_string_values_are_filtered(self, env_vars):
        doc = _make_doc(
            metadata={"source": "test.pdf", "empty_field": "", "valid": "ok"}
        )
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
            patch("ingest.GoogleGenerativeAIEmbeddings"),
            patch("ingest.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = [doc]
            mock_splitter.return_value.split_documents.return_value = [doc]

            ingest_module.ingest_pdf()

            enriched = mock_store.return_value.add_documents.call_args[0][0]
            assert "empty_field" not in enriched[0].metadata
            assert "valid" in enriched[0].metadata

    def test_metadata_none_values_are_filtered(self, env_vars):
        doc = _make_doc(
            metadata={"source": "test.pdf", "none_field": None, "valid": "ok"}
        )
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
            patch("ingest.GoogleGenerativeAIEmbeddings"),
            patch("ingest.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = [doc]
            mock_splitter.return_value.split_documents.return_value = [doc]

            ingest_module.ingest_pdf()

            enriched = mock_store.return_value.add_documents.call_args[0][0]
            assert "none_field" not in enriched[0].metadata
            assert "valid" in enriched[0].metadata

    def test_document_ids_are_sequential(self, env_vars):
        docs = [_make_doc(content=f"doc {i}") for i in range(3)]
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
            patch("ingest.GoogleGenerativeAIEmbeddings"),
            patch("ingest.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = docs
            mock_splitter.return_value.split_documents.return_value = docs

            ingest_module.ingest_pdf()

            ids = mock_store.return_value.add_documents.call_args[1]["ids"]
            assert ids == ["doc-0", "doc-1", "doc-2"]

    def test_add_documents_called_exactly_once(self, env_vars):
        doc = _make_doc()
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
            patch("ingest.GoogleGenerativeAIEmbeddings"),
            patch("ingest.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = [doc]
            mock_splitter.return_value.split_documents.return_value = [doc]

            ingest_module.ingest_pdf()

            mock_store.return_value.add_documents.assert_called_once()

    def test_pgvector_store_created_with_correct_connection(self, env_vars):
        doc = _make_doc()
        with (
            patch("ingest.PyPDFLoader") as mock_loader,
            patch("ingest.RecursiveCharacterTextSplitter") as mock_splitter,
            patch("ingest.GoogleGenerativeAIEmbeddings"),
            patch("ingest.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = [doc]
            mock_splitter.return_value.split_documents.return_value = [doc]

            ingest_module.ingest_pdf()

            _, kwargs = mock_store.call_args
            assert kwargs["connection"] == (
                "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
            )
            assert kwargs["collection_name"] == "test_collection"


class TestIngestModuleMainEntryPoint:
    def test_runs_ingest_when_executed_as_script(self, env_vars):
        doc = _make_doc()

        with (
            patch("langchain_community.document_loaders.PyPDFLoader") as mock_loader,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_google_genai.GoogleGenerativeAIEmbeddings"),
            patch("langchain_postgres.PGVector") as mock_store,
        ):
            mock_loader.return_value.load.return_value = [doc]
            mock_splitter.return_value.split_documents.return_value = [doc]

            runpy.run_path("src/ingest.py", run_name="__main__")

            mock_store.return_value.add_documents.assert_called_once()
