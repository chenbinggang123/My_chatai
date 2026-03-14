# =============================================================================
# 宠物大脑孵化与学习后端 API 主入口
# =============================================================================
# 路由设计：
# - POST /api/v1/hatch              孵化：首次导入聊天记录，生成宠物初始大脑
# - POST /api/v1/learn              学习：对已有大脑增量学习，更新语言与里程碑
# - GET  /api/v1/brain/{id}         读取：按 brain_id 获取当前完整大脑状态
# - GET  /api/v1/chat-imports       查询：回溯历史聊天导入记录
# - GET  /api/v1/health             健康检查
# =============================================================================

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.schemas import (
    BrainStateResponse,
    ChatImportListResponse,
    HatchRequest,
    HealthResponse,
    LearnRequest,
    LearnResponse,
)
from app.services.cpp_bridge import extract_features
from app.services.llm.model_client import generate_brain_state
from app.services.llm.prompt_builder import build_hatch_prompt
from app.services.llm.schema_validator import BrainStateValidationError, validate_brain_state
from app.services.storage.brain_store import (
    delete_brain_state,
    init_brain_store,
    load_brain_state,
    save_brain_state,
    update_brain_state,
)
from app.services.storage.chat_import_store import (
    delete_chat_imports_by_brain_id,
    init_chat_import_store,
    query_chat_imports,
    save_chat_import,
)
from app.services.storage.conversation_store import delete_conversation_messages, init_conversation_store

# ---------------------------------------------------------------------------
# 应用初始化
# ---------------------------------------------------------------------------

