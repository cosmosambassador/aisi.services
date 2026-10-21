import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from daily_brief import build_brief


class DailyBriefTests(unittest.TestCase):
    def setUp(self):
        self.records = json.loads((ROOT / "examples/missions.json").read_text())

    def test_four_domains_and_decisions_visible(self):
        brief = build_brief(self.records, date(2026, 10, 2), "test-digest")
        for domain in ("Land", "Sea", "Air", "Space"):
            self.assertIn(f"{domain}: 1 mission(s)", brief)
        self.assertIn("Awaiting human review: 4", brief)
        self.assertIn("Recorded 1 day(s)", brief)
        self.assertIn("test-digest", brief)
        self.assertIn("Synthetic scenario only", brief)

    def test_rejected_proposal_retained_separately(self):
        self.records[0]["human_review"] = {"status": "rejected", "reviewer": "Test reviewer",
            "reviewed_at": "2026-10-01T10:00:00-05:00", "decision_reference": "test-only"}
        brief = build_brief(self.records, date(2026, 10, 2), "digest")
        self.assertIn("Recorded rejections: 1", brief)
        self.assertIn("LSAS-DEMO-LAND", brief.split("## Rejected proposals")[1])

    def test_invalid_input_blocks_entire_brief(self):
        self.records[1]["sources"] = []
        with self.assertRaisesRegex(ValueError, "record 1"):
            build_brief(self.records, date(2026, 10, 2), "digest")

    def test_markup_escaped_and_missing_domain_visible(self):
        self.records[0]["purpose"] = "<script>\n# misleading heading"
        brief = build_brief(self.records[:1], date(2026, 10, 2), "digest")
        self.assertNotIn("<script>", brief)
        self.assertNotIn("\n# misleading heading", brief)
        self.assertIn("Sea: 0 mission(s) — add a mission", brief)

    def test_generation_does_not_mutate_records(self):
        before = copy.deepcopy(self.records)
        build_brief(self.records, date(2026, 10, 2), "digest")
        self.assertEqual(self.records, before)

    def test_cli_saves_once_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "daily.md"
            cmd = [sys.executable, str(ROOT / "src/daily_brief.py"),
                str(ROOT / "examples/missions.json"), "--date", "2026-10-02", "--output", str(output)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes()
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
