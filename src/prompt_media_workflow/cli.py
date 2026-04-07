from __future__ import annotations

import argparse
import json

from prompt_media_workflow.config import load_dotenv
from prompt_media_workflow.models import IntakeRequest
from prompt_media_workflow.orchestrator.runner import WorkflowRunner


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Prompt media workflow prototype")
    parser.add_argument("prompt", help="Raw user prompt")
    parser.add_argument("--medium", choices=["image", "video"], default=None)
    args = parser.parse_args()

    request = IntakeRequest(raw_prompt=args.prompt, user_medium_hint=args.medium)
    runner = WorkflowRunner()
    result = runner.run_text_pipeline(request)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
