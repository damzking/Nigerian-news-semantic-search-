from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.database import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DATABASE_PATH,
    DEFAULT_EMBEDDING_MODEL,
    get_collection,
)
from src.ingest import VALID_LABELS


def build_where(
    sentiment: str | None = None,
    source: str | None = None,
    section: str | None = None,
) -> dict[str, Any] | None:
    filters = []
    if sentiment:
        filters.append({"label": sentiment})
    if source:
        filters.append({"source": source})
    if section:
        filters.append({"section": section})
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def search_collection(
    collection: object,
    query: str,
    limit: int = 5,
    sentiment: str | None = None,
    source: str | None = None,
    section: str | None = None,
) -> list[dict[str, Any]]:
    where = build_where(sentiment, source, section)
    arguments: dict[str, Any] = {
        "query_texts": [query],
        "n_results": limit,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        arguments["where"] = where

    response = collection.query(**arguments)
    results = []
    for metadata, document, distance in zip(
        response["metadatas"][0],
        response["documents"][0],
        response["distances"][0],
    ):
        results.append(
            {
                "similarity": max(0.0, 1.0 - float(distance)),
                "metadata": metadata,
                "document": document,
            }
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search Nigerian news.")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sentiment", choices=sorted(VALID_LABELS))
    parser.add_argument("--source")
    parser.add_argument("--section")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    collection = get_collection(
        database_path=args.database,
        collection_name=args.collection,
        embedding_model=args.embedding_model,
    )
    results = search_collection(
        collection=collection,
        query=args.query,
        limit=args.limit,
        sentiment=args.sentiment,
        source=args.source,
        section=args.section,
    )
    if not results:
        print("No matching articles found.")
        return

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(
            f"{index}. [{metadata['label']}] {metadata['title']}\n"
            f"   Similarity: {result['similarity']:.3f}\n"
            f"   {metadata['url']}"
        )


if __name__ == "__main__":
    main()

