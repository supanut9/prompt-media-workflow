# Prompt Media Workflow Schemas

## Purpose

This document defines the v1 JSON schemas and validation rules for the prompt-media workflow.

These schemas are derived from `spec.md` and are intended to support:

- module-to-module contracts
- storage validation
- test fixtures
- future API design

This document is intentionally pragmatic. It is not a full JSON Schema spec file, but it defines the exact fields, types, required properties, and enum values needed for v1 implementation.

These schemas are intended to map cleanly to:

- OpenAI Structured Outputs for model-returned typed data
- function tool inputs and outputs for application actions

## Conventions

### Primitive Types

- `string`
- `number`
- `integer`
- `boolean`
- `object`
- `array`
- `null`

### ID Format

All ids are strings.

Recommended prefixes:

- `workflow_id`: `wf_<id>`
- `brief_id`: `brief_<id>`
- `shot_plan_id`: `shotplan_<id>`
- `candidate_id`: `img_<id>` or `vid_<id>`
- `event_id`: `evt_<id>`

### Timestamp Format

All timestamps should use ISO 8601 UTC strings.

Example:

```json
"2026-04-06T00:00:00Z"
```

### File References

Artifact locations should be stored as relative paths or canonical URIs inside the system.

Example:

```json
"artifacts/wf_001/img_001.png"
```

### OpenAI Usage Guidance

- use Structured Outputs for analyzer, clarifier, brief, shot plan, critic, and refiner objects
- use function tools for generator requests, storage writes, retrieval calls, and export actions
- prefer flat schemas where possible to improve tool reliability

## Global Enums

### Medium

```json
["image", "video"]
```

### Workflow Status

```json
[
  "draft",
  "clarifying",
  "ready",
  "generating",
  "reviewing",
  "accepted",
  "rejected",
  "exported"
]
```

### Candidate Status

```json
[
  "generated",
  "scored",
  "selected",
  "rejected",
  "refining",
  "accepted"
]
```

### Decision Type

```json
["ask", "generate", "reject", "refine", "accept", "ask_user"]
```

### Generation Stage

```json
["initial", "reference", "refinement", "video_render"]
```

### Backend Type

```json
["comfyui", "diffusers", "openai", "replicate", "custom"]
```

## 1. Intake Request

Purpose:

- create a workflow from a raw user prompt

Schema:

```json
{
  "type": "object",
  "required": ["raw_prompt"],
  "properties": {
    "raw_prompt": { "type": "string", "min_length": 1 },
    "user_medium_hint": { "type": ["string", "null"], "enum": ["image", "video", null] },
    "user_id": { "type": ["string", "null"] },
    "session_id": { "type": ["string", "null"] }
  }
}
```

Validation rules:

- `raw_prompt` must be non-empty after trimming
- `user_medium_hint` is optional

## 2. Workflow Record

Purpose:

- top-level state for a user request

Schema:

```json
{
  "type": "object",
  "required": [
    "workflow_id",
    "created_at",
    "updated_at",
    "status",
    "raw_prompt",
    "current_prompt_version",
    "clarification_turns"
  ],
  "properties": {
    "workflow_id": { "type": "string" },
    "created_at": { "type": "string" },
    "updated_at": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["draft", "clarifying", "ready", "generating", "reviewing", "accepted", "rejected", "exported"]
    },
    "medium": { "type": ["string", "null"], "enum": ["image", "video", null] },
    "raw_prompt": { "type": "string" },
    "current_prompt_version": { "type": "integer", "minimum": 1 },
    "current_brief_id": { "type": ["string", "null"] },
    "active_candidate_id": { "type": ["string", "null"] },
    "clarification_turns": { "type": "integer", "minimum": 0 },
    "user_id": { "type": ["string", "null"] },
    "session_id": { "type": ["string", "null"] }
  }
}
```

Validation rules:

- `medium` may be null before analysis completes
- `active_candidate_id` may remain null until selection happens

## 3. Prompt Analysis Result

Purpose:

- classify the prompt and decide next action

Schema:

```json
{
  "type": "object",
  "required": [
    "workflow_id",
    "medium",
    "use_case",
    "confidence",
    "unknowns",
    "inferred_defaults",
    "next_action",
    "rejection_reason"
  ],
  "properties": {
    "workflow_id": { "type": "string" },
    "medium": { "type": "string", "enum": ["image", "video"] },
    "use_case": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "unknowns": {
      "type": "array",
      "items": { "type": "string" }
    },
    "inferred_defaults": {
      "type": "object",
      "additional_properties": true
    },
    "next_action": {
      "type": "string",
      "enum": ["ask", "generate", "reject"]
    },
    "rejection_reason": {
      "type": ["string", "null"]
    }
  }
}
```

Validation rules:

