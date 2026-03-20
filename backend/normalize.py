"""Normalize ground-truth and prediction records to a single SOAP string."""

SOAP_KEYS = ("subjective", "objective", "assessment", "plan")


def _flatten_nested_soap_section(content):
    """Convert one SOAP section that may be str, list, or nested dict into text fragments."""
    parts = []
    if isinstance(content, dict):
        for val in content.values():
            if isinstance(val, list):
                parts.extend(str(x) for x in val)
            else:
                parts.append(str(val))
    elif isinstance(content, list):
        parts.extend(str(x) for x in content)
    else:
        parts.append(str(content))
    return parts


def flatten_nested_prediction(data):
    """Convert nested dict/list SOAP (e.g. JarvisMD) into one string for metrics."""
    text_parts: list[str] = []
    for key in SOAP_KEYS:
        content = data.get(key, "")
        if not content and content != 0:
            continue
        text_parts.extend(_flatten_nested_soap_section(content))
    return " ".join(text_parts)


def soap_string_from_groundtruth(record):
    """Concatenate flat SOAP fields from a ground-truth record."""
    return " ".join(str(record.get(k, "") or "") for k in SOAP_KEYS)


def soap_string_from_prediction(record):
    """
    Build SOAP string from a prediction record.
    If all SOAP values look like plain strings (flat schema), concatenate them.
    Otherwise flatten nested structures.
    """
    sections = [record.get(k) for k in SOAP_KEYS]
    if all(
        s is None or isinstance(s, str)
        for s in sections
    ):
        return " ".join(str(s or "") for s in sections)

    return flatten_nested_prediction(record)
