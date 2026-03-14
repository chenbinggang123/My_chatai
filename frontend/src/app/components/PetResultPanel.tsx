import { type BrainSummary } from "../lib/brainSummary";
import { type ChatTurn, type HatchResponse } from "../hooks/usePetLab";

type PetResultPanelProps = {
  result: HatchResponse | null;
  summary: BrainSummary | null;
  chatTurns: ChatTurn[];
  chatInput: string;
  chatSending: boolean;
  onSetChatInput: (value: string) => void;
  onClearChat: () => void;
  onSendChat: () => void;
};

export function PetResultPanel({
  result,
  summary,
  chatTurns,
  chatInput,
  chatSending,
  onSetChatInput,
  onClearChat,
  onSendChat,
}: PetResultPanelProps) {
  return (
    <section className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-xl backdrop-blur">
      <h2 className="text-xl font-semibold">学习结果</h2>
      <p className="mt-2 text-sm text-slate-600">这里展示孵化后的 brain_state。后续你可以基于这个 brain_id 做增量学习和里程碑解锁。</p>

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
                      <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-700">{item.status}</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">{item.behavior || "暂无行为描述"}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">暂无里程碑</p>
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 p-4">
            <p className="text-xs text-slate-500">宠物对话</p>
            <p className="mt-1 text-sm text-slate-600">基于关键词与口癖生成回复风格，先做轻量版互动。</p>

            <div className="mt-3 max-h-56 space-y-2 overflow-auto rounded-xl bg-slate-50 p-3">
              {chatTurns.length > 0 ? (
                chatTurns.map((turn, idx) => (
                  <div
                    key={`${turn.role}-${idx}`}
                    className={`rounded-lg px-3 py-2 text-sm ${
                      turn.role === "user" ? "bg-sky-100 text-sky-900" : "bg-white text-slate-700"
                    }`}
                  >
                    <p className="text-xs opacity-70">{turn.role === "user" ? "你" : "宠物"}</p>
                    <p className="mt-1 whitespace-pre-wrap">{turn.content}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">还没有对话，发送第一句试试。</p>
              )}
            </div>

            <div className="mt-3 flex gap-2">
              <input
                value={chatInput}
                onChange={(e) => onSetChatInput(e.target.value)}
                placeholder="输入一句话，让宠物回应你"
                className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
              />
              <button
                onClick={onClearChat}
                disabled={chatSending || (chatTurns.length === 0 && chatInput.trim().length === 0)}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
              >
                清空对话
              </button>
              <button
                onClick={onSendChat}
                disabled={chatSending}
                className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {chatSending ? "发送中" : "发送"}
              </button>
            </div>
          </div>

          <details className="rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">
            <summary className="cursor-pointer select-none text-slate-200">查看原始 JSON</summary>
            <pre className="mt-3 max-h-[420px] overflow-auto whitespace-pre-wrap break-all">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      ) : (
        <div className="mt-4 rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">
          <p className="text-slate-300">还没有学习结果。提交聊天记录后，将在这里看到宠物大脑、成长阶段和里程碑。</p>
        </div>
      )}
    </section>
  );
}
