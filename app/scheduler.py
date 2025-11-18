"""
Entrypoint for scheduled runs. Railway cron jobs should execute:
    python app/scheduler.py
"""
from app.orchestrator import run_sync
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('app.scheduler')
    logger.info("Scheduled sync starting")
    res = run_sync()
    logger.info("Scheduled sync result: %s", res)
