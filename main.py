from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import uvicorn
import os
import json  # For dump/load in /sync
from sync import run_sync  # Import run_sync from sync.py

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")

@app.get("/")
def root():
    return {"message": "API Sync Orchestrator running."}

@app.post("/sync")
def trigger_sync(body: Dict[str, Any]):  # Manual dict for body (no Pydantic)
    """
    Trigger a manual sync.
    Body: {"config": {...}, "dry_run": false}
    """
    try:
        config = body.get('config', {})
        dry_run = body.get('dry_run', True)
        
        # Save config to temp file
        temp_config = "temp_config.json"
        with open(temp_config, "w") as f:
            json.dump(config, f, indent=2)
        
        # Run sync
        result = run_sync(dry_run=dry_run, config_path=temp_config)
        
        # Read last audit (for response)
        audit_files = [f for f in os.listdir("logs") if f.startswith("audit_")][-1]
        with open(f"logs/{audit_files}", "r") as f:
            audit = json.load(f)
        
        os.remove(temp_config)  # Cleanup
        
        return {"status": "success", "dry_run": dry_run, "result": result, "audit": audit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)