import { type PetWorkspace } from "../hooks/usePetLab";

type PetWorkspaceHeaderProps = {
  petWorkspaces: PetWorkspace[];
  activePetId: string;
  activePetName: string;
  onAddPet: () => void;
  onDeleteActivePet: () => void;
  onSelectPet: (petId: string) => void;
  onRenameActivePet: (name: string) => void;
};

export function PetWorkspaceHeader({
  petWorkspaces,
  activePetId,
  activePetName,
  onAddPet,
  onDeleteActivePet,
  onSelectPet,
  onRenameActivePet,
}: PetWorkspaceHeaderProps) {
  return (
    <div className="mx-auto mb-4 w-full max-w-6xl rounded-3xl border border-slate-200/70 bg-white/90 p-4 shadow-xl backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-800">孵化列表</p>
          <p className="text-xs text-slate-500">可同时维护多个宠物，每个宠物都有独立孵化与学习状态。</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onDeleteActivePet}
            className="rounded-xl border border-rose-300 bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700 transition hover:bg-rose-100"
          >
            删除当前宠物
          </button>
          <button
            onClick={onAddPet}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
          >
            + 新建宠物
          </button>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <label htmlFor="active-pet-name" className="text-xs font-medium text-slate-600">
          当前宠物命名
        </label>
        <input
          id="active-pet-name"
          value={activePetName}
          onChange={(e) => onRenameActivePet(e.target.value)}
          placeholder="给当前宠物取个名字"
          className="w-full max-w-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-400"
        />
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {petWorkspaces.map((pet) => {
          const isActive = pet.id === activePetId;
          return (
            <button
              key={pet.id}
              onClick={() => onSelectPet(pet.id)}
              className={`rounded-xl border px-3 py-2 text-left text-sm transition ${
                isActive
                  ? "border-sky-400 bg-sky-50 text-sky-900"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              <p className="font-semibold">{pet.name}</p>
              <p className="mt-0.5 text-xs opacity-80">{pet.brainIdInput || "未孵化"}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
