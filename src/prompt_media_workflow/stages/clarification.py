from __future__ import annotations

from prompt_media_workflow.ai_models import ClarificationTurnStructuredOutput
from prompt_media_workflow.models import ClarificationQuestion, ClarificationTurn, PromptAnalysisResult
from prompt_media_workflow.openai_client import OpenAIReasoningClient


QUESTION_BANK = {
    "framing": "Do you want a close-up, medium shot, wide shot, or full-body composition?",
    "style": "Should the style feel cinematic anime, realistic, painterly, manga-like, or something else specific?",
    "mood": "Should the mood feel dark, heroic, tense, soft, dramatic, or bright?",
    "duration": "How long should the clip be, for example 5 seconds or 8 seconds?",
}


def build_clarification_turn(analysis: PromptAnalysisResult, turn_index: int = 1) -> ClarificationTurn:
    ai_result = build_clarification_turn_with_openai(analysis, turn_index=turn_index)
    if ai_result is not None:
        return ai_result

    questions = [
        ClarificationQuestion(field=field, question=QUESTION_BANK[field])
        for field in analysis.unknowns[:3]
        if field in QUESTION_BANK
    ]
    return ClarificationTurn(
        workflow_id=analysis.workflow_id,
        turn_index=turn_index,
        questions=questions,
    )


def build_clarification_turn_with_openai(
    analysis: PromptAnalysisResult, turn_index: int = 1
) -> ClarificationTurn | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    instructions = (
        "You are the Clarification stage for a prompt-to-media workflow. "
        "Return only structured output. "
        "Ask at most 3 high-impact clarification questions based only on the provided unknowns. "
        "Do not ask for information that can be safely defaulted. "
        "Questions should be concise, specific, and easy for a user to answer."
    )
    user_input = (
        f"workflow_id: {analysis.workflow_id}\n"
        f"medium: {analysis.medium}\n"
        f"use_case: {analysis.use_case}\n"
        f"confidence: {analysis.confidence}\n"
        f"unknowns: {analysis.unknowns}\n"
        f"inferred_defaults: {analysis.inferred_defaults}\n"
        "Return only the questions."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=ClarificationTurnStructuredOutput,
        )
    except Exception:
        return None

    return ClarificationTurn(
        workflow_id=analysis.workflow_id,
        turn_index=turn_index,
        questions=[ClarificationQuestion(field=item.field, question=item.question) for item in parsed.questions[:3]],
    )
