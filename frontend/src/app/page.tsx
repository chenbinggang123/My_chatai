"use client";

import { useMemo, useState } from "react";

type HatchResponse = {
  brain_id: string;
  brain_state: Record<string, unknown>;
};

type BrainSummary = {
  stageName: string;
  stageDescription: string;
  milestones: Array<{ id: string; name: string; status: string; behavior: string }>;
  catchphrases: string[];
  comfortLines: string[];
  tone: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function Home() {
  const [chatLog, setChatLog] = useState("");
  const [relationshipContext, setRelationshipContext] = useState("");
  const [userPreference, setUserPreference] = useState("");
  const [hatchGoal, setHatchGoal] = useState("");
  const [learnChatLog, setLearnChatLog] = useState("");
  const [learnGoal, setLearnGoal] = useState("");
  const [brainIdInput, setBrainIdInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<HatchResponse | null>(null);

  const canSubmit = useMemo(() => chatLog.trim().length > 0 && !loading, [chatLog, loading]);
  // 将后端返回结构整理为稳定、便于渲染的前端摘要。
  const summary = useMemo<BrainSummary | null>(() => {
    if (!result) return null;

    const brain = result.brain_state;
    const growth = asRecord(brain.growth_model);
    const currentStage = asRecord(growth.current_stage);
    const languageModel = asRecord(brain.language_model);

    // 里程碑字段可能不完整，使用兜底值避免渲染报错。
    const milestones = asArray(growth.milestones).map((item, idx) => {
      const row = asRecord(item);
      return {
        id: asString(row.milestone_id) || `M${idx + 1}`,
        name: asString(row.name) || "未命名里程碑",
        status: asString(row.status) || "planned",
        behavior: asString(row.expected_behavior) || "",
      };
    });

    return {
      stageName: asString(currentStage.stage_name) || "未知阶段",
      stageDescription: asString(currentStage.stage_description) || "暂无描述",
      milestones,
      catchphrases: asStringArray(languageModel.catchphrases),
      comfortLines: asStringArray(languageModel.comfort_lines),
      tone: asStringArray(languageModel.tone),
    };
  }, [result]);

  async function handleHatch() {
    setLoading(true);
    setError("");

    try {
      // 根据聊天记录创建新的 brain。
      const res = await fetch(`${API_BASE}/api/v1/hatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_log: chatLog,
          relationship_context: relationshipContext || undefined,
          user_preference: userPreference || undefined,
          hatch_goal: hatchGoal || undefined,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = (await res.json()) as HatchResponse;
      setResult(data);
      setBrainIdInput(data.brain_id);
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      setError(`孵化失败: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleLearn() {
    const brainId = (brainIdInput || result?.brain_id || "").trim();
    if (!brainId) {
      setError("请先输入 brain_id，或先完成一次孵化");
      return;
    }
    if (!learnChatLog.trim()) {
      setError("请填写用于增量学习的聊天记录");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // 用新增聊天记录对现有 brain 做增量学习。
      const res = await fetch(`${API_BASE}/api/v1/learn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brain_id: brainId,
          chat_log: learnChatLog,
          learn_goal: learnGoal || undefined,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = (await res.json()) as HatchResponse;
      setResult(data);
      setBrainIdInput(data.brain_id);
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      setError(`增量学习失败: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleFetchBrain() {
    const brainId = (brainIdInput || result?.brain_id || "").trim();
    if (!brainId) {
      setError("请先输入 brain_id");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // 按 brain_id 拉取已保存状态，用于恢复或刷新展示。
      const res = await fetch(`${API_BASE}/api/v1/brain/${encodeURIComponent(brainId)}`);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const data = (await res.json()) as HatchResponse;
      setResult(data);
      setBrainIdInput(data.brain_id);
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      setError(`读取大脑失败: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  function handleFileUpload(file: File | null) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? "");
      setChatLog(content);
    };
    reader.readAsText(file, "utf-8");
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,#f3f1ff,transparent_40%),radial-gradient(circle_at_80%_10%,#ffe6d8,transparent_35%),#fbfaf7] px-4 py-8 text-slate-900 sm:px-8">
      <main className="mx-auto grid w-full max-w-6xl gap-6 md:grid-cols-2">
        <section className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-xl backdrop-blur">
          <p className="text-sm tracking-[0.2em] text-slate-500">PET BRAIN HATCH LAB</p>
          <h1 className="mt-2 text-3xl font-semibold leading-tight sm:text-4xl">桌面宠物孵化台</h1>
          <p className="mt-3 text-sm text-slate-600">
            先在网页完成宠物大脑孵化，后续迁移到桌面端。聊天记录就是宠物的喂养数据。
          </p>

          <div className="mt-6 space-y-4">
            <label className="block text-sm font-medium">聊天记录（必填）</label>
            <textarea
              value={chatLog}
              onChange={(e) => setChatLog(e.target.value)}
              placeholder="粘贴聊天记录，或使用下方 txt 上传"
              className="h-56 w-full rounded-2xl border border-slate-300 bg-slate-50 p-4 text-sm outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
            />

            <div className="flex items-center gap-3">
              <input
                type="file"
                accept=".txt,text/plain"
                onChange={(e) => handleFileUpload(e.target.files?.[0] ?? null)}
                className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
              />
            </div>

            <input
              value={relationshipContext}
              onChange={(e) => setRelationshipContext(e.target.value)}
              placeholder="关系背景（可选）：例如 朋友/恋人/家人"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
            />
            <input
              value={userPreference}
              onChange={(e) => setUserPreference(e.target.value)}
              placeholder="偏好（可选）：例如 更可爱、更主动"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
            />
            <input
              value={hatchGoal}
              onChange={(e) => setHatchGoal(e.target.value)}
              placeholder="本次孵化目标（可选）：例如 先学会安慰"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
            />

            <button
              onClick={handleHatch}
              disabled={!canSubmit}
              className="w-full rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? "孵化中..." : "开始孵化宠物大脑"}
            </button>

            <div className="rounded-2xl border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-800">继续喂养（增量学习）</p>
              <p className="mt-1 text-xs text-slate-500">同一个 brain_id 可反复学习，里程碑会推进。</p>

              <input
                value={brainIdInput}
                onChange={(e) => setBrainIdInput(e.target.value)}
                placeholder="brain_id（可自动带出）"
                className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
              />

              <textarea
                value={learnChatLog}
                onChange={(e) => setLearnChatLog(e.target.value)}
                placeholder="粘贴新的聊天记录作为增量喂养数据"
                className="mt-3 h-32 w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-sm outline-none focus:border-sky-400"
              />

              <input
                value={learnGoal}
                onChange={(e) => setLearnGoal(e.target.value)}
                placeholder="学习目标（可选）：例如 强化主动安抚"
                className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
              />

              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <button
                  onClick={handleLearn}
                  disabled={loading}
                  className="w-full rounded-xl bg-slate-800 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
                >
                  {loading ? "处理中..." : "提交增量学习"}
                </button>

                <button
                  onClick={handleFetchBrain}
                  disabled={loading}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed"
                >
                  按 brain_id 读取状态
                </button>
              </div>
            </div>

            {error && <p className="text-sm text-rose-600">{error}</p>}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-xl backdrop-blur">
          <h2 className="text-xl font-semibold">学习结果</h2>
          <p className="mt-2 text-sm text-slate-600">
            这里展示孵化后的 brain_state。后续你可以基于这个 brain_id 做增量学习和里程碑解锁。
          </p>

          {result && summary ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs text-slate-500">brain_id</p>
                <p className="mt-1 break-all text-sm font-medium text-slate-800">{result.brain_id}</p>
              </div>

              <div className="rounded-2xl border border-slate-200 p-4">
                <p className="text-xs text-slate-500">成长阶段</p>
                <h3 className="mt-1 text-lg font-semibold text-slate-900">{summary.stageName}</h3>
                <p className="mt-1 text-sm text-slate-600">{summary.stageDescription}</p>
              </div>

              <div className="rounded-2xl border border-slate-200 p-4">
                <p className="text-xs text-slate-500">语言风格</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {summary.tone.length > 0 ? (
                    summary.tone.map((tone) => (
                      <span key={tone} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
                        {tone}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-slate-500">暂无</span>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 p-4">
                <p className="text-xs text-slate-500">口癖与安抚句</p>
                <p className="mt-2 text-sm font-medium text-slate-700">口癖</p>
                <ul className="mt-1 space-y-1 text-sm text-slate-600">
                  {summary.catchphrases.length > 0 ? (
                    summary.catchphrases.map((line) => <li key={line}>- {line}</li>)
                  ) : (
                    <li>- 暂无</li>
                  )}
                </ul>
                <p className="mt-3 text-sm font-medium text-slate-700">安抚句</p>
                <ul className="mt-1 space-y-1 text-sm text-slate-600">
                  {summary.comfortLines.length > 0 ? (
                    summary.comfortLines.map((line) => <li key={line}>- {line}</li>)
                  ) : (
                    <li>- 暂无</li>
                  )}
                </ul>
              </div>

              <div className="rounded-2xl border border-slate-200 p-4">
                <p className="text-xs text-slate-500">里程碑</p>
                <div className="mt-2 space-y-2">
                  {summary.milestones.length > 0 ? (
                    summary.milestones.map((item) => (
                      <div key={item.id} className="rounded-xl bg-slate-50 p-3">
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-sm font-semibold text-slate-800">{item.name}</p>
                          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-700">
                            {item.status}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-slate-600">{item.behavior || "暂无行为描述"}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">暂无里程碑</p>
                  )}
                </div>
              </div>

              <details className="rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">
                <summary className="cursor-pointer select-none text-slate-200">查看原始 JSON</summary>
                <pre className="mt-3 max-h-[420px] overflow-auto whitespace-pre-wrap break-all">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div className="mt-4 rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">
              <p className="text-slate-300">
                还没有学习结果。提交聊天记录后，将在这里看到宠物大脑、成长阶段和里程碑。
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

// 对 API 返回的未知 JSON 字段做运行时类型守卫。
function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((v): v is string => typeof v === "string");
}
