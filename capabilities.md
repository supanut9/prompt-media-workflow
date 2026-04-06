# Workflow Capabilities

## Purpose

This document defines the core product capabilities of the prompt-media workflow.

These are product-facing capabilities, not special runtime primitives. In implementation terms, each capability will usually map to one of:

- a Structured Output model call
- a function tool
- ordinary application code

This framing is closer to OpenAI’s documented architecture patterns than using generic terms like `skills`.

## Capability Model

A capability is a bounded workflow function with:

- a clear purpose
- a typed input contract
- a typed output contract
- explicit success criteria
- measurable failure modes

Capabilities should align with the schemas in [`schemas.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/schemas.md) and the runtime contracts in [`spec.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/spec.md).

## Recommended V1 Capabilities

The v1 workflow should expose these capabilities:

- `prompt_analysis`
- `clarification`
- `brief_building`
- `shot_planning`
- `prompt_building`
- `image_generation`
- `candidate_critique`
- `refinement_planning`
- `export`

## Capability Definitions

### `prompt_analysis`

Purpose:

- classify the request
- detect high-impact unknowns
- decide whether to ask, generate, or reject

Typical implementation:

- Structured Output model call

Primary outputs:

- medium
- use case
- confidence
- unknowns
- next action

### `clarification`

Purpose:

- ask a small number of high-value follow-up questions

Typical implementation:

- Structured Output model call

Primary outputs:

- up to 3 question objects

### `brief_building`

Purpose:

- convert prompt and answers into a stable creative brief

Typical implementation:

- Structured Output model call

Primary outputs:

- creative brief JSON
- generation prompt
- negative prompt

### `shot_planning`

Purpose:

- create shot-level structure for video-intent workflows

Typical implementation:

- Structured Output model call

Primary outputs:

- shot list
- keyframe requirements
- continuity rules

### `prompt_building`

Purpose:

- transform the structured brief into backend-ready prompt text

Typical implementation:

- Structured Output model call or deterministic application code

Primary outputs:

- positive prompt
- negative prompt
- optional variant deltas

### `image_generation`

Purpose:

- create image candidates from the brief and prompts

Typical implementation:

- function tool backed by local renderer or hosted image backend

Primary outputs:

- candidate records
- artifact paths
- backend metadata

### `candidate_critique`

Purpose:

- evaluate generated candidates against the brief

Typical implementation:

- Structured Output model call

Primary outputs:

- scores
- failure tags
- recommendation
- refinement instruction

### `refinement_planning`

Purpose:

- produce the smallest useful change for a selected branch

Typical implementation:

- Structured Output model call

Primary outputs:

- prompt delta
- preserve constraints

### `export`

Purpose:

- mark the final asset as approved and exported

Typical implementation:

- function tool or application code

Primary outputs:

- export record

## Capability Mapping

Recommended mapping:

- reasoning-heavy capabilities: Structured Outputs
- side-effect capabilities: function tools
- storage and orchestration: application code

This follows OpenAI’s general distinction between typed model outputs and tool-triggered application actions.

## What Not To Model As A Capability

Do not define standalone capabilities for:

- generic assistant chat
- arbitrary free-form rewriting
- storage plumbing
- provider-specific rendering internals
- repeated glue code between always-sequential steps

Those are either infrastructure or implementation details.

## Evaluation

Each capability should be testable independently.

Examples:

- `prompt_analysis`: classification and unknown-detection quality
- `clarification`: question usefulness and question count
- `brief_building`: schema validity and intent preservation
- `candidate_critique`: ranking quality and failure tagging quality

This keeps failures local and measurable.

## Decision Guidance

Use a capability when:

- the workflow needs a repeated function
- the input and output can be stated clearly
- the result can be evaluated

For v1, capabilities should remain narrow and typed.
