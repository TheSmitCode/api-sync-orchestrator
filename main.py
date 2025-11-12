"""
main.py
Provides a REST API to trigger sync and check status.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sync import run_sync

app = FastAPI(title="API Sync Orchestrator")

class SyncRequest(BaseModel):
    dry_run: bool = True

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
        result = run_sync(dry_run=request.dry_run)
        return {"status": "success", "dry_run": request.dry_run, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
