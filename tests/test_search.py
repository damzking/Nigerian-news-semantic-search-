import unittest

from src.search import build_where, search_collection


class FakeCollection:
    def __init__(self) -> None:
        self.arguments = None

    def query(self, **arguments):
        self.arguments = arguments
        return {
            "metadatas": [
                [
                    {
                        "title": "Rescue story",
                        "url": "https://example.com/rescue",
                        "label": "positive",
                    }
                ]
            ],
            "documents": [["Rescue story\n\nResidents returned safely."]],
            "distances": [[0.2]],
        }


class SearchTests(unittest.TestCase):
    def test_combines_metadata_filters(self) -> None:
        self.assertEqual(
            build_where("positive", "Punch", "News"),
            {
                "$and": [
                    {"label": "positive"},
                    {"source": "Punch"},
                    {"section": "News"},
                ]
            },
        )

    def test_returns_similarity(self) -> None:
        collection = FakeCollection()
        results = search_collection(
            collection,
            "rescued residents",
            sentiment="positive",
        )
        self.assertAlmostEqual(results[0]["similarity"], 0.8)
        self.assertEqual(collection.arguments["where"], {"label": "positive"})


if __name__ == "__main__":
    unittest.main()
