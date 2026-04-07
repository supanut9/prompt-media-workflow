from __future__ import annotations

from prompt_media_workflow.ai_models import CriticResultStructuredOutput
from prompt_media_workflow.models import CandidateRecord, CreativeBrief, CriticResult, CriticScores
from prompt_media_workflow.openai_client import OpenAIReasoningClient


def critique_candidate(
    candidate: CandidateRecord, brief: CreativeBrief, candidate_summary: str | None = None
) -> CriticResult:
    ai_result = critique_candidate_with_openai(candidate, brief, candidate_summary=candidate_summary)
    if ai_result is not None:
        return ai_result

    # Simple fallback heuristic favors initial candidates but encourages refinement.
    base_score = 6.5 if candidate.generation_stage == "initial" else 7.0
    scores = CriticScores(
        prompt_match=base_score,
        style_match=base_score - 0.5,
        composition=base_score - 1,
        subject_quality=base_score,
        motion_quality=base_score if brief.medium == "video" else None,
        continuity=base_score - 1 if brief.medium == "video" else None,
        identity_consistency=8.0 if brief.subject.identity_lock else None,
        artifact_penalty=2.0,
    )
    recommendation = "refine" if base_score < 7.5 else "accept"  # type: ignore[arg-type]
    instruction = (
        "Sharpen composition and emphasize hero silhouette while keeping rain atmosphere."
        if recommendation == "refine"
        else None
    )
    return CriticResult(
        candidate_id=candidate.candidate_id,
        brief_id=brief.brief_id,
        scores=scores,
        failures=[],
        recommendation=recommendation,  # type: ignore[arg-type]
        refinement_instruction=instruction,
    )


def critique_candidate_with_openai(
    candidate: CandidateRecord, brief: CreativeBrief, candidate_summary: str | None = None
) -> CriticResult | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    summary = candidate_summary or (
        f"Asset URI: {candidate.asset_uri}. Stage: {candidate.generation_stage}. "
        "Assume overall style matches generation prompt but needs critique."
    )
    instructions = (
        "You are the Critic stage for the workflow. Return only structured output. "
        "Score the candidate against the brief, list any critical failures, and choose a recommendation. "
        "Write a short refinement instruction when recommending refinement."
    )
    user_input = (
        f"candidate_id: {candidate.candidate_id}\n"
        f"brief_id: {brief.brief_id}\n"
        f"brief_goal: {brief.goal}\n"
        f"generation_prompt: {brief.generation_prompt}\n"
        f"constraints: {brief.constraints}\n"
        f"candidate_summary: {summary}\n"
        f"medium: {candidate.medium}\n"
        f"generation_stage: {candidate.generation_stage}\n"
        "Return structured critic scores."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=CriticResultStructuredOutput,
        )
    except Exception:
        return None

    return CriticResult(
        candidate_id=candidate.candidate_id,
        brief_id=brief.brief_id,
        scores=CriticScores(
            prompt_match=parsed.scores.prompt_match,
            style_match=parsed.scores.style_match,
            composition=parsed.scores.composition,
            subject_quality=parsed.scores.subject_quality,
            motion_quality=parsed.scores.motion_quality,
            continuity=parsed.scores.continuity,
            identity_consistency=parsed.scores.identity_consistency,
            artifact_penalty=parsed.scores.artifact_penalty,
        ),
        failures=parsed.failures,
        recommendation=parsed.recommendation,  # type: ignore[arg-type]
        refinement_instruction=parsed.refinement_instruction,
    )
