from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def apply_transform(data, transform=None):
    """
    Apply transformations to data list.
    
    Args:
        data (list): List of dicts to transform.
        transform (dict, optional): Dict with 'add_field' and 'filter' keys.
    
    Returns:
        list: Transformed/filtered data.
    
    Raises:
        ValueError: If data or transform is invalid.
    """
    if not isinstance(data, list):
        raise ValueError("Data must be a list of dicts")
    
    if transform is None:
        transform = {}
    
    if not isinstance(transform, dict):
        raise ValueError("Transform must be a dict")
    
    now_str = datetime.now().isoformat()
    transformed = []
    
    for item in data:
        if not isinstance(item, dict):
            logger.warning("Skipping non-dict item in data")
            continue
        
        new_item = dict(item)
        
        # Add fields
        add_fields = transform.get("add_field", {})
        for k, v in add_fields.items():
            if v == "{{ now() }}":
                new_item[k] = now_str
            else:
                new_item[k] = v
        
        # Filter
        filters = transform.get("filter", {})
        passed = True
        for k, v in filters.items():
            if new_item.get(k) != v:
                passed = False
                break
        
        if passed:
            transformed.append(new_item)
    
    logger.info(f"Transformed: {len(transformed)}/{len(data)} records kept")
    return transformed

if __name__ == "__main__":
    # Example usage
    sample_data = [{"id": "1", "status": "paid"}, {"id": "2", "status": "pending"}]
    sample_transform = {"add_field": {"timestamp": "{{ now() }}"}, "filter": {"status": "paid"}}
    result = apply_transform(sample_data, sample_transform)
    print(result)