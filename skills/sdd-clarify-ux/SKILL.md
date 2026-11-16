---
name: sdd-clarify-ux
description: Resolve material user-facing UX/UI and human-interaction ambiguities in an SDD specification, after general clarification and before the integral-semantic Spec review.
metadata:
---

# SDD UX/UI Clarification

Use only when the feature specification involves an interface, user experience, or human interaction. Its description may make it available to the model, but announcement is not authorization to begin clarification automatically. This is a focused complement to general clarification, not a replacement or duplicate of the project's official `speckit-clarify` Skill. Load that Skill through OpenCode's public `skill` interface for general clarification; use this Skill only for additional material UX/UI and human-interaction questions.

## Position in the workflow

Run after general clarification and before the single integral-semantic Spec review. Read the applicable project Constitution, current specification, and authoritative decisions first. Treat already-resolved information as settled; do not ask again. This clarification is not a review or approval gate.

## Clarify material interaction behavior

Inspect the feature-specific user flows for unresolved decisions that materially affect expected behavior. Depending on the feature, consider interaction, states and transitions, feedback, errors and recovery, navigation, selection, editing, accessibility, and visual adaptation. These are prompts for relevance, not a universal checklist: omit areas that do not apply.

Ask concise, concrete questions only where the user's decision is needed. Explain functional alternatives in plain language when they help the user choose, including meaningful consequences. Ask the highest-impact questions first; group related questions only when that remains clear. Do not ask questions already answered by general clarification or authoritative artifacts, and do not infer or invent the user's choice. If no material ambiguity remains, ask nothing.

## Preserve the Specify boundary

Capture confirmed decisions in the corresponding specification, preserving traceability to the question/decision and consistency with existing authoritative artifacts. Keep Specify focused on **what** users can do and **why** the behavior is needed. Do not prescribe implementation, architecture, frameworks, component libraries, or other Plan-level technical choices. If a user answer implies a technical choice, record the functional constraint or expected outcome and leave the technical how to Plan.

When an answer conflicts with an authoritative artifact or remains ambiguous, identify the conflict and ask for resolution rather than silently overriding it. Do not change the Constitution absent an explicit decision.

## Completion

Finish when material UX/UI and human-interaction ambiguities for the feature are resolved and reflected in the specification. Summarize decisions captured and any unresolved items that prevent a coherent specification, then return control to the SDD workflow's integral-semantic Spec review. Do not create a Clarify review, a separate Specify review, or an additional human gate.

Do not perform practical interface operations, browser testing, or usability tests as part of this clarification.
