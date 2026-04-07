from __future__ import annotations

from prompt_media_workflow.ai_models import CreativeBriefStructuredOutput
from prompt_media_workflow.models import Camera, CreativeBrief, PromptAnalysisResult, Setting, Style, Subject, WorkflowRecord
from prompt_media_workflow.openai_client import OpenAIReasoningClient


def build_brief(
    workflow: WorkflowRecord, analysis: PromptAnalysisResult, answers: dict[str, str] | None = None
) -> CreativeBrief:
    ai_result = build_brief_with_openai(workflow, analysis, answers=answers)
    if ai_result is not None:
        return ai_result

    answers = answers or {}
    prompt = workflow.raw_prompt.strip()
    medium = analysis.medium
    framing = answers.get("framing", "medium shot" if medium == "video" else "wide shot")
    mood = answers.get("mood", "dramatic")
    style_name = answers.get("style", default_inferred_style(analysis))

    subject = Subject(
        type="human" if any(token in prompt.lower() for token in ("man", "woman", "girl", "boy", "hero", "character")) else "subject",
        description=prompt,
        age_band="adult",
        identity_lock=(medium == "video"),
    )
    setting = Setting(location=infer_location(prompt), era="unspecified", world_style="stylized")
    style = Style(
        visual_style=str(style_name),
        palette=infer_palette(prompt),
        lighting="dramatic lighting",
        render_finish="high detail",
    )
    camera = Camera(framing=framing, angle="eye level", motion="slow push-in" if medium == "video" else None)

    return CreativeBrief(
        brief_id=f"brief_{workflow.workflow_id.split('_')[-1]}",
        workflow_id=workflow.workflow_id,
        goal=f"{medium} generation from clarified brief",
        medium=medium,
        subject=subject,
        setting=setting,
        style=style,
        camera=camera,
        mood=mood,
        constraints=["no text"],
        generation_prompt=build_generation_prompt(subject.description, style.visual_style, framing, mood, setting.location),
        negative_prompt=["blurry", "text", "bad anatomy"],
    )


def build_brief_with_openai(
    workflow: WorkflowRecord, analysis: PromptAnalysisResult, answers: dict[str, str] | None = None
) -> CreativeBrief | None:
    client = OpenAIReasoningClient()
    if not client.enabled:
        return None

    answers = answers or {}
    instructions = (
        "You are the Creative Brief Builder for a prompt-to-media workflow. "
        "Return only structured output. "
        "Build a concise but production-ready creative brief for generation. "
        "Use the user answers when available, otherwise apply safe defaults from analysis. "
        "Keep the brief faithful to the prompt and avoid adding unrelated concepts."
    )
    user_input = (
        f"workflow_id: {workflow.workflow_id}\n"
        f"raw_prompt: {workflow.raw_prompt}\n"
        f"medium: {analysis.medium}\n"
        f"use_case: {analysis.use_case}\n"
        f"unknowns: {analysis.unknowns}\n"
        f"inferred_defaults: {analysis.inferred_defaults}\n"
        f"user_answers: {answers}\n"
        "Return a complete brief including generation and negative prompts."
    )

    try:
        parsed = client.parse(
            instructions=instructions,
            user_input=user_input,
            text_format=CreativeBriefStructuredOutput,
        )
    except Exception:
        return None

    return CreativeBrief(
        brief_id=f"brief_{workflow.workflow_id.split('_')[-1]}",
        workflow_id=workflow.workflow_id,
        goal=parsed.goal,
        medium=parsed.medium,  # type: ignore[arg-type]
        subject=Subject(
            type=parsed.subject.type,
            description=parsed.subject.description,
            age_band=parsed.subject.age_band,
            identity_lock=parsed.subject.identity_lock,
            reference_ids=parsed.subject.reference_ids,
        ),
        setting=Setting(
            location=parsed.setting.location,
            era=parsed.setting.era,
            world_style=parsed.setting.world_style,
            background_detail=parsed.setting.background_detail,
        ),
        style=Style(
            visual_style=parsed.style.visual_style,
            palette=parsed.style.palette,
            lighting=parsed.style.lighting,
            render_finish=parsed.style.render_finish,
        ),
        camera=Camera(
            framing=parsed.camera.framing,
            angle=parsed.camera.angle,
            motion=parsed.camera.motion,
        ),
        mood=parsed.mood,
        constraints=parsed.constraints,
        generation_prompt=parsed.generation_prompt,
        negative_prompt=parsed.negative_prompt,
    )


def default_inferred_style(analysis: PromptAnalysisResult) -> str:
    return str(analysis.inferred_defaults.get("style.visual_style", "cinematic"))


def infer_location(prompt: str) -> str:
    lowered = prompt.lower()
    if "alley" in lowered:
        return "neon alley"
    if "throne" in lowered:
        return "throne room"
    if "city" in lowered:
        return "city"
    return "unspecified setting"


def infer_palette(prompt: str) -> list[str]:
    lowered = prompt.lower()
    palette: list[str] = []
    for color in ("red", "blue", "gold", "black", "teal", "purple", "white"):
        if color in lowered:
            palette.append(color)
    return palette or ["neutral"]


def build_generation_prompt(description: str, style: str, framing: str, mood: str, location: str | None) -> str:
    return f"{style} {description}, {framing}, {mood} mood, set in {location or 'an evocative setting'}"