app = FastAPI(title="Pet Brain API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
init_brain_store()
init_chat_import_store()
init_conversation_store()

# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------


def _ensure_meta_dict(brain_state: dict) -> dict:
    """确保 brain_state['meta'] 始终是 dict。"""
    meta = brain_state.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        brain_state["meta"] = meta
    return meta


def _safe_int(value: object, default: int = 0) -> int:
    """安全解析 meta 中的整数字段，容忍类型异常。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _ensure_counter_dict(meta: dict, key: str) -> dict:
    """确保 meta 中的计数字典存在且为 dict 类型。"""
    value = meta.get(key)
    if not isinstance(value, dict):
        value = {}
        meta[key] = value
    return value


def _save_chat_import_safely(**kwargs: object) -> None:
    """尽力写入聊天导入记录；DB 异常不中断主流程。"""
    try:
        save_chat_import(**kwargs)
    except Exception as exc:
        print(f"[warn] failed to persist chat import: {exc}")


_UNWANTED_TEXT_SNIPPETS = (
    "C++ 高频特征",
    "C++ 高频词组",
    "当前样本未出现",
    "低置信度",
)


def _sanitize_brain_state_text(value: object) -> object:
    """Recursively remove unwanted wording from model output text fields."""
    if isinstance(value, dict):
        return {k: _sanitize_brain_state_text(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_brain_state_text(item) for item in value]
    if isinstance(value, str):
        text = value
        for snippet in _UNWANTED_TEXT_SNIPPETS:
            text = text.replace(snippet, "")
        return " ".join(text.split())
    return value

# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """健康检查：确认服务正常运行。"""
    return HealthResponse(status="ok")


@app.post("/api/v1/hatch", response_model=BrainStateResponse)
def hatch(req: HatchRequest) -> BrainStateResponse:
    """
    孵化：根据聊天记录首次生成宠物大脑。

    流程：
    1. C++ 模块提取文本特征（高频词、标点、句长等）
    2. 调用大模型生成结构化 brain_state
    3. 对模型输出做 Schema 校验
    4. 保存大脑状态到 SQLite，返回 brain_id
    5. 将原始聊天记录写入数据库
    """
    cpp_features = extract_features(req.chat_log, mode="hatch")
    try:
        prompt_text = build_hatch_prompt(req, cpp_features)
        model_output = generate_brain_state(prompt_text)
        brain_state = validate_brain_state(model_output)
        meta = _ensure_meta_dict(brain_state)
        meta["cpp_features"] = cpp_features
    except BrainStateValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid model output schema: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Model call failed: {exc}") from exc

    brain_state = _sanitize_brain_state_text(brain_state)
    if not isinstance(brain_state, dict):
        raise HTTPException(status_code=500, detail="Invalid brain_state generated")

    meta = _ensure_meta_dict(brain_state)
    meta.setdefault("learn_count", 0)
    brain_id = save_brain_state(brain_state)

    _save_chat_import_safely(
        mode="hatch",
        brain_id=brain_id,
        chat_log=req.chat_log,
        relationship_context=req.relationship_context,
        user_preference=req.user_preference,
        goal=req.hatch_goal,
    )

    return BrainStateResponse(brain_id=brain_id, brain_state=brain_state)


@app.post("/api/v1/learn", response_model=LearnResponse)
def learn(req: LearnRequest) -> LearnResponse:
    """
    增量学习：对已有大脑持续喂养新聊天数据，更新语言模型与成长里程碑。

    流程：
    1. 加载已有 brain_state
    2. 提取新聊天记录的文本特征
    3. 合并口癖列表（去重，最多保留 12 个）
    4. 按关键词累计命中驱动里程碑解锁
    5. 保存更新，写入数据库
    """
    existing = load_brain_state(req.brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")

    cpp_features = extract_features(req.chat_log, mode="learn")
    brain_state = existing["brain_state"]
    sanitized_existing = _sanitize_brain_state_text(brain_state)
    if isinstance(sanitized_existing, dict):
        brain_state = sanitized_existing

    # 合并口癖（新旧去重，最多保留 12 个）
    catchphrases = brain_state.get("language_model", {}).get("catchphrases", [])
    new_phrases = cpp_features.get("high_freq_phrases", [])
    merged = list(dict.fromkeys(catchphrases + new_phrases))[:12]
    brain_state["language_model"]["catchphrases"] = merged

    meta = _ensure_meta_dict(brain_state)
    meta["learn_count"] = _safe_int(meta.get("learn_count"), 0) + 1

    # 累积关键词命中次数，驱动里程碑解锁（里程碑由命中次数触发，而非学习次数）
    keyword_counts = _ensure_counter_dict(meta, "keyword_counts")

    milestone_rules = {
        "M2": {
            "keywords": ["我在", "抱抱", "辛苦了", "别怕", "陪你", "安慰"],
            "threshold": 3,
        },
        "M3": {
            "keywords": ["喜欢", "偏好", "希望", "想要", "不要", "称呼"],
            "threshold": 4,
        },
        "M4": {
            "keywords": ["你在吗", "最近怎么样", "今天还好吗", "想和你聊聊", "要不要聊聊", "我来找你"],
            "threshold": 3,
        },
    }

    # A. 统计规则关键词命中次数
    for rule in milestone_rules.values():
        for kw in rule["keywords"]:
            hits = req.chat_log.count(kw)
            if hits > 0:
                keyword_counts[kw] = _safe_int(keyword_counts.get(kw), 0) + hits

    # B. C++ 高频短语也计为关键词证据
    for phrase in new_phrases:
        if isinstance(phrase, str) and phrase:
            keyword_counts[phrase] = _safe_int(keyword_counts.get(phrase), 0) + 1

    milestones = brain_state.get("growth_model", {}).get("milestones", [])
    # 兼容旧 brain：若缺少 M4 则自动补齐
    if isinstance(milestones, list) and not any(
        isinstance(item, dict) and item.get("milestone_id") == "M4" for item in milestones
    ):
        milestones.append(
            {
                "milestone_id": "M4",
                "name": "第一次主动发起话题",
                "unlock_condition": "主动发起相关关键词累计命中达到 3 次",
                "expected_behavior": "在轻度沉默场景下，主动发出简短探问",
                "status": "locked",
            }
        )

    for milestone in milestones:
        milestone_id = milestone.get("milestone_id")
        rule = milestone_rules.get(milestone_id)
        if not rule:
            continue

        total_hits = sum(_safe_int(keyword_counts.get(kw), 0) for kw in rule["keywords"])
        threshold = _safe_int(rule.get("threshold"), 1)
        if total_hits >= threshold:
            milestone["status"] = "unlocked"
        elif total_hits > 0:
            milestone["status"] = "in_progress"
        else:
            milestone["status"] = "locked"

        meta[f"{milestone_id.lower()}_keyword_hits"] = total_hits
        meta[f"remaining_keywords_for_{milestone_id.lower()}"] = max(0, threshold - total_hits)

    meta["last_cpp_features"] = cpp_features

    update_brain_state(req.brain_id, brain_state)

    _save_chat_import_safely(
        mode="learn",
        brain_id=req.brain_id,
        chat_log=req.chat_log,
        goal=req.learn_goal,
    )

    return LearnResponse(
        brain_id=req.brain_id,
        updated_fields=[
            "language_model.catchphrases",
            "growth_model.milestones",
            "meta.learn_count",
            "meta.keyword_counts",
        ],
        brain_state=brain_state,
    )


@app.get("/api/v1/brain/{brain_id}", response_model=BrainStateResponse)
def get_brain(brain_id: str) -> BrainStateResponse:
    """读取大脑：按 brain_id 获取已保存的完整大脑状态。"""
    existing = load_brain_state(brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")
    brain_state = _sanitize_brain_state_text(existing["brain_state"])
    if not isinstance(brain_state, dict):
        raise HTTPException(status_code=500, detail="Invalid brain_state in store")
    return BrainStateResponse(brain_id=brain_id, brain_state=brain_state)


@app.get("/api/v1/chat-imports", response_model=ChatImportListResponse)
def list_chat_imports(
    brain_id: str | None = Query(default=None),
    mode: str | None = Query(default=None, pattern="^(hatch|learn)$"),
    keyword: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ChatImportListResponse:
    """查询聊天导入记录：按 brain_id / 模式 / 关键词回溯历史导入数据。"""
    items, total = query_chat_imports(
        brain_id=brain_id,
        mode=mode,
        keyword=keyword,
        limit=limit,
        offset=offset,
    )
    return ChatImportListResponse(items=items, total=total, limit=limit, offset=offset)


@app.delete("/api/v1/brain/{brain_id}")
def delete_brain(brain_id: str) -> dict[str, object]:
    """删除宠物：删除 brain_state 以及其关联的导入记录和对话记录。"""
    existing = load_brain_state(brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")

    deleted_chat_imports = delete_chat_imports_by_brain_id(brain_id)
    deleted_conversation_messages = delete_conversation_messages(brain_id)
    deleted_brain = delete_brain_state(brain_id)

    return {
        "brain_id": brain_id,
        "deleted_brain": deleted_brain,
        "deleted_chat_imports": deleted_chat_imports,
        "deleted_conversation_messages": deleted_conversation_messages,
    }
