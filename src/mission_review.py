"""Offline mission-record validation and review. Uses only Python's standard library."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DOMAINS = {"land", "sea", "air", "space"}
KINDS = {"observation", "testimony", "interpretation", "canon", "simulation", "ai_inference"}


def text_required(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
    except ValueError:
        return False


def validate_mission(record):
    """Return errors; completeness is never proof that evidence or approval is authentic."""
    if not isinstance(record, dict):
        return ["mission must be an object"]
    errors = []
    for key in ("id", "purpose", "uncertainty", "proposed_action", "success_measure"):
        if not text_required(record.get(key)):
            errors.append(f"{key} must be nonempty text")
    for key, choices in (("domain", DOMAINS), ("evidence_kind", KINDS)):
        if not isinstance(record.get(key), str) or record[key] not in choices:
            errors.append(f"{key} must be one of {', '.join(sorted(choices))}")
    if not timestamp(record.get("recorded_at")):
        errors.append("recorded_at must be an ISO timestamp with timezone")
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain at least one provenance record")
    else:
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"sources[{index}] must be an object")
                continue
            for key in ("reference", "attribution"):
                if not text_required(source.get(key)):
                    errors.append(f"sources[{index}].{key} must be nonempty text")
            if not timestamp(source.get("retrieved_at")):
                errors.append(f"sources[{index}].retrieved_at needs a timezone timestamp")
    review = record.get("human_review")
    if not isinstance(review, dict):
        errors.append("human_review must be an object")
    else:
        status = review.get("status")
        if not isinstance(status, str) or status not in {"pending", "approved", "rejected"}:
            errors.append("human_review.status must be pending, approved, or rejected")
        if status in {"approved", "rejected"}:
            if not text_required(review.get("reviewer")):
                errors.append("completed human review requires reviewer")
            if not timestamp(review.get("reviewed_at")):
                errors.append("completed human review requires reviewed_at with timezone")
            if not text_required(review.get("decision_reference")):
                errors.append("completed human review requires decision_reference")
    return errors


def review_records(records):
    if not isinstance(records, list) or not records:
        raise ValueError("input must be a nonempty JSON list of missions")
    results, seen = [], set()
    for index, record in enumerate(records):
        errors = validate_mission(record)
        mission_id = record.get("id") if isinstance(record, dict) else None
        if text_required(mission_id):
            if mission_id in seen:
                errors.append("duplicate mission id")
            seen.add(mission_id)
        valid = not errors
        results.append({
            "index": index,
            "id": mission_id,
            "domain": record.get("domain") if isinstance(record, dict) else None,
            "record_valid": valid,
            "review_status": record.get("human_review", {}).get("status") if valid else "invalid",
            "evidence_kind": record.get("evidence_kind") if valid else None,
            "errors": errors,
        })
    return {"mode": "offline_review", "executes_actions": False, "missions": results}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Review Land–Sea–Air–Space mission records offline.")
    parser.add_argument("input", type=Path, help="JSON mission list; originals are read only")
    args = parser.parse_args(argv)
    try:
        report = review_records(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(f"Mission review failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if all(row["record_valid"] for row in report["missions"]) else 1


if __name__ == "__main__":
    sys.exit(main())
