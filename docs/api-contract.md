# API 契约（V2：孵化与学习）

## 1. 孵化接口

- Method: `POST`
- Path: `/api/v1/hatch`
- Content-Type: `application/json`

请求体：

```json
{
  "chat_log": "string, required",
  "relationship_context": "string, optional",
  "user_preference": "string, optional",
  "hatch_goal": "string, optional"
}
```

成功响应：

```json
{
  "brain_id": "string",
  "brain_state": {
    "brain_profile": {},
    "language_model": {},
    "emotion_model": {},
    "relationship_model": {},
    "growth_model": {},
    "runtime_assets": {}
  }
}
```

失败响应：

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "chat_log is required",
    "details": {}
  }
}
```

## 2. 增量学习接口

- Method: `POST`
- Path: `/api/v1/learn`

请求体：

```json
{
  "brain_id": "string, required",
  "chat_log": "string, required",
  "learn_goal": "string, optional"
}
```

响应：

```json
{
  "brain_id": "string",
  "updated_fields": [
    "language_model.catchphrases",
    "growth_model.milestones"
  ],
  "brain_state": {
    "brain_profile": {},
    "language_model": {},
    "emotion_model": {},
    "relationship_model": {},
    "growth_model": {},
    "runtime_assets": {}
  }
}
```

## 3. 读取大脑状态

- Method: `GET`
- Path: `/api/v1/brain/{brain_id}`

响应：

```json
{
  "brain_id": "string",
  "brain_state": {
    "brain_profile": {},
    "language_model": {},
    "emotion_model": {},
    "relationship_model": {},
    "growth_model": {},
    "runtime_assets": {}
  }
}
```

## 4. 里程碑事件上报（预留）

- Method: `POST`
- Path: `/api/v1/milestone/trigger`

请求体：

```json
{
  "brain_id": "string",
  "milestone_id": "string",
  "event_payload": {}
}
```

## 5. C++ 特征接口（Python 内部调用）

建议先使用 JSON stdin/stdout，后续可切 pybind11。

输入：

```json
{
  "chat_log": "string",
  "mode": "hatch | learn"
}
```

输出：

```json
{
  "sentence_length_distribution": {
    "short": 0.3,
    "medium": 0.5,
    "long": 0.2
  },
  "punctuation_habits": ["...", "~~"],
  "high_freq_phrases": ["好啦", "我在"],
  "repeated_patterns": ["先安抚再建议"]
}
```

## 6. 状态码建议

- `200` 成功
- `400` 参数错误
- `404` brain_id 不存在
- `413` 输入过大
- `422` 模型返回结构不合法
- `429` 频率限制
- `500` 内部错误
- `504` 上游模型超时
