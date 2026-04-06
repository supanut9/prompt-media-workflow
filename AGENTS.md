# AGENTS.md

## Purpose

This is the primary Codex instruction file for the repository.

It is intended to follow the Codex documentation pattern: repository guidance belongs in `AGENTS.md`, with optional project-scoped Codex configuration in `.codex/config.toml`.

## Architecture Split

There are two layers in this repo:

### 1. Product Architecture

Use the OpenAI-style documents as the source of truth for the shipped system:

- `README.md`
- `spec.md`
- `schemas.md`
- `capabilities.md`
- `workflow-roles.md`
- `tool-contracts.md`

These define:

- Responses API orchestration
- Structured Outputs
- function tools
- workflow state

### 2. Internal Implementation Architecture

Use Codex-style internal conventions for implementation:

- `AGENTS.md` for repo instructions
- optional `.codex/config.toml` for project-scoped Codex config
- optional named agent roles through `.codex/agents/*.toml`
- repo-local runtime config in `config/internal.json`

These are implementation details and must not replace the product contracts above.

## Implementation Rules

- Keep schemas in `schemas.md` authoritative.
- Keep tool boundaries in `tool-contracts.md` authoritative.
- Treat workflow roles as the public reasoning model.
- Use internal implementation modules only where they help delivery.
- Use named sub-agents only where isolation clearly helps.
- Do not let internal agent configs invent conflicting contracts.
- When adding implementation roles, map them back to the public capability, role, and schema.

## Expected Code Layout

When implementation begins, prefer a layout like:

```text
src/
  orchestrator/
  skills/
  subagents/
  tools/
  storage/
config/
  internal.json
```

## Internal Terms

### Sub-Agent

A Codex-configured specialized runtime for one workflow role.

### Tool

A callable application action matching `tool-contracts.md`.

### Required Mapping

Each implementation role should explicitly state:

- mapped public capability
- mapped public role
- mapped public schema
- allowed tools

## Priority Order

When there is ambiguity, use this order:

1. `schemas.md`
2. `tool-contracts.md`
3. `spec.md`
4. `workflow-roles.md`
5. `.codex` project configuration

## Initial Implementation Focus

Build in this order:

1. typed schemas/models
2. orchestrator
3. prompt analysis stage
4. clarification stage
5. brief building stage
6. generator tool adapter
7. critic
8. refinement

## Notes For Codex

- This repo intentionally supports Codex-oriented implementation.
- `AGENTS.md` is the main Codex-discovered instruction file.
- `.codex/config.toml` defines project-scoped Codex agent configuration.
- Public docs should continue to use OpenAI-style architecture language.
