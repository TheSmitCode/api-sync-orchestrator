import os
import json
import time
import logging
import requests
from dotenv import load_dotenv
from argparse import ArgumentParser

# Load environment variables from .env
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Environment API keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE")

# Default retries
RETRIES = int(os.getenv("RETRIES", 3))


def load_config(path="sync_config.json"):
    """Load the sync configuration from JSON"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON config: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        raise


def fetch_stripe_invoices(limit=10):
    """Fetch invoices from Stripe API"""
    url = f"https://api.stripe.com/v1/invoices?limit={limit}"
    headers = {
        "Authorization": f"Bearer {STRIPE_SECRET_KEY}"
    }

    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Stripe fetch successful, {len(response.json().get('data', []))} invoices found")
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            logger.warning(f"Fetch attempt {attempt} failed for Stripe: {e}")
            time.sleep(2 ** attempt)

    logger.error("All Stripe fetch attempts failed")
    return []


def fetch_airtable_records():
    """Fetch records from Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            records = response.json().get("records", [])
            logger.info(f"Airtable fetch successful, {len(records)} records found")
            return records
        except requests.exceptions.RequestException as e:
            logger.warning(f"Fetch attempt {attempt} failed for Airtable: {e}")
            time.sleep(2 ** attempt)

    logger.error("All Airtable fetch attempts failed")
    return []


def main(config_path="sync_config.json", dry_run=False):
    """Main sync function"""
    try:
        config = load_config(config_path)
        logger.info(f"Validated config: {len(config.get('sources', []))} sources, {RETRIES} retries")
    except Exception:
        logger.error("Exiting due to invalid config")
        return

    all_data = []

    if "stripe" in config.get("sources", []):
        stripe_data = fetch_stripe_invoices(limit=config.get("stripe_limit", 10))
        if stripe_data:
            all_data.extend(stripe_data)
        else:
            logger.warning("No data fetched from Stripe")

    if "airtable" in config.get("sources", []):
        airtable_data = fetch_airtable_records()
        if airtable_data:
            all_data.extend(airtable_data)
        else:
            logger.warning("No data fetched from Airtable")

    if dry_run:
        logger.info(f"Dry run mode: {len(all_data)} items would be synced")
    else:
        # Implement your actual sync logic here
        logger.info(f"Syncing {len(all_data)} items...")
        # e.g., push to Google Sheets, database, etc.
        logger.info("Sync completed successfully")


if __name__ == "__main__":
    parser = ArgumentParser(description="API Sync Orchestrator")
    parser.add_argument("--config", default="sync_config.json", help="Path to sync configuration JSON")
    parser.add_argument("--dry-run", action="store_true", help="Run sync in dry-run mode (no writes)")
    args = parser.parse_args()

    main(config_path=args.config, dry_run=args.dry_run)
