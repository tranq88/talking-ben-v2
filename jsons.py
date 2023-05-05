import json


def read_json(filename: str) -> dict:
    """Load ./jsons/<filename> and return it as a dictionary."""
    with open(f'./jsons/{filename}', 'r') as f:
        return json.load(f)


def write_json(filename: str, json_: dict) -> None:
    """Overwrite ./jsons/<filename> with <json_>."""
    with open(f'./jsons/{filename}', 'w') as f:
        json.dump(json_, f, indent=4)
