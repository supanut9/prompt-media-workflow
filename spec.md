# Prompt Media Workflow Spec

## Purpose

This document defines the v1 module contracts and runtime behavior for the prompt-to-media workflow described in `README.md`.

The system goal is to turn rough image or video prompts into structured, repeatable generation workflows that converge through clarification, branching, critique, and controlled refinement.

The recommended implementation target is an OpenAI-aligned agentic workflow:

- `Responses API` for orchestration
- Structured Outputs for typed model results
- function tools for backend actions and state transitions

## Scope

v1 covers:

- prompt intake
- prompt analysis
- clarification loop
- creative brief generation
- image generation pipeline
- video pre-production pipeline
- candidate tracking
- critic scoring and refinement routing

v1 does not require:

- advanced post-processing
- multi-user collaboration
- fine-tuned models
- long-term asset management beyond prototype storage

## Design Rules

The workflow must follow these rules:

- use structured JSON payloads between modules
- prefer Structured Outputs over free-form JSON prompting
- keep user-visible clarification lightweight
- ask only for details that materially affect output quality
- preserve stable constraints across retries
- generate multiple candidates before refining
- refine the best branch instead of restarting from scratch
- keep an auditable record of what changed between iterations
- keep tool contracts explicit and small enough for reliable tool calling

## OpenAI API Mapping

The recommended OpenAI mapping for v1 is:

- `Responses API` as the top-level runtime loop
- `text.format` Structured Outputs for typed stage results
- function tools for:
  - `generate_image_candidates`
  - `load_candidate`
  - `save_workflow_record`
  - `save_brief`
  - `save_critic_result`
  - `export_final_asset`

Use Structured Outputs when the model is returning typed stage outputs.

Use function tools when the model must trigger application logic or external services.

## Runtime Stages

The default stage order is:

1. intake
2. prompt analysis
3. clarification if needed
4. creative brief generation
5. shot planning for video only
6. candidate generation
7. critic scoring
8. branch selection
9. refinement or acceptance
10. export

## Shared Concepts

### Medium

Allowed values:

- `image`
- `video`

### Request Status

Allowed values:

- `draft`
- `clarifying`
- `ready`
- `generating`
- `reviewing`
- `accepted`
- `rejected`
- `exported`

### Candidate Status

Allowed values:

- `generated`
- `scored`
- `selected`
- `rejected`
- `refining`
- `accepted`

### Decision Types

Allowed values:

- `ask`
- `generate`
- `reject`
- `refine`
- `accept`
- `ask_user`

## Top-Level Workflow Object

Each user request creates a single workflow record.

Required fields:

```json
{
  "workflow_id": "wf_001",
  "created_at": "2026-04-06T00:00:00Z",
  "updated_at": "2026-04-06T00:00:00Z",
  "status": "draft",
  "medium": "video",
  "raw_prompt": "anime swordswoman in a rainy neon alley",
  "current_prompt_version": 1,
  "current_brief_id": null,
  "active_candidate_id": null,
  "clarification_turns": 0
}
```

## Module Contracts

### 1. Intake

Purpose:

- accept the raw user prompt
- create the initial workflow record
- normalize minimal metadata

Input:

```json
{
  "raw_prompt": "anime swordswoman in a rainy neon alley",
  "user_medium_hint": "video"
}
```

Output:

```json
{
  "workflow_id": "wf_001",
  "status": "draft",
  "raw_prompt": "anime swordswoman in a rainy neon alley",
  "medium_hint": "video"
}
```

Behavior:

- if the user explicitly states `image` or `video`, treat that as a strong hint
- if no medium is stated, the analyzer must infer one
- empty or unsafe prompts may be rejected before later stages

OpenAI usage:

- may be ordinary application code before invoking the model

### 2. Prompt Analyzer

Purpose:

- inspect the initial prompt and latest clarifying answers
- classify the request
- estimate readiness for generation
- identify unknowns that materially affect quality

Input:

```json
{
  "workflow_id": "wf_001",
  "raw_prompt": "anime swordswoman in a rainy neon alley",
  "user_answers": [],
  "medium_hint": "video"
}
```

Output:

