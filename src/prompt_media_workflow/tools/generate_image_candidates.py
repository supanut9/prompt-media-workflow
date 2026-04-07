from __future__ import annotations

import logging
from pathlib import Path

from prompt_media_workflow.generators.openai_images import OpenAIImageGenerator


LOGGER = logging.getLogger(__name__)


def generate_image_candidates(
    *,
    workflow_id: str,
    brief_id: str,
    medium: str,
    candidate_count: int = 4,
    prompt: str | None = None,
    negative_prompt: list[str] | None = None,
    shot_plan_id: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    width: int = 1024,
    height: int = 1024,
    quality: str | None = None,
    background: str | None = None,
    output_format: str | None = "png",
) -> dict:
    """Generator adapter that prefers OpenAI images and falls back to stubs."""
    if backend == "openai":
        generated = _try_generate_with_openai(
            workflow_id=workflow_id,
            brief_id=brief_id,
            candidate_count=candidate_count,
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            width=width,
            height=height,
            quality=quality,
            background=background,
            output_format=output_format,
        )
        if generated:
            return {"generated_candidates": generated}

    return {
        "generated_candidates": [
            {
                "candidate_id": f"img_{index + 1:03d}",
                "workflow_id": workflow_id,
                "brief_id": brief_id,
                "asset_uri": f"artifacts/{workflow_id}/img_{index + 1:03d}.png",
                "status": "generated",
            }
            for index in range(candidate_count)
        ]
    }


def _try_generate_with_openai(
    *,
    workflow_id: str,
    brief_id: str,
    candidate_count: int,
    prompt: str | None,
    negative_prompt: list[str] | None,
    model: str | None,
    width: int,
    height: int,
    quality: str | None,
    background: str | None,
    output_format: str | None,
) -> list[dict] | None:
    generator = OpenAIImageGenerator(model=model or "gpt-image-1.5")
    if not generator.enabled:
        LOGGER.info("OpenAI image generator unavailable; using stub output")
        return None

    output_paths = [
        Path("artifacts") / workflow_id / f"img_{index + 1:03d}.{output_format or 'png'}"
        for index in range(candidate_count)
    ]
    text_prompt = prompt or ""
    if negative_prompt:
        avoid_clause = f"Avoid: {', '.join(negative_prompt)}"
        text_prompt = f"{text_prompt}\n{avoid_clause}" if text_prompt else avoid_clause

    try:
        saved_paths = generator.generate(
            prompt=text_prompt,
            candidate_count=candidate_count,
            width=width,
            height=height,
            output_paths=output_paths,
            quality=quality,
            background=background,
            output_format=output_format,
        )
    except Exception as exc:  # pragma: no cover - external dependency
        LOGGER.warning("OpenAI image generation failed: %s", exc)
        return None

    generated: list[dict] = []
    for index, path in enumerate(saved_paths):
        generated.append(
            {
                "candidate_id": f"img_{index + 1:03d}",
                "workflow_id": workflow_id,
                "brief_id": brief_id,
                "asset_uri": str(path.relative_to(Path.cwd()) if path.is_absolute() else path),
                "backend": "openai",
                "model": model or "gpt-image-1.5",
                "status": "generated",
            }
        )
    return generated
