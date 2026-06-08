import csv
import tempfile
import unittest
from pathlib import Path

from src.ingest import article_id, load_records, row_to_record


class IngestTests(unittest.TestCase):
    def test_builds_record(self) -> None:
        row = {
            "title": "Troops rescue residents",
            "text": "The residents returned safely after an operation.",
            "url": "https://example.com/rescue",
            "label": "positive",
            "source": "Punch",
            "section": "News",
            "published_at": "2026-06-08",
        }
        record = row_to_record(row)
        self.assertEqual(record.article_id, article_id(row["url"]))
        self.assertIn(row["title"], record.document)
        self.assertEqual(record.metadata["label"], "positive")

    def test_rejects_invalid_label(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid label"):
            row_to_record(
                {
                    "title": "Headline",
                    "text": "Article excerpt",
                    "url": "https://example.com/article",
                    "label": "mixed",
                }
            )

    def test_load_records_deduplicates_urls(self) -> None:
        rows = [
            {
                "title": "Headline",
                "text": "Article excerpt",
                "url": "https://example.com/article",
                "label": "neutral",
            },
            {
                "title": "Duplicate headline",
                "text": "Duplicate excerpt",
                "url": "https://example.com/article",
                "label": "neutral",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "articles.csv"
            with path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            self.assertEqual(len(load_records(path)), 1)


if __name__ == "__main__":
    unittest.main()