```json
{
  "medium": "video",
  "use_case": "anime_cinematic_scene",
  "confidence": 0.58,
  "unknowns": [
    "shot_framing",
    "mood",
    "duration"
  ],
  "inferred_defaults": {
    "setting.location": "rainy neon alley"
  },
  "next_action": "ask",
  "rejection_reason": null
}
```

Decision rules:

- return `ask` when high-impact fields are missing and confidence is below threshold
- return `generate` when required fields are complete or safe defaults exist
- return `reject` when the request is empty, disallowed, or too ambiguous to recover with short clarification

OpenAI usage:

- model call with Structured Output schema
- do not parse free-form prose to recover fields

Initial thresholds:

- `generate` when confidence is `>= 0.75`
- `ask` when confidence is `< 0.75` and fewer than 3 high-impact unknowns can improve quality
- `reject` when the prompt cannot be made actionable within the clarification policy

Required high-impact fields by medium:

For `image`:

- subject
- framing
- style
- setting or background intent

For `video`:

- subject
- framing
- style
- setting
- duration band
- motion intent

### 3. Clarification Agent

Purpose:

- ask a small number of targeted follow-up questions
- resolve only the missing details with high quality impact
- stop once the brief is good enough

Input:

```json
{
  "workflow_id": "wf_001",
  "analysis": {
    "medium": "video",
    "unknowns": [
      "shot_framing",
      "mood",
      "duration"
    ],
    "next_action": "ask"
  }
}
```

Output:

```json
{
  "questions": [
    {
      "field": "shot_framing",
      "question": "Do you want a close-up, medium shot, or full-body shot?"
    },
    {
      "field": "mood",
      "question": "Should the scene feel tense and dramatic, soft and emotional, or bright and energetic?"
    },
    {
      "field": "duration",
      "question": "Should this be a very short clip around 5 seconds, or closer to 8 to 10 seconds?"
    }
  ],
  "stop_after_answer": false
}
```

Policy:

- ask at most 3 questions per turn
- questions must map to concrete fields
- avoid asking about fields with safe defaults
- avoid repeating answered questions unless the answer conflicts with earlier constraints
- stop asking when the analyzer would return `generate`

Stop conditions:

- required fields are sufficiently complete
- analyzer confidence reaches threshold
- clarification turns reach configured max
- user explicitly says to proceed

Initial limits:

- maximum clarification turns: `2`
- maximum questions per turn: `3`

OpenAI usage:

- return typed question objects via Structured Outputs
- keep the schema flat where possible for reliability

### 4. Creative Director

Purpose:

- convert prompt and answers into a stable creative brief
- normalize user language into generator-ready fields
- preserve constraints across iterations

Input:

```json
{
  "workflow_id": "wf_001",
  "raw_prompt": "anime swordswoman in a rainy neon alley",
  "answers": {
    "shot_framing": "medium shot",
    "mood": "tense and dramatic",
    "duration": "8 seconds"
  },
  "analysis": {
    "medium": "video",
    "use_case": "anime_cinematic_scene"
  }
}
```

Output:

```json
{
  "brief_id": "brief_001",
  "goal": "8-second anime-style cinematic clip",
  "medium": "video",
  "subject": {
    "type": "human",
    "description": "female swordswoman",
    "age_band": "adult",
    "identity_lock": true
  },
  "setting": {
    "location": "rainy neon alley",
    "era": "modern",
    "world_style": "Tokyo-inspired"
  },
  "style": {
    "visual_style": "cinematic anime",
    "palette": ["teal", "red", "neon reflections"],
    "lighting": "night rain with glowing signage"
  },
  "camera": {
    "framing": "medium shot",
    "motion": "slow push-in"
  },
  "mood": "tense and dramatic",
  "constraints": [
    "no text",
    "preserve same outfit",
    "single scene"
  ],
  "generation_prompt": "Cinematic anime swordswoman standing in a rainy neon alley at night...",
  "negative_prompt": [
    "text overlays",
    "extra characters",
    "outfit changes"
  ]
}
```

Behavior:

- normalize vague user language into controlled schema values where possible
- preserve user-stated constraints verbatim when important
- infer low-risk defaults without asking unnecessary questions
- create both structured brief fields and generator-facing prompts

OpenAI usage:

