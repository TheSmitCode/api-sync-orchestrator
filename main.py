from fastapi import FastAPI
from sync import run_sync

app = FastAPI(title="API Sync Orchestrator")

@app.get("/sync")
def trigger_sync(dry_run: bool = False):
    """Trigger sync via API."""
    run_sync(dry_run=dry_run)
    return {"status": "success", "dry_run": dry_run}

@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}
