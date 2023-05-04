import json


def read_config(filename: str) -> dict:
    """Load ./configs/<filename> and return it as a dictionary."""
    with open(f'./configs/{filename}', 'r') as f:
        return json.load(f)


def write_config(filename: str, config: dict) -> None:
    """Overwrite ./configs/<filename> with <config>."""
    with open(f'./configs/{filename}', 'w') as f:
        json.dump(config, f, indent=4)
