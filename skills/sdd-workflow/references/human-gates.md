# Human Gates

Each gate suspends progression until the user/operator explicitly approves the stated scope. Present a concise explanation, relevant artifact/evidence, findings, and requested decision. Silence, implied consent, a tool completing successfully, or approval of another phase is not approval.

| Gate | Required before proceeding |
| --- | --- |
| Integral-semantic Spec review | Only after technical PASS, explain the complete functional summary for operator intent comparison and obtain explicit human PASS/FAIL. Technical FAIL returns blockers to the Spec owner without requesting approval. On human PASS, the coordinator continues to Plan in the same conversation; no separate `/sdd-approve` or `/sdd-resume` invocation is required. On human FAIL, correct the Spec and repeat the same review. |
| Post-Plan architectural review | On technical FAIL, the coordinator autonomously corrects only objective Plan/contract defects that preserve approved behavior and repeats this same Review. Continue without a fixed retry count only while corrections make evidence-backed progress; if ownership is unclear, no supported correction exists, findings persist without a new resolution path, or remediations oscillate, stop without requesting approval as a waiver. If resolution requires a functional decision, suspend for operator input in Specify/Clarify without altering approved requirements. A material approval invalidation returns to the earliest affected phase and its review and human gate. Only after PASS/PASS WITH WARNINGS, present the architecture explanation and complete extraction, including the raw Plan tree, path responsibilities/relationships, and actual-versus-proposed path status; then obtain the single explicit human approval before Tasks. Disclose warnings. |
| Test Scope Review | Explain refined test scope, technical automation versus human-only operational tests, traceability, proportionality, dependencies, and timing. Obtain conversational approval; do not create an act or duplicate review checkpoint. |
| Refined DAG review | Explain Plan-to-Tasks/DAG coverage, omissions, task outcomes, dependencies, and parallelism. Obtain explicit human PASS before execution. |
| Operational acceptance | After Converge PASS, operator executes designated human-only tests and explicitly accepts the observed outcome. A not-run or failed test is not a pass. |
| Git authorization | After operational acceptance, obtain explicit authorization for Git closeout. Approval must cover the requested action; do not infer commit or push authorization. |

## Suspension and resumption

At a gate, stop downstream work and ask for the decision. Keep status pending until explicit approval or a clear rejection. On rejection or requested changes, route remediation to the owning artifact, show the revised result, and repeat the affected gate. Resume from the earliest affected phase; preserve approvals only for unchanged scope and evidence. A material change invalidates downstream approvals that depend on it.

Do not add a separate Specify review, Plan review, checklist, or Review Checkpoint by Wave. Do not create redundant human approvals beyond the gates defined by the workflow. Technical read-only reviews remain distinct from approval: passing a review internally does not satisfy the human gate.
