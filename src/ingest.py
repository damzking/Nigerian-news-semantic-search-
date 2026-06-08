from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.database import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DATABASE_PATH,
    DEFAULT_EMBEDDING_MODEL,
    get_collection,
)


REQUIRED_COLUMNS = {"title", "text", "url", "label"}
VALID_LABELS = {"negative", "neutral", "positive"}


@dataclass(frozen=True)
class NewsRecord:
    article_id: str
    document: str
    metadata: dict[str, str]


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def row_to_record(row: dict[str, str]) -> NewsRecord:
    title = clean(row.get("title"))
    text = clean(row.get("text"))
    url = clean(row.get("url"))
    label = clean(row.get("label")).lower()

    if not title or not text or not url:
        raise ValueError("title, text, and url must not be empty")
    if label not in VALID_LABELS:
        raise ValueError(f"invalid label: {label!r}")

    metadata = {
        "title": title,
        "url": url,
        "label": label,
        "source": clean(row.get("source")),
        "section": clean(row.get("section")),
        "published_at": clean(row.get("published_at")),
    }
    return NewsRecord(
        article_id=article_id(url),
        document=f"{title}\n\n{text}",
        metadata=metadata,
    )


def load_records(csv_path: Path) -> list[NewsRecord]:
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")

        records: list[NewsRecord] = []
        seen_ids: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            try:
                record = row_to_record(row)
            except ValueError as error:
                raise ValueError(f"row {row_number}: {error}") from error
            if record.article_id not in seen_ids:
                seen_ids.add(record.article_id)
                records.append(record)
        return records


def ingest_records(collection: object, records: list[NewsRecord]) -> None:
    collection.upsert(
        ids=[record.article_id for record in records],
        documents=[record.document for record in records],
        metadatas=[record.metadata for record in records],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest news into ChromaDB.")
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_records(args.csv)
    collection = get_collection(
        database_path=args.database,
        collection_name=args.collection,
        embedding_model=args.embedding_model,
    )
    ingest_records(collection, records)
    print(f"Ingested {len(records)} articles into {args.collection!r}.")


if __name__ == "__main__":
    main()

