---
description: Report SDD status from explicitly supplied artifacts without changing files.
agent: sdd-reviewer
subagent: false
---

Provide a strictly consultative, read-only status report from user-supplied artifact paths, evidence, and context: $ARGUMENTS. This direct status request needs no prior Coordinator delegation.

Load `sdd-workflow` and consult only the relevant existing workflow guidance. This is a status-only task, not a formal Review: do not load or perform a Review Skill, issue a review verdict, or approve a gate.

Do not enumerate or search the repository, modify files, run commands, invoke agents, or approve a gate. Report only what the supplied evidence supports: current phase, observed approvals and pending human decisions, blockers/evidence gaps, and the next action allowed by the existing `sdd-workflow` Skills. Separate verified facts from unknowns. If paths or read authorization are missing, return a blocked/incomplete status and identify what the user must provide; do not guess. The paths are user-supplied scope, not an authenticated signal that this Markdown command was invoked.
