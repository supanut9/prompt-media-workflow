from __future__ import annotations

from prompt_media_workflow.models import IntakeRequest, WorkflowRecord
from prompt_media_workflow.stages.brief_building import build_brief
from prompt_media_workflow.stages.clarification import build_clarification_turn
from prompt_media_workflow.stages.prompt_analysis import analyze_prompt


class WorkflowRunner:
    def __init__(self, workflow_prefix: str = "wf") -> None:
        self.workflow_prefix = workflow_prefix

    def create_workflow(self, request: IntakeRequest, ordinal: int = 1) -> WorkflowRecord:
        return WorkflowRecord(
            workflow_id=f"{self.workflow_prefix}_{ordinal:03d}",
            raw_prompt=request.raw_prompt,
            user_id=request.user_id,
            session_id=request.session_id,
        )

    def run_text_pipeline(self, request: IntakeRequest, ordinal: int = 1, answers: dict[str, str] | None = None) -> dict:
        workflow = self.create_workflow(request, ordinal=ordinal)
        analysis = analyze_prompt(workflow, request)
        clarification = build_clarification_turn(analysis) if analysis.next_action == "ask" else None
        brief = build_brief(workflow, analysis, answers=answers)
        workflow.medium = analysis.medium
        workflow.current_brief_id = brief.brief_id
        workflow.status = "ready"
        return {
            "workflow": workflow.model_dump(),
            "analysis": analysis.model_dump(),
            "clarification": clarification.model_dump() if clarification else None,
            "brief": brief.model_dump(),
        }

