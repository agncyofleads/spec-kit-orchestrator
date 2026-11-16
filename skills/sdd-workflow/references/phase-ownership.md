# Phase Ownership

Keep each artifact within its contract and make the phase that owns an artifact responsible for correcting it. Reviews diagnose; they do not edit the reviewed artifact.

| Phase / artifact | Contract and owner |
| --- | --- |
| Constitution | Project principles; establish only during initialization. Explicit decision required for any later amendment. |
| Specify | User-facing **what and why**, including behavior and constraints. Spec owner resolves semantic gaps and review findings. |
| General / UX clarification | Resolve functional ambiguity; UX clarification is conditional on interface, UX, or human interaction. Feed outcomes into Specify, not technical design. |
| Spec review | Read-only integral-semantic assessment of completeness, coherence, and user vision. Findings return to Specify. |
| Plan | Technical **how** aligned with approved Spec. Plan owner resolves architecture/design findings; do not alter Spec to hide a technical mismatch. |
| Architectural review | Read-only assessment of post-Plan architecture against approved requirements and expectations. Findings return to Plan or the actual owning artifact. |
| Tasks and tests | Executable decomposition and test definitions derived from approved Spec/Plan. Task owner fixes omitted, unclear, or invalid work and test links. |
| Test Scope Review | Evaluates and refines the proposed test scope through findings and recommendations: technical automation versus exclusively human operational tests, traceability, proportionality, dependencies, ownership, and timing. It does not directly modify Tasks or tests; their owner applies approved changes in the owning artifacts. Obtain conversational approval without creating an independent act or review record. |
| Refined DAG | Executable task dependencies and parallelism. DAG/task owners correct ordering, granularity, or coverage defects. |
| DAG review | Read-only coverage and execution-shape assessment. Findings return to Plan when requirements/design are missing, otherwise to Tasks/DAG. |
| Analyze | Cross-artifact consistency check. The reviewer is strictly read-only and reports evidence, severity, affected artifacts, impact, and likely owner. The SDD Coordinator owns the Analyze → remediation → reanalysis control loop, not the correction itself. |
| Implement | Task implementation belongs to its assigned task/session. A code defect returns to that task; a requirement, design, or dependency gap returns upstream to the corresponding owner. |
| Converge | Global read-only assessment of implementation against approved artifacts and evidence. Route each gap to its true owner, then repeat convergence. |
| Operational tests | Operator performs tests designated human-only after Converge PASS. Record observed results; do not convert these into automated claims. |
| Git closeout | Operator/user authorization governs closeout; it is not an implementation phase and cannot be inferred from test approval. |

## Escalation

When ownership is ambiguous, pause and identify the conflicting artifacts and candidate owners. Do not patch a downstream artifact to conceal an upstream defect, modify approved intent without authorization, or let a reviewer silently become the implementer. Re-review any gate whose approved scope or artifact changes.

## Analyze remediation ownership

- The SDD Coordinator classifies each Analyze finding, resolves ownership, delegates correction to the existing owner, and requests a fresh read-only Analyze after each completed remediation. The reviewer never edits the artifacts it reviews.
- Objective corrections are autonomous only when they preserve the approved functional behavior, architecture intent, test scope, and applicable human approvals. Route Spec findings to Specify, technical-design findings to Plan, decomposition/test/DAG findings to Tasks, and implementation findings to their assigned implementation task.
- A finding that requires choosing, changing, or inferring user-visible behavior, relaxing an approved requirement, or changing the approved scope is a functional decision: suspend the loop and ask the operator. Do not edit the approved Spec or downstream artifacts to guess the answer.
- If a correction materially changes an artifact or decision on which an approval depends, invalidate that approval and all dependent downstream approvals. Resume at the earliest affected phase and repeat its required review and human gate before continuing. An Analyze PASS does not waive or recreate an invalidated approval.
- If an owner cannot make a supported correction, ownership remains ambiguous, or reanalysis does not establish convergence, report the unresolved evidence, impacts, and owners and stop before Implement. Do not force PASS or advance on the basis of a correction attempt.
- There is no fixed round limit. Continue only while each iteration makes evidence-backed progress within approved scope. Detect cycles or non-progress (the same material finding persists, returns without a new resolution path, or remediation oscillates between artifacts); at that point stop and request the specific operator decision or owner action needed to break the cycle.
