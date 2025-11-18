# api/main.py
from fastapi import FastAPI, HTTPException
from mangum import Mangum
import os
import json
import tempfile
from sync import run_sync  # your sync logic
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
from loguru import logger

# -----------------------------
# Serverless-safe temp directory
# -----------------------------
TMP_DIR = tempfile.gettempdir()
os.makedirs(TMP_DIR, exist_ok=True)

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="API Sync Orchestrator", version="1.0.0")

class SyncRequest(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    config: Dict[str, Any]
    dry_run: bool = False

@app.get("/")
async def root():
    return {"message": "API Sync Orchestrator is live!"}

@app.post("/sync")
async def trigger_sync(request: SyncRequest):
    try:
        temp_config = os.path.join(TMP_DIR, "temp_config.json")
        with open(temp_config, "w", encoding="utf-8") as f:
            json.dump(request.config, f, indent=2)

        result = run_sync(dry_run=request.dry_run, config_path=temp_config)

        audit_path = os.path.join(TMP_DIR, "audit_report.json")
        audit = {}
        if os.path.exists(audit_path):
            try:
                with open(audit_path, "r", encoding="utf-8") as f:
                    audit = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read audit file: {e}")

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
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# -----------------------------
# Mangum handler for Vercel
# -----------------------------
handler = Mangum(app)

# -----------------------------
# Local dev
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
