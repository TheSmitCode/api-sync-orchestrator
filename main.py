from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import uvicorn
import os
import json
from sync import main as sync_main  # Import the main function from sync.py

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")

@app.post("/sync")
async def sync_endpoint(body: Dict[str, Any]):
    """
    Accepts a JSON body with:
    {
        "config": {...},  # Optional override config
        "dry_run": True/False
    }
    """
    try:
        config = body.get('config', None)
        dry_run = body.get('dry_run', False)

        temp_config_path = None
        if config:
            # Save override config to temp file
            temp_config_path = "temp_config.json"
            with open(temp_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

        # Use temp config if provided, else default sync_config.json
        config_path = temp_config_path or "sync_config.json"

        sync_main(config_path, dry_run=dry_run)

        # Read latest audit log
        audit_files = sorted(
            [f for f in os.listdir("logs") if f.startswith("audit_")]
        )
        audit_data = {}
        if audit_files:
            last_audit_file = audit_files[-1]
            with open(f"logs/{last_audit_file}", "r", encoding="utf-8") as f:
                audit_data = json.load(f)

        # Cleanup temp file
        if temp_config_path and os.path.exists(temp_config_path):
            os.remove(temp_config_path)

        return {
            "status": "complete",
            "synced_count": audit_data.get("synced_count", 0),
            "audit": audit_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
