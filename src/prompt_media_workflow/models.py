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


class AppConfig(BaseModel):
    raw: dict

