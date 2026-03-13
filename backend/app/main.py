# =============================================================================
# 宠物大脑孵化与学习后端 API 主入口
# =============================================================================
# 路由设计：
# - POST /api/v1/hatch          孵化：首次导入聊天记录，生成宠物初始大脑
# - POST /api/v1/learn          学习：对已有大脑增量学习，更新语言与里程碑
# - GET  /api/v1/brain/{id}     读取：按 brain_id 获取当前完整大脑状态
# - GET  /api/v1/health         健康检查
# =============================================================================

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 数据模型（Pydantic 类）
from app.schemas import BrainStateResponse, HatchRequest, HealthResponse, LearnRequest, LearnResponse
# 业务逻辑服务
from app.services.brain_builder import build_mock_brain_state  # Mock 生成器
from app.services.cpp_bridge import extract_features           # C++ 文本特征提取
from app.services.model_client import generate_brain_state     # 真实 LLM 调用
from app.services.prompt_builder import build_hatch_prompt     # 拼接 Prompt
from app.services.schema_validator import BrainStateValidationError, validate_brain_state  # JSON 校验
from app.services.store import load_brain_state, save_brain_state, update_brain_state  # 数据持久化

# 初始化 FastAPI 应用
app = FastAPI(title="Pet Brain API", version="0.1.0")

# 配置 CORS 中间件：允许前端跨域请求（开发环境允许所有来源，生产环境应该缩小范围）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """健康检查端点：用于验证后端服务是否正常运行"""
    return HealthResponse(status="ok")


@app.post("/api/v1/hatch", response_model=BrainStateResponse)
def hatch(req: HatchRequest) -> BrainStateResponse:
    """
    孵化端点：根据聊天记录首次生成宠物大脑
    
    流程：
    1. 调用 C++ 模块提取文本特征（高频词、标点、句长等）
    2. 根据 USE_MOCK_MODEL 环境变量选择生成模式：
       - True:  使用 Mock 生成器（快速，用于开发）
       - False: 调用真实 LLM（需要 OpenAI API Key）
    3. 对 LLM 输出进行 Schema 校验
    4. 如果 LLM 失败且 FALLBACK_TO_MOCK_ON_ERROR=true，自动回退到 Mock
    5. 保存大脑状态到本地 JSON，返回 brain_id
    """
    # 1. C++ 模块提取文本特征（如高频短语、句子长度等）
    cpp_features = extract_features(req.chat_log, mode="hatch")
    
    # 2. 从环境变量读取模式控制开关
    use_mock = os.getenv("USE_MOCK_MODEL", "true").lower() == "true"
    fallback_to_mock = os.getenv("FALLBACK_TO_MOCK_ON_ERROR", "true").lower() == "true"

    # 3. 选择生成模式
    if use_mock:
        # Mock 模式：快速生成，不需要真实 LLM
        brain_state = build_mock_brain_state(
            chat_log=req.chat_log,
            user_preference=req.user_preference,
            cpp_features=cpp_features,
        )
    else:
        # LLM 模式：调用真实大模型生成，带错误处理和回退
        try:
            # 3a. 拼接完整的 Prompt（融合输入 + C++ 特征）
            prompt_text = build_hatch_prompt(req, cpp_features)
            # 3b. 调用 LLM（OpenAI 兼容接口）
            model_output = generate_brain_state(prompt_text)
            # 3c. 校验返回的 JSON 是否符合 brain_state schema
            brain_state = validate_brain_state(model_output)
            # 3d. 标记为 LLM 模式，记录 C++ 特征
            brain_state.setdefault("meta", {})
            brain_state["meta"]["model_mode"] = "llm"
            brain_state["meta"]["cpp_features"] = cpp_features
        except BrainStateValidationError as exc:
            # Schema 校验失败，返回 422 (Unprocessable Entity)
            raise HTTPException(status_code=422, detail=f"Invalid model output schema: {exc}") from exc
        except Exception as exc:
            # LLM 调用其他错误（网络、超时等）
            if not fallback_to_mock:
                # 不回退，直接返回 500
                raise HTTPException(status_code=500, detail=f"Model call failed: {exc}") from exc
            # 自动回退到 Mock
            brain_state = build_mock_brain_state(
                chat_log=req.chat_log,
                user_preference=req.user_preference,
                cpp_features=cpp_features,
            )
            brain_state.setdefault("meta", {})
            brain_state["meta"]["model_mode"] = "mock_fallback"  # 标记为回退模式
            brain_state["meta"]["model_error"] = str(exc)  # 记录原始错误

    # 4. 保存到本地文件系统（backend/data/<brain_id>.json）
    brain_id = save_brain_state(brain_state)
    # 5. 返回生成的大脑 ID 和完整状态
    return BrainStateResponse(brain_id=brain_id, brain_state=brain_state)


@app.post("/api/v1/learn", response_model=LearnResponse)
def learn(req: LearnRequest) -> LearnResponse:
    """
    增量学习端点：对已有大脑持续喂养新聊天数据，更新语言模型与成长里程碑
    
    流程：
    1. 加载已有的 brain_state（按 brain_id）
    2. 提取新聊天记录的文本特征
    3. 合并口癖列表（新旧数据去重）
    4. 推进里程碑状态
    5. 保存更新
    """
    # 1. 从本地存储加载该大脑
    existing = load_brain_state(req.brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")

    # 2. 提取新记录的特征
    cpp_features = extract_features(req.chat_log, mode="learn")
    brain_state = existing["brain_state"]

    # 3. 增量更新口癖：合并旧口癖和新抽取的高频短语，去重，保留最多 12 个
    catchphrases = brain_state.get("language_model", {}).get("catchphrases", [])
    new_phrases = cpp_features.get("high_freq_phrases", [])
    merged = list(dict.fromkeys(catchphrases + new_phrases))[:12]  # 去重并切割
    brain_state["language_model"]["catchphrases"] = merged

    # 4. 推进里程碑：如果有多个里程碑，将第二个设为"进行中"状态
    milestones = brain_state.get("growth_model", {}).get("milestones", [])
    if len(milestones) > 1:
        milestones[1]["status"] = "in_progress"

    # 5. 记录本次学习元数据
    brain_state.setdefault("meta", {})["last_learn_mode"] = "mock"  # 当前为 Mock 模式，未来升级为真实 LLM
    brain_state["meta"]["last_cpp_features"] = cpp_features

    # 6. 保存到本地
    update_brain_state(req.brain_id, brain_state)

    # 7. 返回变更摘要和完整新状态
    return LearnResponse(
        brain_id=req.brain_id,
        updated_fields=["language_model.catchphrases", "growth_model.milestones"],
        brain_state=brain_state,
    )


@app.get("/api/v1/brain/{brain_id}", response_model=BrainStateResponse)
def get_brain(brain_id: str) -> BrainStateResponse:
    """
    读取大脑端点：按 brain_id 获取已保存的完整大脑状态
    
    用途：前端可按 ID 恢复之前培养的宠物大脑，或查看学习后的变化
    """
    # 从本地存储加载指定 brain_id 的数据
    existing = load_brain_state(brain_id)
    if not existing:
        raise HTTPException(status_code=404, detail="brain_id not found")
    # 返回完整的大脑状态
    return BrainStateResponse(brain_id=brain_id, brain_state=existing["brain_state"])
