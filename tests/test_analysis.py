import unittest
from pathlib import Path

from instagram_analytics.analyzers import analyze_documents
from instagram_analytics.loaders import load_json_text


class AnalysisTests(unittest.TestCase):
    def test_sample_export_extracts_interactions_and_post_metrics(self):
        sample = Path("examples/sample_export.json").read_text(encoding="utf-8")
        documents = [load_json_text(sample, "sample_export.json")]

        summary = analyze_documents(documents)

        self.assertEqual(summary["total_interactions"], 3)
        self.assertEqual(summary["unique_accounts"], 2)
        self.assertEqual(summary["top_account"]["account"], "example_friend")
        self.assertEqual(summary["top_account"]["count"], 2)
        self.assertEqual(summary["post_summary"]["count"], 2)
        self.assertEqual(summary["post_summary"]["average_likes"], 50)

    def test_invalid_json_raises_useful_error(self):
        with self.assertRaisesRegex(ValueError, "broken.json: invalid JSON"):
            load_json_text("{", "broken.json")


if __name__ == "__main__":
    unittest.main()