- `unknowns` should contain only materially relevant fields
- `rejection_reason` must be non-null when `next_action = "reject"`
- `rejection_reason` should be null otherwise

## 4. Clarification Question

Schema:

```json
{
  "type": "object",
  "required": ["field", "question"],
  "properties": {
    "field": { "type": "string" },
    "question": { "type": "string", "min_length": 1 }
  }
}
```

## 5. Clarification Turn

Purpose:

- store one clarification round

Schema:

```json
{
  "type": "object",
  "required": ["workflow_id", "turn_index", "questions", "answers", "created_at"],
  "properties": {
    "workflow_id": { "type": "string" },
    "turn_index": { "type": "integer", "minimum": 1 },
    "questions": {
      "type": "array",
      "min_items": 1,
      "max_items": 3,
      "items": {
        "type": "object",
        "required": ["field", "question"],
        "properties": {
          "field": { "type": "string" },
          "question": { "type": "string" }
        }
      }
    },
    "answers": {
      "type": "object",
      "additional_properties": { "type": "string" }
    },
    "created_at": { "type": "string" }
  }
}
```

Validation rules:

- no more than 3 questions per turn
- question `field` values should map to known brief fields
- answers may be incomplete if the user skips a field

## 6. Creative Brief

Purpose:

- canonical structured prompt representation

Schema:

