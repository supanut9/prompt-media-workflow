# Workflow Roles

## Purpose

This document defines the reasoning roles used by the workflow.

These roles are conceptual workflow stages, not necessarily separate deployed agents. This framing is closer to OpenAI’s documented tool-and-orchestration patterns than treating every stage as an autonomous agent.

## Recommended V1 Runtime

Use one primary orchestrator built on the OpenAI `Responses API`.

That orchestrator should:

- maintain workflow state
- invoke typed reasoning stages
- call function tools when side effects are needed
- persist outputs and artifacts

In v1, most roles should be implemented as structured stages within one orchestrated workflow.

## Role Definitions

### Prompt Analyzer

Purpose:

- determine medium, use case, unknowns, and next action

Typical output:

- prompt analysis object

### Clarifier

Purpose:

- ask a small number of targeted questions when confidence is low

Typical output:

- clarification questions

### Creative Director

Purpose:

- translate user intent into a stable creative brief

Typical output:

- brief object
- prompt fields

### Shot Planner

Purpose:

- create a shot plan for video requests

Typical output:

- shot plan object

### Critic

Purpose:

- score outputs and identify the smallest useful next step

Typical output:

- critic result

### Refiner

Purpose:

- define a small prompt delta for the selected branch

Typical output:

- refiner output

## Role Boundaries

Each role should receive only the context required for that stage.

Recommended boundaries:

- `Prompt Analyzer`: raw prompt, medium hint, prior clarification summary
- `Clarifier`: analyzer output, unanswered fields, prior answers
- `Creative Director`: prompt, answers, analysis, locked constraints
- `Shot Planner`: brief plus video-specific constraints
- `Critic`: candidate metadata, artifact reference, brief, optional shot plan
- `Refiner`: critic output, selected candidate, preserved constraints

The model should not receive unnecessary backend details.

## Role Implementation Guidance

For v1:

- use Structured Outputs for typed role results
- keep schemas small and explicit
- keep tool access limited
- do not treat every role as a separate autonomous runtime

This design is easier to debug, evaluate, and evolve.

## When To Split A Role Into A Separate Agent

Promote a role into a more independent runtime only when:

- it needs a distinct tool set
- it needs substantially different instructions
- it benefits from persistent specialized context
- evals show measurable quality gains from isolation

Examples of later specialization:

- dedicated video continuity planner
- dedicated style critic
- dedicated reference selector

## What To Avoid

Avoid:

- a swarm of loosely defined agents
- overlapping role responsibilities
- unrestricted tool access for all roles
- free-form role outputs when a schema is possible

## Decision Standard

For this repo, the default is:

- one orchestrator
- several typed reasoning roles
- a small tool surface
- application code for routing and persistence

That is the correct v1 balance between modularity and reliability.
