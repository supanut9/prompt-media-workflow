from __future__ import annotations

from pathlib import Path

from prompt_media_workflow.models import CandidateRecord, CreativeBrief, ShotPlan, WorkflowRecord
from prompt_media_workflow.tools.generate_image_candidates import generate_image_candidates

ARTIFACT_ROOT = Path("artifacts")


def generate_candidates(
    workflow: WorkflowRecord,
    brief: CreativeBrief,
    shot_plan: ShotPlan | None = None,
    candidate_count: int = 4,
) -> list[CandidateRecord]:
    response = generate_image_candidates(
        workflow_id=workflow.workflow_id,
        brief_id=brief.brief_id,
        medium=brief.medium,
        candidate_count=candidate_count,
        prompt=brief.generation_prompt,
        negative_prompt=brief.negative_prompt,
        shot_plan_id=shot_plan.shot_plan_id if shot_plan else None,
    )
    candidates: list[CandidateRecord] = []
    for record in response.get("generated_candidates", []):
        asset_uri = record["asset_uri"]
        ensure_artifact(asset_uri)
        candidates.append(
            CandidateRecord(
                candidate_id=record["candidate_id"],
                workflow_id=workflow.workflow_id,
                medium=brief.medium,
                brief_id=brief.brief_id,
                shot_plan_id=shot_plan.shot_plan_id if shot_plan else None,
                parent_candidate_id=record.get("parent_candidate_id"),
                prompt_version=workflow.current_prompt_version,
                generation_stage="initial",
                input_references=record.get("input_references", []),
                asset_uri=asset_uri,
                thumbnail_uri=record.get("thumbnail_uri"),
                seed=record.get("seed"),
                backend=record.get("backend"),
                model=record.get("model"),
                critic_score=None,
                status="generated",
            )
        )
    return candidates


def ensure_artifact(asset_uri: str) -> None:
    path = Path(asset_uri)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(b"")
