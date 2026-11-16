---
name: sdd-test-scope
description: Conversationally review and refine proposed technical and human-operational test scope after Tasks and before DAG refinement.
---

# SDD Test Scope Review

## Use and inputs

Use after initial Tasks and test proposals exist and before task/DAG refinement. This is the single test-scope review, not a test execution phase.

Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/phase-ownership.md`, `references/human-gates.md`, and `references/execution-policy.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Review approved Spec and Plan, Tasks, proposed tests, dependencies, owners, and execution timing.

## Review and refinement

Assess test coverage and refine the proposal for traceability to requirements/design, proportionality, dependencies, ownership, and the legitimate point of execution. Identify missing, redundant, misclassified, or incorrectly assigned tests. Give concrete corrections to the owning Tasks/test artifacts; their owner applies approved changes. Do not directly modify Tasks or tests.

Separate strictly:

- **Technical tests:** automatable checks that an authorized implementation/execution mechanism may run and report with actual evidence.
- **Operational tests:** checks that only the human operator can perform. Keep them explicitly assigned to the operator and scheduled after Converge PASS. Never delegate or claim them as agent-executed.

Do not execute tests. Distinguish proposed, executed, failed, blocked, and not-run; never infer PASS.

## Conversational approval

Explain the refined scope, classification, traceability, material findings, and proposed owner corrections. Obtain explicit human approval through the conversation before DAG refinement. If rejected or changes are requested, route corrections to task/test owners and revisit affected scope.

Do not create an act, verdict file, or independent review record. Do not add another human gate, checklist phase, review of Tasks, or Review Checkpoint by Wave.
