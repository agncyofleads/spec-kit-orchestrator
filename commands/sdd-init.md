---
description: Initialize a new project using the approved SDD workflow.
agent: sdd-coordinator
---

Initialize a new project using the authoritative `sdd-workflow` Skill and its `references/full-path.md`. Request/context: $ARGUMENTS

First establish whether this is genuinely a new project. For a new project, interactively ask the operator for its rules, principles, and constraints before creating/populating Constitution. Generate it only from those answers, then stop and request the desired functionality. After that input, run Specify using only the provided functionality, produce `spec.md`, and stop before Clarify to invite general functional clarification. Apply only agreed clarification decisions to the Spec; run UX/UI clarification only when applicable. Perform the single integral-semantic Spec review only after applicable clarification is complete, then stop at its existing explicit PASS/FAIL gate before Plan. The two pauses for Constitution rules/functionality and the post-Spec Clarify dialogue are information handoffs, not approval gates; do not ask for approvals there or use `/sdd-approve`. If the conversation is non-interactive or a question is canceled, stop without inventing answers or continuing.

For an existing project, preserve its current Constitution and require an explicit decision before any amendment. Follow only the existing Full workflow and its human approvals; do not add phases, reviews, or gates.

Global `/sdd-*` commands are prompt templates, not tools agents can invoke. Use the project integration's applicable Spec Kit Skill instructions as the phase procedure and perform its artifact work with the owning agent's available OpenCode tools. The Spec Kit `artifact` CLI inspects definitions; it does not execute phase commands, and its workflow engine must not replace this methodology. If a required external hook or operation cannot be performed through available tools, report the exact limitation and request only its necessary operator action/result. Do not simulate command execution, durable state, locks, or DAG enforcement.
