---
name: sdd-tasks-refinement
description: Refine approved Tasks after Test Scope approval into a traceable, feasible DAG with appropriate granularity and safe parallelism.
---

# SDD Tasks Refinement

## Use and inputs

Use after Tasks and tests have been created and Test Scope Review has explicit conversational approval; finish before the single human DAG review.

Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/delta-path.md`, `references/phase-ownership.md`, and `references/execution-policy.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Preserve approved Spec, Plan, task/test scope, test owners, and valid completed work.

## Refinement

Reduce excessive fragmentation and group cohesive work without losing requirement, design, or test traceability. Preserve functional and technical coverage and approved test classifications/owners. Improve dependencies and produce a valid acyclic execution graph. Identify prerequisites, blockers, completion criteria, tasks that can safely run in parallel, and conflicts such as shared-file ownership that require serialization or isolation.

Do not invent functional decisions or change approved test scope. Route missing requirements/design to their owners and test-scope changes back for the required review and approval. Prepare the DAG for coordinator-managed execution through native OpenCode subagents. Independent tasks may be delegated concurrently; identify output ownership and serialize only conflicting shared-file writes (especially `tasks.md`). This is coordination, not a scheduler, lock, or session/worktree isolation. No per-task coordinator reviews or per-wave reviews.

## Narrow delta omission

For a delta only, formal refinement may be omitted when Converge identifies exactly one new, well-bounded task, Test Scope Review for that delta is approved, and there is no excessive fragmentation or dependency to reorganize. Preserve inherited valid work and approvals. If any condition is uncertain or false, refine the affected task set normally; do not invent other exceptions. This is the narrow exception documented in `sdd-workflow/references/delta-path.md`; it does not waive DAG review or other required controls.

This phase creates/refines the DAG; it does not approve it. Hand the result to the single human DAG review.
