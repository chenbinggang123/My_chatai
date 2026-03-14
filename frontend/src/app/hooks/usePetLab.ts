"use client";

import { useEffect, useMemo, useState } from "react";

export type HatchResponse = {
  brain_id: string;
  brain_state: Record<string, unknown>;
};

type ChatResponse = {
  brain_id: string;
  reply: string;
};

export type ChatTurn = {
  role: "user" | "pet";
  content: string;
};

export type PetWorkspace = {
  id: string;
  name: string;
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
  result: HatchResponse | null;
  chatInput: string;
  chatTurns: ChatTurn[];
};

function createEmptyPetWorkspace(index: number): PetWorkspace {
  const randomId =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `${Date.now()}-${index}`;

  return {
    id: randomId,
    name: `宠物 ${index}`,
    chatLog: "",
    relationshipContext: "",
    userPreference: "",
    hatchGoal: "",
    learnChatLog: "",
    learnGoal: "",
    brainIdInput: "",
    loading: false,
    chatSending: false,
    error: "",
    result: null,
    chatInput: "",
    chatTurns: [],
  };
}

function resetPetWorkspace(pet: PetWorkspace, index: number): PetWorkspace {
  const emptyPet = createEmptyPetWorkspace(index);
  return {
    ...emptyPet,
    id: pet.id,
    name: pet.name,
  };
}

