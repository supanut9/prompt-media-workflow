from __future__ import annotations


def generate_image_candidates(*, workflow_id: str, brief_id: str, candidate_count: int = 4) -> dict:
    """Stub tool adapter for later backend integration."""
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

