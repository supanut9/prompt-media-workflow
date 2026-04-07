from __future__ import annotations

from prompt_media_workflow.models import Camera, CreativeBrief, PromptAnalysisResult, Setting, Style, Subject, WorkflowRecord


def build_brief(
    workflow: WorkflowRecord, analysis: PromptAnalysisResult, answers: dict[str, str] | None = None
) -> CreativeBrief:
    answers = answers or {}
    prompt = workflow.raw_prompt.strip()
    medium = analysis.medium
    framing = answers.get("framing", "medium shot" if medium == "video" else "wide shot")
    mood = answers.get("mood", "dramatic")
    style_name = answers.get("style", analysis.inferred_defaults.get("style.visual_style", "cinematic"))

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

