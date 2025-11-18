import logging
logger = logging.getLogger('app.transform')
logger.setLevel(logging.INFO)


def apply_transformations(raw_results):
    """
    Apply deterministic transforms to raw results and return normalized data.
    This function should be replaced/extended with your real logic.
    """
    normalized = []
    for item in raw_results:
        try:
            data = item.get('data') if isinstance(item, dict) else item
            # Example transform: flatten lists, keep dicts as-is, else wrap.
            if isinstance(data, dict):
                normalized.append(data)
            elif isinstance(data, list):
                normalized.extend(data)
            else:
                normalized.append({'value': data})
        except Exception as e:
            logger.exception('Transform error: %s', str(e))
            normalized.append({'error': str(e)})
    return normalized
