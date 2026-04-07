from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from prompt_media_workflow.config import get_openai_api_key

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional at runtime until dependency install
    OpenAI = None  # type: ignore[assignment]


ModelT = TypeVar("ModelT", bound=BaseModel)


class OpenAIReasoningClient:
    def __init__(self, model: str = "gpt-5") -> None:
        self.model = model
        self.api_key = get_openai_api_key()
        self._client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def parse(self, *, instructions: str, user_input: str, text_format: type[ModelT]) -> ModelT:
        if not self._client:
            raise RuntimeError("OpenAI client is not configured")

        response = self._client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_input},
            ],
            text_format=text_format,
        )

        for output in response.output:
            if output.type != "message":
                continue
            for item in output.content:
                refusal = getattr(item, "refusal", None)
                if refusal:
                    raise RuntimeError(f"Model refused request: {refusal}")
                parsed = getattr(item, "parsed", None)
                if parsed is not None:
                    return parsed
        raise RuntimeError("No parsed structured output returned by model")
