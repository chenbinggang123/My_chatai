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


def generate_brain_state(prompt_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when USE_MOCK_MODEL=false")

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

    json_text = _extract_json_block(content)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model output is not valid JSON: {exc}") from exc
