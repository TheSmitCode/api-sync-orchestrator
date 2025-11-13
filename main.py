# =========================
# FILE: main.py
# DESCRIPTION: FastAPI server exposing endpoints for manual sync and health checks.
# =========================

from __future__ import annotations  # solves forward ref issues
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
import uvicorn
import os
import json
from sync import run_sync  # your existing sync.py

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")


class SyncRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    config: Dict[str, Any]  # Accept full JSON payload
    dry_run: bool = False


@app.get("/")
def root():
    return {"message": "API Sync Orchestrator running."}


@app.post("/sync")
def trigger_sync(request: SyncRequest):
    """
    Trigger a manual sync.
    dry_run=True skips pushing to targets.
    """
    try:
        # Save config to temp file
        temp_config = "temp_config.json"
        with open(temp_config, "w") as f:
            json.dump(request.config, f, indent=2)

        # Run sync using your existing logic
        result = run_sync(dry_run=request.dry_run)

        # Read last audit (if exists)
        audit_files = [f for f in os.listdir("logs") if f.startswith("audit_")]
        audit = {}
        if audit_files:
            latest_audit_file = sorted(audit_files)[-1]
            with open(f"logs/{latest_audit_file}", "r") as f:
                audit = json.load(f)

        os.remove(temp_config)  # cleanup

        return {"status": "success", "dry_run": request.dry_run, "result": result, "audit": audit}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
