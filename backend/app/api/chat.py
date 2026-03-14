from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services.llm.model_client import generate_chat_reply
from app.services.storage.chat_import_store import get_recent_chat_logs
from app.services.storage.conversation_store import (
    delete_conversation_messages,
    get_recent_conversation_messages,
    save_conversation_message,
)
from app.services.storage.store import load_brain_state

router = APIRouter()


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _build_system_prompt(brain_state: dict, chat_log_snippets: list[str]) -> str:
    brain_profile = brain_state.get("brain_profile", {})
    language_model = brain_state.get("language_model", {})
    emotion_model = brain_state.get("emotion_model", {})
    relationship_model = brain_state.get("relationship_model", {})
    runtime_assets = brain_state.get("runtime_assets", {})

    tone = "、".join(_as_str_list(language_model.get("tone"))[:3]) or "温和"
    catchphrases = "、".join(_as_str_list(language_model.get("catchphrases"))[:3])
    comfort_lines = "、".join(_as_str_list(language_model.get("comfort_lines"))[:2])
    topics = "、".join(_as_str_list(runtime_assets.get("topics") if isinstance(runtime_assets, dict) else [])[:5])

    profile_summary = ""
    if isinstance(brain_profile, dict):
        profile_summary = "、".join(
            f"{k}: {v}" for k, v in brain_profile.items()
            if isinstance(v, str) and v
        )

    emotion_summary = ""
    if isinstance(emotion_model, dict):
        emotion_summary = "、".join(
            f"{k}: {v}" for k, v in emotion_model.items()
            if isinstance(v, str) and v
        )

    relationship_summary = ""
    if isinstance(relationship_model, dict):
        relationship_summary = "、".join(
            f"{k}: {v}" for k, v in relationship_model.items()
            if isinstance(v, str) and v
        )

    # 最近几条聊天记录片段，截取前 400 字符避免 token 过多
    snippet_text = ""
    if chat_log_snippets:
        excerpts = [s[:400] for s in chat_log_snippets if s]
        snippet_text = "\n\n".join(f"[聊天记录片段]\n{exc}" for exc in excerpts)

    parts = [
        "你是用户的专属宠物陪伴 AI，拥有独特的性格和语言风格，请始终保持角色一致性。",
    ]
    if profile_summary:
        parts.append(f"性格特征：{profile_summary}")
    if emotion_summary:
        parts.append(f"情感倾向：{emotion_summary}")
    if relationship_summary:
        parts.append(f"关系模式：{relationship_summary}")
    parts.append(f"说话风格：{tone}")
    if catchphrases:
        parts.append(f"口头禅：{catchphrases}")
    if comfort_lines:
        parts.append(f"安慰语：{comfort_lines}")
    if topics:
        parts.append(f"用户关注的话题：{topics}")
    if snippet_text:
        parts.append(f"\n以下是用户过去导入的聊天记录，用于帮助你了解用户习惯和背景：\n{snippet_text}")
    parts.append("\n根据以上背景，自然地回应用户，语言简洁、有温度，不超过 150 字。")

    return "\n".join(parts)


def _save_conversation_message_safely(*, brain_id: str, role: str, content: str) -> None:
    try:
        save_conversation_message(brain_id=brain_id, role=role, content=content)
    except Exception as exc:
        print(f"[warn] failed to persist conversation message: {exc}")


@router.post("/api/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """对话端点：结合 brain_state、历史聊天记录和对话上下文生成回复。"""
    existing = load_brain_state(req.brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")

    brain_state = existing.get("brain_state", {})
    if not isinstance(brain_state, dict):
        brain_state = {}

    # 从数据库拉取该 brain_id 最近的聊天记录作为背景上下文
    chat_log_snippets = get_recent_chat_logs(req.brain_id, limit=3)

    # 优先使用数据库中的真实对话历史；兼容旧前端时再回退到请求体里的 history。
    stored_messages = get_recent_conversation_messages(req.brain_id, limit=20)
    if stored_messages:
        history_messages = [
            {"role": "user" if turn["role"] == "user" else "assistant", "content": turn["content"]}
            for turn in stored_messages
        ]
    else:
        history_messages = [
            {"role": "user" if turn.role == "user" else "assistant", "content": turn.content}
            for turn in req.history
        ]

    system_prompt = _build_system_prompt(brain_state, chat_log_snippets)

    try:
        reply = generate_chat_reply(system_prompt, history_messages, req.user_message)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"模型调用失败: {exc}") from exc

    _save_conversation_message_safely(brain_id=req.brain_id, role="user", content=req.user_message)
    _save_conversation_message_safely(brain_id=req.brain_id, role="assistant", content=reply)

    return ChatResponse(brain_id=req.brain_id, reply=reply)


@router.delete("/api/v1/conversation/{brain_id}")
def clear_conversation(brain_id: str) -> dict[str, object]:
    """删除某个 brain_id 对应的全部对话历史。"""
    existing = load_brain_state(brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")

    deleted_count = delete_conversation_messages(brain_id)
    return {"brain_id": brain_id, "deleted_count": deleted_count}
