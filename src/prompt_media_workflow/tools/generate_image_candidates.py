from __future__ import annotations

import logging
from pathlib import Path

from prompt_media_workflow.generators.openai_images import OpenAIImageGenerator
from prompt_media_workflow.generators.comfyui import ComfyUIGenerator


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
    comfyui_config: dict | None = None,
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

    result = {
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
    if backend == "comfyui" and comfyui_config:
        generated = _try_generate_with_comfyui(
            workflow_id=workflow_id,
            brief_id=brief_id,
            candidate_count=candidate_count,
            prompt=prompt or "",
            negative_prompt=", ".join(negative_prompt or []),
            output_format=output_format,
            comfy_cfg=comfyui_config,
        )
        if generated:
            return {"generated_candidates": generated}
    return result


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


def _try_generate_with_comfyui(
    *,
    workflow_id: str,
    brief_id: str,
    candidate_count: int,
    prompt: str,
    negative_prompt: str,
    output_format: str | None,
    comfy_cfg: dict,
) -> list[dict] | None:
    generator = ComfyUIGenerator(
        server_url=comfy_cfg.get("server_url", "http://127.0.0.1:8188"),
        workflow_path=comfy_cfg.get("workflow_path", "comfyui/workflows/base.json"),
        prompt_field=comfy_cfg.get("prompt_field", "{{PROMPT}}"),
        negative_prompt_field=comfy_cfg.get("negative_prompt_field", "{{NEGATIVE_PROMPT}}"),
        timeout_seconds=int(comfy_cfg.get("timeout_seconds", 60)),
    )
    if not generator.enabled:
        LOGGER.info("ComfyUI workflow template not found; falling back to stub output")
        return None

    output_paths = [
        Path("artifacts") / workflow_id / f"img_{index + 1:03d}.{output_format or 'png'}"
        for index in range(candidate_count)
    ]
    try:
        saved_paths = generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            candidate_count=candidate_count,
            output_paths=output_paths,
        )
    except Exception as exc:  # pragma: no cover - external dependency
        LOGGER.warning("ComfyUI image generation failed: %s", exc)
        return None

    generated: list[dict] = []
    for index, path in enumerate(saved_paths):
        generated.append(
            {
                "candidate_id": f"img_{index + 1:03d}",
                "workflow_id": workflow_id,
                "brief_id": brief_id,
                "asset_uri": str(path.relative_to(Path.cwd()) if path.is_absolute() else path),
                "backend": "comfyui",
                "model": comfy_cfg.get("workflow_path"),
                "status": "generated",
            }
        )
    return generated
