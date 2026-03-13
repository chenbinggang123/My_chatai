import json
from pathlib import Path
from uuid import uuid4

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_brain_state(brain_state: dict) -> str:
    brain_id = str(uuid4())
    payload = {"brain_id": brain_id, "brain_state": brain_state}
    path = DATA_DIR / f"{brain_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return brain_id


def load_brain_state(brain_id: str) -> dict | None:
    path = DATA_DIR / f"{brain_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def update_brain_state(brain_id: str, brain_state: dict) -> None:
    payload = {"brain_id": brain_id, "brain_state": brain_state}
    path = DATA_DIR / f"{brain_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
