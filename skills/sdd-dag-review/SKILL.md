---
name: sdd-dag-review
description: Perform the single read-only human review of the refined SDD DAG for Plan coverage, dependencies, ordering, and execution shape before Analyze/Implement.
---

# SDD DAG Review

## Use and workflow position

Use once after Test Scope approval and task/DAG refinement, before Analyze and Implement. This is the sole human DAG review.

Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/phase-ownership.md`, and `references/human-gates.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Review approved Spec and Plan, refined Tasks/DAG, and approved test classifications and ownership.

## Read-only coverage review

Remain read-only. Explicitly trace **Plan → Tasks/DAG**: verify every planned capability and relevant technical obligation has executable work assigned, with no material omissions. Check task-to-requirement/design traceability, prerequisites, ordering, acyclicity, parallelism, shared-file/resource conflicts, ownership, and clear completion criteria.

Explain to the user what work will happen, in what order, what can safely run simultaneously and why, and the expected result of each meaningful task/group. Identify omissions, blockers, and concrete remediation recommendations with the correct owner: return missing requirements/design to Plan or its actual owner; return decomposition/dependency defects to Tasks/DAG.

## Verdict and human gate

Give a reasoned **PASS** or **FAIL**. PASS requires adequate Plan-to-executable-work coverage and a feasible DAG; technical assessment alone is not approval. On FAIL, report gaps and owners, suspend execution, and review the corrected DAG again. On PASS, request explicit human PASS and suspend before Analyze/Implement until given.

Do not edit artifacts, introduce a Review of Tasks, checklist, extra gate, or Review Checkpoint by Wave.
