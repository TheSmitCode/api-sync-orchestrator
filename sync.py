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

# --- Manual Config Validation (No Pydantic) ---
def validate_config(data: Dict[str, Any]) -> Dict[str, Any]:
    # Check required keys
    required_keys = ['sources', 'transform', 'target', 'schedule', 'retries']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    # Validate types/len
    if not isinstance(data['sources'], list) or len(data['sources']) == 0:
        raise ValueError("sources must be a non-empty list")
    for s in data['sources']:
        if not all(k in s for k in ['api', 'endpoint', 'auth']):
            raise ValueError("Each source must have 'api', 'endpoint', 'auth'")
        if 'auth' in s and not all(k in s['auth'] for k in ['type', 'token']):
            raise ValueError("auth must have 'type' and 'token'")
    
    if not isinstance(data['transform'], dict):
        raise ValueError("transform must be a dict")
    if not isinstance(data['target'], dict) or not all(k in data['target'] for k in ['type', 'base_id', 'table', 'api_key']):
        raise ValueError("target must have 'type', 'base_id', 'table', 'api_key'")
    
    if not isinstance(data['schedule'], str):
        raise ValueError("schedule must be a str")
    if not isinstance(data['retries'], int) or data['retries'] < 1:
        raise ValueError("retries must be a positive int")
    
    logger.info(f"Validated config: {len(data['sources'])} sources, {data['retries']} retries")
    return data

# --- Load Config ---
def load_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file '{path}' not found.")
    with open(path, "r") as f:
        data = json.load(f)
    return validate_config(data)

# --- Fetch with Retries (Real Stripe API – Fixed URL) ---
def fetch_from_source(source: Dict[str, Any], retries: int = 3) -> List[Dict[str, Any]]:
    base_url = "https://api.stripe.com/v1"
    endpoint = source['endpoint'].lstrip('/')  # Fix: Strip leading "/" to avoid double v1
    url = f"{base_url}/{endpoint}"
    token = source['auth']['token'] or os.getenv('STRIPE_SECRET_KEY')  # JSON or .env
    headers = {"Authorization": f"Bearer {token}"}
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, params=source['params'], timeout=10)
            response.raise_for_status()
            data = response.json()
            records = data.get('data', [])
            logger.info(f"Fetched {len(records)} records from {source['api']} (attempt {attempt})")
            return records
        except RequestException as e:
            logger.warning(f"Fetch attempt {attempt} failed for {source['api']}: {e}")
            if attempt == retries:
                logger.error(f"All {retries} attempts failed")
                return []
            time.sleep(2 ** attempt)  # Exponential backoff

# --- Transform ---
def apply_transform(data: List[Dict[str, Any]], transform: Dict[str, Any]) -> List[Dict[str, Any]]:
    now_str = datetime.now().isoformat()
    transformed = []
    for item in data:
        # Add fields
        for k, v in transform.get('add_field', {}).items():
            if v == "{{ now() }}":
                item[k] = now_str
            else:
                item[k] = v
        # Filter
        keep = True
        for k, v in transform.get('filter', {}).items():
            if item.get(k) != v:
                keep = False
                break
        if keep:
            transformed.append(item.copy())  # Avoid mutating original
    logger.info(f"Transformed: {len(transformed)}/{len(data)} records kept")
    return transformed

# --- Push (Dummy Log for MVP; Real Airtable in Day 7) ---
def push_to_target(data: List[Dict[str, Any]], target: Dict[str, Any]) -> Dict[str, Any]:
    # Dummy "push" (create audit JSON)
    audit = {
        "timestamp": datetime.now().isoformat(),
        "synced_count": len(data),
        "target_type": target['type'],
        "data_sample": data[:2] if data else []
    }
    audit_file = f"logs/audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(audit_file, "w") as f:
        json.dump(audit, f, indent=2)
    logger.info(f"Pushed {len(data)} items to {target['type']} (audit: {audit_file})")
    return audit

# --- Main ---
def main(config_path: str, dry_run: bool = False):
    try:
        config = load_config(config_path)
        all_data = []
        for source in config['sources']:
            fetched = fetch_from_source(source, config['retries'])
            if not fetched:
                logger.warning(f"Skipping source {source['api']} (no data)")
                continue
            transformed = apply_transform(fetched, config['transform'])
            all_data.extend(transformed)
        
        if not all_data:
            logger.warning("No data to sync—check sources/transform")
            return
        
        if dry_run:
            logger.info(f"Dry run: would sync {len(all_data)} records")
        else:
            audit = push_to_target(all_data, config['target'])
            logger.info(f"Audit summary: {len(all_data)} synced")
        
        logger.info("Sync complete!")
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API Sync Orchestrator")
    parser.add_argument("--config", default="sync_config.json", help="Path to config (default: sync_config.json)")
    parser.add_argument("--dry-run", action="store_true", help="Test without pushing")
    args = parser.parse_args()
    main(args.config, args.dry_run)