from typing import Any


def parse_json_body(req) -> dict[str, Any]:
    data = req.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def parse_phone_list(raw_value) -> list[str]:
    import json

    if not raw_value:
        return []
    if isinstance(raw_value, list):
        return raw_value
    if isinstance(raw_value, str):
        try:
            parsed = json.loads(raw_value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []
