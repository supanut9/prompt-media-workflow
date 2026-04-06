# Prompt Media Workflow Evaluation

## Purpose

This document defines how v1 should be evaluated.

The goal is not to prove that one image model is universally best. The goal is to verify that the workflow produces better, more stable results than direct one-shot prompting on the same backend.

This evaluation design is consistent with OpenAI guidance for image evals: use workflow-specific rubrics, explicit failure gates, structured outputs, and human calibration where needed.

The evaluation framework should answer these questions:

- does clarification improve prompt completeness
- does the structured brief improve generation quality
- does branch-based refinement outperform random prompt retries
- does the image-first process improve video pre-production quality
- does the system reduce drift across iterations

## Evaluation Principle

The system should be measured against a baseline that uses the same rendering backend with no staged workflow.

Baseline:

- raw user prompt sent directly to generator
- no clarification
- no structured brief
- no explicit branch tracking
- optional user retries with manual prompt rewrites

Workflow system:

- prompt analysis
- clarification loop
- structured brief
- multi-candidate generation
- critic scoring
- branch selection
- controlled refinement

This comparison isolates the value of the workflow rather than conflating it with a stronger model.

For OpenAI-based implementations, the evaluator and critic stages should return typed results via Structured Outputs so scoring data is machine-reliable.

## Success Criteria

v1 succeeds if it shows meaningful improvement in:

- prompt match
- style match
- composition accuracy
- identity consistency
- refinement stability
- user effort reduction

Minimum directional goals:

- better average prompt-match scores than the baseline
- fewer user retries to reach an acceptable result
- fewer random full rewrites between attempts
- more consistent candidate selection and refinement behavior

## Evaluation Dimensions

### 1. Prompt Understanding

Questions:

- did the analyzer classify the request correctly
- did it identify the missing fields that actually mattered
- did it choose `ask` versus `generate` appropriately

Metrics:

- medium classification accuracy
- use-case classification accuracy
- unknown-field precision
- unknown-field recall
- next-action accuracy

### 2. Clarification Quality

Questions:

- were the follow-up questions high impact
- did the system avoid unnecessary questions
- did the system stop at the right time

Metrics:

- questions per turn
- clarification turns per workflow
- answer usefulness rate
- unnecessary question rate
- post-clarification confidence lift

### 3. Brief Quality

Questions:

- does the structured brief preserve user intent
- does it introduce useful specificity without hallucinating too much

Metrics:

- brief completeness score
- intent preservation score
- contradiction count
- schema validity rate

### 4. Image Generation Quality

Questions:

- are generated candidates better aligned with the intended prompt
- does multi-candidate generation help surface better options

Metrics:

- top-1 prompt-match score
- top-3 average score
- style-match score
- composition score
- artifact rate

### 5. Refinement Quality

Questions:

- does refining the best branch improve quality
- are preserved constraints actually preserved

Metrics:

- refinement gain over parent
- identity preservation rate
- constraint preservation rate
- full-rewrite rate

### 6. Video Pre-Production Quality

Questions:

- do shot plans improve the quality of video preparation
- do approved still references reduce drift later

Metrics:

- shot-plan completeness score
- continuity-rule coverage
- reference approval usefulness score
- visual-anchor consistency score

## Evaluation Modes

### Offline Evaluation

Use fixed prompts and score outputs after the fact.

Use this for:

- benchmark comparisons
- regression testing
- tuning analyzer and clarification policies

### Human Review Evaluation

Use human raters to compare outputs.

Use this for:

- taste-sensitive judgments
- subjective prompt adherence
- side-by-side baseline comparisons

### Workflow Analytics

Use system logs and stored workflow state.

Use this for:

- retry counts
- branch counts
- question counts
- acceptance rates

## Benchmark Prompt Set

The benchmark set should cover multiple prompt types and difficulty levels.

### Category A: Simple, Well-Specified Image Prompts

Purpose:

- verify that the system does not over-clarify already-usable prompts

Examples:

- product photo of a silver wristwatch on black reflective stone, studio lighting, luxury ad style
- anime portrait of a calm blue-haired mage, close-up, soft moonlight, painterly style
- cinematic still of a red sports car drifting on a wet city street at night

Expected behavior:

- analyzer often returns `generate`
- minimal or no clarification

### Category B: Vague Image Prompts

Purpose:

- measure the value of clarification and brief generation

Examples:

- cool anime girl
- dramatic battle scene
- make a beautiful fantasy landscape

Expected behavior:

- analyzer returns `ask`
- clarification resolves framing, style, mood, or subject gaps

### Category C: Identity-Sensitive Image Prompts

Purpose:

- test character consistency and refinement preservation

Examples:

- young pirate hero confronting a shadow ruler in a ruined throne room
- cyberpunk detective woman in a neon alley, same outfit across iterations
- fantasy queen in ceremonial armor, preserve face and crown design

Expected behavior:

- the workflow preserves important visual identity traits across refinements

### Category D: Video-Like Requests Needing Image-First Planning

Purpose:

- test whether the system correctly routes visual anchoring before motion generation

Examples:

- 8-second anime showdown in a rainy alley
- short cinematic clip of a swordsman turning toward camera in a burning palace
- emotional close-up of a singer on stage with slow push-in camera motion

Expected behavior:

- analyzer chooses `video`
- clarification covers duration, motion, and continuity needs
- still references are generated before any motion stage

## Test Case Structure

Each benchmark test case should store:

```json
{
  "case_id": "img_vague_001",
  "category": "vague_image",
  "raw_prompt": "dramatic battle scene",
  "expected_medium": "image",
  "expected_unknowns": ["subject", "framing", "style"],
  "requires_clarification": true,
  "notes": "Should ask about composition and art direction before generation."
}
```

## Core Metrics

### Quantitative Metrics

- analyzer accuracy
- clarification question count
- clarification turn count
- brief schema pass rate
- candidate generation success rate
- top-1 critic score
- top-3 critic score average
- acceptance rate
- retries to acceptable output
- refinement delta success rate

### Qualitative Metrics

- prompt fidelity
- style fidelity
- composition correctness
- emotional tone match
- continuity consistency
- user preference satisfaction

## Scoring Rubric

Use a 0 to 10 scale for each scored category.

### Prompt Match

- `9-10`: strongly matches subject, setting, and requested action
- `7-8`: mostly matches but misses one important detail
- `5-6`: partially matches but key constraints are weak or incorrect
- `0-4`: major mismatch

### Style Match

- `9-10`: visual style clearly matches the requested direction
- `7-8`: generally correct style with small drift
- `5-6`: mixed or weak style adherence
- `0-4`: wrong style

### Composition

- `9-10`: framing and scene arrangement match the request closely
- `7-8`: mostly correct with minor framing drift
- `5-6`: composition is usable but noticeably off
- `0-4`: framing is wrong or confusing

### Identity Consistency

- `9-10`: face, outfit, and character cues remain stable
- `7-8`: mostly stable with minor drift
- `5-6`: obvious drift but still recognizable
- `0-4`: identity effectively changes

### Motion Quality

For later video evaluation:

- `9-10`: motion is coherent, intentional, and artifact-light
- `7-8`: generally good with minor drift or jitter
- `5-6`: acceptable but unstable
- `0-4`: visibly broken

## Comparison Method

Each benchmark prompt should be run in both modes:

1. baseline direct generation
2. workflow-assisted generation

Comparison outputs:

- baseline top candidate
- workflow top candidate
- workflow clarification transcript
- workflow brief
- workflow refinement path if used

Preferred review format:

- side-by-side human scoring
- blind ranking when possible

## Human Review Protocol

Reviewers should score candidates without being told which system produced them when possible.

Review questions:

- which result better matches the original user intent
- which result has better style adherence
- which result has clearer composition
- which result would you choose to refine
- which workflow would you prefer as a user

Use at least 2 reviewers for small studies and 3 or more for stronger signal.

## Refinement Evaluation

Refinement should be tested separately from first-pass generation.

Protocol:

1. choose a candidate with a specific weakness
2. run critic and refiner
3. generate child candidate
4. compare parent and child

Success means:

- target weakness improves
- preserved constraints stay stable
- no major new defects appear

## Failure Taxonomy

The critic and human reviewers should categorize failures consistently.

Suggested failure tags:

- `wrong_subject`
- `wrong_style`
- `wrong_framing`
- `weak_expression`
- `identity_drift`
- `outfit_drift`
- `background_drift`
- `artifact_face`
- `artifact_hands`
- `extra_characters`
- `text_present`
- `low_detail`

This taxonomy should be reused in evaluation logs.

## Logging Requirements

To support evaluation, each workflow run should persist:

- raw prompt
- analyzer output
- clarification turns
- final brief
- generation prompts
- candidate metadata
- critic outputs
- final user or system selection

Without this data, the system cannot be compared reliably over time.

If implemented with the Responses API, store response ids or run ids alongside workflow ids so model behavior can be audited and replayed.

## Regression Suite

Once benchmark cases exist, a smaller regression suite should run repeatedly.

Recommended regression pack:

- 5 simple image prompts
- 5 vague image prompts
- 5 identity-sensitive prompts
- 5 video-intent prompts

This is enough to catch major workflow regressions without excessive cost.

## v1 Evaluation Milestones

### Milestone 1

Evaluate analyzer and clarification only.

Goal:

- prompt classification works
- clarification stays concise

### Milestone 2

Evaluate image generation workflow against direct prompting.

Goal:

- structured brief plus multi-candidate path beats baseline on average

### Milestone 3

Evaluate refinement loop.

Goal:

- selected-branch refinement improves outputs more reliably than random prompt rewrites

### Milestone 4

Evaluate video pre-production artifacts.

Goal:

- shot plans and still references improve continuity readiness

## Decision Standard

The workflow should be considered better than baseline when:

- average human preference favors the workflow
- average prompt-match scores improve
- retries to acceptable output decrease
- refinement preserves constraints more consistently than baseline retries

## Follow-Up

Next implementation tasks from this document:

- build a benchmark prompt set file
- define critic scoring weights
- create test fixtures for analyzer and brief validation
- add run logging for every workflow stage