```json
{
  "type": "object",
  "required": [
    "brief_id",
    "workflow_id",
    "goal",
    "medium",
    "subject",
    "setting",
    "style",
    "camera",
    "mood",
    "constraints",
    "generation_prompt",
    "negative_prompt"
  ],
  "properties": {
    "brief_id": { "type": "string" },
    "workflow_id": { "type": "string" },
    "goal": { "type": "string" },
    "medium": { "type": "string", "enum": ["image", "video"] },
    "subject": {
      "type": "object",
      "required": ["type", "description"],
      "properties": {
        "type": { "type": "string" },
        "description": { "type": "string" },
        "age_band": { "type": ["string", "null"] },
        "identity_lock": { "type": ["boolean", "null"] },
        "reference_ids": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "setting": {
      "type": "object",
      "properties": {
        "location": { "type": ["string", "null"] },
        "era": { "type": ["string", "null"] },
        "world_style": { "type": ["string", "null"] },
        "background_detail": { "type": ["string", "null"] }
      }
    },
    "style": {
      "type": "object",
      "properties": {
        "visual_style": { "type": ["string", "null"] },
        "palette": {
          "type": "array",
          "items": { "type": "string" }
        },
        "lighting": { "type": ["string", "null"] },
        "render_finish": { "type": ["string", "null"] }
      }
    },
    "camera": {
      "type": "object",
      "properties": {
        "framing": { "type": ["string", "null"] },
        "angle": { "type": ["string", "null"] },
        "motion": { "type": ["string", "null"] }
      }
    },
    "mood": { "type": ["string", "null"] },
    "constraints": {
      "type": "array",
      "items": { "type": "string" }
    },
    "generation_prompt": { "type": "string" },
    "negative_prompt": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

Validation rules:

- `identity_lock` should be true for continuity-sensitive video requests when identity matters
- `negative_prompt` is stored as an array for easier editing and auditability
- `generation_prompt` must reflect the brief but does not need to be deterministic across providers

## 7. Shot Plan

Purpose:

- video-only planning object

Schema:

```json
{
  "type": "object",
  "required": [
    "shot_plan_id",
    "workflow_id",
    "brief_id",
    "duration_seconds",
    "shots",
    "keyframe_requirements"
  ],
  "properties": {
    "shot_plan_id": { "type": "string" },
    "workflow_id": { "type": "string" },
    "brief_id": { "type": "string" },
    "duration_seconds": { "type": "number", "minimum": 1 },
    "shots": {
      "type": "array",
      "min_items": 1,
      "items": {
        "type": "object",
        "required": [
          "shot_id",
          "duration_seconds",
          "purpose",
          "composition",
          "subject_action",
          "camera_motion",
          "continuity_rules"
        ],
        "properties": {
          "shot_id": { "type": "string" },
          "duration_seconds": { "type": "number", "minimum": 0.5 },
          "purpose": { "type": "string" },
          "composition": { "type": "string" },
          "subject_action": { "type": "string" },
          "camera_motion": { "type": "string" },
          "environment_motion": { "type": ["string", "null"] },
          "continuity_rules": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "keyframe_requirements": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

Validation rules:

- `shots` should sum approximately to `duration_seconds`
- single-shot plans are valid
- `shot_plan` must not exist for `image` workflows

## 8. Generator Request

Purpose:

- normalized request to any rendering backend

Recommended usage:

- function tool input

Schema:

```json
{
  "type": "object",
  "required": [
    "workflow_id",
    "brief_id",
    "candidate_count",
    "width",
    "height"
  ],
  "properties": {
    "workflow_id": { "type": "string" },
    "brief_id": { "type": "string" },
    "shot_plan_id": { "type": ["string", "null"] },
    "prompt": { "type": ["string", "null"] },
    "negative_prompt": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "candidate_count": { "type": "integer", "minimum": 1, "maximum": 8 },
    "width": { "type": "integer", "minimum": 256 },
    "height": { "type": "integer", "minimum": 256 },
    "references": {
      "type": "array",
      "items": { "type": "string" }
    },
    "seed": { "type": ["integer", "null"] },
    "backend": {
      "type": ["string", "null"],
      "enum": ["comfyui", "diffusers", "openai", "replicate", "custom", null]
    },
    "model": { "type": ["string", "null"] }
  }
}
```

Validation rules:

- `candidate_count` should default to `4`
- `references` may be empty
- `shot_plan_id` is required for video render stages

## 9. Candidate Record

Purpose:

- one generated media artifact and its lineage

Recommended usage:

- function tool output and persisted storage object

Schema:

```json
{
  "type": "object",
  "required": [
    "candidate_id",
    "workflow_id",
    "medium",
    "brief_id",
    "parent_candidate_id",
    "prompt_version",
    "generation_stage",
    "input_references",
    "asset_uri",
    "status"
  ],
  "properties": {
    "candidate_id": { "type": "string" },
    "workflow_id": { "type": "string" },
    "medium": { "type": "string", "enum": ["image", "video"] },
    "brief_id": { "type": "string" },
    "shot_plan_id": { "type": ["string", "null"] },
    "parent_candidate_id": { "type": ["string", "null"] },
    "prompt_version": { "type": "integer", "minimum": 1 },
    "generation_stage": {
      "type": "string",
      "enum": ["initial", "reference", "refinement", "video_render"]
    },
    "input_references": {
      "type": "array",
      "items": { "type": "string" }
    },
    "asset_uri": { "type": "string" },
    "thumbnail_uri": { "type": ["string", "null"] },
    "seed": { "type": ["integer", "null"] },
    "backend": {
      "type": ["string", "null"],
      "enum": ["comfyui", "diffusers", "openai", "replicate", "custom", null]
    },
    "model": { "type": ["string", "null"] },
    "critic_score": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
    "status": {
      "type": "string",
      "enum": ["generated", "scored", "selected", "rejected", "refining", "accepted"]
    }
  }
}
```

Validation rules:

- root candidates must use `parent_candidate_id = null`
- refinement candidates must have a non-null `parent_candidate_id`
- `asset_uri` must exist before status can move past `generated`

## 10. Critic Result

Purpose:

- evaluation output for one candidate

Recommended usage:

- Structured Output result from the critic stage

Schema:

```json
{
  "type": "object",
  "required": [
    "candidate_id",
    "brief_id",
    "scores",
    "failures",
    "recommendation",
    "refinement_instruction"
  ],
  "properties": {
    "candidate_id": { "type": "string" },
    "brief_id": { "type": "string" },
    "scores": {
      "type": "object",
      "required": ["prompt_match", "style_match"],
      "properties": {
        "prompt_match": { "type": "number", "minimum": 0, "maximum": 10 },
        "style_match": { "type": "number", "minimum": 0, "maximum": 10 },
        "composition": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
        "subject_quality": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
        "motion_quality": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
        "continuity": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
        "identity_consistency": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
        "artifact_penalty": { "type": ["number", "null"], "minimum": 0, "maximum": 10 }
      }
    },
    "failures": {
      "type": "array",
      "items": { "type": "string" }
    },
    "recommendation": {
      "type": "string",
      "enum": ["accept", "refine", "ask_user", "reject"]
    },
    "refinement_instruction": { "type": ["string", "null"] }
  }
}
```

Validation rules:

- `refinement_instruction` should be non-null when recommendation is `refine`
- `refinement_instruction` should usually be null when recommendation is `accept`
- `artifact_penalty` should be interpreted as worse when higher

## 11. Refiner Output

Purpose:

- minimal delta to improve a selected candidate

Recommended usage:

- Structured Output result from the refiner stage

Schema:

```json
{
  "type": "object",
  "required": [
    "parent_candidate_id",
    "refinement_prompt_delta",
    "preserve_constraints"
  ],
  "properties": {
    "parent_candidate_id": { "type": "string" },
    "refinement_prompt_delta": { "type": "string" },
    "preserve_constraints": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

Validation rules:

- `preserve_constraints` must include all locked identity and continuity constraints
- `refinement_prompt_delta` must not be empty

## 12. Export Record

Purpose:

- track final asset approval and export

Schema:

```json
{
  "type": "object",
  "required": [
    "workflow_id",
    "candidate_id",
    "exported_at",
    "export_uri"
  ],
  "properties": {
    "workflow_id": { "type": "string" },
    "candidate_id": { "type": "string" },
    "exported_at": { "type": "string" },
    "export_uri": { "type": "string" },
    "format": { "type": ["string", "null"] },
    "notes": { "type": ["string", "null"] }
  }
}
```

Validation rules:

- export is only valid for accepted candidates

## 13. Error Object

Purpose:

- standard error payload across modules

Schema:

```json
{
  "type": "object",
  "required": ["error_code", "message", "retryable", "stage"],
  "properties": {
    "error_code": { "type": "string" },
    "message": { "type": "string" },
    "retryable": { "type": "boolean" },
    "stage": { "type": "string" }
  }
}
```

Suggested error codes:

- `UNSUPPORTED_MEDIUM`
- `INVALID_PROMPT`
- `UNSAFE_REQUEST`
- `SCHEMA_VALIDATION_ERROR`
- `GENERATOR_BACKEND_FAILURE`
- `CRITIC_UNAVAILABLE`
- `MISSING_REFERENCE_ASSET`

## 14. Event Record

Purpose:

- observability and audit trail

Schema:

```json
{
  "type": "object",
  "required": [
    "event_id",
    "workflow_id",
    "stage",
    "timestamp",
    "status",
    "latency_ms"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "workflow_id": { "type": "string" },
    "stage": { "type": "string" },
    "timestamp": { "type": "string" },
    "input_ref": { "type": ["string", "null"] },
    "output_ref": { "type": ["string", "null"] },
    "status": { "type": "string" },
    "latency_ms": { "type": "integer", "minimum": 0 },
    "metadata": {
      "type": "object",
      "additional_properties": true
    }
  }
}
```

## Cross-Schema Rules

These rules are not captured by single objects alone and must be enforced by workflow logic.

### Medium Consistency

- `workflow.medium`, `analysis.medium`, `brief.medium`, and `candidate.medium` must agree

### Shot Plan Presence

- `shot_plan` must exist for video rendering stages
- `shot_plan` must not exist for ordinary image-only runs

### Candidate Lineage

- a refinement candidate must reference a parent candidate from the same workflow
- parent and child candidates must share the same `brief_id` unless the workflow explicitly increments prompt version and brief revision

### Status Transitions

Valid workflow transitions:

- `draft -> clarifying`
- `draft -> ready`
- `clarifying -> ready`
- `ready -> generating`
- `generating -> reviewing`
- `reviewing -> accepted`
- `reviewing -> rejected`
- `accepted -> exported`

Valid candidate transitions:

- `generated -> scored`
- `scored -> selected`
- `scored -> rejected`
- `selected -> refining`
- `selected -> accepted`

### Clarification Limits

- no more than 2 clarification turns in v1 by default
- no more than 3 questions per turn

### Candidate Count

- image generation should default to 4 candidates
- v1 maximum candidate count per generation request is 8

### Tool Contract Guidance

- prefer one tool per meaningful application action
- avoid exposing provider-specific generator params directly to the reasoning model unless needed
- do not require the model to fill values the application already knows

## Example Minimal Image Workflow

```json
{
  "workflow": {
    "workflow_id": "wf_001",
    "created_at": "2026-04-06T00:00:00Z",
    "updated_at": "2026-04-06T00:00:00Z",
    "status": "ready",
    "medium": "image",
    "raw_prompt": "heroic anime battle scene in a ruined throne room",
    "current_prompt_version": 1,
    "current_brief_id": "brief_001",
    "active_candidate_id": null,
    "clarification_turns": 1
  },
  "brief": {
    "brief_id": "brief_001",
    "workflow_id": "wf_001",
    "goal": "single anime battle illustration",
    "medium": "image",
    "subject": {
      "type": "human",
      "description": "young pirate hero confronting a shadow ruler",
      "age_band": "young adult",
      "identity_lock": false,
      "reference_ids": []
    },
    "setting": {
      "location": "ruined royal throne chamber",
      "era": "fantasy modern",
      "world_style": "grand ceremonial palace",
      "background_detail": "broken marble, torn banners, floating dust"
    },
    "style": {
      "visual_style": "cinematic anime",
      "palette": ["red", "gold", "black"],
      "lighting": "dramatic backlight",
      "render_finish": "high detail illustration"
    },
    "camera": {
      "framing": "wide shot",
      "angle": "low angle",
      "motion": null
    },
    "mood": "high tension",
    "constraints": ["no text", "clear silhouette separation"],
    "generation_prompt": "Cinematic anime battle in a ruined throne chamber...",
    "negative_prompt": ["blurry", "text", "bad anatomy"]
  }
}
```

## Follow-Up

This document should be used next to:

- create actual JSON Schema files if validation is automated
- scaffold Python dataclasses or Pydantic models
- define fixture payloads for tests
