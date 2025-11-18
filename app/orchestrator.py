import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Attempt relative imports; if run from top-level, use package imports
try:
    from app import targets, transform, utils
except Exception:
    import targets, transform, utils  # fallback for local runs

logger = logging.getLogger('app.orchestrator')
logger.setLevel(logging.INFO)
# File handler logs to app/logs/sync.log (ensure folder exists)
file_handler = logging.FileHandler('app/logs/sync.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(file_handler)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type(Exception))
def _run_once():
    """
    Single run attempt: calls targets, applies transforms and returns a summary structure.
    This function is retried by tenacity on exceptions.
    """
    logger.info("Orchestrator: starting run_once")
    results = []
    # run_targets should return iterable of raw results or raise
    raw = targets.run_targets()
    logger.info("Orchestrator: got %s raw results", len(raw) if hasattr(raw, '__len__') else 'unknown')
    transformed = transform.apply_transformations(raw)
    logger.info("Orchestrator: transformed results count=%s", len(transformed) if hasattr(transformed, '__len__') else 'unknown')

    # Here you would push transformed results to destinations. For safety, we return summary.
    results.append({
        'raw_count': len(raw) if hasattr(raw, '__len__') else None,
        'transformed_count': len(transformed) if hasattr(transformed, '__len__') else None
    })
    return results


def run_sync():
    """
    Public synchronous API: run a sync and return a result dict.
    Handles timing and exception capture.
    """
    start = time.time()
    try:
        res = _run_once()
        duration = time.time() - start
        logger.info("Orchestrator: completed in %.2fs", duration)
        return {'status': 'ok', 'duration_s': duration, 'result': res}
    except Exception as e:
        duration = time.time() - start
        logger.exception("Orchestrator: failed after %.2fs: %s", duration, str(e))
        return {'status': 'error', 'duration_s': duration, 'error': str(e)}


def run_sync_guarded(task_id: str):
    """
    Guarded variant for background tasks. Persists a task result JSON for debugging.
    """
    logger.info("Guarded sync start: %s", task_id)
    result = run_sync()
    # write result file (best-effort)
    try:
        import json as _json
        with open(f"app/logs/task-{task_id}.json", "w", encoding="utf-8") as fh:
            _json.dump({'task_id': task_id, 'result': result}, fh, indent=2)
    except Exception:
        logger.exception("Failed to write task result file for %s", task_id)
    logger.info("Guarded sync complete: %s", task_id)
    return result
