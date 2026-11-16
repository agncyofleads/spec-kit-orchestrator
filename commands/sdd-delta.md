---
description: Start an approved change to an existing feature using the SDD delta path.
agent: sdd-coordinator
---

Start this change using the authoritative `sdd-workflow` Skill and `references/delta-path.md`. Existing feature, requested change, and known artifact paths: $ARGUMENTS

Preserve valid prior Constitution, Spec, Plan, Tasks/DAG, decisions, and completed work. Update only affected scope. Reuse an unchanged phase only when its authoritative output remains available and demonstrably valid. Recover missing, stale, contradictory, or insufficient upstream phases in dependency order. Apply the documented narrow Tasks-refinement omission only when every stated condition is verified; otherwise refine normally. Do not add phases, reviews, or gates.

Use project Spec Kit phase instructions and artifacts through the owning agent's available OpenCode tools; read applicable project integration Skills when they provide the phase procedure. OpenCode Markdown commands are prompt templates, not callable tools. Do not use Spec Kit workflow automation if it changes the authoritative Delta path or adds/reorders gates. If a required external hook or operation cannot be performed through available tools, identify the exact limitation and request only the necessary operator action. Never claim an operation ran unless it actually did.

Delegate ready independent implementation tasks concurrently through native OpenCode subagents when the approved DAG permits and their writes do not conflict. Implementers mark only their own tasks `[x]` in `tasks.md`; serialize only conflicting writes to that file, not the full task execution. The coordinator does not inspect or validate tasks individually; Converge is the single global implementation review.
