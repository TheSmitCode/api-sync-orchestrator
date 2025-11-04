import json
import time
from datetime import datetime
import logging
from sync import main  # Import main from sync.py

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Run the sync
def run_sync():
    try:
        main("sync_config.json", dry_run=False)  # Full run
        logger.info(f"Scheduled sync complete at {datetime.now()}")
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")

# Load schedule from JSON
def load_schedule():
    with open("sync_config.json", "r") as f:
        data = json.load(f)
    return data['schedule']

# Start scheduler
if __name__ == "__main__":
    from croniter import croniter
    schedule_str = load_schedule()
    cron = croniter(schedule_str, datetime.now())
    next_run = cron.get_next(datetime)
    logger.info(f"Starting scheduler with {schedule_str}. Next run at {next_run}")
    while True:
        if datetime.now() >= next_run:
            run_sync()
            next_run = cron.get_next(datetime)
        time.sleep(60)  # Check every minute