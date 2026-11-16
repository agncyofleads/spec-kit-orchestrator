---
name: sdd-spec-review
description: Perform the single read-only integral-semantic review of an SDD Spec after applicable clarification and before Plan.
---

# SDD Spec Review

## Use and workflow position

Use once after general clarification and conditional UX/UI clarification, and before Plan. This is the sole integral-semantic Spec review. Do not create a Clarify review or another Specify review.

Before reviewing, load the `sdd-workflow` Skill by its exact ID `sdd-workflow`, then use the base directory OpenCode provides for that loaded Skill to read `references/full-path.md`, `references/phase-ownership.md`, and `references/human-gates.md`. For the global installation, that directory is `~/.config/opencode/skills/sdd-workflow/`. Starting from the supplied Spec path, independently locate and read the project Constitution and only directly relevant Spec Kit artifacts (for example, related feature contracts or decision records) using scoped directory reads. Do not depend on the coordinator to relay the operator's original request or conversation history, and do not infer intent from conversation context. Do not enumerate unrelated repository content. For clarification, load the project's official `speckit-clarify` Skill through OpenCode's public `skill` interface and follow it rather than duplicating its procedure.

## Review contract

Remain read-only. Evaluate the Spec for completeness, internal coherence, clarity, testability/verifiability, contradictions, and material ambiguity. Check alignment with the project Constitution and directly relevant authoritative artifacts; identify omissions, unsupported additions, and conflicts within those sources. Do not judge alignment with the operator's original intent from conversation history: the human gate owns that comparison. Preserve Specify's scope: the Spec states **what** the system does and **why**, not the technical **how** owned by Plan.

For each finding, state the concrete semantic or technical misalignment, impact, supporting evidence/location, and correct remediation owner (normally Specify/Spec; route conflicts to the actual authoritative owner). Do not edit artifacts or silently resolve decisions. Distinguish blocking failures from non-blocking observations.

## Verdict and gate

Provide a technically reasoned verdict: **PASS** only when the Spec is sufficiently complete, coherent, clear, verifiable, unambiguous for planning, and aligned with Constitution and applicable authoritative artifacts; otherwise **FAIL** with concrete misalignments, evidence/location, impact, and owners.

- **On technical FAIL:** report only the technical verdict, blockers/findings, evidence, impacts, owners, and evidence gaps. Do not provide the functional approval summary, ask the operator for PASS/FAIL, or imply that a human decision could waive blockers. Stop for Spec-owner remediation; after the Spec changes, repeat this same review.
- **On technical PASS:** provide a plain-language, sufficiently complete functional summary of the Spec for the operator to compare with their intent. Include relevant scenarios/behaviors, inputs and accepted ranges, outputs, validation/rejection behavior, exceptions, and material decisions/remaining non-blocking limitations. State that the reviewer has not judged the operator's original intent. Ask the operator for explicit human PASS or FAIL. A technical PASS is not human approval; suspend before Plan until that decision.

Do not add a checklist phase, separate Specify review, extra human gate, or Review Checkpoint by Wave. This Skill does not authorize Plan or implementation before the gate.
