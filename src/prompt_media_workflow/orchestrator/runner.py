from __future__ import annotations

from prompt_media_workflow.config import load_internal_config
from prompt_media_workflow.models import IntakeRequest, WorkflowRecord
from prompt_media_workflow.stages.brief_building import build_brief
from prompt_media_workflow.stages.clarification import build_clarification_turn
from prompt_media_workflow.stages.critic import critique_candidate
from prompt_media_workflow.stages.generation import generate_candidates
from prompt_media_workflow.stages.prompt_analysis import analyze_prompt
from prompt_media_workflow.stages.refiner import plan_refinement
from prompt_media_workflow.stages.shot_planning import build_shot_plan
from prompt_media_workflow.tools.persistence import (
    save_brief,
    save_candidates,
    save_critic_result,
    save_refiner_output,
    save_shot_plan,
    save_workflow,
)


class WorkflowRunner:
    def __init__(self, workflow_prefix: str = "wf", app_config: dict | None = None) -> None:
        self.workflow_prefix = workflow_prefix
        self.app_config = app_config or load_internal_config()

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
        shot_plan = build_shot_plan(workflow, brief, duration_hint=answers.get("duration") if answers else None)
        candidate_count = (
            self.app_config.get("rendering", {}).get("candidate_count", 4)
            if isinstance(self.app_config, dict)
            else 4
        )
        candidates = generate_candidates(workflow, brief, shot_plan=shot_plan, candidate_count=candidate_count)
        primary_candidate = candidates[0] if candidates else None
        critic_result = critique_candidate(primary_candidate, brief) if primary_candidate else None
        refiner = (
            plan_refinement(primary_candidate, brief, critic_result)
            if primary_candidate and critic_result
            else None
        )

        save_brief(brief)
        if shot_plan:
            save_shot_plan(shot_plan)
        if candidates:
            save_candidates(candidates)
        if critic_result:
            save_critic_result(critic_result)
        if refiner:
            save_refiner_output(refiner)

        workflow.medium = analysis.medium
        workflow.current_brief_id = brief.brief_id
        if primary_candidate:
            workflow.active_candidate_id = primary_candidate.candidate_id
            workflow.status = "reviewing"
        else:
            workflow.status = "ready"
        save_workflow(workflow)
        return {
            "workflow": workflow.model_dump(),
            "analysis": analysis.model_dump(),
            "clarification": clarification.model_dump() if clarification else None,
            "brief": brief.model_dump(),
            "shot_plan": shot_plan.model_dump() if shot_plan else None,
            "candidates": [candidate.model_dump() for candidate in candidates],
            "critic": critic_result.model_dump() if critic_result else None,
            "refiner": refiner.model_dump() if refiner else None,
        }
