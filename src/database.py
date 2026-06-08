from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_DATABASE_PATH = Path("chroma_data")
DEFAULT_COLLECTION_NAME = "nigerian_news"
DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL) -> Any:
    from chromadb.utils.embedding_functions import (
        SentenceTransformerEmbeddingFunction,
    )

    return SentenceTransformerEmbeddingFunction(model_name=model_name)


def get_collection(
    database_path: Path = DEFAULT_DATABASE_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Any:
    import chromadb

    client = chromadb.PersistentClient(path=str(database_path))
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(embedding_model),
        metadata={"hnsw:space": "cosine"},
    )

