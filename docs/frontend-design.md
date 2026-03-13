# 前端设计说明（Web 孵化台）

本文档说明当前前端页面的设计与实现，重点解释 `frontend/src/app/page.tsx` 的职责和功能。

## 1. 页面定位

当前前端是一个单页孵化台，目标是完成以下闭环：

1. 导入聊天记录（粘贴 + txt 上传）
2. 调用后端进行首次孵化（hatch）
3. 对已有 brain 进行增量学习（learn）
4. 按 brain_id 拉取并恢复历史状态
5. 可视化展示成长阶段、语言风格、里程碑等结果

## 2. 主要文件与职责

- `frontend/src/app/page.tsx`
  - 主页核心交互与业务逻辑
  - 表单状态管理、接口请求、结果渲染
  - 后端返回数据的运行时兜底解析

- `frontend/src/app/layout.tsx`
  - 根布局与全局字体注入
  - 页面元数据（title、description）

- `frontend/src/app/globals.css`
  - 全局样式变量与 body 基础样式

## 3. page.tsx 实现了什么功能

### 3.1 状态管理

页面基于 React Hook 管理输入与请求状态：

- 孵化输入：`chatLog`、`relationshipContext`、`userPreference`、`hatchGoal`
- 增量学习输入：`learnChatLog`、`learnGoal`、`brainIdInput`
- 运行态：`loading`、`error`
- 返回数据：`result`（包含 `brain_id` 与 `brain_state`）

同时通过 `useMemo` 计算：

- `canSubmit`：控制“开始孵化”按钮启用条件
- `summary`：把后端原始 JSON 整理成稳定的渲染模型（阶段、里程碑、语言风格等）

### 3.2 三个核心交互动作

1. `handleHatch`
  - 调用 `POST /api/v1/hatch`
  - 用聊天记录创建新的 brain
  - 成功后更新 `result`，并自动回填 `brain_id`

2. `handleLearn`
  - 调用 `POST /api/v1/learn`
  - 对已有 brain 进行增量学习
  - 会先校验 `brain_id` 与新增聊天记录是否为空

3. `handleFetchBrain`
  - 调用 `GET /api/v1/brain/{brain_id}`
  - 拉取已保存状态，用于恢复和刷新展示

接口基地址由 `NEXT_PUBLIC_API_BASE` 控制，默认值是 `http://localhost:8000`。

### 3.3 数据导入能力

- 支持手动粘贴聊天记录到 textarea
- 支持上传 `.txt` 文件
- `handleFileUpload` 使用 `FileReader` 读取文本并写入 `chatLog`

### 3.4 结果展示能力

当 `result` 存在时，右侧面板展示：

- `brain_id`
- 当前成长阶段名称与描述
- 语言风格标签（tone）
- 口癖（catchphrases）与安抚句（comfort_lines）
- 里程碑列表（名称、状态、预期行为）
- 原始 JSON（`<details>` 折叠查看）

当无结果时，展示空状态提示。

### 3.5 运行时安全兜底

页面底部定义了辅助函数：

- `asRecord`
- `asArray`
- `asString`
- `asStringArray`

作用是把后端返回的未知结构安全转为可渲染数据，避免字段缺失或类型不一致导致页面崩溃。

## 4. 视觉与布局设计

- 整体：浅色背景 + 渐变光斑，强调“孵化实验台”氛围
- 布局：`md` 以上双栏网格（左输入、右结果），小屏自动单栏
- 组件：圆角卡片、轻阴影、清晰层级，提升可读性
- 交互反馈：
  - 请求中按钮显示“孵化中/处理中”
  - 错误信息以醒目文字展示
  - 禁用态按钮防止重复提交

## 5. 当前前端边界

已实现：

- 孵化、增量学习、按 ID 恢复三类核心请求
- 关键结果可视化
- 文本导入与错误反馈

未实现（可作为下一步）：

- 多页面路由拆分（如 `/hatch/[brainId]`、`/growth/[brainId]`）
- 结果图表化（里程碑进度条、成长时间线）
- 更细粒度的加载骨架与请求状态管理

## 6. 一句话总结

`page.tsx` 本质是“宠物大脑孵化控制台”：负责收集喂养数据、驱动后端学习接口、并把返回的 brain_state 转成可读可追踪的成长视图。