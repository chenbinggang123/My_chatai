import json
import os

from openai import OpenAI


def _extract_json_block(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    return text


def _extract_balanced_json_object(text: str) -> str:
    """Extract first balanced JSON object substring from arbitrary text."""
    start = text.find("{")
    if start < 0:
        return ""

    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]

    return ""


def _parse_json_candidates(content: str) -> dict:
    """Try parsing model output with progressively tolerant extraction."""
    candidates = []
    raw = content.strip()
    if raw:
        candidates.append(raw)

    fenced = _extract_json_block(raw)
    if fenced and fenced not in candidates:
        candidates.append(fenced)

    balanced = _extract_balanced_json_object(raw)
    if balanced and balanced not in candidates:
        candidates.append(balanced)

    if fenced:
        balanced_fenced = _extract_balanced_json_object(fenced)
        if balanced_fenced and balanced_fenced not in candidates:
            candidates.append(balanced_fenced)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    if last_error:
        raise last_error
    raise json.JSONDecodeError("Empty model output", "", 0)


def _repair_json_with_model(client: OpenAI, model_name: str, invalid_output: str) -> str:
    """Ask the model to repair malformed JSON and return JSON only."""
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You fix malformed JSON. Output valid JSON only with no markdown and no explanation.",
            },
            {
                "role": "user",
                "content": invalid_output,
            },
        ],
        temperature=0.0,
    )
    return completion.choices[0].message.content or ""


def generate_brain_state(prompt_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    base_url = os.getenv("OPENAI_BASE_URL") or None
    model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")

    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You must output valid JSON only.",
            },
            {
                "role": "user",
                "content": prompt_text,
            },
        ],
        temperature=0.4,
    )

    content = completion.choices[0].message.content or ""
    if not content:
        raise RuntimeError("Model returned empty content")

    try:
        return _parse_json_candidates(content)
    except json.JSONDecodeError as exc:
        # One automatic repair pass: useful for minor JSON formatting mistakes.
        repaired = _repair_json_with_model(client, model_name, content)
        if not repaired:
            raise RuntimeError(f"Model output is not valid JSON: {exc}") from exc
        try:
            return _parse_json_candidates(repaired)
        except json.JSONDecodeError as repair_exc:
            raise RuntimeError(f"Model output is not valid JSON: {repair_exc}") from repair_exc


def generate_chat_reply(
    system_prompt: str,
    history: list[dict],
    user_message: str,
) -> str:
    """调用大模型生成对话回复。history 中 role 应为 'user' 或 'assistant'。"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    base_url = os.getenv("OPENAI_BASE_URL") or None
    model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")

    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,  # type: ignore[arg-type]
        temperature=0.7,
    )
    return (completion.choices[0].message.content or "").strip()
