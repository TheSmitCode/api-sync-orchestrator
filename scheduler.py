import json
import logging
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from sync import main as sync_main
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.getenv("SYNC_CONFIG_PATH", "sync_config.json")
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", 300))  # default 5 min

scheduler = BlockingScheduler()

def run_sync():
    try:
        logger.info("Starting scheduled sync...")
        sync_main(config_path=CONFIG_PATH, dry_run=False)
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")

def load_schedule():
    """Optional: Load a JSON schedule if you want custom times per source"""
    schedule_file = os.getenv("SCHEDULE_FILE", "schedule.json")
    if os.path.exists(schedule_file):
        with open(schedule_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

if __name__ == "__main__":
    # Example: run every X seconds
    scheduler.add_job(run_sync, "interval", seconds=SYNC_INTERVAL_SECONDS)
    logger.info(f"Scheduler started, running every {SYNC_INTERVAL_SECONDS} seconds")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
