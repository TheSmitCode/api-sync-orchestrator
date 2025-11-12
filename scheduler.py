import os
from apscheduler.schedulers.blocking import BlockingScheduler
from sync import run_sync

scheduler = BlockingScheduler()

# Default every 5 min; replace with config if needed
@scheduler.scheduled_job('cron', minute='*/5')
def scheduled_sync():
    run_sync()

if __name__ == "__main__":
    os.environ["DRY_RUN"] = "1"  # Change to 0 to push
    scheduler.start()
