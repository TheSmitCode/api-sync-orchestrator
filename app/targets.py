import json
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger('app.targets')
logger.setLevel(logging.INFO)


def load_targets(config_path='sync_config.json'):
    """
    Load a JSON config that defines `targets` as a list of objects:
    { "targets": [ { "name": "...", "url": "...", "timeout": 10, "headers": {...} }, ... ] }
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
            return cfg.get('targets', [])
    except FileNotFoundError:
        logger.warning('Config %s not found, using empty targets', config_path)
        return []
    except Exception:
        logger.exception('Failed to parse targets config')
        return []


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8),
       retry=retry_if_exception_type(Exception))
def call_target(target):
    """
    Call the target endpoint with sensible timeout and return JSON or text.
    Raises on non-2xx so the retry can trigger.
    """
    url = target.get('url')
    if not url:
        raise ValueError('Target missing url')
    timeout = target.get('timeout', 10)
    headers = target.get('headers') or {}
    logger.info('Calling target %s', url)
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return resp.text


def run_targets():
    """
    Iterate configured targets, call them and collect structured results.
    Errors are caught per-target and returned as part of the results.
    """
    targets = load_targets()
    results = []
    for t in targets:
        try:
            r = call_target(t)
            results.append({'target': t.get('name', 'unknown'), 'data': r})
        except Exception as e:
            logger.exception('Target failed: %s', t.get('url'))
            results.append({'target': t.get('name', 'unknown'), 'error': str(e)})
    return results
