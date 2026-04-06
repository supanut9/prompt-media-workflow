# Prompt Media Workflow

This folder contains the planning documents for an AI workflow system that turns rough user prompts into stronger image and video generation results through a structured, tool-driven pipeline.

The main problem to solve is not only model quality.

The main problem is that users often start with an underspecified prompt, generate media too early, and then retry randomly without a stable process.

This project aims to replace that with a guided AI pipeline:

1. collect intent
2. detect missing details
3. ask high-value follow-up questions
4. build a structured creative brief
5. generate variants
6. evaluate outputs
7. refine only the best branch
8. generate final image or video assets

## Product Goal

Build a system that can:

- accept a rough user prompt for image or video generation
- decide whether the prompt is already usable or needs clarification
- ask targeted follow-up questions in a limited "plan mode"
- convert answers into structured generation specs
- generate images first when video quality depends on visual anchors
- create multiple candidates instead of one-shot outputs
- critique outputs against the brief
- retry with controlled refinements instead of random rewrites

## AI Architecture Direction

The system should be designed as an agentic AI workflow, not a chain of ad hoc prompt calls.

Recommended foundation:

- OpenAI `Responses API` for orchestration
- Structured Outputs for typed JSON between workflow stages
- function tools for generator, storage, retrieval, and export actions
- image generation through either:
  - OpenAI hosted `image_generation` tool
  - a local backend behind the same generator interface

This keeps the workflow aligned with current OpenAI guidance for tool-using, stateful, multimodal systems.

## Core Design Principle

The system should treat prompt-to-media generation as a staged AI production workflow, not as one API call.

The best default pipeline is:

`raw prompt -> prompt analysis -> clarification loop -> creative brief -> shot plan -> reference images -> selection -> refinement -> video generation -> post-process`

## User Problem Statement

Current failure pattern:

- user enters a short prompt
- generator guesses too much
- output misses the intended style, framing, mood, or identity
- user retries with another vague prompt
- quality does not converge

Target behavior:

- the system should identify which missing details matter
- it should ask only a small number of useful questions
- it should keep a stable spec for retries
- it should explain what changed between iterations

## System Roles

The workflow should separate responsibilities into distinct modules exposed as structured AI steps and tools.

### 1. Prompt Analyzer

Purpose:

- inspect the raw prompt
- classify request type
- detect missing or ambiguous details
- estimate whether generation can proceed safely

Outputs:

- medium type: `image` or `video`
- use case: `portrait`, `anime scene`, `product shot`, `short cinematic clip`, and similar
- confidence score
- list of unknowns
- recommendation: `ask`, `generate`, or `reject`

Implementation note:

- should return Structured Output JSON
- should run as a typed reasoning step, not free-form text

### 2. Clarification Agent

Purpose:

- ask a small number of high-impact questions
- behave like a guided plan mode
- stop asking once the brief is good enough

Rules:

- ask at most 3 questions per turn
- ask only about fields that materially affect quality
- prefer defaults when uncertainty is low
- do not ask for information that can be inferred safely

Suggested model role:

- Gemma 3 or another low-cost instruction model

Implementation note:

- should emit typed question objects
- should use a small structured schema rather than open-ended chat formatting

### 3. Creative Director

Purpose:

- convert prompt plus answers into a structured creative brief
- normalize user language into generation-ready specifications
- preserve key constraints between iterations

Outputs:

- creative brief JSON
- generation prompt
- negative prompt or avoid list

Implementation note:

- brief JSON should be produced with Structured Outputs
- prompt fields should be normalized for downstream tool calls

### 4. Shot Planner

Purpose:

- for video requests, split the request into a sequence of shots
- define composition, subject action, camera motion, and constraints per shot

Outputs:

- shot list JSON
- keyframe requirements
- continuity rules

Implementation note:

- should be treated as a typed planning tool for video-intent requests

### 5. Generator

Purpose:

- call image or video generation backends
- produce multiple candidates per stage
- preserve a branch history for refinement

Notes:

- video requests should usually start with one or more still reference images
- identity-sensitive scenes should lock approved character references before motion generation

Implementation note:

- should be exposed as a function tool or backend adapter
- provider-specific details must stay behind the generator interface

### 6. Critic

Purpose:

- score candidates against the structured brief
- detect failure reasons
- propose the smallest useful next change

Outputs:

- scores by criterion
- failure summary
- retry instruction
- recommendation: `accept`, `refine`, or `ask user`

Implementation note:

- should return a typed score object plus failure tags
- should support evaluation logging and benchmark reuse

## Suggested v1 Workflow

### Image Path

1. user enters prompt
2. analyzer checks prompt completeness
3. clarification agent asks follow-up questions if needed
4. creative director builds a brief
5. generator creates 4 to 8 image variants
6. critic scores variants
7. user or system selects one branch
8. refinement prompt improves only the selected branch
9. final image is exported

