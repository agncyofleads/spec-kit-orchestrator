---
description: Reconstruct verifiable SDD state and identify the next permitted action.
agent: sdd-coordinator
---

Resume only from state verifiable in this conversation and the supplied/current authoritative project artifacts. Relevant paths or context: $ARGUMENTS

Load `sdd-workflow` and only the applicable Skills/references. Distinguish observed artifacts and explicit approvals from assumptions; do not invent persistence, approval, completed work, or test evidence. If state, ownership, or prerequisites are unclear, report the blocker and request the missing evidence rather than advancing.

For the next phase, use the owning agent's available OpenCode tools and the relevant project Spec Kit integration Skill instructions/artifacts where applicable; global OpenCode Markdown commands are prompt templates, not callable agent tools. Do not run a separate Spec Kit workflow that conflicts with the authoritative method. If a required external hook or operation cannot be performed through available tools, report that exact limitation and request only its needed operator action/result. Continue only from observed artifacts; never claim unexecuted work or durable state. Resume eligible independent implementation through native subagents when safe, serialize only conflicting `tasks.md` writes, and leave the only global implementation review to Converge.
