from __future__ import annotations

from collections.abc import Iterable

from prompt_media_workflow.models import (
    CandidateRecord,
    CreativeBrief,
    CriticResult,
    RefinerOutput,
    ShotPlan,
    WorkflowRecord,
)
from prompt_media_workflow.storage import write_json


def save_workflow(workflow: WorkflowRecord) -> str:
    path = f"workflows/{workflow.workflow_id}.json"
    write_json(path, workflow.model_dump())
    return path


def save_brief(brief: CreativeBrief) -> str:
    path = f"briefs/{brief.brief_id}.json"
    write_json(path, brief.model_dump())
    return path


def save_shot_plan(shot_plan: ShotPlan) -> str:
    path = f"shot_plans/{shot_plan.shot_plan_id}.json"
    write_json(path, shot_plan.model_dump())
    return path


def save_candidates(candidates: Iterable[CandidateRecord]) -> list[str]:
    saved_paths: list[str] = []
    for candidate in candidates:
        path = f"candidates/{candidate.workflow_id}/{candidate.candidate_id}.json"
        write_json(path, candidate.model_dump())
        saved_paths.append(path)
    return saved_paths


def save_critic_result(result: CriticResult) -> str:
    path = f"critics/{result.candidate_id}.json"
    write_json(path, result.model_dump())
    return path


def save_refiner_output(output: RefinerOutput) -> str:
    path = f"refiners/{output.parent_candidate_id}.json"
    write_json(path, output.model_dump())
    return path
