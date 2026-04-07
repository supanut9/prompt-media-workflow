from __future__ import annotations

import base64
import logging
from pathlib import Path

from prompt_media_workflow.config import get_openai_api_key

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore[assignment]


LOGGER = logging.getLogger(__name__)


class OpenAIImageGenerator:
    def __init__(self, model: str = "gpt-image-1.5") -> None:
        self.model = model
        api_key = get_openai_api_key()
        self._client = OpenAI(api_key=api_key) if OpenAI and api_key else None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def generate(
        self,
        *,
        prompt: str,
        candidate_count: int,
        width: int,
        height: int,
        output_paths: list[Path] | None = None,
        quality: str | None = None,
        background: str | None = None,
        output_format: str | None = "png",
    ) -> list[Path]:
        if not self._client:
            raise RuntimeError("OpenAI client unavailable for image generation")

        size = f"{width}x{height}"
        kwargs: dict[str, str] = {}
        if quality:
            kwargs["quality"] = quality
        if background:
            kwargs["background"] = background
        # Images API returns base64 JSON by default; leave response_format unset for compatibility.

        LOGGER.debug("Requesting %s image(s) via OpenAI model=%s size=%s", candidate_count, self.model, size)
        response = self._client.images.generate(
            model=self.model,
            prompt=prompt,
            n=candidate_count,
            size=size,
            **kwargs,
        )

        paths: list[Path] = []
        for index, item in enumerate(response.data):
            image_base64 = item.b64_json
            if not image_base64:
                continue
            image_bytes = base64.b64decode(image_base64)
            filename = (
                output_paths[index] if output_paths and index < len(output_paths) else Path.cwd() / f"candidate_{index + 1}.{output_format or 'png'}"
            )
            filename.parent.mkdir(parents=True, exist_ok=True)
            filename.write_bytes(image_bytes)
            paths.append(filename)
        return paths
