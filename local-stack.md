# Codex Plus Local Image Backend

## Purpose

This document defines the recommended v1 architecture for running the prompt-media workflow with OpenAI-style agentic orchestration for text reasoning and a local image backend for image generation.

The goal is to keep early development low-cost, modular, and aligned with the staged workflow in `README.md` and `spec.md`.

## Why This Stack

This stack separates reasoning from rendering.

- A Responses API reasoning loop handles prompt understanding, clarification, structured brief creation, scoring, and refinement logic.
- A local image backend handles the actual image synthesis.

This is the right v1 tradeoff because:

- it avoids per-image API cost during prototyping
- it preserves the workflow design described in the repo
- it keeps the generator backend replaceable later
- it lets the product focus on better process, not training a model from scratch

## System Boundary

### Reasoning Layer Responsibilities

The reasoning layer should be used for:

- prompt analysis
- missing-detail detection
- clarification question generation
- structured creative brief generation
- prompt and negative prompt construction
- candidate critique
- refinement instruction generation

Implementation recommendation:

- use OpenAI `Responses API`
- use Structured Outputs for typed stage results
- use function tools for application actions

The reasoning layer should not be treated as the image renderer.

### Local Backend Responsibilities

The local backend should be used for:

- text-to-image generation
- image-to-image refinement when needed
- multi-candidate batch generation
- saving output files
- returning artifact paths and generation metadata

The local backend should not own the workflow logic.

## Recommended v1 Architecture

```text
User Prompt
  -> Prompt Analyzer (Responses API)
  -> Clarification Agent (Responses API, if needed)
  -> Creative Brief Builder (Responses API)
  -> Prompt Builder (Responses API)
  -> Image Generator Adapter
  -> Local Backend (ComfyUI / Diffusers)
  -> Candidate Artifacts
  -> Critic (Responses API)
  -> Refiner (Responses API)
  -> Local Backend Again
```

Recommended tool mapping:

- Structured Outputs:
  - analyzer result
  - clarification questions
  - creative brief
  - critic result
  - refiner output
- function tools:
  - `generate_image_candidates`
  - `save_workflow_record`
  - `save_brief`
  - `load_candidate`
  - `save_critic_result`
  - `export_final_asset`

## Preferred Backend Options

### Option A: ComfyUI

Recommended default for v1.

Why:

- strong ecosystem
- easy node-based experimentation
- can be called from a local API
- supports SDXL and Flux workflows
- good fit for image-first experimentation

Use ComfyUI when:

- fast iteration matters
- visual workflow control matters
- the team may experiment with different generation graphs

### Option B: Diffusers

Recommended if you want a more code-centric stack.

Why:

- pure Python integration
- easier to version alongside the app
- more direct control in code

Use Diffusers when:

- you want fewer external moving parts
- you prefer backend behavior defined in Python rather than workflow JSON

## Recommended Model Path

Start with:

- `SDXL` for the easiest practical local baseline

Upgrade later if needed to:

- `Flux` for stronger image quality if hardware supports it

Do not block v1 on finding the perfect model. The product leverage comes from the workflow quality first.

## v1 Module Mapping

### Prompt Analyzer

Input:

- raw prompt
- optional user medium hint
- clarification history

Output:

- medium
- use case
- confidence
- unknowns
- next action

Runtime owner:

- Responses API structured reasoning step

### Clarification Agent

Input:

- analyzer output
- prior answers

Output:

- up to 3 targeted questions

Runtime owner:

- Responses API structured reasoning step

### Creative Brief Builder

Input:

- raw prompt
- user answers
- analyzer result

Output:

- structured brief JSON
- normalized constraints

Runtime owner:

- Responses API structured reasoning step

### Prompt Builder

Input:

- structured brief

Output:

- positive prompt
- negative prompt
- optional prompt variants

Runtime owner:

- Responses API structured reasoning step

### Image Generator Adapter

Input:

- prompts
- candidate count
- image size
- seed or variation settings
- optional references

Output:

- candidate records
- local file paths
- backend metadata

Runtime owner:

- local Python service

### Critic

Input:

- candidate artifact paths
- structured brief

Output:

- scores
- failures
- recommendation
- refinement instruction

Runtime owner:

- Responses API structured reasoning step

## Proposed Folder Layout

```text
prompt-media-workflow/
  README.md
  spec.md
  local-stack.md
  schemas.md
  src/
    analyzer.py
    clarifier.py
    brief_builder.py
    prompt_builder.py
    critic.py
    refiner.py
    workflow_runner.py
    generators/
      base.py
      comfyui.py
      diffusers.py
  data/
    workflows/
    briefs/
    candidates/
  artifacts/
```

## Generator Interface

The workflow should depend on an abstract generator interface, not on ComfyUI directly.

Example:

```python
class ImageGenerator:
    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        candidate_count: int = 4,
        width: int = 1024,
        height: int = 1024,
        references: list[str] | None = None,
    ) -> list[dict]:
        raise NotImplementedError
```

This matters because:

- the workflow stays stable if the backend changes
- local generation can be swapped for an API later
- tests can mock the generator cleanly
- the reasoning model only needs one generator tool contract

## Candidate Generation Strategy

For v1 image requests:

- generate 4 candidates by default
- use prompt variants only when they are intentional, not random rewrites
- keep seeds and prompt deltas for traceability
- score all candidates before any refinement

Refinement rules:

- refine only one selected branch at a time
- preserve locked constraints
- change as little as possible between iterations

## Local Backend Contract

The adapter should return a normalized payload regardless of backend.

Example:

```json
{
  "generated_candidates": [
    {
      "candidate_id": "img_001",
      "asset_uri": "artifacts/wf_001/img_001.png",
      "seed": 12345,
      "backend": "comfyui",
      "model": "sdxl",
      "status": "generated"
    }
  ]
}
```

## Initial Configuration

Recommended defaults:

- backend: `comfyui`
- model: `sdxl`
- candidate count: `4`
- output size: `1024x1024`
- clarification max turns: `2`
- questions per turn: `3`

These defaults are good enough for a first end-to-end prototype.

## Risks

### Hardware Constraints

Local image generation quality and speed depend heavily on GPU capability.

Mitigation:

- start with SDXL
- keep image size fixed initially
- avoid large batch counts on weak hardware

### Prompt Overfitting

The reasoning model may over-specify prompts and reduce creative flexibility.

Mitigation:

- keep the structured brief compact
- use refinement deltas instead of full rewrites
- store prompt history for review

### Backend Lock-In

Calling ComfyUI directly from workflow code can create tight coupling.

Mitigation:

- use an adapter interface
- keep provider-specific payload building inside generator modules only

## Immediate Build Order

1. finalize `schemas.md` from `spec.md`
2. create Responses API stage wrappers and structured schemas in code
3. create generator interface and local backend adapter
4. create analyzer, clarifier, and brief builder modules
5. add a CLI for prompt intake and candidate review
6. add critic and refinement loop

## Decision

The recommended v1 implementation is:

- Responses API for all text reasoning and workflow decisions
- ComfyUI plus SDXL as the first local image generation backend
- backend abstraction from day one so the renderer can be replaced later
