type PetControlPanelProps = {
  chatLog: string;
  relationshipContext: string;
  userPreference: string;
  hatchGoal: string;
  learnChatLog: string;
  learnGoal: string;
  brainIdInput: string;
  loading: boolean;
  chatSending: boolean;
  error: string;
  canSubmit: boolean;
  onSetChatLog: (value: string) => void;
  onSetRelationshipContext: (value: string) => void;
  onSetUserPreference: (value: string) => void;
  onSetHatchGoal: (value: string) => void;
  onSetLearnChatLog: (value: string) => void;
  onSetLearnGoal: (value: string) => void;
  onSetBrainIdInput: (value: string) => void;
  onFileUpload: (file: File | null) => void;
  onLearnFileUpload: (file: File | null) => void;
  onHatch: () => void;
  onRestartHatch: () => void;
  onLearn: () => void;
  onFetchBrain: () => void;
};

export function PetControlPanel({
  chatLog,
  relationshipContext,
  userPreference,
  hatchGoal,
  learnChatLog,
  learnGoal,
  brainIdInput,
  loading,
  chatSending,
  error,
  canSubmit,
  onSetChatLog,
  onSetRelationshipContext,
  onSetUserPreference,
  onSetHatchGoal,
  onSetLearnChatLog,
  onSetLearnGoal,
  onSetBrainIdInput,
  onFileUpload,
  onLearnFileUpload,
  onHatch,
  onRestartHatch,
  onLearn,
  onFetchBrain,
}: PetControlPanelProps) {
  return (
    <section className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-xl backdrop-blur">
      <p className="text-sm tracking-[0.2em] text-slate-500">PET BRAIN HATCH LAB</p>
      <h1 className="mt-2 text-3xl font-semibold leading-tight sm:text-4xl">桌面宠物孵化台</h1>
      <p className="mt-3 text-sm text-slate-600">先在网页完成宠物大脑孵化，后续迁移到桌面端。聊天记录就是宠物的喂养数据。</p>

      <div className="mt-6 space-y-4">
        <label className="block text-sm font-medium">聊天记录（必填）</label>
        <textarea
          value={chatLog}
          onChange={(e) => onSetChatLog(e.target.value)}
          placeholder="粘贴聊天记录，或使用下方 txt 上传"
          className="h-56 w-full rounded-2xl border border-slate-300 bg-slate-50 p-4 text-sm outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
        />

        <div className="flex items-center gap-3">
          <input
            type="file"
            accept=".txt,text/plain"
            onChange={(e) => onFileUpload(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
          />
        </div>

        <input
          value={relationshipContext}
          onChange={(e) => onSetRelationshipContext(e.target.value)}
          placeholder="关系背景（可选）：例如 朋友/恋人/家人"
          className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
        />
        <input
          value={userPreference}
          onChange={(e) => onSetUserPreference(e.target.value)}
          placeholder="偏好（可选）：例如 更可爱、更主动"
          className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
        />
        <input
          value={hatchGoal}
          onChange={(e) => onSetHatchGoal(e.target.value)}
          placeholder="本次孵化目标（可选）：例如 先学会安慰"
          className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
        />

        <button
          onClick={onHatch}
          disabled={!canSubmit}
          className="w-full rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? "孵化中..." : "开始孵化宠物大脑"}
        </button>

        <button
          onClick={onRestartHatch}
          disabled={loading || chatSending}
          className="w-full rounded-2xl border border-rose-300 bg-rose-50 px-5 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
        >
          重新孵化当前宠物
        </button>

        <div className="rounded-2xl border border-slate-200 p-4">
          <p className="text-sm font-semibold text-slate-800">继续喂养（增量学习）</p>
          <p className="mt-1 text-xs text-slate-500">同一个 brain_id 可反复学习，里程碑会推进。</p>

          <input
            value={brainIdInput}
            onChange={(e) => onSetBrainIdInput(e.target.value)}
            placeholder="brain_id（可自动带出）"
            className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
          />

          <textarea
            value={learnChatLog}
            onChange={(e) => onSetLearnChatLog(e.target.value)}
            placeholder="粘贴新的聊天记录作为增量喂养数据"
            className="mt-3 h-32 w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-sm outline-none focus:border-sky-400"
          />

          <div className="mt-3 flex items-center gap-3">
            <input
              type="file"
              accept=".txt,text/plain"
              onChange={(e) => onLearnFileUpload(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
            />
          </div>

          <input
            value={learnGoal}
            onChange={(e) => onSetLearnGoal(e.target.value)}
            placeholder="学习目标（可选）：例如 强化主动安抚"
            className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
          />

          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            <button
              onClick={onLearn}
              disabled={loading}
              className="w-full rounded-xl bg-slate-800 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? "处理中..." : "提交增量学习"}
            </button>

            <button
              onClick={onFetchBrain}
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
  );
}
