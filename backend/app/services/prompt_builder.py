import json
from pathlib import Path

from app.schemas import HatchRequest


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_hatch_prompt(req: HatchRequest, cpp_features: dict) -> str:
    prompt_path = _project_root() / "prompt.md"
    template = prompt_path.read_text(encoding="utf-8")

    replacements = {
        "{{CHAT_LOG}}": req.chat_log,
        "{{RELATIONSHIP_CONTEXT}}": req.relationship_context or "",
        "{{USER_PREFERENCE}}": req.user_preference or "",
        "{{HATCH_GOAL}}": req.hatch_goal or "",
    }

    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)

    if cpp_features:
        output += "\n\ncpp_features:\n"
        output += json.dumps(cpp_features, ensure_ascii=False, indent=2)

    return output
