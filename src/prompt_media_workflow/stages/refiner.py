from __future__ import annotations

from prompt_media_workflow.ai_models import RefinerOutputStructured
from prompt_media_workflow.models import CandidateRecord, CreativeBrief, CriticResult, RefinerOutput
from prompt_media_workflow.openai_client import OpenAIReasoningClient


def plan_refinement(
    candidate: CandidateRecord, brief: CreativeBrief, critic_result: CriticResult | None = None
) -> RefinerOutput:
    ai_result = plan_refinement_with_openai(candidate, brief, critic_result=critic_result)
    if ai_result is not None:
        return ai_result

    preserve = ["hero identity lock"] if brief.subject.identity_lock else []
    if brief.medium == "video":
        preserve.append("continuity of motion and rain density")
    delta = "Increase contrast on the subject and reinforce key lighting while keeping the same composition."
    if critic_result and critic_result.refinement_instruction:
        delta = critic_result.refinement_instruction
    return RefinerOutput(
        parent_candidate_id=candidate.candidate_id,
        refinement_prompt_delta=delta,
        preserve_constraints=preserve or ["keep core subject identity"],
    )


def plan_refinement_with_openai(
    candidate: CandidateRecord, brief: CreativeBrief, critic_result: CriticResult | None = None
) -> RefinerOutput | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    critique_summary = critic_result.refinement_instruction if critic_result else "No critic summary."
    instructions = (
        "You are the Refinement Planner. Return only structured output. "
        "Propose the minimum prompt delta necessary to address the critic feedback while preserving locked constraints."
    )
    user_input = (
        f"candidate_id: {candidate.candidate_id}\n"
        f"brief_id: {brief.brief_id}\n"
        f"generation_prompt: {brief.generation_prompt}\n"
        f"subject_identity_lock: {brief.subject.identity_lock}\n"
        f"critic_recommendation: {critic_result.recommendation if critic_result else 'unknown'}\n"
        f"critic_instruction: {critique_summary}\n"
        "Return the refinement delta and constraints."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=RefinerOutputStructured,
        )
    except Exception:
        return None

    preserve = parsed.preserve_constraints or []
    if brief.subject.identity_lock and "subject identity" not in " ".join(preserve).lower():
        preserve.append("subject identity lock")
    return RefinerOutput(
        parent_candidate_id=candidate.candidate_id,
        refinement_prompt_delta=parsed.refinement_prompt_delta,
        preserve_constraints=preserve,
    )
