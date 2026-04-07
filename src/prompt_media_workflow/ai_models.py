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


class ShotDetailStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shot_id: str
    duration_seconds: float
    purpose: str
    composition: str
    subject_action: str
    camera_motion: str
    environment_motion: str | None
    continuity_rules: list[str]


class ShotPlanStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration_seconds: float
    shots: list[ShotDetailStructuredOutput]
    keyframe_requirements: list[str]


class CriticScoresStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_match: float
    style_match: float
    composition: float | None
    subject_quality: float | None
    motion_quality: float | None
    continuity: float | None
    identity_consistency: float | None
    artifact_penalty: float | None


class CriticResultStructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: CriticScoresStructuredOutput
    failures: list[str]
    recommendation: str
    refinement_instruction: str | None


class RefinerOutputStructured(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refinement_prompt_delta: str
    preserve_constraints: list[str]
