from datetime import datetime

def apply_transform(data, transform):
    result = []

    for item in data:
        new_item = dict(item)

        # Add fields
        add_fields = transform.get("add_field", {})
        for k, v in add_fields.items():
            if v == "{{ now() }}":
                new_item[k] = datetime.utcnow().isoformat()
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
            result.append(new_item)

    return result
