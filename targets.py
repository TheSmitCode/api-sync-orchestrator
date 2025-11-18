# targets.py
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def push_to_target(data, target=None):
    """
    Push data to a target such as Airtable or console debugging.

    Args:
        data (list): List of dicts to push.
        target (dict, optional): Should contain:
            - type: "airtable" or "console"
            - base_id, table: for Airtable (future)
            - api_key: ENV var name containing Airtable API key

    Returns:
        dict: Basic audit information about the sync.
    """

    # ---- Validate data ----
    if not isinstance(data, list):
        raise ValueError("Data must be a list of dicts")

    if target is None:
        target = {}

    if not isinstance(target, dict):
        raise ValueError("Target must be a dict")

    target_type = target.get("type", "console")

    # ---- Airtable push ----
    if target_type == "airtable":
        api_key_name = target.get("api_key")

        if not api_key_name:
            logger.error("Airtable target missing 'api_key' field.")
            return {
                "timestamp": datetime.now().isoformat(),
                "synced_count": 0,
                "target_type": "airtable",
                "error": "Missing api_key"
            }

        api_key = os.getenv(api_key_name)
        if not api_key:
            logger.warning(
                f"Airtable API key '{api_key_name}' not found in env — using dummy."
            )
            api_key = f"DUMMY_{api_key_name}"

        # Log first part of key for diagnostic only (don't leak full key)
        display_key = api_key[:6] + "..." if len(api_key) > 6 else api_key
        logger.info(f"Pushing {len(data)} records to Airtable (key={display_key})")

        # -------- REAL Airtable push planned for Day 7 --------
        # For now we emulate a successful sync.

        audit = {
            "timestamp": datetime.now().isoformat(),
            "synced_count": len(data),
            "target_type": target_type,
            "data_sample": data[:2] if data else []
        }

        # Ensure logs directory exists
        try:
            os.makedirs("logs", exist_ok=True)
            audit_file = f"logs/airtable_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(audit, f, indent=2)
            logger.info(f"Airtable push complete (audit saved: {audit_file})")
        except Exception as e:
            logger.warning(f"Could not write audit file to logs/: {e}")

        return audit

    # ---- Unknown or console target: fallback to logging only ----
    logger.info(f"Pushing {len(data)} records to {target_type} (sample: {data[:2]})")

    return {
        "timestamp": datetime.now().isoformat(),
        "synced_count": len(data),
        "target_type": target_type,
        "data_sample": data[:2] if data else []
    }


if __name__ == "__main__":
    # Example debug usage
    sample_data = [{"id": "1", "status": "paid"}]
    sample_target = {"type": "airtable", "api_key": "AIRTABLE_API_KEY"}

    audit = push_to_target(sample_data, sample_target)
    print(audit)
