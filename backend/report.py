"""Write evaluation artifacts (JSON and CSV)."""

import csv
import json
from pathlib import Path


def write_summary_json(out_dir, payload):
    path = Path(out_dir) / "summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def write_per_case_csv(out_dir, rows):
    path = Path(out_dir) / "summary.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return
    fieldnames = sorted({k for row in rows for k in row})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_aggregate_csv(out_dir, rows):
    path = Path(out_dir) / "summary_by_model.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return
    fieldnames = sorted({k for row in rows for k in row})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
