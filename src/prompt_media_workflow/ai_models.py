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
