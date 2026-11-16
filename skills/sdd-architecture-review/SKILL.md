---
name: sdd-architecture-review
description: Perform the single read-only post-Plan architecture review against approved Spec requirements and expectations.
---

# SDD Architectural Review

## Use and workflow position

Use once after Plan and before Tasks. This is the sole architectural review; do not create a Review of Plan or another architecture gate.

Load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/phase-ownership.md`, and `references/human-gates.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Review the approved Spec, its human-approved expected behavior, applicable Constitution, and Plan as authoritative inputs.

## Review contract

Remain read-only. Evaluate technical soundness, architectural boundaries, integration, reuse, risks, and internal coherence of the Plan. Explicitly trace approved functional requirements and expectations from Spec to the proposed architecture; identify requirements not met or architectural choices that undermine them. Do not change Spec or Plan.

For every finding, give evidence/location, impact, blocker status, and remediation owner. Classify each blocker as either:
- **Plan-remediable:** an objective technical or contract defect that can be corrected while preserving approved functional requirements. Return it to the coordinator/Plan owner for autonomous correction and repeat this same Review.
- **Functional decision required:** resolving it would select, change, or narrow approved user-visible behavior, scope, or an unresolved Specify/Clarify decision. Do not decide or alter the Spec; stop and ask the operator for the needed Specify/Clarify decision.

The reviewer remains read-only and never edits Plan or Spec. For a Plan-remediable FAIL, return findings to the coordinator as an internal remediation handoff; do not produce an intermediate user-facing final report or request human architectural approval while blockers remain. The coordinator owns Plan remediation and re-delegates this same Review after each correction. Do not impose a fixed retry count: continue only while each correction makes evidence-backed progress within approved behavior and the fresh review verifies it. Stop and report evidence and owners if ownership is unclear, no supported correction exists, findings repeat without a new resolution path, or remediation oscillates. Any blocker requiring a functional decision suspends the loop immediately for operator input. Material approval invalidation returns the workflow to the earliest affected phase and its review and human gate.

## Verdict, extraction, and approval

Issue a reasoned **PASS**, **PASS WITH WARNINGS**, or **FAIL**. Warnings and residual risks must be explicit. On FAIL, provide only the review, findings, and owners; omit the complete architectural extraction. Remediation belongs to the owner; repeat this review after changes.

On PASS or PASS WITH WARNINGS, provide the understandable architecture explanation and complete architectural extraction, retaining warnings. The extraction MUST include:

1. The **verbatim/raw file-and-directory tree recorded in the Plan**, without silently normalizing, adding, or dropping nodes.
2. For every listed path, its stated or clearly evidenced responsibility and its relevant relationships/dependencies to other paths and Spec requirements.
3. A distinction between paths present in the Plan and paths actually present in the project at review time. Do not label proposed source/test paths as existing when they are only planned; note missing/empty directories as such.

Use the Plan and directly relevant artifacts as the source of truth; do not create a new artifact for this extraction. Present the technical verdict, understandable architecture explanation, warnings, and extraction to the operator, then request the single explicit human approval and suspend before Tasks. A technical verdict alone is not human approval.

Do not add a Review of Plan, another architectural gate, checklist phase, or Review Checkpoint by Wave.
