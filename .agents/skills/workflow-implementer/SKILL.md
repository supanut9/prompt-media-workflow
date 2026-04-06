---
name: "workflow-implementer"
description: "Implements the prompt-media workflow from the repo planning docs in the correct order: typed models first, orchestrator next, then stage modules and tool adapters, while preserving the contracts in spec.md, schemas.md, workflow-roles.md, and tool-contracts.md."
---

# Workflow Implementer

Use this skill when implementing the prompt-media workflow codebase from the planning documents in this repository.

## Goal

Turn the repository docs into working code without drifting from the documented architecture.

This skill is for implementation work, not for redefining the architecture.

## Source Of Truth

Read and follow these files in this order:

1. `AGENTS.md`
2. `schemas.md`
3. `tool-contracts.md`
4. `spec.md`
5. `workflow-roles.md`
6. `roadmap.md`
7. `config/internal.json`
8. `.codex/config.toml`

If there is a conflict, prefer the earlier file in the list.

## Implementation Priorities

Implement in this order unless the user explicitly asks for something else:

1. typed models and schema bindings
2. orchestrator and stage routing
3. prompt analysis stage
4. clarification stage
5. brief building stage
6. generator tool adapter
7. candidate critique stage
8. refinement stage
9. video-specific planning stages

## Required Constraints

- Do not invent new schema fields unless the user asks for a schema change.
- Do not invent new tool contracts unless the user asks for a contract change.
- Keep names aligned with `schemas.md`, `tool-contracts.md`, and `workflow-roles.md`.
- Keep side effects behind tool or adapter boundaries.
- Keep stage outputs typed and machine-validated where possible.
- Prefer small, composable modules over broad framework abstractions.

## Expected Code Layout

Prefer a structure like:

```text
src/
  orchestrator/
  models/
  stages/
  tools/
  generators/
  storage/
  agents/
```

Use the repo’s actual layout if it already exists.

## Stage Mapping

Map workflow roles to code modules like this:

- `Prompt Analyzer` -> `stages/prompt_analysis.py`
- `Clarifier` -> `stages/clarification.py`
- `Creative Director` -> `stages/brief_building.py`
- `Shot Planner` -> `stages/shot_planning.py`
- `Critic` -> `stages/candidate_critique.py`
- `Refiner` -> `stages/refinement.py`

Map tool contracts like this:

- `generate_image_candidates` -> `tools/generate_image_candidates.py`
- `save_workflow_record` -> `tools/save_workflow_record.py`
- `save_brief` -> `tools/save_brief.py`
- `load_candidate` -> `tools/load_candidate.py`
- `save_critic_result` -> `tools/save_critic_result.py`
- `export_final_asset` -> `tools/export_final_asset.py`

## Codex Agent Alignment

The repo may define Codex agent roles in `.codex/config.toml`.

When those roles exist:

- keep implementation compatible with those role names
- do not create conflicting role names in code
- treat those roles as execution helpers, not replacements for the documented workflow contracts

## Working Style

When using this skill:

- scaffold first
- validate naming second
- implement one stage or tool at a time
- keep diffs small and reviewable
- add minimal tests when practical

## Done Criteria

A task is done only when:

- the implemented code matches the repo contracts
- file and symbol names are consistent with the docs
- tool boundaries remain explicit
- any new config is wired into the repo structure cleanly
