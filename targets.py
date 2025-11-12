import os
import logging

def push_to_target(data, target):
    target_type = target.get("type", "console")
    if target_type == "airtable":
        api_key_name = target.get("api_key")
        api_key = os.getenv(api_key_name, f"DUMMY_{api_key_name}")
        logging.info(f"Pushing {len(data)} records to Airtable (api_key={api_key[:6]}...)")
    else:
        logging.info(f"Pushing {len(data)} records to {target_type}: {data}")
