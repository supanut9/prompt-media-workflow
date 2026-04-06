# Tool Contracts

## Purpose

This document defines the application tools that the orchestrator may call.

This is the OpenAI-style layer that sits between typed reasoning outputs and real side effects such as generation, persistence, loading, and export.

## Design Principles

Tool contracts should follow these rules:

- one tool should perform one clear application action
- names and parameters should be explicit
- schemas should be flat where possible
- tools should not require the model to provide values the application already knows
- the number of initially available tools should stay small

These principles align with OpenAI’s function-calling guidance.

## Recommended V1 Tool Set

The v1 orchestrator should start with a small set of tools:

- `generate_image_candidates`
- `save_workflow_record`
- `save_brief`
- `load_candidate`
- `save_critic_result`
- `export_final_asset`

Additional tools should only be added when a real workflow need appears.

## Tool Definitions

### `generate_image_candidates`

Purpose:

- invoke the configured image backend and return generated candidate records

Input:

- workflow id
- brief id
- candidate count
- width
- height
- optional references
- optional backend selection

Output:

- generated candidates with ids, artifact paths, and backend metadata

Notes:

- backend-specific details should stay inside the adapter
- this tool may call a local backend or hosted image service internally

### `save_workflow_record`

Purpose:

- persist workflow state updates

Input:

- workflow object

Output:

- save confirmation or saved record reference

### `save_brief`

Purpose:

- persist the current creative brief

Input:

- brief object

Output:

- brief reference

### `load_candidate`

Purpose:

- retrieve a candidate and its metadata for critique or refinement

Input:

- candidate id

Output:

- candidate record
- artifact reference

### `save_critic_result`

Purpose:

- persist candidate evaluation results

Input:

- critic result object

Output:

- saved result reference

### `export_final_asset`

Purpose:

- create the final export record for an accepted candidate

Input:

- workflow id
- candidate id
- export format

Output:

- export record

## Tool Availability By Stage

Not every stage should see every tool.

Recommended exposure:

- analyzer: no side-effect tools
- clarifier: no side-effect tools
- brief builder: optionally save tools only if orchestration requires inline persistence
- generator stage: `generate_image_candidates`
- critic stage: `load_candidate`, optionally `save_critic_result`
- export stage: `export_final_asset`

This reduces ambiguity and improves reliability.

## What Not To Expose As Tools

Avoid these patterns:

- one giant tool that does multiple unrelated actions
- overlapping tools with unclear differences
- tools that exist only to pass through obvious application state
- tools that force the model to select low-level backend settings unnecessarily

## Relationship To Schemas

Recommended split:

- model-returned typed reasoning objects belong in [`schemas.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/schemas.md)
- side-effecting application actions belong in this document

This keeps reasoning contracts separate from tool contracts.

## Relationship To Capabilities

- capabilities describe what the product can do
- workflow roles describe which reasoning stage is responsible
- tool contracts describe how the orchestrator triggers application actions

These three layers should stay distinct.

## Implementation Guidance

In code, these tools should map to narrow functions or methods with clear parameter types.

Good implementation pattern:

- validation at the tool boundary
- backend-specific logic hidden behind adapters
- deterministic persistence behavior
- minimal application state passed into the model

## Decision Guidance

If a step only transforms data into another typed object, it probably should not be a tool.

If a step causes side effects or external calls, it probably should be a tool.
