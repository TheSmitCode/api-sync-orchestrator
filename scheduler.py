from apscheduler.schedulers.blocking import BlockingScheduler
from sync import run_sync

sched = BlockingScheduler()

# Every 5 minutes
sched.add_job(run_sync, 'cron', minute='*/5', kwargs={"dry_run": False})

if __name__ == "__main__":
    print("[SCHEDULER] Starting...")
    sched.start()
