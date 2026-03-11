import pytest

REQUIRED_ENV = {
    "DATABASE_URL": "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
    "PG_VECTOR_COLLECTION_NAME": "test_collection",
    "GOOGLE_API_KEY": "test_key",
    "GOOGLE_EMBEDDING_MODEL": "models/text-embedding-004",
    "PDF_PATH": "/tmp/test.pdf",
}


@pytest.fixture()
def env_vars(monkeypatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
