from __future__ import annotations

from prompt_media_workflow.ai_models import PromptAnalysisStructuredOutput
from prompt_media_workflow.models import IntakeRequest, PromptAnalysisResult, WorkflowRecord
from prompt_media_workflow.openai_client import OpenAIReasoningClient


IMAGE_HINTS = ("image", "portrait", "illustration", "poster", "photo")
VIDEO_HINTS = ("video", "clip", "shot", "seconds", "camera", "motion", "scene")


def analyze_prompt(workflow: WorkflowRecord, request: IntakeRequest) -> PromptAnalysisResult:
    ai_result = analyze_prompt_with_openai(workflow, request)
    if ai_result is not None:
        return ai_result

    prompt = request.raw_prompt.strip()
    lowered = prompt.lower()

    medium = request.user_medium_hint or infer_medium(lowered)
    unknowns = infer_unknowns(lowered, medium)
    confidence = max(0.2, min(0.95, 0.9 - (0.12 * len(unknowns))))
    next_action = "generate" if confidence >= 0.75 or not unknowns else "ask"

    return PromptAnalysisResult(
        workflow_id=workflow.workflow_id,
        medium=medium,
        use_case=infer_use_case(lowered, medium),
        confidence=confidence,
        unknowns=unknowns,
        inferred_defaults=infer_defaults(lowered, medium),
        next_action=next_action,
    )


def analyze_prompt_with_openai(workflow: WorkflowRecord, request: IntakeRequest) -> PromptAnalysisResult | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    instructions = (
        "You are the Prompt Analyzer for a prompt-to-media workflow. "
        "Return only a structured result. "
        "Classify the request as image or video, estimate confidence, list only high-impact unknowns, "
        "infer safe defaults where obvious, and choose next_action from ask, generate, or reject."
    )
    user_input = (
        f"raw_prompt: {request.raw_prompt}\n"
        f"user_medium_hint: {request.user_medium_hint}\n"
        "Return a concise structured analysis."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=PromptAnalysisStructuredOutput,
        )
    except Exception:
        return None
    return PromptAnalysisResult(
        workflow_id=workflow.workflow_id,
        medium=parsed.medium,  # type: ignore[arg-type]
        use_case=parsed.use_case,
        confidence=parsed.confidence,
        unknowns=parsed.unknowns,
        inferred_defaults={item.key: item.value for item in parsed.inferred_defaults},
        next_action=parsed.next_action,  # type: ignore[arg-type]
        rejection_reason=parsed.rejection_reason,
    )


def infer_medium(prompt: str) -> str:
    if any(token in prompt for token in VIDEO_HINTS):
        return "video"
    if any(token in prompt for token in IMAGE_HINTS):
        return "image"
    return "image"


def infer_use_case(prompt: str, medium: str) -> str:
    if "anime" in prompt:
        return f"anime_{'scene' if medium == 'video' else 'illustration'}"
    if "product" in prompt:
        return "product_shot"
    if "portrait" in prompt:
        return "portrait"
    return "general_visual_generation"


def infer_unknowns(prompt: str, medium: str) -> list[str]:
    unknowns: list[str] = []
    if not any(token in prompt for token in ("close-up", "close up", "medium shot", "wide", "portrait", "full-body", "full body")):
        unknowns.append("framing")
    if not any(token in prompt for token in ("anime", "cinematic", "realistic", "illustration", "painterly", "manga")):
        unknowns.append("style")
    if not any(token in prompt for token in ("dark", "bright", "dramatic", "soft", "tense", "heroic", "moody")):
        unknowns.append("mood")
    if medium == "video" and not any(token in prompt for token in ("second", "seconds", "short", "clip")):
        unknowns.append("duration")
    return unknowns


def infer_defaults(prompt: str, medium: str) -> dict[str, str]:
    defaults: dict[str, str] = {}
    if "anime" in prompt:
        defaults["style.visual_style"] = "cinematic anime"
    if medium == "video":
        defaults["camera.motion"] = "slow push-in"
    return defaults
