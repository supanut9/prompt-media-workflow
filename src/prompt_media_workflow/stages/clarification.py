from __future__ import annotations

from prompt_media_workflow.models import ClarificationQuestion, ClarificationTurn, PromptAnalysisResult


QUESTION_BANK = {
    "framing": "Do you want a close-up, medium shot, wide shot, or full-body composition?",
    "style": "Should the style feel cinematic anime, realistic, painterly, manga-like, or something else specific?",
    "mood": "Should the mood feel dark, heroic, tense, soft, dramatic, or bright?",
    "duration": "How long should the clip be, for example 5 seconds or 8 seconds?",
}


def build_clarification_turn(analysis: PromptAnalysisResult, turn_index: int = 1) -> ClarificationTurn:
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

