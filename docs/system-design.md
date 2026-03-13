# 系统设计（V2：桌面宠物孵化）

## 1. 产品目标

短期目标（当前版本）：

- 提供网页孵化台
- 支持聊天记录导入（粘贴、txt 上传）
- 让 AI 从聊天记录学习并生成宠物初始大脑

中长期目标（未来版本）：

- 从网页迁移到桌面宠物形态
- 支持持续学习、成长阶段与里程碑解锁
- 形成“像孩子一样长大”的长期陪伴体验

## 2. 技术选型

- 前端：Next.js 15 + React + TypeScript + Tailwind CSS
- AI 后端：Python + FastAPI
- 性能模块：C++（长文本切片、语言统计）
- 模型调用：OpenAI 兼容 API（由 Python 统一调用）

## 3. 核心概念

- 孵化（Hatch）：首次导入聊天记录，生成宠物大脑初始状态
- 学习（Learn）：后续导入新数据，增量更新大脑
- 成长阶段（Stage）：宠物能力发展层级，如孵化期、学语期、陪伴期
- 里程碑（Milestone）：可触发事件，如第一次开口说话

## 4. 分层架构

### 前端层

职责：

- 上传/粘贴聊天记录
- 配置孵化偏好（更可爱、更主动等）
- 展示学习结果（语言层、情绪层、关系层、成长层）
- 展示里程碑进度

页面建议：

- `/` 孵化入口页
- `/hatch/[brainId]` 孵化结果页
- `/growth/[brainId]` 成长与里程碑页

### AI 应用层（Python）

职责：

- 输入清洗、敏感信息处理
- 调用 C++ 统计模块
- 组装提示词并调用模型
- 校验 JSON 输出并存储大脑状态
- 执行“增量学习”合并策略

核心模块：

- `api/hatch.py`
- `api/learn.py`
- `services/prompt_builder.py`
- `services/model_client.py`
- `services/brain_state_merger.py`
- `services/schema_validator.py`
- `services/cpp_bridge.py`

### C++ 模块层

职责：

- 长文本切片
- 句长分布统计
- 标点习惯统计
- 高频短语提取
- 重复表达模式提取

输出：结构化 JSON，供 Python 回填到学习上下文。

## 5. 核心流程

1. 用户上传聊天记录并提交孵化请求。
2. Python 后端清洗数据并调用 C++ 特征提取。
3. Python 组装 prompt，调用大模型生成宠物大脑。
4. 后端校验并存储 brain_profile、growth_model、runtime_assets。
5. 前端展示“当前成长阶段 + 可解锁里程碑”。
6. 用户追加新聊天记录触发 learn，系统增量更新大脑。

## 6. 数据模型（概念）

- `PetBrain`
  - id
  - pet_name
  - brain_profile
  - language_model
  - emotion_model
  - relationship_model
  - growth_model
  - runtime_assets
  - created_at
  - updated_at

- `LearningRecord`
  - id
  - brain_id
  - raw_chat_log
  - cpp_features
  - learned_delta
  - created_at

## 7. 当前阶段交付边界

当前只做：

- 网页设计
- 聊天记录导入
- AI 学习生成初始大脑

暂不做：

- 桌面端常驻与系统托盘
- 动画宠物形象与动作系统
- 长期记忆数据库优化

## 8. 可面试亮点

- 从“单次分析”升级为“可成长 AI 大脑”架构
- Python + C++ 协作，兼顾迭代效率和性能
- 里程碑机制设计，具备明确产品演进路线
