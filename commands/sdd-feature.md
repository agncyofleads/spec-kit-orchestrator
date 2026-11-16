---
description: Start a feature through the approved full SDD workflow.
agent: sdd-coordinator
---

Start this feature using the authoritative `sdd-workflow` Skill and `references/full-path.md`. Feature/request: $ARGUMENTS

Use the full path without reinitializing an existing project or changing its Constitution. Follow the existing phase order, owners, and human approvals exactly; add no phase, review, or gate. Load applicable existing Skills rather than restating their methods.

Use project Spec Kit phase instructions and artifacts through the owning agent's available OpenCode tools; read applicable project integration Skills when they provide the phase procedure. OpenCode Markdown commands are prompt templates, not callable tools. Do not use Spec Kit workflow automation if it changes the authoritative Full path or adds/reorders gates. If a required external hook or operation cannot be performed through available tools, identify the exact limitation and request only the necessary operator action. Never claim an operation ran unless it actually did.

Delegate ready independent implementation tasks concurrently through native OpenCode subagents when the approved DAG permits and their writes do not conflict. Implementers mark only their own tasks `[x]` in `tasks.md`; serialize only conflicting writes to that file, not the full task execution. The coordinator does not inspect or validate tasks individually; Converge is the single global implementation review.
