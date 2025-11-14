from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
import uvicorn
import os
import json
from loguru import logger

# Ensure serverless-safe temp directory exists
TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

from sync import run_sync  # import AFTER creating /tmp

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")


class SyncRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
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
        with open(temp_config, "w") as f:
            json.dump(request.config, f, indent=2)

        # Run sync
        result = run_sync(dry_run=request.dry_run, config_path=temp_config)

        # Read last audit
        audit_path = os.path.join(TMP_DIR, "audit_report.json")
        audit = {}
        if os.path.exists(audit_path):
            try:
                with open(audit_path, "r") as f:
                    audit = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read audit file: {e}")

        # Cleanup
        try:
            os.remove(temp_config)
        except Exception:
            pass

        return {
            "status": "success",
            "dry_run": request.dry_run,
            "result": result,
            "audit": audit
        }

    except Exception as e:
        logger.exception("Error during /sync")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
