# Project Agents

## Purpose

This document defines `agents` as an internal implementation concept used by this project.

These agents are internal runtime units. They do not replace the OpenAI-style product architecture, which still centers on one orchestrator, Structured Outputs, and function tools.

## Relationship To The Main Architecture

The main architecture remains:

- one workflow orchestrator
- typed reasoning stages
- function tools for side effects
- shared schemas and tool contracts

Inside that architecture, an internal `agent` is an optional specialized runtime for one reasoning role.

## Definition

A project agent is a bounded execution unit that has:

- a narrow role
- limited context
- limited tool access
- stage-specific instructions

An agent should only exist when isolating that stage improves reliability or maintainability.

## Recommended V1 Agent Model

V1 should use:

- one main orchestrator
- mostly in-process typed stages
- optional internal sub-agents only for selected stages

Default v1 position:

- do not create separate agents for every stage

## Candidate V1 Agents

Likely internal agent candidates:

- `CriticAgent`
- `ShotPlannerAgent`

Possible later additions:

- `ReferenceSelectorAgent`
- `StyleCriticAgent`
- `ContinuityCriticAgent`

## Suggested Layout

```text
src/subagents/
  critic_agent.py
  shot_planner_agent.py
```

## Rules

- agents must use shared schemas
- agents must use shared tool contracts
- agents should receive minimal context
- agents should not introduce new public architecture terms

## When To Use An Agent

Use an internal agent when:

- a stage needs isolated instructions
- a stage needs a distinct tool subset
- a stage benefits from separate context handling
- evaluation shows measurable benefit from separation

## When Not To Use An Agent

Do not create an internal agent when:

- the stage is just a simple typed transformation
- the stage has no special tool or context needs
- the role can be handled cleanly by the main orchestrator

## Decision Standard

For this project, `agents` are allowed as an internal implementation detail, but the shipped system should still be described primarily in terms of workflow roles, capabilities, and tool contracts.
