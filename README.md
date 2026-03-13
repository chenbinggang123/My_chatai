# My_chatai

一个“可成长桌面宠物”项目，当前先做 Web 孵化台。

## 产品方向

- 最终目标：桌面宠物（Desktop Pet）
- 当前目标：网页设计 + 聊天记录导入 + AI 学习
- 核心理念：聊天记录是宠物的大脑喂养数据，不是一次性分析样本

## 关键能力

- 孵化：首次导入聊天记录，生成宠物初始大脑
- 学习：继续导入聊天记录，增量更新大脑
- 成长：按里程碑演进，例如“第一次开口说话”

## 文档入口

- 主提示词：[prompt.md](prompt.md)
- 系统设计：[docs/system-design.md](docs/system-design.md)
- API 契约：[docs/api-contract.md](docs/api-contract.md)
- 路线图：[docs/mvp-roadmap.md](docs/mvp-roadmap.md)

## 技术栈

- 前端：Next.js + TypeScript + Tailwind CSS
- 后端：Python FastAPI
- 性能模块：C++

## 当前开发重点

1. 实现 Web 孵化页面
2. 实现聊天记录导入（文本/文件）
3. 打通 `/api/v1/hatch` AI 学习接口

## 本地运行

### 1) 启动后端（FastAPI）

```bash
--
```

### 2) 启动前端（Next.js）

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

### 3) 可选：构建 C++ 特征模块

```bash
cd cpp
cmake -S . -B build
cmake --build build
```
