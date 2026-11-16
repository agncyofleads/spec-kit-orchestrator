---
name: sdd-implement
description: Execute approved implementation tasks after Analyze, subject to the human-approved DAG, available capabilities, permissions, and evidence.
---

# SDD Implementation

## Use and authoritative policy

Use only after Analyze has resolved relevant consistency findings and the refined DAG has explicit human PASS. Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/execution-policy.md`, `references/phase-ownership.md`, and the applicable `references/full-path.md` or `references/delta-path.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`.

This defines an execution contract, not an implemented scheduler. Use native OpenCode child sessions for delegation; independent tasks may be launched concurrently when approved DAG prerequisites are complete and their owned outputs do not conflict. Child sessions do not imply filesystem isolation, atomic writes, or automatic dependency scheduling. Do not claim or simulate unavailable capabilities. If a required operation lacks a supported callable interface, explain that exact limitation and stop or execute only work safely supported and authorized.

## Task execution contract

Execute only approved DAG tasks whose prerequisites and inputs are ready. Respect ownership, declared outputs, acceptance evidence, and shared-resource constraints. Delegate to specialized sessions when supported and useful; keep each prompt minimal and scoped to its task, with relevant authoritative requirements, Plan decisions, dependencies, and constraints.

Run independent tasks concurrently where the approved DAG permits. Prevent overlapping edits to shared files; serialize only the conflicting write (especially the `tasks.md` checkbox update), not otherwise independent task execution. For the complete `tasks.md` read-modify-write, use Linux `flock` on a stable sibling lock file (for example, `tasks.md.sdd-lock`): acquire exclusively before reading, update only the assigned task, write before releasing, and retain the lock file. Do not use a separate edit-tool read/write for this operation. Implementers update their own task checkboxes; `tasks.md` is the only implementation-progress source of truth. The coordinator does not review tasks individually.

For failures or discovered gaps, record evidence and route remediation to the owning task or upstream artifact. Reassess affected dependencies, rerun impacted technical checks, and do not conceal failure or modify approved intent to force completion.

## Permissions, tests, and safety

Request necessary permissions for actions within the approved task scope. Do not bypass denied permissions or replace an authorized action with an unsafe workaround. Pause for user direction when requested access exceeds scope or cannot be granted safely.

Run only authorized technical automated tests supported by the environment and report what actually executed and its evidence. Never claim PASS for unrun checks. Do not perform practical administrator operations or operational journeys reserved for the human operator; preserve these for after Converge PASS.

Do not add reviews or gates by wave. Do not commit or push without separate explicit human authorization after operational acceptance. Hand the implemented result and truthful evidence to the single global Converge review, which performs the only implementation-wide review.
