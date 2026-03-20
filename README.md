# evaluation-pipeline

Multi-model evaluation for **SOAP clinical summaries** (subjective, objective, assessment, plan). Compare any number of model output JSON files against a single ground-truth file, using **medical entity recall** (scispaCy) and **ROUGE-L F1**.

## Setup

From the repository root (not inside `backend/`):

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate
pip install -r requirements.txt
cd ..
```

## Ground truth and predictions

- **Ground truth** [`datasets/Groundtruth_Summary.json`](datasets/Groundtruth_Summary.json): array of objects with `case_id` and **string** fields `subjective`, `objective`, `assessment`, `plan` (and optionally `dialogue`).
- **Predictions**: array of objects with the same `case_id`. Each model file can use either:
  - **Flat SOAP**: all four fields are strings (or empty), same shape as ground truth; or
  - **Nested SOAP**: dict/list structure per section, as in [`datasets/JarvisMD_Summary.json`](datasets/JarvisMD_Summary.json).

Records are aligned **only** by `case_id`. If a model file lacks a `case_id` present in ground truth, that row is reported as `missing_prediction` and averages exclude it.

## Run evaluation

```bash
python -m backend.run --gt datasets/Groundtruth_Summary.json ^
  -p datasets/JarvisMD_Summary.json ^
  -p path/to/second_model.json ^
  -p path/to/third_model.json ^
  --out results
```

(Use `\` instead of `^` on Unix.)

### Metrics (`--metrics`)

Comma-separated list (default: `entity_recall,rouge_l`):

| Metric            | Meaning |
|-------------------|--------|
| `entity_recall`   | Of biomedical entities extracted by scispaCy from the **reference** SOAP string, the fraction whose **lowercased span** appears somewhere in the **predicted** SOAP string. If the reference has no entities, the score is `0`. |
| `rouge_l`         | ROUGE-L F1 between full reference and predicted SOAP strings (stemmed tokenizer). |

## Outputs (`--out`, default `results/`)

| File                    | Contents |
|-------------------------|----------|
| `summary.json`          | Full run: paths, chosen metrics, per-model aggregates, per-case scores and status. |
| `summary.csv`           | One row per ground-truth case × model (`case_id`, `model`, scores, `status`). |
| `summary_by_model.csv`  | One row per model: means, counts, missing predictions. |

## Visualize results (frontend)

This serves a small dashboard at `/` that reads `results/summary.json`.

```bash
backend\venv\Scripts\python.exe -m backend.server
```

Then open: `http://127.0.0.1:8000/`

## Layout

- [`backend/run.py`](backend/run.py) — CLI entry.
- [`backend/loaders.py`](backend/loaders.py) — JSON loading and `case_id` index.
- [`backend/normalize.py`](backend/normalize.py) — Flat vs nested SOAP → single string.
- [`backend/metrics.py`](backend/metrics.py) — Entity recall and ROUGE-L.
- [`backend/report.py`](backend/report.py) — JSON/CSV writers.
