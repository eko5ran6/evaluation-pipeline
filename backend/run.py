"""CLI to evaluate multiple model SOAP summaries against ground truth."""

from __future__ import annotations

import argparse
from pathlib import Path

import scispacy  # noqa: F401  -- ensures scispacy-linked models register
import spacy

from backend.loaders import ground_truth_case_ids, load_records
from backend.metrics import entity_recall, rouge_l_f1
from backend.normalize import soap_string_from_groundtruth, soap_string_from_prediction
from backend.report import write_aggregate_csv, write_per_case_csv, write_summary_json

DEFAULT_METRICS = ("entity_recall", "rouge_l")


def _parse_metrics_arg(s: str) -> tuple[str, ...]:
    parts = tuple(m.strip() for m in s.split(",") if m.strip())
    unk = [m for m in parts if m not in DEFAULT_METRICS and m != "rouge_l_f1"]
    if unk:
        raise ValueError(f"Unknown metrics: {unk}. Valid: {', '.join(DEFAULT_METRICS)}")
    # alias
    return tuple("rouge_l" if m == "rouge_l_f1" else m for m in parts)


def run_evaluation(
    gt_path: Path,
    prediction_paths: list[Path],
    out_dir: Path,
    metrics: tuple[str, ...],
):
    nlp = spacy.load("en_core_sci_sm")
    gt_lookup = load_records(gt_path)
    case_ids = ground_truth_case_ids(gt_lookup)

    models_payload = []
    per_case_rows = []
    aggregate_rows = []

    for pred_path in prediction_paths:
        label = pred_path.stem
        pred_lookup = load_records(pred_path)
        per_case = []

        sum_entity = 0.0
        sum_rouge = 0.0
        n_ok = 0

        for cid in case_ids:
            gt_soap = soap_string_from_groundtruth(gt_lookup[cid])
            row_base = {"case_id": cid, "model": label}

            if cid not in pred_lookup:
                row = {
                    **row_base,
                    "status": "missing_prediction",
                }
                if "entity_recall" in metrics:
                    row["entity_recall"] = ""
                if "rouge_l" in metrics:
                    row["rouge_l_f1"] = ""
                per_case.append(
                    {
                        "case_id": cid,
                        "entity_recall": None,
                        "rouge_l_f1": None,
                        "status": "missing_prediction",
                    }
                )
                per_case_rows.append(row)
                continue

            pred_soap = soap_string_from_prediction(pred_lookup[cid])
            rec = None
            rlf1 = None
            if "entity_recall" in metrics:
                rec = entity_recall(nlp, gt_soap, pred_soap)
            if "rouge_l" in metrics:
                rlf1 = rouge_l_f1(gt_soap, pred_soap)

            status = "ok"
            case_entry = {"case_id": cid, "status": status}
            out_row = {**row_base, "status": status}
            if rec is not None:
                case_entry["entity_recall"] = rec
                sum_entity += rec
                out_row["entity_recall"] = f"{rec:.6f}"
            if rlf1 is not None:
                case_entry["rouge_l_f1"] = rlf1
                sum_rouge += rlf1
                out_row["rouge_l_f1"] = f"{rlf1:.6f}"
            n_ok += 1
            per_case.append(case_entry)
            per_case_rows.append(out_row)

        agg = {
            "model": label,
            "prediction_path": str(pred_path.resolve()),
            "n_ground_truth_cases": len(case_ids),
            "n_evaluated": n_ok,
            "n_missing_prediction": len(case_ids) - n_ok,
        }
        if n_ok and "entity_recall" in metrics:
            agg["entity_recall_mean"] = sum_entity / n_ok
        if n_ok and "rouge_l" in metrics:
            agg["rouge_l_f1_mean"] = sum_rouge / n_ok

        aggregate_rows.append(agg)
        models_payload.append(
            {
                "label": label,
                "path": str(pred_path.resolve()),
                "aggregate": agg,
                "per_case": per_case,
            }
        )

    payload = {
        "ground_truth": str(gt_path.resolve()),
        "metrics": list(metrics),
        "models": models_payload,
    }

    write_summary_json(out_dir, payload)
    write_per_case_csv(out_dir, per_case_rows)
    write_aggregate_csv(out_dir, aggregate_rows)
    return payload


def build_arg_parser():
    p = argparse.ArgumentParser(
        description="Evaluate one or more SOAP summary JSON files against ground truth.",
    )
    p.add_argument(
        "--gt",
        required=True,
        type=Path,
        help="Path to ground-truth JSON (list of records with case_id and SOAP fields).",
    )
    p.add_argument(
        "-p",
        "--predictions",
        action="append",
        dest="predictions",
        required=True,
        type=Path,
        help="Path to a model prediction JSON (repeat -p for each model).",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("results"),
        help="Output directory for summary.json and CSV files (default: results).",
    )
    p.add_argument(
        "--metrics",
        type=str,
        default="entity_recall,rouge_l",
        help=f"Comma-separated metrics (default: entity_recall,rouge_l). Choices: {', '.join(DEFAULT_METRICS)}",
    )
    return p


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        metrics = _parse_metrics_arg(args.metrics)
    except ValueError as e:
        parser.error(str(e))

    run_evaluation(
        gt_path=args.gt,
        prediction_paths=args.predictions,
        out_dir=args.out,
        metrics=metrics,
    )
    print(f"Wrote {args.out / 'summary.json'}, summary.csv, summary_by_model.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