export function usePetLab(apiBase: string) {
  const [petWorkspaces, setPetWorkspaces] = useState<PetWorkspace[]>(() => [createEmptyPetWorkspace(1)]);
  const [activePetId, setActivePetId] = useState("");

  const activePet = useMemo(() => petWorkspaces.find((pet) => pet.id === activePetId), [petWorkspaces, activePetId]);

  useEffect(() => {
    if (!activePetId && petWorkspaces.length > 0) {
      setActivePetId(petWorkspaces[0].id);
      return;
    }
    if (activePetId && !petWorkspaces.some((pet) => pet.id === activePetId) && petWorkspaces.length > 0) {
      setActivePetId(petWorkspaces[0].id);
    }
  }, [activePetId, petWorkspaces]);

  const updatePetById = (petId: string, updater: (pet: PetWorkspace) => PetWorkspace) => {
    setPetWorkspaces((prev) => prev.map((pet) => (pet.id === petId ? updater(pet) : pet)));
  };

  const updateActivePet = (updater: (pet: PetWorkspace) => PetWorkspace) => {
    if (!activePet) return;
    updatePetById(activePet.id, updater);
  };

  const chatLog = activePet?.chatLog ?? "";
  const relationshipContext = activePet?.relationshipContext ?? "";
  const userPreference = activePet?.userPreference ?? "";
  const hatchGoal = activePet?.hatchGoal ?? "";
  const learnChatLog = activePet?.learnChatLog ?? "";
  const learnGoal = activePet?.learnGoal ?? "";
  const brainIdInput = activePet?.brainIdInput ?? "";
  const loading = activePet?.loading ?? false;
  const chatSending = activePet?.chatSending ?? false;
  const error = activePet?.error ?? "";
  const result = activePet?.result ?? null;
  const chatInput = activePet?.chatInput ?? "";
  const chatTurns = activePet?.chatTurns ?? [];

  const setChatLog = (value: string) => updateActivePet((pet) => ({ ...pet, chatLog: value }));
  const setRelationshipContext = (value: string) =>
    updateActivePet((pet) => ({ ...pet, relationshipContext: value }));
  const setUserPreference = (value: string) => updateActivePet((pet) => ({ ...pet, userPreference: value }));
  const setHatchGoal = (value: string) => updateActivePet((pet) => ({ ...pet, hatchGoal: value }));
  const setLearnChatLog = (value: string) => updateActivePet((pet) => ({ ...pet, learnChatLog: value }));
  const setLearnGoal = (value: string) => updateActivePet((pet) => ({ ...pet, learnGoal: value }));
  const setBrainIdInput = (value: string) => updateActivePet((pet) => ({ ...pet, brainIdInput: value }));
  const setChatInput = (value: string) => updateActivePet((pet) => ({ ...pet, chatInput: value }));
  const setChatTurns = (value: ChatTurn[] | ((prev: ChatTurn[]) => ChatTurn[])) =>
    updateActivePet((pet) => ({
      ...pet,
      chatTurns: typeof value === "function" ? (value as (prev: ChatTurn[]) => ChatTurn[])(pet.chatTurns) : value,
    }));

  useEffect(() => {
    try {
      const saved = localStorage.getItem("pet-brain-session");
      if (saved) {
        const data = JSON.parse(saved);
        if (Array.isArray(data.petWorkspaces) && data.petWorkspaces.length > 0) {
          const restoredPets: PetWorkspace[] = data.petWorkspaces.map((item: Partial<PetWorkspace>, idx: number) => {
            const base = createEmptyPetWorkspace(idx + 1);
            return {
              ...base,
              ...item,
              id: typeof item.id === "string" && item.id ? item.id : base.id,
              name: typeof item.name === "string" && item.name ? item.name : base.name,
              loading: false,
              chatSending: false,
              error: typeof item.error === "string" ? item.error : "",
              chatTurns: Array.isArray(item.chatTurns) ? item.chatTurns : [],
            };
          });
          setPetWorkspaces(restoredPets);
          const restoredActiveId =
            typeof data.activePetId === "string" && restoredPets.some((pet) => pet.id === data.activePetId)
              ? data.activePetId
              : restoredPets[0].id;
          setActivePetId(restoredActiveId);
          return;
        }

        const legacyPet = createEmptyPetWorkspace(1);
        legacyPet.name = "宠物 1";
        if (typeof data.chatLog === "string") legacyPet.chatLog = data.chatLog;
        if (typeof data.relationshipContext === "string") legacyPet.relationshipContext = data.relationshipContext;
        if (typeof data.userPreference === "string") legacyPet.userPreference = data.userPreference;
        if (typeof data.hatchGoal === "string") legacyPet.hatchGoal = data.hatchGoal;
        if (typeof data.learnChatLog === "string") legacyPet.learnChatLog = data.learnChatLog;
        if (typeof data.learnGoal === "string") legacyPet.learnGoal = data.learnGoal;
        if (typeof data.brainIdInput === "string") legacyPet.brainIdInput = data.brainIdInput;
        if (data.result && typeof data.result === "object") legacyPet.result = data.result as HatchResponse;
        if (Array.isArray(data.chatTurns)) legacyPet.chatTurns = data.chatTurns;
        setPetWorkspaces([legacyPet]);
        setActivePetId(legacyPet.id);
      }
    } catch (e) {
      console.error("Failed to restore session:", e);
    }
  }, []);

  useEffect(() => {
    const sessionData = { activePetId, petWorkspaces };
    localStorage.setItem("pet-brain-session", JSON.stringify(sessionData));
  }, [activePetId, petWorkspaces]);

  function handleAddPetWorkspace() {
    setPetWorkspaces((prev) => {
      const nextIndex = prev.length + 1;
      const newPet = createEmptyPetWorkspace(nextIndex);
      setActivePetId(newPet.id);
      return [...prev, newPet];
    });
  }

  function handleRenameActivePet(name: string) {
    if (!activePet) return;
    const normalized = name.trim();
    updatePetById(activePet.id, (pet) => ({
      ...pet,
      name: normalized.length > 0 ? normalized : pet.name,
    }));
  }

  const canSubmit = useMemo(() => chatLog.trim().length > 0 && !loading, [chatLog, loading]);

  async function handleHatch() {
    const currentPet = petWorkspaces.find((pet) => pet.id === activePetId);
    if (!currentPet) return;
    const petId = currentPet.id;
    updatePetById(petId, (pet) => ({ ...pet, loading: true, error: "" }));

    try {
      const res = await fetch(`${apiBase}/api/v1/hatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_log: currentPet.chatLog,
          relationship_context: currentPet.relationshipContext || undefined,
          user_preference: currentPet.userPreference || undefined,
          hatch_goal: currentPet.hatchGoal || undefined,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = (await res.json()) as HatchResponse;
      updatePetById(petId, (pet) => ({ ...pet, result: data, brainIdInput: data.brain_id }));
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      updatePetById(petId, (pet) => ({ ...pet, error: `孵化失败: ${message}` }));
    } finally {
      updatePetById(petId, (pet) => ({ ...pet, loading: false }));
    }
  }

  async function handleLearn() {
    if (!activePet) return;
    const petId = activePet.id;
    const brainId = (activePet.brainIdInput || activePet.result?.brain_id || "").trim();
    if (!brainId) {
      updatePetById(petId, (pet) => ({ ...pet, error: "请先输入 brain_id，或先完成一次孵化" }));
      return;
    }
    if (!activePet.learnChatLog.trim()) {
      updatePetById(petId, (pet) => ({ ...pet, error: "请填写用于增量学习的聊天记录" }));
      return;
    }

    updatePetById(petId, (pet) => ({ ...pet, loading: true, error: "" }));

    try {
      const res = await fetch(`${apiBase}/api/v1/learn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brain_id: brainId,
          chat_log: activePet.learnChatLog,
          learn_goal: activePet.learnGoal || undefined,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = (await res.json()) as HatchResponse;
      updatePetById(petId, (pet) => ({ ...pet, result: data, brainIdInput: data.brain_id }));
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      updatePetById(petId, (pet) => ({ ...pet, error: `增量学习失败: ${message}` }));
    } finally {
      updatePetById(petId, (pet) => ({ ...pet, loading: false }));
    }
  }

  async function handleFetchBrain() {
    if (!activePet) return;
    const petId = activePet.id;
    const brainId = (activePet.brainIdInput || activePet.result?.brain_id || "").trim();
    if (!brainId) {
      updatePetById(petId, (pet) => ({ ...pet, error: "请先输入 brain_id" }));
      return;
    }

    updatePetById(petId, (pet) => ({ ...pet, loading: true, error: "" }));

    try {
      const res = await fetch(`${apiBase}/api/v1/brain/${encodeURIComponent(brainId)}`);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const data = (await res.json()) as HatchResponse;
      updatePetById(petId, (pet) => ({ ...pet, result: data, brainIdInput: data.brain_id }));
    } catch (e) {
      const message = e instanceof Error ? e.message : "未知错误";
      updatePetById(petId, (pet) => ({ ...pet, error: `读取大脑失败: ${message}` }));
    } finally {
      updatePetById(petId, (pet) => ({ ...pet, loading: false }));
    }
  }

  function handleFileUpload(file: File | null) {
    if (!file || !activePet) return;
    const petId = activePet.id;
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? "");
      updatePetById(petId, (pet) => ({ ...pet, chatLog: content }));
    };
    reader.readAsText(file, "utf-8");
  }

  function handleLearnFileUpload(file: File | null) {
    if (!file || !activePet) return;
    const petId = activePet.id;
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? "");
      updatePetById(petId, (pet) => ({ ...pet, learnChatLog: content }));
    };
    reader.readAsText(file, "utf-8");
  }

  function handleRestartHatch() {
    if (!activePet) return;
    if (!confirm(`确定要重新孵化「${activePet.name}」吗？这只会清空当前宠物的数据。`)) {
      return;
    }

    updatePetById(activePet.id, (pet) => resetPetWorkspace(pet, petWorkspaces.findIndex((item) => item.id === pet.id) + 1));
  }

  async function handleSendChat() {
    if (!activePet) return;
    const petId = activePet.id;
    const brainId = (activePet.brainIdInput || activePet.result?.brain_id || "").trim();
    const message = activePet.chatInput.trim();
    if (!brainId) {
      updatePetById(petId, (pet) => ({ ...pet, error: "请先输入 brain_id，或先完成一次孵化" }));
      return;
    }
    if (!message) {
      return;
    }

    updatePetById(petId, (pet) => ({
      ...pet,
      chatSending: true,
      error: "",
      chatInput: "",
      chatTurns: [...pet.chatTurns, { role: "user", content: message }],
    }));

    try {
      // 把当前轮次之前的历史（不含刚刚追加的 user 消息）传给后端
      const historySnapshot = activePet.chatTurns.map((t) => ({
        role: t.role,
        content: t.content,
      }));

      const res = await fetch(`${apiBase}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brain_id: brainId,
          user_message: message,
          history: historySnapshot,
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = (await res.json()) as ChatResponse;
      updatePetById(petId, (pet) => ({
        ...pet,
        chatTurns: [...pet.chatTurns, { role: "pet", content: data.reply }],
      }));
    } catch (e) {
      const messageText = e instanceof Error ? e.message : "未知错误";
      updatePetById(petId, (pet) => ({ ...pet, error: `对话失败: ${messageText}` }));
    } finally {
      updatePetById(petId, (pet) => ({ ...pet, chatSending: false }));
    }
  }

  function handleClearChat() {
    if (!activePet) return;
    const petId = activePet.id;
    const brainId = (activePet.brainIdInput || activePet.result?.brain_id || "").trim();

    updatePetById(petId, (pet) => ({
      ...pet,
      chatInput: "",
      chatTurns: [],
    }));

    if (!brainId) {
      return;
    }

    fetch(`${apiBase}/api/v1/conversation/${encodeURIComponent(brainId)}`, {
      method: "DELETE",
    }).catch((e) => {
      const messageText = e instanceof Error ? e.message : "未知错误";
      updatePetById(petId, (pet) => ({ ...pet, error: `清空数据库对话失败: ${messageText}` }));
    });
  }

  return {
    petWorkspaces,
    activePet,
    activePetId,
    setActivePetId,
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
    result,
    chatInput,
    chatTurns,
    canSubmit,
    setChatLog,
    setRelationshipContext,
    setUserPreference,
    setHatchGoal,
    setLearnChatLog,
    setLearnGoal,
    setBrainIdInput,
    setChatInput,
    handleAddPetWorkspace,
    handleRenameActivePet,
    handleHatch,
    handleLearn,
    handleFetchBrain,
    handleFileUpload,
    handleLearnFileUpload,
    handleRestartHatch,
    handleSendChat,
    handleClearChat,
  };
}
