from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uuid
import logging

# Import orchestrator
from app.orchestrator import run_sync, run_sync_guarded

app = FastAPI(title="API Sync Orchestrator")

# Logger for API calls
logger = logging.getLogger("app.api")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app/logs/api.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
if not logger.handlers:
    logger.addHandler(file_handler)


@app.get("/health")
def health():
    """
    Simple endpoint Railway uses to check if the app is alive.
    """
    return {"status": "ok", "service": "api-sync-orchestrator"}


@app.post("/sync")
def manual_sync():
    """
    Trigger a sync manually and return results.
    """
    try:
        result = run_sync()
        logger.info("Manual sync completed successfully.")
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.exception("Manual sync failed.")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


@app.post("/sync/background")
def background_sync():
    """
    Trigger a background sync that writes results to logs.
    """
    task_id = str(uuid.uuid4())[:8]
    logger.info(f"Background sync triggered: {task_id}")

    try:
        result = run_sync_guarded(task_id)
        return JSONResponse(
            content={"status": "ok", "task_id": task_id, "result": result},
            status_code=200
        )
    except Exception as e:
        logger.exception("Background sync failed.")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )
