from fastapi import FastAPI, BackgroundTasks
from app.orchestrator import run_sync, run_sync_guarded

app = FastAPI(
    title="API Sync Orchestrator",
    description="Backend orchestrator for API sync tasks",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "API Sync Orchestrator is running"}


@app.post("/run-sync")
def run_sync_endpoint():
    return run_sync()


@app.post("/run-sync/background")
def run_sync_background(task: BackgroundTasks):
    import uuid

    task_id = str(uuid.uuid4())
    task.add_task(run_sync_guarded, task_id)

    return {"status": "queued", "task_id": task_id}


@app.get("/health")
def health_check():
    return {"status": "ok"}