- return the brief as Structured Output
- prompt text can be included as typed fields inside the brief object

### 5. Shot Planner

Purpose:

- convert video briefs into shot-level generation instructions
- define motion and continuity rules before video generation

Input:

```json
{
  "brief_id": "brief_001",
  "medium": "video"
}
```

Output:

```json
{
  "shot_plan_id": "shotplan_001",
  "video_id": "draft-001",
  "duration_seconds": 8,
  "shots": [
    {
      "shot_id": "s1",
      "duration_seconds": 8,
      "purpose": "hero reveal",
      "composition": "medium shot",
      "subject_action": "character stands still with subtle breathing",
      "camera_motion": "slow push-in",
      "environment_motion": "light rain and sign flicker",
      "continuity_rules": [
        "same face",
        "same outfit",
        "same alley background"
      ]
    }
  ],
  "keyframe_requirements": [
    "front-facing hero frame",
    "approved character identity reference"
  ]
}
```

Behavior:

- only runs for `video`
- should prefer a single-shot plan when user intent does not require cuts
- must include continuity rules that can be checked later by the critic

OpenAI usage:

- return structured shot plan JSON with explicit continuity arrays

### 6. Generator

Purpose:

- create media candidates from the brief or shot plan
- preserve parent-child relationships for later refinement

Input:

For image generation:

```json
{
  "workflow_id": "wf_001",
  "brief_id": "brief_001",
  "candidate_count": 4,
  "references": []
}
```

For video generation:

```json
{
  "workflow_id": "wf_001",
  "brief_id": "brief_001",
  "shot_plan_id": "shotplan_001",
  "reference_candidate_ids": ["img_004"]
}
```

Output:

```json
{
  "generated_candidates": [
    {
      "candidate_id": "img_001",
      "parent_candidate_id": null,
      "medium": "image",
      "asset_uri": "artifacts/img_001.png",
      "prompt_version": 1,
      "status": "generated"
    }
  ]
}
```

Rules:

- generate 4 to 8 image candidates by default
- for video requests, prefer generating still references before motion output
- refinement generations must reference a selected parent candidate
- generator implementation must be backend-agnostic behind a provider interface

OpenAI usage:

- this stage should be exposed as an application function tool
- if using OpenAI hosted image generation, the tool implementation may internally call the `image_generation` tool or Images API
- if using local rendering, the same tool interface should call the local backend

### 7. Critic

Purpose:

- score each candidate against the brief
- identify failures
- recommend accept, refine, or ask user

Input:

```json
{
  "candidate_id": "img_004",
  "brief_id": "brief_001",
  "shot_plan_id": null
}
```

Output:

```json
{
  "candidate_id": "img_004",
  "scores": {
    "prompt_match": 8.5,
    "style_match": 9.0,
    "composition": 7.0,
    "identity_consistency": 8.0
  },
  "failures": [
    "camera is wider than requested",
    "facial expression is too neutral"
  ],
  "recommendation": "refine",
  "refinement_instruction": "Keep the composition and outfit. Tighten to a medium close-up and increase dramatic facial tension."
}
```

Scoring criteria:

For `image`:

- prompt match
- style match
- composition
- subject quality
- artifact penalty

For `video`:

- prompt match
- style match
- continuity
- motion quality
- identity consistency
- artifact penalty

Routing rules:

- `accept` when total weighted score is above acceptance threshold and there are no critical failures
- `refine` when one or two focused changes are likely to improve the result
- `ask_user` when multiple candidates are viable or preference tradeoffs are subjective

Initial thresholds:

- auto-accept threshold: `8.8 / 10`
- refine threshold: `7.0 - 8.79 / 10`
- below `7.0`, reject branch unless user explicitly wants alternatives

OpenAI usage:

- critic output should be structured and typed
- failure tags should be logged for evaluation reuse

### 8. Refiner

Purpose:

- produce the smallest prompt or control change needed to improve a selected branch

Input:

```json
{
  "candidate_id": "img_004",
  "brief_id": "brief_001",
  "critic_output": {
    "recommendation": "refine",
    "refinement_instruction": "Keep the composition and outfit. Tighten to a medium close-up and increase dramatic facial tension."
  }
}
```

Output:

