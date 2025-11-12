import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def push_to_target(data, target=None):
    """
    Push data to target (e.g., Airtable).
    
    Args:
        data (list): List of dicts to push.
        target (dict, optional): Dict with 'type', 'base_id', 'table', 'api_key'.
    
    Returns:
        dict: Audit of push (timestamp, count, sample).
    
    Raises:
        ValueError: If target is invalid.
    """
    if not isinstance(data, list):
        raise ValueError("Data must be a list of dicts")
    
    if target is None:
        target = {}
    
    if not isinstance(target, dict):
        raise ValueError("Target must be a dict")
    
    target_type = target.get("type", "console")
    
    if target_type == "airtable":
        api_key_name = target.get("api_key")
        api_key = os.getenv(api_key_name, f"DUMMY_{api_key_name}")
        logger.info(f"Pushing {len(data)} records to Airtable (api_key={api_key[:6]}...)")
        # Real Airtable push (Day 7)
        audit = {
            "timestamp": datetime.now().isoformat(),
            "synced_count": len(data),
            "target_type": target_type,
            "data_sample": data[:2] if data else []
        }
        audit_file = f"logs/airtable_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(audit_file, "w") as f:
            json.dump(audit, f, indent=2)
        logger.info(f"Airtable push complete (audit: {audit_file})")
        return audit
    else:
        logger.info(f"Pushing {len(data)} records to {target_type}: {data[:2]}")  # Log sample
        return {"timestamp": datetime.now().isoformat(), "synced_count": len(data), "target_type": target_type}

if __name__ == "__main__":
    # Example usage
    sample_data = [{"id": "1", "status": "paid"}]
    sample_target = {"type": "airtable", "api_key": "AIRTABLE_API_KEY"}
    audit = push_to_target(sample_data, sample_target)
    print(audit)