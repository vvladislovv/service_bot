import json
from typing import Any, List, Union

def convert_to_json(data: Union[List[Any], Any]) -> str:
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Error converting to JSON: {e}")
