"use client";

import { useMemo } from "react";

import { PetControlPanel } from "./components/PetControlPanel";
import { PetResultPanel } from "./components/PetResultPanel";
import { PetWorkspaceHeader } from "./components/PetWorkspaceHeader";
import { usePetLab } from "./hooks/usePetLab";
import { buildBrainSummary } from "./lib/brainSummary";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function Home() {
  const {
    petWorkspaces,
    activePet,
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
  } = usePetLab(API_BASE);
  const summary = useMemo(() => buildBrainSummary(result), [result]);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,#f3f1ff,transparent_40%),radial-gradient(circle_at_80%_10%,#ffe6d8,transparent_35%),#fbfaf7] px-4 py-8 text-slate-900 sm:px-8">
      <PetWorkspaceHeader
        petWorkspaces={petWorkspaces}
        activePetId={activePet?.id ?? ""}
        activePetName={activePet?.name ?? ""}
        onAddPet={handleAddPetWorkspace}
        onSelectPet={setActivePetId}
        onRenameActivePet={handleRenameActivePet}
      />

      <main className="mx-auto grid w-full max-w-6xl gap-6 md:grid-cols-2">
        <PetControlPanel
          chatLog={chatLog}
          relationshipContext={relationshipContext}
          userPreference={userPreference}
          hatchGoal={hatchGoal}
          learnChatLog={learnChatLog}
          learnGoal={learnGoal}
          brainIdInput={brainIdInput}
          loading={loading}
          chatSending={chatSending}
          error={error}
          canSubmit={canSubmit}
          onSetChatLog={setChatLog}
          onSetRelationshipContext={setRelationshipContext}
          onSetUserPreference={setUserPreference}
          onSetHatchGoal={setHatchGoal}
          onSetLearnChatLog={setLearnChatLog}
          onSetLearnGoal={setLearnGoal}
          onSetBrainIdInput={setBrainIdInput}
          onFileUpload={handleFileUpload}
          onLearnFileUpload={handleLearnFileUpload}
          onHatch={handleHatch}
          onRestartHatch={handleRestartHatch}
          onLearn={handleLearn}
          onFetchBrain={handleFetchBrain}
        />

        <PetResultPanel
          result={result}
          summary={summary}
          chatTurns={chatTurns}
          chatInput={chatInput}
          chatSending={chatSending}
          onSetChatInput={setChatInput}
          onClearChat={handleClearChat}
          onSendChat={handleSendChat}
        />
      </main>
    </div>
  );
}
