import json
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
from sync import run_sync
from croniter import croniter

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = "sync_config.json"


def start_scheduler(dry_run=False):
    """
    Start the scheduler using cron from JSON config.
    """
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        schedule_str = config.get("schedule", "*/5 * * * *")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Invalid config: {e}")
        return

    cron = croniter(schedule_str, datetime.now())
    next_run = cron.get_next(datetime)
    logger.info(f"Scheduler started with {schedule_str}, next run at {next_run}")

    while True:
        now = datetime.now()
        if now >= next_run:
            logger.info(f"Running scheduled sync at {now}")
            run_sync(dry_run=dry_run)
            next_run = cron.get_next(datetime)
        time.sleep(60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scheduler for API Sync Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Do not push to targets")
    args = parser.parse_args()
    start_scheduler(dry_run=args.dry_run)
