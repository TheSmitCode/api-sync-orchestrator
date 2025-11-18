from __future__ import annotations
import os
import json
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
import uvicorn
from loguru import logger

# Serverless-safe temp directory (cross-platform)
TMP_DIR = tempfile.gettempdir()
os.makedirs(TMP_DIR, exist_ok=True)

# Import run_sync after TMP_DIR exists (your original pattern)
from sync import run_sync  # noqa: E402

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")


class SyncRequest(BaseModel):
    # Correct typed assignment for Pydantic v2 ConfigDict usage
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    config: Dict[str, Any]
    dry_run: bool = False


@app.get("/")
def root():
    return {"message": "API Sync Orchestrator running."}


@app.post("/sync")
def trigger_sync(request: SyncRequest):
    try:
        # Save config to temp file
        temp_config = os.path.join(TMP_DIR, "temp_config.json")
        with open(temp_config, "w", encoding="utf-8") as f:
            json.dump(request.config, f, indent=2)

        # Run sync
        result = run_sync(dry_run=request.dry_run, config_path=temp_config)

        # Read last audit
        audit_path = os.path.join(TMP_DIR, "audit_report.json")
        audit = {}
        if os.path.exists(audit_path):
            try:
                with open(audit_path, "r", encoding="utf-8") as f:
                    audit = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read audit file: {e}")

        # Cleanup temp config (best-effort)
        try:
            os.remove(temp_config)
        except Exception:
            pass

        return {
            "status": "success",
            "dry_run": request.dry_run,
            "result": result,
            "audit": audit,
        }

    except Exception as e:
        logger.exception("Error during /sync")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


# Allow running directly for local dev: `python api/main.py` or container usage
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Use uvicorn.run with app object to avoid import path issues
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
