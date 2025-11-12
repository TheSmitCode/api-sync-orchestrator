import os
import json
import time
import logging
import requests
from dotenv import load_dotenv
from argparse import ArgumentParser

# Load environment variables from .env
load_dotenv()

# Logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE", "")

# Default retry attempts
RETRIES = int(os.getenv("RETRIES", 3))


def load_config(path="sync_config.json"):
    """Load JSON config safely"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config: {e}")
        raise


def fetch_stripe_invoices(limit=10):
    """Fetch invoices from Stripe"""
    if not STRIPE_SECRET_KEY:
        logger.warning("Stripe key missing, skipping fetch")
        return []

    url = f"https://api.stripe.com/v1/invoices?limit={limit}"
    headers = {"Authorization": f"Bearer {STRIPE_SECRET_KEY}"}

    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            invoices = response.json().get("data", [])
            logger.info(f"Fetched {len(invoices)} Stripe invoices")
            return invoices
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt} failed for Stripe: {e}")
            time.sleep(2 ** attempt)

    logger.error("All Stripe fetch attempts failed")
    return []


def fetch_airtable_records():
    """Fetch records from Airtable"""
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        logger.warning("Airtable credentials missing, skipping fetch")
        return []

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            records = response.json().get("records", [])
            logger.info(f"Fetched {len(records)} Airtable records")
            return records
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt} failed for Airtable: {e}")
            time.sleep(2 ** attempt)

    logger.error("All Airtable fetch attempts failed")
    return []


def main(config_path="sync_config.json", dry_run=False):
    """Main orchestrator function"""
    try:
        config = load_config(config_path)
        logger.info(f"Config loaded: {len(config.get('sources', []))} sources")
    except Exception:
        logger.error("Aborting due to invalid config")
        return

    all_data = []

    for source in config.get("sources", []):
        if source.get("api") == "stripe":
            limit = source.get("params", {}).get("limit", 10)
            all_data.extend(fetch_stripe_invoices(limit=limit))
        elif source.get("api") == "airtable":
            all_data.extend(fetch_airtable_records())

    if dry_run:
        logger.info(f"Dry run: {len(all_data)} items would be synced")
    else:
        # Placeholder: implement your actual sync logic
        logger.info(f"Syncing {len(all_data)} items...")
        # Example: write to Google Sheets or other target
        logger.info("Sync completed successfully")

    # Optional: write audit log
    os.makedirs("logs", exist_ok=True)
    audit_path = f"logs/audit_{int(time.time())}.json"
    audit_data = {"synced_count": len(all_data), "timestamp": int(time.time())}
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    logger.info(f"Audit saved: {audit_path}")


if __name__ == "__main__":
    parser = ArgumentParser(description="API Sync Orchestrator")
    parser.add_argument("--config", default="sync_config.json", help="Path to config JSON")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode")
    args = parser.parse_args()

    main(config_path=args.config, dry_run=args.dry_run)
