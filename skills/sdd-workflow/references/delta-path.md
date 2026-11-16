# Delta Path

Use the Short Path for an approved extension or change to an existing feature. Preserve prior authoritative artifacts and project decisions; do not restart initialization or rewrite unaffected work without cause.

1. Identify the existing feature, its approved Spec, Plan, Tasks/DAG, Constitution, and implementation state. Treat these as inputs, not disposable scaffolding.
2. Specify the delta: define only the new or changed **what and why**, and retain unchanged requirements as inherited context. Resolve functional ambiguity; perform UX/UI clarification only if the delta includes interface, UX, or human interaction.
3. Apply the integral-semantic Spec review to the changed specification in context of the existing feature. Explain expected behavior and obtain explicit human PASS. On failure, remediate the Spec owner and repeat.
4. Update the technical Plan only as required by the approved delta. Run the post-Plan architectural review on affected architecture and its alignment with approved expectations. Explain it and obtain approval; remediate the owning artifact and repeat on FAIL. Generate complete architectural extraction only on PASS or PASS WITH WARNINGS.
5. Create or update affected Tasks and tests. Review test scope with the same strict technical-automated versus operational-human distinction, traceability, proportionality, dependencies, and execution timing; obtain conversational approval without an act.
6. Refine the affected task set and its dependencies into an executable DAG. Preserve completed and still-valid prior tasks. Explicitly review Plan-to-Tasks/DAG coverage and obtain human PASS.
7. Analyze consistency across changed and inherited authoritative artifacts using the Analyze → remediation → reanalysis loop in `phase-ownership.md` and `execution-policy.md`. Analyze remains read-only; the Coordinator routes objective corrections to existing owners and repeats the review after each correction. Suspend for functional decisions or material approval invalidation, and stop without PASS on unresolved ownership, unsupported remediation, or non-convergent findings. Do not use a fixed round limit.
8. Implement only after supported Analyze PASS and confirmation that affected human approvals and the DAG remain valid. Respect dependencies, concurrency, and existing work. Converge globally against the resulting feature state; route gaps to owners and repeat to PASS.
9. Run operational human tests only after Converge PASS. Git closeout remains blocked until human operational acceptance and explicit authorization.

## Narrow refinement omission

When the delta's Test Scope Review is approved and Converge identifies exactly one new, well-bounded task, it is permissible to proceed directly to Implement without a formal Tasks-refinement pass only if there is no excessive fragmentation and no dependency that needs reorganizing. Preserve approved tests and their owners. If any condition is not met or is uncertain, refine the affected task set normally. This exception does not waive DAG review or any other required phase or approval.

## Recovering omitted phases

Short Path does not waive required controls. If an affected upstream artifact is missing, stale, contradictory, or insufficient to support a downstream decision, recover the relevant phase(s) in dependency order before proceeding. Reuse valid prior approvals only for unchanged scope; changed behavior, architecture, test scope, or DAG requires its corresponding review and approval. Do not invent exceptions or treat an absent artifact as approval.

Unchanged phases may be omitted only when their authoritative outputs remain available and demonstrably valid for the delta. If validity is uncertain, stop and ask the user or recover the phase. Never amend Constitution without an explicit decision.
