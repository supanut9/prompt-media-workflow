from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


Medium = Literal["image", "video"]
WorkflowStatus = Literal[
    "draft", "clarifying", "ready", "generating", "reviewing", "accepted", "rejected", "exported"
]
CandidateStatus = Literal["generated", "scored", "selected", "rejected", "refining", "accepted"]
AnalysisAction = Literal["ask", "generate", "reject"]
CriticRecommendation = Literal["accept", "refine", "ask_user", "reject"]
GenerationStage = Literal["initial", "reference", "refinement", "video_render"]
BackendType = Literal["comfyui", "diffusers", "openai", "replicate", "custom"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class IntakeRequest(BaseModel):
    raw_prompt: str
    user_medium_hint: Medium | None = None
    user_id: str | None = None
    session_id: str | None = None


class WorkflowRecord(BaseModel):
    workflow_id: str
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    status: WorkflowStatus = "draft"
    medium: Medium | None = None
    raw_prompt: str
    current_prompt_version: int = 1
    current_brief_id: str | None = None
    active_candidate_id: str | None = None
    clarification_turns: int = 0
    user_id: str | None = None
    session_id: str | None = None


class PromptAnalysisResult(BaseModel):
    workflow_id: str
    medium: Medium
    use_case: str
    confidence: float = Field(ge=0, le=1)
    unknowns: list[str]
    inferred_defaults: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    next_action: AnalysisAction
    rejection_reason: str | None = None


class ClarificationQuestion(BaseModel):
    field: str
    question: str


class ClarificationTurn(BaseModel):
    workflow_id: str
    turn_index: int
    questions: list[ClarificationQuestion]
    answers: dict[str, str] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class Subject(BaseModel):
    type: str
    description: str
    age_band: str | None = None
    identity_lock: bool | None = None
    reference_ids: list[str] = Field(default_factory=list)


class Setting(BaseModel):
    location: str | None = None
    era: str | None = None
    world_style: str | None = None
    background_detail: str | None = None


class Style(BaseModel):
    visual_style: str | None = None
    palette: list[str] = Field(default_factory=list)
    lighting: str | None = None
    render_finish: str | None = None


class Camera(BaseModel):
    framing: str | None = None
    angle: str | None = None
    motion: str | None = None


class CreativeBrief(BaseModel):
    brief_id: str
    workflow_id: str
    goal: str
    medium: Medium
    subject: Subject
    setting: Setting
    style: Style
    camera: Camera
    mood: str | None = None
    constraints: list[str] = Field(default_factory=list)
    generation_prompt: str
    negative_prompt: list[str] = Field(default_factory=list)


class ShotDetail(BaseModel):
    shot_id: str
    duration_seconds: float
    purpose: str
    composition: str
    subject_action: str
    camera_motion: str
    environment_motion: str | None = None
    continuity_rules: list[str] = Field(default_factory=list)


class ShotPlan(BaseModel):
    shot_plan_id: str
    workflow_id: str
    brief_id: str
    duration_seconds: float
    shots: list[ShotDetail]
    keyframe_requirements: list[str] = Field(default_factory=list)


class CandidateRecord(BaseModel):
    candidate_id: str
    workflow_id: str
    medium: Medium
    brief_id: str
    shot_plan_id: str | None = None
    parent_candidate_id: str | None = None
    prompt_version: int = 1
    generation_stage: GenerationStage = "initial"
    input_references: list[str] = Field(default_factory=list)
    asset_uri: str
    thumbnail_uri: str | None = None
    seed: int | None = None
    backend: BackendType | None = None
    model: str | None = None
    critic_score: float | None = None
    status: CandidateStatus = "generated"


class CriticScores(BaseModel):
    prompt_match: float
    style_match: float
    composition: float | None = None
    subject_quality: float | None = None
    motion_quality: float | None = None
    continuity: float | None = None
    identity_consistency: float | None = None
    artifact_penalty: float | None = None


class CriticResult(BaseModel):
    candidate_id: str
    brief_id: str
    scores: CriticScores
    failures: list[str] = Field(default_factory=list)
    recommendation: CriticRecommendation
    refinement_instruction: str | None = None


class RefinerOutput(BaseModel):
    parent_candidate_id: str
    refinement_prompt_delta: str
    preserve_constraints: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    raw: dict
