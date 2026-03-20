"""Load evaluation JSON files and build case_id lookups."""

import json
from pathlib import Path


def load_records(path):
    """Load a JSON file that must be a list of objects with at least case_id."""
    p = Path(path)
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {p}")
    lookup = {}
    for item in data:
        if not isinstance(item, dict) or "case_id" not in item:
            continue
        cid = item["case_id"]
        lookup[cid] = item
    return lookup


def ground_truth_case_ids(gt_lookup):
    return sorted(gt_lookup.keys())
