from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InferredDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: str | None


class PromptAnalysisStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    medium: str = Field(description="Either image or video.")
    use_case: str
    confidence: float
    unknowns: list[str]
    inferred_defaults: list[InferredDefault]
    next_action: str
    rejection_reason: str | None


class ClarificationQuestionStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    question: str


class ClarificationTurnStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[ClarificationQuestionStructuredOutput]


class BriefSubjectStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    description: str
    age_band: str | None
    identity_lock: bool | None
    reference_ids: list[str]


class BriefSettingStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str | None
    era: str | None
    world_style: str | None
    background_detail: str | None


class BriefStyleStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visual_style: str | None
    palette: list[str]
    lighting: str | None
    render_finish: str | None


class BriefCameraStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framing: str | None
    angle: str | None
    motion: str | None


class CreativeBriefStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    medium: str
    subject: BriefSubjectStructuredOutput
    setting: BriefSettingStructuredOutput
    style: BriefStyleStructuredOutput
    camera: BriefCameraStructuredOutput
    mood: str | None
    constraints: list[str]
    generation_prompt: str
    negative_prompt: list[str]
