from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LOGGER = logging.getLogger(__name__)


class ComfyUIGenerator:
    def __init__(
        self,
        *,
        server_url: str,
        workflow_path: str,
        prompt_field: str = "{{PROMPT}}",
        negative_prompt_field: str = "{{NEGATIVE_PROMPT}}",
        timeout_seconds: int = 60,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.workflow_path = Path(workflow_path)
        self.prompt_field = prompt_field
        self.negative_prompt_field = negative_prompt_field
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return self.workflow_path.exists()

    def generate(
        self,
        *,
        prompt: str,
        negative_prompt: str,
        candidate_count: int,
        output_paths: list[Path],
    ) -> list[Path]:
        if not self.enabled:
            raise RuntimeError(f"ComfyUI workflow not found at {self.workflow_path}")

        graph_template = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        prepared_graph = self._inject_prompts(graph_template, prompt, negative_prompt)
        prompt_id = self._queue_prompt(prepared_graph)
        images = self._wait_for_images(prompt_id, candidate_count)

        saved_paths: list[Path] = []
        for index, image in enumerate(images):
            file_path = output_paths[index] if index < len(output_paths) else output_paths[-1]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            image_bytes = self._fetch_image(image["filename"], image["subfolder"], image["type"])
            file_path.write_bytes(image_bytes)
            saved_paths.append(file_path)
        return saved_paths

    def _inject_prompts(self, graph: dict[str, Any], prompt: str, negative_prompt: str) -> dict[str, Any]:
        for node in graph.values():
            inputs = node.get("inputs")
            if not isinstance(inputs, dict):
                continue
            for key, value in inputs.items():
                if isinstance(value, str):
                    if self.prompt_field in value:
                        inputs[key] = value.replace(self.prompt_field, prompt)
                    if self.negative_prompt_field in value:
                        inputs[key] = value.replace(self.negative_prompt_field, negative_prompt)
        return graph

    def _queue_prompt(self, graph: dict[str, Any]) -> str:
        payload = json.dumps({"prompt": graph}).encode("utf-8")
        request = Request(
            f"{self.server_url}/prompt",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("prompt_id")

    def _wait_for_images(self, prompt_id: str, candidate_count: int) -> list[dict[str, str]]:
        deadline = time.time() + self.timeout_seconds
        while time.time() < deadline:
            request = Request(f"{self.server_url}/history/{prompt_id}")
            with urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            history = payload.get(prompt_id)
            if not history:
                time.sleep(1)
                continue
            outputs = history.get("outputs") or {}
            images: list[dict[str, str]] = []
            for node_output in outputs.values():
                for image in node_output.get("images", []):
                    images.append(image)
            if len(images) >= candidate_count:
                return images[:candidate_count]
            time.sleep(1)
        raise TimeoutError("Timed out waiting for ComfyUI images")

    def _fetch_image(self, filename: str, subfolder: str, filetype: str) -> bytes:
        params = urlencode({"filename": filename, "subfolder": subfolder, "type": filetype})
        request = Request(f"{self.server_url}/view?{params}")
        with urlopen(request, timeout=5) as response:
            return response.read()
