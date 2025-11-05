from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # v1 locked—no conflicts
from typing import Dict, Any
import uvicorn
from sync import main  # Import main from sync.py

app = FastAPI(title="API Sync Orchestrator", version="1.0.0")

class SyncRequest(BaseModel):
    config: Dict[str, Any]  # Full JSON config
    dry_run: bool = False

@app.post("/sync")
async def sync_endpoint(req: SyncRequest):
    try:
        # Save config to temp file (for main())
        temp_config = "temp_config.json"
        with open(temp_config, "w") as f:
            json.dump(req.config, f, indent=2)
        
        # Run sync
        main(temp_config, req.dry_run)
        
        # Read audit (last file in logs/)
        audit_files = [f for f in os.listdir("logs") if f.startswith("audit_")][-1]
        with open(f"logs/{audit_files}", "r") as f:
            audit = json.load(f)
        
        os.remove(temp_config)  # Cleanup
        
        return {"status": "complete", "synced_count": audit["synced_count"], "audit": audit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)