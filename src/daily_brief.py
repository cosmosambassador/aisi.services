"""Build a daily work brief from local mission records; never execute actions."""

import argparse
import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from mission_review import review_records


def inline(value):
    """Keep record text on one Markdown line and display markup literally."""
    value = " ".join(str(value).split())
    for char in "\\`*_{}[]<>()#!|":
        value = value.replace(char, "\\" + char)
    return value


def build_brief(records, day, digest):
    report = review_records(records)
    invalid = [row for row in report["missions"] if not row["record_valid"]]
    if invalid:
        details = "; ".join(f"record {row['index']}: {', '.join(row['errors'])}" for row in invalid)
        raise ValueError("Repair mission records before briefing: " + details)
    groups = {status: [] for status in ("pending", "approved", "rejected")}
    for record in records:
        groups[record["human_review"]["status"]].append(record)
    domains = {record["domain"] for record in records}
    lines = [f"# Earth stewardship daily work brief — {day.isoformat()}", "",
        f"Input SHA-256: `{digest}`", "",
        f"Missions: {len(records)}. Awaiting human review: {len(groups['pending'])}. "
        f"Recorded approvals: {len(groups['approved'])}. Recorded rejections: {len(groups['rejected'])}.", "",
        "This brief summarizes supplied records. It performs no fresh research or actions. "
        "Review metadata is self-reported and does not authenticate authorization.", "",
        "## Domain coverage", ""]
    for domain in ("land", "sea", "air", "space"):
        count = sum(record["domain"] == domain for record in records)
        lines.append(f"- {domain.title()}: {count} mission(s)" + (" — add a mission for this domain." if domain not in domains else "."))
    for status, title in (("pending", "Decisions awaiting review"),
                          ("approved", "Recorded approvals — verify before action"),
                          ("rejected", "Rejected proposals — retained for continuity")):
        lines.extend(["", f"## {title}", ""])
        if not groups[status]:
            lines.append("None recorded.")
        for record in groups[status]:
            observed_day = datetime.fromisoformat(record["recorded_at"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Chicago")).date()
            age = (day - observed_day).days
            freshness = f"Recorded {age} day(s) before this brief." if age >= 0 else "Record is dated after this brief; check its timestamp."
            lines.extend([f"### {inline(record['id'])} — {record['domain'].title()}", "",
                f"Purpose: {inline(record['purpose'])}", "",
                f"Evidence label: {inline(record['evidence_kind'])}. {freshness}", "",
                f"Proposed next step: {inline(record['proposed_action'])}", "",
                f"Evidence gap / uncertainty: {inline(record['uncertainty'])}", "",
                f"Measure of success: {inline(record['success_measure'])}", "", "Provenance:", ""])
            for source in record["sources"]:
                lines.append(f"- {inline(source['reference'])} — {inline(source['attribution'])}; retrieved {inline(source['retrieved_at'])}.")
            if status != "pending":
                review = record["human_review"]
                lines.extend(["", f"Review record: {inline(review['reviewer'])}; {inline(review['reviewed_at'])}; "
                    f"reference {inline(review['decision_reference'])}."])
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a daily Earth stewardship work brief.")
    parser.add_argument("input", type=Path, help="JSON mission list")
    parser.add_argument("--date", type=date.fromisoformat, help="Brief date YYYY-MM-DD; default today in America/Chicago")
    parser.add_argument("--output", type=Path, help="Save a new Markdown file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
        records = json.loads(raw)
        day = args.date or datetime.now(ZoneInfo("America/Chicago")).date()
        brief = build_brief(records, day, hashlib.sha256(raw).hexdigest())
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(brief)
            print(f"Saved {args.output}")
        else:
            print(brief, end="")
    except (OSError, ValueError) as exc:
        print(f"Daily brief failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
