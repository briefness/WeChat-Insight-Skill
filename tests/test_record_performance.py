import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "tools" / "record_performance.py"
SPEC = importlib.util.spec_from_file_location("record_performance", MODULE_PATH)
record_performance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(record_performance)


class RecordPerformanceTests(unittest.TestCase):
    def test_matches_latest_history_and_preserves_null_for_missing_metrics(self):
        history = [
            {"time": "2026-11-20T10:00:00", "title": "旧文章", "media_id": "m-old"},
            {"time": "2026-11-25T21:00:00", "title": "新文章", "media_id": "m-new"},
        ]

        matched = record_performance.match_publish_history(history, use_latest=True)
        record = record_performance.build_performance_record(
            title=matched["title"],
            metrics={"reads": 1200, "shares": 45, "favorites": 60},
            config={"positioning": {"primary_audience": "独立开发者"}},
            history_match=matched,
            title_angle="认知冲突",
        )

        self.assertEqual("新文章", record["title"])
        self.assertEqual("2026-11-25", record["published_at"])
        self.assertEqual("m-new", record["media_id"])
        self.assertEqual("独立开发者", record["audience"])
        self.assertEqual(1200, record["metrics"]["reads"])
        self.assertIsNone(record["metrics"]["impressions"])
        self.assertIsNone(record["metrics"]["negative_feedback"])

    def test_diagnose_record_uses_only_provided_metrics(self):
        record = record_performance.build_performance_record(
            title="测试",
            metrics={
                "impressions": 10000,
                "clicks": 800,
                "reads": 750,
                "shares": 30,
                "favorites": 45,
                "completion_rate": 0.42,
                "negative_feedback": 2,
            },
        )

        hints = record_performance.diagnose_record(record)
        joined = "\n".join(hints)

        self.assertIn("8.0%", joined)
        self.assertIn("42.0%", joined)
        self.assertIn("转发率 4.0%", joined)
        self.assertIn("负反馈（2）", joined)

    def test_append_and_read_jsonl_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            perf_file = Path(tmp_dir) / "performance.jsonl"
            rec = record_performance.build_performance_record(
                title="回环测试",
                metrics={"reads": 500},
            )
            record_performance.append_performance_record(rec, perf_file)
            loaded = record_performance.read_jsonl(perf_file)

            self.assertEqual(1, len(loaded))
            self.assertEqual("回环测试", loaded[0]["title"])
            self.assertEqual(500, loaded[0]["metrics"]["reads"])


if __name__ == "__main__":
    unittest.main()