### Video Path

1. user enters prompt
2. analyzer checks prompt completeness
3. clarification agent asks follow-up questions if needed
4. creative director builds a brief
5. shot planner creates a shot list
6. generator creates keyframes, character references, or environment references
7. critic selects the strongest visual anchor
8. video generator uses the approved stills plus motion instructions
9. critic reviews the result for drift, continuity, and prompt match
10. final video is exported after optional post-processing

## Why Image-First Matters For Video

Pure prompt-to-video often fails because the model has too many variables to invent at once.

An image-first pipeline reduces drift in:

- character identity
- outfit consistency
- color palette
- environment design
- framing
- emotional tone

For anime-style work this is especially important because small changes in face design, hair shape, eye style, and clothing can make the output feel like a different character.

## Clarification Loop Design

The clarification loop should behave like an efficient pre-production assistant.

It should ask only when needed.

Examples of good clarification questions:

- Is this for a single image or a short video?
- Do you want a close-up portrait, half-body shot, or full-body scene?
- Should the anime style feel bright and clean, gritty and cinematic, or soft and emotional?
- Should the scene stay in one location or cut between shots?

Examples of bad clarification questions:

- asking about every possible field before any generation happens
- asking for details that do not materially change the result
- repeating already answered questions

Stop conditions:

- the required fields are complete
- prompt confidence crosses a threshold
- the user explicitly asks the system to proceed

## Structured Data Model

The system should use structured JSON objects instead of raw text between modules.

For OpenAI-based implementations:

- use Structured Outputs when the model is returning typed data
- use function tools when the model needs to call generation, storage, or retrieval actions

### Prompt Analysis Schema

```json
{
  "medium": "video",
  "use_case": "anime_cinematic_scene",
  "confidence": 0.58,
  "unknowns": [
    "character age band",
    "shot framing",
    "mood",
    "duration"
  ],
  "next_action": "ask"
}
```

### Creative Brief Schema

```json
{
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
  ]
}
```

### Shot Plan Schema

```json
{
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
  ]
}
```

### Critic Output Schema

```json
{
  "candidate_id": "img-004",
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

## Candidate Management

The system should track branches explicitly.

Each generation step should store:

- prompt version
- parent candidate
- input references
- output asset path or URL
- critic scores
- accept or reject status

This prevents random retries and allows the system to refine the best branch instead of restarting from scratch.

## Recommended Initial Stack

### Orchestration

- Python backend for workflow logic
- OpenAI `Responses API` for tool-using reasoning loops
- simple job queue or background worker
- JSON storage for early prototypes

### Models

- planner and clarifier: Gemma 3 or another low-cost instruction model
- image generator: high-quality image API
- video generator: high-quality video API
- critic: either the planner model or a stronger review model

### UI

- lightweight web app or CLI
- chat-style intake area
- generated brief viewer
- shot plan viewer
- candidate gallery
- refine and approve actions

## OpenAI-Aligned Build Direction

If built on OpenAI first, the workflow should map to the platform like this:

- `Responses API`: top-level orchestration loop
- Structured Outputs: analyzer, clarifier, brief builder, critic outputs
- function tools: local generator call, artifact storage, candidate lookup, export
- `image_generation` tool: optional hosted image path

This project is therefore best understood as an AI workflow system for media generation, not only a prompt-writing project.

## v1 Build Phases

### Phase 0: Planning

Deliverables:

- problem statement
- workflow design
- JSON schemas
- module boundaries
- model routing rules

### Phase 1: Prompt Clarification Prototype

Deliverables:

- prompt analyzer
- clarification loop
- creative brief generator
- CLI or simple web form

Success criteria:

- vague prompts become consistent structured briefs
- the system asks fewer than 3 questions per round

### Phase 2: Image Generation Pipeline

Deliverables:

- image prompt builder
- variant generation
- critic scoring
- branch selection and refinement

Success criteria:

- system produces better results than one-shot prompting on repeated test cases

### Phase 3: Video Pre-Production Pipeline

Deliverables:

- shot planner
- keyframe generation path
- continuity rules

Success criteria:

- video prompts use approved still references rather than raw prompt only

### Phase 4: Video Generation And Review

Deliverables:

- video generation backend
- critic loop for motion and continuity
- export flow

Success criteria:

- reduced drift in identity, framing, and scene continuity

## Immediate Next Documents To Write

The next planning docs should be:

1. `spec.md` for exact module contracts
2. `schemas.md` for request and response JSON definitions
3. `evaluation.md` for scoring rules and benchmark prompts
4. `roadmap.md` for implementation order and milestones

## Immediate Next Build Step

Start with the prompt clarification subsystem first.

That is the leverage point for both image and video quality because it determines whether the rest of the pipeline operates on a stable brief or on a vague user guess.
