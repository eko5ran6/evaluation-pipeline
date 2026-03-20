from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


def _repo_root() -> Path:
    # backend/server.py -> backend -> repo root
    return Path(__file__).resolve().parent.parent


app = FastAPI(title="Summary Evaluation Dashboard")


@app.get("/api/summary")
def get_summary():
    summary_path = _repo_root() / "results" / "summary.json"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="results/summary.json not found. Run the pipeline first.")

    # Ensure JSON serializes cleanly (and avoids weird issues if we ever include numpy types later).
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    return JSONResponse(payload)


frontend_dir = _repo_root() / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

