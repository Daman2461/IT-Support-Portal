import json
from datetime import datetime

LOG_FILE = "action_log.jsonl"

def log_action(action: str, params: dict, result: dict):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "params": params,
        "result": result
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
