---
name: sdd-converge
description: Perform the single global read-only final review of implementation against approved SDD artifacts and evidence, routing gaps to owners until supported PASS.
---

# SDD Converge

## Use and policy

Use after implementation and before human operational acceptance. This is the single global final review, not a per-wave checkpoint.

Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/phase-ownership.md`, and `references/execution-policy.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Compare actual implementation and evidence with authoritative Constitution, approved Spec, approved Plan, and approved Tasks/DAG.

## Global review

Remain read-only. Assess implementation integrity and completeness, integration and contracts, requirement/design/task coverage, regressions, and actual technical validation evidence. Identify gaps, unfinished work, and conflicts. For every finding, state impact, evidence, and correct owner: implementation/task defects return to their task; requirement gaps to Specify; design/architecture gaps to Plan; decomposition/dependency defects to Tasks/DAG.

Distinguish executed-and-passed, executed-and-failed, blocked, and not-run checks. Never convert missing evidence or inference into PASS. Do not perform remediation in the reviewed artifacts; the owner corrects findings and provides updated evidence.

## Iteration and outcome

Issue a reasoned **PASS** only when the global result is supported by implementation and evidence; otherwise **FAIL** with owner-routed findings. After remediation, repeat the global review against the changed result until supported PASS. Do not add intermediate or wave-based reviews.

Converge PASS enables the next stage only: the operator's human-only operational tests and acceptance. Do not execute, substitute for, or claim those tests. Git closeout remains later and requires operational acceptance plus separate explicit human authorization. A Converge PASS is not Git authorization.
