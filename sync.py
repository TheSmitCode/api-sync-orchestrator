import os
import requests
import json
from datetime import datetime

DRY_RUN = os.getenv("DRY_RUN", "1") == "1"

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "TEST_KEY_123")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "TEST_KEY_123")

CONFIG_FILE = "sync_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Config file {CONFIG_FILE} not found.")
        return None
    with open(CONFIG_FILE) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return None

def fetch_api_data(source):
    if DRY_RUN:
        print(f"[MOCK] Fetching {source.get('endpoint')}")
        return [{"id": "mock_invoice_1", "amount": 1000, "status": "paid"}]
    headers = {}
    auth = source.get("auth", {})
    if auth.get("type") == "bearer":
        headers["Authorization"] = f"Bearer {auth.get('token')}"
    try:
        r = requests.get(source.get("endpoint"), headers=headers, params=source.get("params", {}))
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[ERROR] Fetching {source.get('endpoint')}: {e}")
        return None

def transform_data(data, rules):
    if not data:
        return None
    transformed = []
    for item in data:
        new_item = item.copy()
        add_field = rules.get("add_field", {})
        for k, v in add_field.items():
            new_item[k] = v if not v.startswith("{{") else datetime.now().isoformat()
        filter_rules = rules.get("filter", {})
        if all(item.get(k) == v for k, v in filter_rules.items()):
            transformed.append(new_item)
    return transformed

def push_to_target(data, target):
    if DRY_RUN:
        print(f"[DRY-RUN] Data prepared: {data}")
        return True
    # Example Airtable push
    if target.get("type") == "airtable":
        headers = {"Authorization": f"Bearer {target.get('api_key')}", "Content-Type": "application/json"}
        for record in data:
            try:
                r = requests.post(f"https://api.airtable.com/v0/{target.get('base_id')}/{target.get('table')}",
                                  headers=headers, json={"fields": record})
                r.raise_for_status()
            except requests.RequestException as e:
                print(f"[ERROR] Pushing record: {e}")
                continue
    return True

def run_sync():
    config = load_config()
    if not config:
        return
    sources = config.get("sources", [])
    for source in sources:
        data = fetch_api_data(source)
        transformed = transform_data(data, config.get("transform", {}))
        push_to_target(transformed, config.get("target", {}))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Do not push data")
    args = parser.parse_args()
    if args.dry_run:
        os.environ["DRY_RUN"] = "1"
    run_sync()
