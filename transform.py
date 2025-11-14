# transform.py
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def apply_transform(data, transform=None):
    """
    Apply transformation and optional filtering on a list of dicts.

    This supports:
      - Adding static fields
      - Adding dynamic fields like "{{ now() }}"
      - Simple equality filters

    Args:
        data (list): List of dicts to transform.
        transform (dict, optional): Contains optional keys:
            - 'add_field': {"field": "value" or "{{ now() }}"}
            - 'filter': {"field": "value"}

    Returns:
        list: Transformed/filtered data.

    Raises:
        ValueError: If input format is invalid.
    """

    # ---- Validate data ----
    if not isinstance(data, list):
        raise ValueError("Data must be a list of dicts")

    if transform is None:
        transform = {}

    if not isinstance(transform, dict):
        raise ValueError("Transform must be a dict")

    now_str = datetime.now().isoformat()
    transformed = []

    # ---- Process each record ----
    for item in data:
        if not isinstance(item, dict):
            logger.warning("Skipping non-dict item in data")
            continue

        new_item = dict(item)  # shallow clone

        # ---- Apply add_field ----
        add_fields = transform.get("add_field", {})
        if not isinstance(add_fields, dict):
            logger.warning("Invalid add_field structure — skipping")
            add_fields = {}

        for k, v in add_fields.items():
            if v == "{{ now() }}":
                new_item[k] = now_str
            else:
                new_item[k] = v

        # ---- Apply simple filters ----
        filters = transform.get("filter", {})
        if not isinstance(filters, dict):
            logger.warning("Invalid filter structure — skipping")
            filters = {}

        passed = True
        for fk, fv in filters.items():
            if new_item.get(fk) != fv:
                passed = False
                break

        if passed:
            transformed.append(new_item)

    logger.info(f"Transformed: {len(transformed)}/{len(data)} records kept")

    return transformed


if __name__ == "__main__":
    # Example usage for debugging
    sample_data = [
        {"id": "1", "status": "paid"},
        {"id": "2", "status": "pending"}
    ]
    sample_transform = {
        "add_field": {"timestamp": "{{ now() }}"},
        "filter": {"status": "paid"}
    }
    result = apply_transform(sample_data, sample_transform)
    print(result)
