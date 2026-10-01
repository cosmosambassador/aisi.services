import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mission_review import review_records, validate_mission


class MissionReviewTests(unittest.TestCase):
    def setUp(self):
        self.examples = json.loads((ROOT / "examples" / "missions.json").read_text())
        self.record = copy.deepcopy(self.examples[0])

    def test_all_domains_are_examples_and_pending(self):
        report = review_records(self.examples)
        self.assertEqual({r["domain"] for r in report["missions"]}, {"land", "sea", "air", "space"})
        self.assertTrue(all(r["record_valid"] for r in report["missions"]))
        self.assertTrue(all(r["review_status"] == "pending" for r in report["missions"]))
        self.assertFalse(report["executes_actions"])

    def test_incomplete_approval_is_invalid(self):
        self.record["human_review"] = {"status": "approved"}
        self.assertEqual(len(validate_mission(self.record)), 3)

    def test_complete_review_remains_a_record_not_execution(self):
        self.record["human_review"] = {"status": "approved", "reviewer": "Test reviewer",
            "reviewed_at": "2026-10-01T10:00:00-05:00", "decision_reference": "test-only"}
        report = review_records([self.record])
        self.assertTrue(report["missions"][0]["record_valid"])
        self.assertFalse(report["executes_actions"])

    def test_missing_provenance_and_uncertainty(self):
        self.record["sources"] = []
        self.record["uncertainty"] = " "
        self.assertEqual(len(validate_mission(self.record)), 2)

    def test_invalid_nested_types_do_not_crash(self):
        for key in ("domain", "evidence_kind"):
            record = copy.deepcopy(self.record)
            record[key] = []
            self.assertTrue(validate_mission(record))
        for malformed in (None, [], "mission", {"human_review": []}, {"sources": [None]}):
            self.assertTrue(validate_mission(malformed))

    def test_timezone_required(self):
        self.record["recorded_at"] = "2026-10-01T10:00:00"
        self.assertTrue(validate_mission(self.record))

    def test_duplicate_ids_rejected(self):
        report = review_records([self.record, self.record])
        self.assertIn("duplicate mission id", report["missions"][1]["errors"])

    def test_empty_or_wrong_collection_rejected(self):
        for value in ([], {}, None):
            with self.assertRaises(ValueError):
                review_records(value)

    def test_cli_preserves_input_and_emits_json(self):
        path = ROOT / "examples" / "missions.json"
        before = path.read_bytes()
        run = subprocess.run([sys.executable, str(ROOT / "src" / "mission_review.py"), str(path)],
            capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(json.loads(run.stdout)["missions"]), 4)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
