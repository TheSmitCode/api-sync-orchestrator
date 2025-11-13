# =========================
# FILE: sync.py
# DESCRIPTION: Handles data fetching, transformation, and pushing to targets.
# =========================

import json
import time
import os
from typing import List, Dict, Any
import logging
from datetime import datetime
import argparse
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv  # Load .env
from transform import apply_transform  # Modular transform
from targets import push_to_target  # Modular push

load_dotenv()  # Loads .env or Vercel env vars

# Setup logging (console + file)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = "sync_config.json"


def fetch_stripe_invoices(limit=5, token=None):
    """
    Fetch invoices from Stripe.
    Returns JSON list of invoices.
    """
    if not token:
        token = os.getenv("STRIPE_SECRET_KEY", "TEST_KEY_123")
    
    url = f"https://api.stripe.com/v1/invoices?limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"[ERROR] Fetching Stripe invoices: {e}")
        return []


def run_sync(dry_run=False):
    """
    Main sync function. Can be called by scheduler or API.
    dry_run=True skips pushes to targets.
    """
    # Load config
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"{CONFIG_FILE} not found.")
        return
    except json.JSONDecodeError:
        logger.error(f"{CONFIG_FILE} is invalid JSON.")
        return

    # Step 1: Fetch data
    sources = config.get("sources", [])
    all_data = []
    for source in sources:
        if source.get("api") == "stripe":
            limit = source.get("params", {}).get("limit", 5)
            token = source.get("auth", {}).get("token") or os.getenv("STRIPE_SECRET_KEY")
            data = fetch_stripe_invoices(limit, token)
            if not data:
                logger.info("No invoices fetched.")
            all_data.extend(data)

    # Step 2: Apply transforms
    transform_rules = config.get("transform", {})
    transformed_data = apply_transform(all_data, transform_rules)

    if dry_run:
        logger.info(f"[DRY-RUN] Data prepared: {len(transformed_data)} records")
        return transformed_data

    # Step 3: Push to targets
    target_config = config.get("target", {})
    audit = push_to_target(transformed_data, target_config)
    logger.info("[INFO] Sync complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run API Sync Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Do not push to targets")
    args = parser.parse_args()
    run_sync(dry_run=args.dry_run)
