import json
import os
import subprocess
from pathlib import Path


def extract_features(chat_log: str, mode: str) -> dict:
    bin_path = os.getenv("CPP_FEATURE_BIN", "")
    if not bin_path:
        return {}

    target = Path(__file__).resolve().parents[3] / bin_path
    if not target.exists():
        return {}

    payload = {"chat_log": chat_log, "mode": mode}

    try:
        proc = subprocess.run(
            [str(target)],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=5,
        )
        return json.loads(proc.stdout.decode("utf-8"))
    except (subprocess.SubprocessError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
