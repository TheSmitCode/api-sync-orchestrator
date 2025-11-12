from fastapi import FastAPI
from sync import run_sync

app = FastAPI(title="API Sync Orchestrator")

@app.get("/sync")
def sync_endpoint():
    try:
        run_sync()
        return {"status": "success", "message": "Sync completed (dry-run if enabled)."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}
