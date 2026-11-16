---
name: sdd-workflow
description: Reusable, project-agnostic guidance for Spec-Driven Development workflows, phase ownership, human approvals, and execution policy.
metadata:
---

# SDD Workflow

Use this skill to guide an explicitly requested SDD workflow. Its description may make it available to the model, but announcement is not authorization to start phases automatically. Respect the project's Constitution and authoritative artifacts; do not assume the orchestration engine exists. Reuse the project's official Spec Kit workflows rather than duplicating them.

Keep prompts contextually minimal. Preserve the strict boundary: Specify defines **what and why**, Plan defines **how**, and Tasks define executable work. Reviews are read-only; corrections belong to the owning artifact or task. Never report an unexecuted test as passing.

Choose the applicable path and consult its references before acting:

- Full initialization or end-to-end workflow: [references/full-path.md](references/full-path.md)
- Change to an existing feature: [references/delta-path.md](references/delta-path.md)
- Ownership and remediation: [references/phase-ownership.md](references/phase-ownership.md)
- Human approvals and suspension: [references/human-gates.md](references/human-gates.md)
- DAG execution, evidence, and convergence: [references/execution-policy.md](references/execution-policy.md)

Supporting references are not loaded automatically. Read only those relevant to the current phase. This skill describes workflow guidance; it does not enable automation or authorize implementation, operational testing, or Git actions.
