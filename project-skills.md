# Project Skills

## Purpose

This document defines `skills` as an internal implementation concept used by this project.

These skills do not replace the OpenAI-style architecture described elsewhere in the repo. They exist to organize code, prompts, schemas, and stage logic inside the implementation.

## Relationship To The Main Architecture

The primary product architecture remains:

- `Responses API` orchestration
- Structured Outputs
- function tools
- centralized workflow state

Within that architecture, a `skill` is the internal package that implements one workflow capability.

## Definition

A project skill is a reusable implementation unit with:

- one main responsibility
- a typed input/output contract
- stage-specific instructions or logic
- clear evaluation criteria

## Recommended V1 Skills

- `prompt_analysis`
- `clarification`
- `brief_building`
- `shot_planning`
- `prompt_building`
- `image_generation`
- `candidate_critique`
- `refinement_planning`
- `export`

## Mapping

| Capability | Internal skill |
| --- | --- |
| `prompt_analysis` | `prompt_analysis` |
| `clarification` | `clarification` |
| `brief_building` | `brief_building` |
| `shot_planning` | `shot_planning` |
| `prompt_building` | `prompt_building` |
| `image_generation` | `image_generation` |
| `candidate_critique` | `candidate_critique` |
| `refinement_planning` | `refinement_planning` |
| `export` | `export` |

## Suggested Skill Layout

```text
src/skills/
  prompt_analysis/
    instructions.md
    schema.py
    runner.py
  clarification/
    instructions.md
    schema.py
    runner.py
  brief_building/
  shot_planning/
  prompt_building/
  image_generation/
  candidate_critique/
  refinement_planning/
  export/
```

## Rules

- one skill should map to one capability
- skills should not define their own conflicting schemas
- skills should use the shared tool contracts
- skills should stay narrow and testable

## What A Skill Is Not

A skill is not:

- the public API contract
- a free-form assistant personality
- a replacement for the orchestrator
- a replacement for tool contracts

## Decision Standard

For this project, `skills` are allowed and recommended as an internal code-organization layer under the main OpenAI-aligned design.
