import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ----------------------------------------------------------------------
# RENDER-SAFE LOGGING
# ----------------------------------------------------------------------
# Render allows writing ONLY to /opt/render/project/tmp
LOG_DIR = "/opt/render/project/tmp/app_logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "sync.log")

logger = logging.getLogger("app.orchestrator")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

# ----------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------
try:
    from app import targets, transform, utils
except Exception:
    import targets, transform, utils


# ----------------------------------------------------------------------
# CORE SYNC EXECUTION
# ----------------------------------------------------------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
)
def _run_once():
    logger.info("Orchestrator: starting run_once")

    raw = targets.run_targets()
    logger.info("Orchestrator: got %s raw results", len(raw) if hasattr(raw, "__len__") else "unknown")

    transformed = transform.apply_transformations(raw)
    logger.info(
        "Orchestrator: transformed results count=%s",
        len(transformed) if hasattr(transformed, "__len__") else "unknown",
    )

    return [
        {
            "raw_count": len(raw) if hasattr(raw, "__len__") else None,
            "transformed_count": len(transformed) if hasattr(transformed, "__len__") else None,
        }
    ]


def run_sync():
    start = time.time()
    try:
        result = _run_once()
        duration = time.time() - start
        logger.info("Orchestrator: completed in %.2fs", duration)
        return {"status": "ok", "duration_s": duration, "result": result}
    except Exception as e:
        duration = time.time() - start
        logger.exception("Orchestrator: failed after %.2fs: %s", duration, str(e))
        return {"status": "error", "duration_s": duration, "error": str(e)}


def run_sync_guarded(task_id: str):
    logger.info("Guarded sync start: %s", task_id)
    result = run_sync()

    # Render-safe temporary directory for write access
    TASK_FILE = os.path.join(LOG_DIR, f"task-{task_id}.json")

    try:
        import json
        with open(TASK_FILE, "w", encoding="utf-8") as fh:
            json.dump({"task_id": task_id, "result": result}, fh, indent=2)
    except Exception:
        logger.exception("Failed to write task result file for %s", task_id)

    logger.info("Guarded sync complete: %s", task_id)
    return result
