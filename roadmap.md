# Prompt Media Workflow Roadmap

## Purpose

This document defines the recommended implementation roadmap for v1 of the prompt-media workflow.

The roadmap is optimized for:

- fast end-to-end progress
- low infrastructure cost
- measurable checkpoints
- minimal premature complexity

It assumes the current stack direction:

- Responses API for text reasoning and orchestration
- local image backend for rendering
- file-based or simple local storage in early prototypes

## Delivery Strategy

Build the system in the order of highest leverage.

That means:

- first make vague prompts become stable structured briefs
- then make image generation reliable
- then add critique and refinement
- only after that expand into video pre-production and video generation

This order matters because weak prompt understanding will contaminate every downstream stage.

## Guiding Principles

- prefer one working vertical slice over broad partial coverage
- separate reasoning from rendering from day one
- keep interfaces stable even if implementations are simple
- track state and branch history early
- avoid building video infrastructure before image-first workflows are solid
- align early architecture with Structured Outputs and function tools rather than free-form prompting

## Phase 0: Planning And Contracts

Status:

- in progress and mostly complete through current docs

Deliverables:

- `README.md`
- `spec.md`
- `schemas.md`
- `local-stack.md`
- `evaluation.md`
- `roadmap.md`

Exit criteria:

- module boundaries are explicit
- schema shapes are defined
- local stack direction is chosen
- evaluation approach is documented

Risks if skipped:

- implementation drift
- schema churn
- unclear backend boundaries

## Phase 1: Prompt Clarification Prototype

Goal:

- turn rough prompts into stable structured briefs

Why first:

- this is the highest-leverage subsystem in the whole product
- both image and video quality depend on it

Scope:

- prompt intake
- prompt analyzer
- clarification logic
- creative brief builder
- prompt builder
- simple CLI or terminal workflow
- Responses API stage wrappers
- Structured Output schemas in code

Recommended outputs:

- workflow record
- analysis result
- clarification transcript
- final creative brief
- generation prompt and negative prompt

Implementation tasks:

1. scaffold project structure under `src/`
2. create Python models or Pydantic models from `schemas.md`
3. create Responses API wrapper for typed stage execution
4. implement analyzer interface
5. implement clarification policy
6. implement brief builder
7. implement prompt builder
8. create a CLI command to run one prompt through the text pipeline

Success criteria:

- vague prompts are transformed into valid briefs
- clarification is limited to at most 3 questions per turn
- no more than 2 clarification turns by default
- generated briefs pass schema validation consistently

Suggested milestone demo:

- input: `cool anime girl`
- output: analyzer result, clarification questions, finalized brief JSON, final generation prompt

## Phase 2: Local Image Generation Vertical Slice

Goal:

- generate real image candidates from structured briefs using a local backend

Scope:

- generator base interface
- ComfyUI adapter or Diffusers adapter
- artifact saving
- candidate records
- 4-candidate default image generation

Implementation tasks:

1. create `generators/base.py`
2. create `generators/comfyui.py`
3. create normalized generator request and candidate output handling
4. save images to `artifacts/<workflow_id>/`
5. save candidate metadata to `data/candidates/`
6. connect generator stage to workflow runner

Success criteria:

- one validated brief can produce 4 stored image candidates
- outputs are tracked with candidate ids and artifact paths
- backend-specific logic stays confined to generator modules

Suggested milestone demo:

- input: finalized image brief
- output: 4 generated files plus candidate metadata

## Phase 3: Critic And Branch Selection

Goal:

- evaluate candidates and choose the best branch for refinement

Scope:

- critic scoring
- candidate ranking
- failure tagging
- manual or automatic selection

Implementation tasks:

1. implement critic result schema handling
2. define initial scoring weights
3. add failure taxonomy tagging
4. rank generated candidates
5. add basic selection policy:
   - auto-select if one candidate is clearly best
   - ask user if tradeoffs are subjective

Success criteria:

- all generated candidates receive comparable scores
- top candidate selection is reproducible
- workflow stores critic outputs for later analysis

Suggested milestone demo:

- input: 4 candidates
- output: scored list with recommended next action

## Phase 4: Refinement Loop

Goal:

- improve one selected candidate without restarting from scratch

Scope:

- refiner
- child candidate generation
- preserved-constraint handling
- branch history

Implementation tasks:

1. implement refiner output object
2. build refinement prompt delta generation
3. generate one child candidate from selected parent
4. enforce parent-child lineage in storage
5. compare parent and child via critic

Success criteria:

