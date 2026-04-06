# Internal Implementation Config

## Purpose

This document defines the internal implementation layer for the prompt-media workflow.

It exists to support code organization and runtime control inside the project while keeping the product architecture aligned with OpenAI-style patterns:

- `Responses API` for orchestration
- Structured Outputs for typed reasoning results
- function tools for side effects
- application-managed workflow state

This means internal concepts like `skills` and `sub-agents` are allowed, but they are implementation details, not the primary public architecture.

See also:

- [`project-skills.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/project-skills.md)
- [`project-agents.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/project-agents.md)

## Layering Rule

The system should be understood in three layers:

### 1. Product Architecture

This is the external design described in:

- [`README.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/README.md)
- [`spec.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/spec.md)
- [`schemas.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/schemas.md)
- [`tool-contracts.md`](/Users/supanut.tan/projects/supanut9/prompt-media-workflow/tool-contracts.md)

This layer should use OpenAI-standard language:

- capabilities
- workflow roles
- tool contracts
- structured outputs

### 2. Internal Runtime Architecture

This is where `skills` and `sub-agents` may be used.

- `skills` package reusable stage logic
- `sub-agents` isolate selected specialized roles
- the orchestrator manages routing and state

### 3. Infrastructure Layer

This includes:

- local image backend
- storage
- artifact handling
- environment configuration

## Internal Terms

### Skill

A skill is an internal package for implementing one capability.

A skill may contain:

- prompt instructions
- schema bindings
- parsing helpers
- stage-specific policies
- local evaluation helpers

A skill is not the public product contract.

### Sub-Agent

A sub-agent is an internal execution unit for a specific reasoning role.

A sub-agent may have:

- specialized instructions
- limited tool access
- stage-specific context
- dedicated evaluation logic

A sub-agent is not required for every role.

## Recommended V1 Internal Mapping

Map public capabilities to internal structures like this:

| Public capability | Internal skill | Sub-agent needed in v1 |
| --- | --- | --- |
| `prompt_analysis` | `skills/prompt_analysis` | no |
| `clarification` | `skills/clarification` | no |
| `brief_building` | `skills/brief_building` | no |
| `shot_planning` | `skills/shot_planning` | optional |
| `prompt_building` | `skills/prompt_building` | no |
| `image_generation` | `skills/image_generation` | no |
| `candidate_critique` | `skills/candidate_critique` | optional |
| `refinement_planning` | `skills/refinement_planning` | no |
| `export` | `skills/export` | no |

Default rule:

- use skills for most stage implementations
- use sub-agents only where isolation creates clear value

## Recommended V1 Config Model

The internal config should define:

- enabled capabilities
- skill bindings
- sub-agent enablement
- model selection per stage
- tool availability per stage
- backend selection
- evaluation settings

## Example Internal Config

```json
{
  "orchestrator": {
    "provider": "openai",
    "api_mode": "responses",
    "model": "gpt-5",
    "use_structured_outputs": true
  },
  "capabilities": {
    "prompt_analysis": {
      "enabled": true,
      "skill": "prompt_analysis",
      "subagent": false,
      "model": "gpt-5-mini"
    },
    "clarification": {
      "enabled": true,
      "skill": "clarification",
      "subagent": false,
      "model": "gpt-5-mini",
      "max_questions_per_turn": 3,
      "max_turns": 2
    },
    "brief_building": {
      "enabled": true,
      "skill": "brief_building",
      "subagent": false,
      "model": "gpt-5"
    },
    "shot_planning": {
      "enabled": true,
      "skill": "shot_planning",
      "subagent": false,
      "model": "gpt-5"
    },
    "candidate_critique": {
      "enabled": true,
      "skill": "candidate_critique",
      "subagent": false,
      "model": "gpt-5"
    }
  },
  "tools": {
    "generate_image_candidates": true,
    "save_workflow_record": true,
    "save_brief": true,
    "load_candidate": true,
    "save_critic_result": true,
    "export_final_asset": true
  },
  "rendering": {
    "backend": "comfyui",
    "model": "sdxl",
    "candidate_count": 4,
    "width": 1024,
    "height": 1024
  },
  "evaluation": {
    "enable_failure_tags": true,
    "store_run_artifacts": true
  }
}
```

## Suggested Directory Layout

```text
src/
  orchestrator/
    runner.py
    routing.py
    config.py
  skills/
    prompt_analysis/
    clarification/
    brief_building/
    shot_planning/
    prompt_building/
    image_generation/
    candidate_critique/
    refinement_planning/
    export/
  subagents/
    critic_agent.py
    shot_planner_agent.py
  tools/
    generate_image_candidates.py
    save_workflow_record.py
    save_brief.py
    load_candidate.py
    save_critic_result.py
    export_final_asset.py
```

## What Goes Inside A Skill

A skill package may include:

- instructions
- schema adapters
- prompt templates
- stage defaults
- evaluation fixtures

Example:

```text
skills/
  prompt_analysis/
    instructions.md
    schema.py
    runner.py
    fixtures.json
```

This keeps each capability implementation isolated without redefining the public architecture.

## When To Enable A Sub-Agent

Enable a sub-agent only when at least one of these is true:

- the stage needs different tools than the main flow
- the stage needs distinct instructions that should stay isolated
- the stage benefits from separate caching or context handling
- evaluation shows better quality when the stage is separated

Likely first candidates:

- `candidate_critique`
- `shot_planning`

## What Not To Do

Do not:

- expose internal `skills` as the public architecture language
- replace schemas with loose skill-specific outputs
- let each sub-agent invent its own tool contract
- create sub-agents for every stage by default

The orchestrator, schemas, and tool contracts remain the stable system boundary.

## Configuration Rules

Internal config should:

- reference public capabilities by stable names
- bind each capability to one skill
- explicitly mark whether a sub-agent is enabled
- define model/tool/backend choices centrally
- avoid embedding hidden business logic in config strings

## Recommended Files

Suggested internal config files:

- `config/workflow.json`
- `config/models.json`
- `config/tools.json`

Or one merged file for v1:

- `config/internal.json`

## Decision Standard

Use internal config to control implementation strategy, not to redefine the product.

The public design should remain OpenAI-style.

The internal codebase may use skills and sub-agents underneath that design as long as:

- schemas remain authoritative
- tool contracts remain stable
- orchestration remains centralized