```json
{
  "parent_candidate_id": "img_004",
  "refinement_prompt_delta": "Tighten from medium shot to medium close-up. Increase dramatic facial tension. Keep outfit, setting, and palette unchanged.",
  "preserve_constraints": [
    "same outfit",
    "same character identity",
    "same neon alley background"
  ]
}
```

Rules:

- refinement must preserve all locked constraints
- refinement should change as little as possible
- the system must never silently replace the parent branch with a full rewrite

OpenAI usage:

- should return only prompt delta and preserve constraints, not a full replacement brief by default

## Candidate Graph

Candidates form a directed tree per workflow.

Required fields:

```json
{
  "candidate_id": "img_004",
  "workflow_id": "wf_001",
  "parent_candidate_id": "img_002",
  "brief_id": "brief_001",
  "shot_plan_id": null,
  "prompt_version": 2,
  "generation_stage": "refinement",
  "input_references": ["img_002"],
  "asset_uri": "artifacts/img_004.png",
  "critic_score": 8.4,
  "status": "selected"
}
```

Constraints:

- each candidate has at most one parent
- root candidates have `parent_candidate_id = null`
- selected candidates may produce children through refinement only
- rejected branches must remain stored for evaluation and traceability

## Required Storage Objects

v1 storage may use JSON files, but the system must persist these logical records:

- workflow
- prompt analysis result
- clarification history
- creative brief
- shot plan
- candidate record
- critic result
- export record

Recommended prototype layout:

- `data/workflows/<workflow_id>.json`
- `data/briefs/<brief_id>.json`
- `data/shot_plans/<shot_plan_id>.json`
- `data/candidates/<candidate_id>.json`
- `artifacts/<workflow_id>/...`

## Clarification Field Priority

When the analyzer decides to ask questions, fields should be ranked by expected quality impact.

Suggested priority order:

For `image`:

1. subject identity or type
2. framing
3. style
4. setting
5. mood

For `video`:

1. subject identity or type
2. framing
3. motion intent
4. duration
5. continuity-critical constraints
6. style
7. setting
8. mood

## Defaults Policy

Safe defaults are allowed only when they are low-risk and easy to override later.

Allowed default examples:

- age band: `adult` when the prompt clearly describes an adult-coded subject
- clip duration: `5-8 seconds` for short cinematic clips
- camera motion: `static` or `slow push-in` for simple hero shots

Unsafe defaults that should usually trigger clarification:

- brand-specific art direction
- character identity details that affect likeness
- framing when composition is central to the request
- scene transitions for video

## Human-In-The-Loop Rules

The system may proceed automatically until one of these conditions happens:

- clarification max is reached and uncertainty remains high
- critic returns `ask_user`
- multiple candidates are strong but differ in taste rather than correctness
- the user requests manual selection before refinement

User approval is required before:

- locking identity references for downstream video generation
- exporting the final asset

## Error Handling

The system must produce structured errors for these conditions:

- unsupported medium
- unsafe or disallowed request
- generator backend failure
- critic unavailable
- missing reference asset
- invalid schema payload

Error shape:

```json
{
  "error_code": "GENERATOR_BACKEND_FAILURE",
  "message": "Image provider returned a timeout",
  "retryable": true,
  "stage": "generator"
}
```

## Observability

Every stage should emit a structured event with:

- `workflow_id`
- `stage`
- `timestamp`
- `input_ref`
- `output_ref`
- `status`
- `latency_ms`

This is required for debugging and later evaluation.

This also supports OpenAI-recommended evaluation patterns for workflow-specific image systems.

## v1 Acceptance Criteria

The system is considered functionally complete for v1 when it can:

- convert vague prompts into structured briefs with at most 2 clarification turns
- keep clarification to at most 3 questions per turn
- generate multiple image candidates from one brief
- score and rank candidates against explicit criteria
- refine only the chosen branch while preserving locked constraints
- generate video requests through an image-first or reference-first path
- persist workflow state and candidate history for replay

## Open Questions

These decisions are intentionally left open for follow-up documents:

- exact schema enums and validation rules
- provider-specific generation parameters
- weighting formulas for critic scores
- moderation and policy handling details
- whether v1 storage remains file-based or moves to a database early
