import { type HatchResponse } from "../hooks/usePetLab";

export type BrainSummary = {
  stageName: string;
  stageDescription: string;
  milestones: Array<{ id: string; name: string; status: string; behavior: string }>;
  catchphrases: string[];
  comfortLines: string[];
  tone: string[];
};

export function buildBrainSummary(result: HatchResponse | null): BrainSummary | null {
  if (!result) return null;

  const brain = result.brain_state;
  const growth = asRecord(brain.growth_model);
  const currentStage = asRecord(growth.current_stage);
  const languageModel = asRecord(brain.language_model);

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
}

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
