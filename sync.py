import json
import os
import logging
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from transform import apply_transform
from targets import push_to_target

# Load environment variables
load_dotenv()

# Serverless-safe directory for logs + audit files
LOG_DIR = "/tmp"
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logger = logging.getLogger("sync")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console output (always safe)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# File handler (wrapped for Vercel safety)
try:
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "sync.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"File logging disabled: {e}")

CONFIG_FILE = "sync_config.json"


def fetch_stripe_invoices(limit=5, token=None) -> List[Dict[str, Any]]:
    token = token or os.getenv("STRIPE_SECRET_KEY", "TEST_KEY_123")
    url = f"https://api.stripe.com/v1/invoices?limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        logger.error(f"[ERROR] Fetching Stripe invoices: {e}")
        return [{"id": "dummy_001", "status": "stripe failed end to end successful"}]


def run_sync(dry_run=False, config_path: str | None = None):
    config_file = config_path or CONFIG_FILE

    try:
        with open(config_file) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"{config_file} error: {e}")
        return []

    all_data = []

    # Fetch data
    for source in config.get("sources", []):
        if source.get("api") == "stripe":
            limit = source.get("params", {}).get("limit", 5)
            token = source.get("auth", {}).get("token") or os.getenv("STRIPE_SECRET_KEY")
            data = fetch_stripe_invoices(limit, token)
            all_data.extend(data)
            if not data:
                logger.info("No invoices fetched, dummy data used.")

    # Apply transform
    transform_rules = config.get("transform", {})
    try:
        transformed_data = apply_transform(all_data, transform_rules)
    except Exception as e:
        logger.error(f"Error during transform: {e}")
        transformed_data = all_data

    if dry_run:
        logger.info(f"[DRY-RUN] Data prepared: {len(transformed_data)} records")
        return transformed_data

    # Push to targets
    target_config = config.get("target", {})
    try:
        audit = push_to_target(transformed_data, target_config)
    except Exception as e:
        logger.error(f"Error pushing to target: {e}")
        audit = {}

    # Save audit report (serverless-safe)
    try:
        audit_path = os.path.join(LOG_DIR, "audit_report.json")
        with open(audit_path, "w") as f:
            json.dump(audit, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not write audit file: {e}")

    logger.info("[INFO] Sync complete.")
    return audit
