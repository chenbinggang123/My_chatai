from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError


class BrainStateValidationError(Exception):
    pass


class BrainProfile(BaseModel):
    pet_name: str
    pet_seed_personality: str
    confidence: float
    evidence_quality: Literal["high", "medium", "low"]
    limitations: list[str] = Field(default_factory=list)


class LanguageModel(BaseModel):
    tone: list[str] = Field(default_factory=list)
    sentence_length: Literal["short", "medium", "long", "mixed"]
    emoji_style: str
    punctuation_habits: list[str] = Field(default_factory=list)
    catchphrases: list[str] = Field(default_factory=list)
    comfort_lines: list[str] = Field(default_factory=list)


class EmotionModel(BaseModel):
    emotional_intensity: Literal["low", "medium", "high"]
    soothing_style: str
    conflict_style: str
    attention_style: str


class RelationshipModel(BaseModel):
    closeness_pacing: Literal["slow", "medium", "fast"]
    boundary_style: str
    dependency_style: str
    safe_topics: list[str] = Field(default_factory=list)
    trigger_topics: list[str] = Field(default_factory=list)


class Stage(BaseModel):
    stage_id: int
    stage_name: str
    stage_description: str


class Milestone(BaseModel):
    milestone_id: str
    name: str
    unlock_condition: str
    expected_behavior: str
    status: str | None = None


class GrowthModel(BaseModel):
    current_stage: Stage
    milestones: list[Milestone] = Field(default_factory=list)
    next_training_data: list[str] = Field(default_factory=list)


class RuntimeAssets(BaseModel):
    system_prompt: str
    starter_messages: list[str] = Field(default_factory=list)
    do: list[str] = Field(default_factory=list)
    dont: list[str] = Field(default_factory=list)


class BrainState(BaseModel):
    brain_profile: BrainProfile
    language_model: LanguageModel
    emotion_model: EmotionModel
    relationship_model: RelationshipModel
    growth_model: GrowthModel
    runtime_assets: RuntimeAssets
    meta: dict[str, Any] | None = None


def validate_brain_state(data: dict) -> dict:
    try:
        parsed = BrainState.model_validate(data)
        return parsed.model_dump()
    except ValidationError as exc:
        raise BrainStateValidationError(str(exc)) from exc
