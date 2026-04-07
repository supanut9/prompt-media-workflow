from __future__ import annotations

from prompt_media_workflow.ai_models import ShotPlanStructuredOutput
from prompt_media_workflow.models import CreativeBrief, ShotDetail, ShotPlan, WorkflowRecord
from prompt_media_workflow.openai_client import OpenAIReasoningClient


def build_shot_plan(
    workflow: WorkflowRecord, brief: CreativeBrief, duration_hint: float | None = None
) -> ShotPlan | None:
    if brief.medium != "video":
        return None

    ai_result = build_shot_plan_with_openai(workflow, brief, duration_hint=duration_hint)
    if ai_result is not None:
        return ai_result

    return fallback_shot_plan(workflow, brief, duration_hint=duration_hint)


def build_shot_plan_with_openai(
    workflow: WorkflowRecord, brief: CreativeBrief, duration_hint: float | None = None
) -> ShotPlan | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    duration = duration_hint or 6.0
    instructions = (
        "You are the Shot Planner for a video generation workflow. "
        "Return only structured output. "
        "Create a concise shot plan covering the full duration with 2-4 meaningful shots. "
        "Shots should include purpose, composition, subject + camera motion, and continuity notes. "
        "Ensure total duration roughly matches the requested length."
    )
    user_input = (
        f"workflow_id: {workflow.workflow_id}\n"
        f"brief_id: {brief.brief_id}\n"
        f"goal: {brief.goal}\n"
        f"subject: {brief.subject.description}\n"
        f"setting: {brief.setting.location}\n"
        f"style: {brief.style.visual_style}\n"
        f"camera: {brief.camera.model_dump()}\n"
        f"duration_hint: {duration}\n"
        "Return the structured shot plan."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=ShotPlanStructuredOutput,
        )
    except Exception:
        return None

    shot_plan_id = f"shotplan_{workflow.workflow_id.split('_')[-1]}"
    return ShotPlan(
        shot_plan_id=shot_plan_id,
        workflow_id=workflow.workflow_id,
        brief_id=brief.brief_id,
        duration_seconds=parsed.duration_seconds,
        shots=[
            ShotDetail(
                shot_id=item.shot_id,
                duration_seconds=item.duration_seconds,
                purpose=item.purpose,
                composition=item.composition,
                subject_action=item.subject_action,
                camera_motion=item.camera_motion,
                environment_motion=item.environment_motion,
                continuity_rules=item.continuity_rules,
            )
            for item in parsed.shots
        ],
        keyframe_requirements=parsed.keyframe_requirements,
    )


def fallback_shot_plan(
    workflow: WorkflowRecord, brief: CreativeBrief, duration_hint: float | None = None
) -> ShotPlan:
    duration = duration_hint or 6.0
    per_shot = max(duration / 3, 1.5)
    shots = [
        ShotDetail(
            shot_id="shot_intro",
            duration_seconds=per_shot,
            purpose="Establish location and weather",
            composition="wide establishing view of the alley",
            subject_action="character steps into frame, cloak fluttering",
            camera_motion="slow dolly in",
            continuity_rules=["keep rain intensity constant"],
        ),
        ShotDetail(
            shot_id="shot_action",
            duration_seconds=per_shot,
            purpose="Show hero stance and sword energy",
            composition="medium shot angled from below",
            subject_action="raise sword as energy arcs",
            camera_motion="handheld sway",
            continuity_rules=["maintain blue energy hue"],
        ),
        ShotDetail(
            shot_id="shot_finish",
            duration_seconds=max(duration - (2 * per_shot), 1.0),
            purpose="Resolve action with dramatic push",
            composition="tight shot on determined expression",
            subject_action="charge forward through rain",
            camera_motion="fast push-in then whip pan",
            continuity_rules=["subject stays sharp despite rain"],
        ),
    ]
    return ShotPlan(
        shot_plan_id=f"shotplan_{workflow.workflow_id.split('_')[-1]}",
        workflow_id=workflow.workflow_id,
        brief_id=brief.brief_id,
        duration_seconds=duration,
        shots=shots,
        keyframe_requirements=["first frame hero entrance", "mid-frame sword energy", "final frame strike pose"],
    )