- refinement changes are small and intentional
- locked constraints remain stable
- the child candidate improves targeted weaknesses more often than not

Suggested milestone demo:

- input: selected candidate with critic feedback
- output: refined child candidate and before/after score comparison

## Phase 5: Benchmarking And Regression Harness

Goal:

- make the workflow measurable instead of anecdotal

Scope:

- benchmark prompt set
- baseline direct prompting path
- side-by-side result logging
- repeatable regression cases

Implementation tasks:

1. create benchmark prompt fixtures
2. add baseline generation mode
3. log workflow versus baseline outputs
4. store critic and human-review results
5. define a small recurring regression suite

Success criteria:

- benchmark cases can be replayed
- workflow outputs can be compared to baseline outputs
- regressions can be detected after prompt or policy changes

## Phase 6: Video Pre-Production

Goal:

- support video-intent workflows up to the reference and planning stage

Scope:

- video prompt analysis
- clarification for motion and duration
- shot plan creation
- reference image generation
- continuity rules

Implementation tasks:

1. extend analyzer for video routing
2. implement shot planner
3. define keyframe and continuity requirements
4. generate still references from the shot plan
5. add reference approval step

Success criteria:

- video requests produce valid shot plans
- still references are generated before any motion rendering
- continuity rules are explicit and stored

Suggested milestone demo:

- input: `8-second anime showdown in a rainy alley`
- output: analysis, clarification, brief, shot plan, approved still references

## Phase 7: Video Generation And Review

Goal:

- produce motion output from approved still references and a shot plan

Scope:

- video backend adapter
- video candidate records
- video critic logic
- export path

Implementation tasks:

1. define video generator interface
2. add video candidate schema usage
3. implement video critic scoring dimensions
4. add export record handling
5. add final approval flow

Success criteria:

- video generation uses approved visual anchors
- critic can score continuity and motion quality
- final export path works for accepted candidates

## Recommended Build Order Within The Repo

Create files in this order:

1. `src/models.py` or `src/schemas.py`
2. `src/openai_client.py`
3. `src/analyzer.py`
4. `src/clarifier.py`
5. `src/brief_builder.py`
6. `src/prompt_builder.py`
7. `src/generators/base.py`
8. `src/generators/comfyui.py`
9. `src/workflow_runner.py`
10. `src/critic.py`
11. `src/refiner.py`

This order supports an early vertical slice without waiting for the full final architecture.

## Team And Ownership Suggestion

If split across contributors, ownership should be:

- workflow logic: analyzer, clarifier, brief builder, workflow runner
- generation adapters: backend integration modules
- evaluation: benchmark fixtures, scoring review tools, regression harness
- UI later: prompt intake, brief viewer, candidate gallery

## Risks By Phase

### Early Risk: Overdesign

Failure mode:

- spending too long on docs and abstractions before proving the pipeline

Mitigation:

- move into a CLI vertical slice immediately after docs

### Mid Risk: Backend Coupling

Failure mode:

- workflow logic becomes ComfyUI-specific

Mitigation:

- keep all backend request building inside adapter modules

### Mid Risk: Weak Critic

Failure mode:

- the system chooses bad branches because scoring is noisy

Mitigation:

- keep user selection available
- log failures and compare with human review

### Late Risk: Video Complexity

Failure mode:

- the team starts motion generation before still-reference quality is stable

Mitigation:

- enforce image-first readiness gates for video

## Near-Term Milestones

### Milestone A

Deliver:

- text-only prompt clarification CLI using Responses API structured stages

Definition of done:

- one prompt goes to structured brief successfully

### Milestone B

Deliver:

- first end-to-end local image generation workflow

Definition of done:

- one prompt goes from intake to 4 stored image candidates

### Milestone C

Deliver:

- scored candidates plus one refinement branch

Definition of done:

- the system can improve a chosen candidate with traceable lineage

### Milestone D

Deliver:

- benchmark harness and baseline comparison

Definition of done:

- at least 10 benchmark prompts can run through both baseline and workflow modes

## What Not To Build Yet

Avoid these until the core workflow is proven:

- database-heavy infrastructure
- multi-user auth and collaboration
- advanced frontend application
- fine-tuning a custom image model
- full production video pipeline

These are downstream optimizations, not v1 blockers.

## Immediate Next Step

Start implementing Phase 1 as a CLI-first prototype using the schemas and contracts already defined, with Responses API orchestration and Structured Outputs from the start.

That path gives the fastest proof that the workflow improves prompt quality before any substantial generation infrastructure is built.
