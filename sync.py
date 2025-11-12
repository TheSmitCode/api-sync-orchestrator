import os
import json
import requests
from datetime import datetime
from typing import Any

CONFIG_FILE = "test-sync.json"

# Load secrets from environment
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "TEST_KEY_123")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "TEST_KEY_123")

def fetch_api_data(source: dict) -> Any:
    """Fetch data from API source."""
    try:
        headers = {}
        if "auth_token" in source:
            headers["Authorization"] = f"Bearer {source['auth_token']}"
        response = requests.get(source["endpoint"], headers=headers, params=source.get("params", {}))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Fetching {source.get('endpoint')}: {e}")
        return None

def transform_data(data: Any, rules: dict) -> Any:
    """Transform data according to rules."""
    if not data:
        return None
    # Example: add timestamp field
    add_fields = rules.get("add_field", {})
    for k, v in add_fields.items():
        data[k] = datetime.utcnow().isoformat() if v == "{{ now() }}" else v
    # Additional filtering could be added here
    return data

def push_to_target(target: dict, data: Any) -> bool:
    """Push data to target (Airtable placeholder example)."""
    if not data:
        return False
    try:
        if target["type"] == "airtable":
            url = f"https://api.airtable.com/v0/{target['base_id']}/{target['table']}"
            headers = {"Authorization": f"Bearer {target.get('api_key', AIRTABLE_API_KEY)}",
                       "Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json={"fields": data})
            response.raise_for_status()
            return True
        # Additional targets (Postgres, webhooks) can be added here
        return False
    except Exception as e:
        print(f"[ERROR] Pushing to {target.get('type')}: {e}")
        return False

def load_config():
    """Load JSON sync configuration."""
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Loading config: {e}")
        return None

def run_sync(dry_run=False):
    """Run full sync."""
    config = load_config()
    if not config:
        return

    sources = config.get("sources", [])
    transform_rules = config.get("transform", {})
    target = config.get("target", {})

    for src in sources:
        data = fetch_api_data(src)
        data = transform_data(data, transform_rules)
        if dry_run:
            print(f"[DRY-RUN] Data prepared: {data}")
        else:
            success = push_to_target(target, data)
            print(f"[SYNC] Pushed to {target.get('type')} - Success: {success}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Test sync without pushing")
    args = parser.parse_args()
    run_sync(dry_run=args.dry_run)
