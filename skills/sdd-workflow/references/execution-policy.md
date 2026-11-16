# Execution Policy

This is coordination policy, not a scheduler implementation. OpenCode native subagents may be launched concurrently by the coordinator; do not claim filesystem isolation, atomic writes, automatic DAG scheduling, or durable recovery.

## DAG and concurrency

- Execute only approved, refined tasks represented in the human-approved DAG.
- A task is eligible when its declared prerequisites are complete and its inputs are available. Do not start dependents early.
- Run tasks concurrently when the approved DAG establishes independence and their owned outputs do not conflict.
- Serialize only conflicting writes to shared files, especially updates to `tasks.md`; independent implementation work need not wait for that checkbox update. Implementers mark only their assigned task `[x]`, after reading the latest file and preserving all other content. This is conversational coordination, not an atomic lock.
- Preserve existing valid work on a delta; schedule only affected or newly required tasks and their unmet dependencies.
- If DAG coverage, ordering, ownership, or feasibility is unclear, suspend and return the issue to the DAG/task owner. Do not improvise dependencies.

## Ownership, isolation, and context

Assign each task a clear scope, owner, inputs, outputs, and acceptance evidence. Keep prompts contextually minimal and include relevant Constitution, Spec, Plan, Tasks/DAG, contracts, and other phase-relevant artifacts. Use native OpenCode subagents where supported. Do not assume filesystem isolation; prevent overlapping output edits through ownership and serialize only the conflicting write.

## Evidence and remediation

Report what actually ran, its result, and the evidence. Never mark an unexecuted test PASS; distinguish not run, blocked, failed, and passed. Technical automated tests and human-only operational tests are separate classes. Do not run operational human tests on behalf of the operator or claim their acceptance.

Route every defect discovered by Converge to its owning task or upstream artifact. Do not add coordinator review/validation of individual completed tasks. Apply corrections at their owner, update affected dependencies/evidence, rerun impacted checks, and preserve actual results without fabricating records. A changed input invalidates dependent outputs and approvals as appropriate.

## Analyze → remediate → reanalyze

- Analyze is a read-only diagnostic. Its reviewer reports findings; it does not edit Spec, Plan, Tasks, tests, or implementation.
- The SDD Coordinator owns orchestration: map each finding to the owner in `phase-ownership.md`, delegate a narrowly scoped correction to that existing owner, then invoke the same read-only Analyze review against the current artifacts after every correction. Do not ask the reviewer to remediate its own findings or introduce a new reviewer/agent role for this loop.
- Permit autonomous correction only when it is objective, supported by approved intent, and within the owner's existing write contract. If the fix would choose or alter functional behavior, change approved scope, or cannot be grounded in existing decisions, suspend and ask the operator; preserve the artifacts until that decision is made.
- Before resuming, compare the correction with the approval history in the conversation. If it materially invalidates an approval or a downstream artifact/gate, return to the earliest affected phase and repeat its review and explicit human gate. Analyze PASS alone never authorizes bypassing an invalidated gate.
- Do not impose a fixed iteration count. Continue while each correction changes the relevant evidence and the fresh analysis verifies the result. If ownership is unresolved, correction is unsupported, findings repeat without a new path, or successive remediations oscillate, stop before Implement with the remaining findings, evidence, owner, and precise operator decision/action required. No PASS may be claimed while material findings remain.
- After a fresh Analyze reports PASS and all still-applicable approvals and DAG gates remain valid, the Coordinator may hand off to Implement in the same authorized workflow. This policy is coordination guidance, not a scheduler or durable approval-state mechanism; do not claim automatic persistence or recovery.

## Converge

After implementation, review the whole result against approved Constitution, Spec, Plan, Tasks/DAG, and actual evidence. Converge is global, not a per-wave checkpoint. On a gap, identify owner and impact, remediate, execute affected tasks/checks, and repeat the global review until supported PASS. Warnings and unverified items remain explicit; no unsupported PASS.

Only after Converge PASS may the operator perform human-only operational tests. Git closeout is allowed only after explicit operational acceptance and separate explicit authorization. This policy does not implement a scheduler, create automation, or authorize Git actions.
