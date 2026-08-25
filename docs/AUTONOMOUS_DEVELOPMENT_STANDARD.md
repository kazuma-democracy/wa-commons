# Autonomous Development Standard v1.2

Standard-Version: `1.2`

Canonical cross-project operating standard for autonomous software development.

Source repository: `kazuma-democracy/autonomous-dev-oss-lab`

This file defines project-independent rules. Product repositories may add stricter project-specific rules, but must not silently weaken this standard. If a project needs an exception, record the reason in its durable decision log.

## 1. Objective

Optimize for **useful product progress per unit of human time, model effort, and compute cost**.

Do not optimize for token count, number of tool calls, number of tests passed, or apparent activity.

Every non-trivial action must do at least one of these:

1. advance **Product State**;
2. increase **Information State** by resolving a concrete uncertainty;
3. make validated work **Durable State** in the repository.

If an action does none of these, do not perform it.

## 2. SEARCH BEFORE BUILD

**BUILD BEFORE SEARCH is prohibited.**

Before creating a non-trivial framework, orchestration layer, persistence mechanism, scheduler, simulation technique, agent system, reusable subsystem, or infrastructure:

1. inspect existing repository capabilities;
2. inspect official product/tooling capabilities;
3. inspect suitable OSS, standards, libraries, and relevant research;
4. compare **USE / BORROW / ADAPT / BUILD**;
5. prefer USE, then BORROW, then ADAPT;
6. BUILD is the last resort.

Do not create custom supervisors, task databases, message buses, retry engines, checkpoint systems, agent communication layers, Git orchestration, or QA infrastructure merely because they are easy to imagine. Reuse proven mechanisms unless they are demonstrably insufficient.

SEARCH BEFORE BUILD means targeted uncertainty reduction, not broad reading. Before significant research identify:

- `UNCERTAINTY`: what is unknown;
- `DECISION`: what choice depends on it;
- `STOP_EVIDENCE`: what evidence is sufficient to decide.

Once `STOP_EVIDENCE` is met, stop researching and execute. Do not open another file, commit, framework document, or test merely for reassurance.

## 3. Durable state over conversation memory

Conversation context is disposable. Git/repository state is durable.

Keep durable facts in project files: product source of truth, task/queue state, decisions, blockers, acceptance criteria, handoffs, and recurring failure evidence needed for later root-cause decisions.

Do not use a long conversation or giant prompt as the authoritative project memory.

Prefer a short index that points to detailed documents over copying large documents into agent context.

Interrupted or time-bounded work must preserve compact continuation state whenever it is safe to do so. A preferred handoff shape is:

```text
COMPLETED:
OBSERVED:
RULED_OUT:
NEXT_ACTION:
DEFERRED:
```

`NEXT_ACTION` must be specific enough that the next worker does not repeat discovery already performed.

## 4. Bounded state machine

Autonomous work should follow an explicit state progression:

`SELECT -> INSPECT -> PLAN -> EXECUTE -> VERIFY -> COMMIT -> DONE`

Failure paths are:

`VERIFY -> DIAGNOSE -> REPAIR -> VERIFY`

or

`DIAGNOSE -> ESCALATE / BLOCKED`

Do not jump back to broad repository exploration after every failure. Preserve what has already been learned and continue from the current information state.

A single autonomous worker should normally complete one coherent, durable increment. **A Queue/plan row is not automatically the same thing as one worker increment.** If the parent task is too large for the worker boundary, complete a safe sub-increment, preserve the handoff, leave the parent task actionable, commit/push the checkpoint, and stop.

A smaller durable checkpoint is better than an oversized uncommitted attempt.

## 5. Information-efficient inspection and research

Research exists to resolve a named uncertainty, not to create reassurance.

Before a significant search, know:

- what is currently unknown;
- why that uncertainty blocks a decision;
- what evidence would resolve it.

Prefer repository-local evidence first. Use external research when the answer depends on external facts, official behavior, OSS, standards, compatibility, or current technology.

Do not repeatedly rediscover a known blocker. Re-check only if new evidence suggests the environment or underlying fact changed.

Do not use mandatory reading as a substitute for task targeting. At startup, load only the assignment/selected task, its existing handoff, directly referenced contracts/decisions, and the smallest relevant source/tests. Shared standards, large canonical indexes, historical plans, and root-cause guides may be loaded on demand when the assigned work actually requires them.

## 6. No retry without state change

**Repeating the same attempt from the same state is prohibited.**

A retry is justified only if at least one changed:

- new evidence was obtained;
- a hypothesis was eliminated or changed;
- code/product state changed;
- the approach changed;
- the model/capability was meaningfully escalated;
- a missing dependency or environment condition changed.

Do not perform cheap retries simply because they are cheap.

The runtime/supervisor must enforce this mechanically where practical. After a worker exits, compare durable/product/worktree state. If the relevant state is unchanged, do not relaunch the same task merely under the name `recovery` or `retry`.

A retry counter is not permission for same-state retries.

## 7. Scope discipline: discover != fix

Finding an adjacent problem does not authorize fixing it.

If a useful issue is outside the selected increment:

1. record concise evidence;
2. defer it to the project queue/backlog/issue list;
3. continue the selected increment.

Do not refactor, redesign, clean up, add features, or broaden tests merely because adjacent work is visible.

## 8. Claim-based verification

**VERIFY CLAIMS, NOT SUITES. TEST THE FAILURE MODE, NOT THE TEST COUNT.**

Before verification, identify the claims introduced or relied upon by the change. Example:

```text
C1: old saves still load
C2: new state survives save/load
C3: the UI action reaches the authoritative domain path
```

Each meaningful test or check should falsify at least one concrete claim or known failure mode.

Start with the smallest useful evidence:

1. diff/static/syntax inspection when sufficient;
2. targeted unit/helper regression;
3. narrow integration boundary test;
4. broader adjacent tests only when concrete evidence justifies expansion;
5. full suite/end-to-end/long simulation at milestone, release, shared-core, or specifically evidenced regression gates.

"Just in case", "for confidence", "related area", and "more passes" are not sufficient reasons to expand verification.

Do not rerun an expensive successful check against unchanged relevant code/state.

## 9. Stop when evidence is sufficient

Stop testing and move to review/commit when:

- the relevant failure mode is reproduced or understood;
- the intended change is implemented;
- the targeted claim(s) pass;
- required boundary integration passes;
- no concrete adjacent risk remains that requires immediate validation.

Do not continue solely to increase test counts or reduce uncertainty to zero.

Before any additional non-trivial action ask: **can this action reasonably change the next decision, Product State, Information State, or Durable State?** If not, do not perform it.

## 10. Review discipline

Independent/fresh-context review is valuable when risk warrants it, not as a ritual for every tiny increment.

Use independent review especially for:

- architecture choices;
- shared contracts/APIs;
- persistence/schema/save compatibility;
- security or data-loss risk;
- large cross-subsystem changes;
- unresolved manager uncertainty.

For small localized changes, diff inspection plus claim-based targeted verification can be sufficient.

A reviewer must report only issues that materially affect requirements, correctness, safety, maintainability at the changed boundary, or explicitly requested quality criteria. Do not demand that a reviewer "find something wrong".

## 11. Context diet

Do not feed whole repositories or large historical documents to agents by default.

When a manager/supervisor supplies an exact task contract, the worker must not rescan the full Queue to select another task. The manager owns selection; the worker owns bounded execution.

At worker start, prefer only:

1. the exact assignment/task row;
2. the task-specific handoff, if any;
3. directly referenced documents;
4. source/tests needed for the next action.

Detailed implementation history and broad governance/canonical documents are loaded on demand, not ritualistically every run.

Prefer fresh specialized contexts for research/review over one indefinitely growing context.

## 12. Manager / worker separation

When the runtime supports it, separate high-value judgment from routine execution.

**Manager responsibilities**:
- select the bounded work item;
- maintain the information state;
- decide what not to do;
- choose the minimum useful research/verification;
- judge DONE / REPAIR / ESCALATE / BLOCKED;
- defer scope creep;
- choose a worker boundary small enough to finish or checkpoint safely.

**Worker responsibilities**:
- execute the exact narrow task contract;
- return diff/evidence/results;
- avoid broad replanning or task reselection unless explicitly delegated;
- preserve a durable checkpoint before the work becomes an oversized uncommitted attempt.

Current preferred default for the owner's environment:

- **Claude Code**: manager/decision layer;
- **DeepSeek V4 Flash**: normal worker;
- **DeepSeek V4 Pro**: hard worker/targeted escalation when justified;
- **Codex / strong Claude model**: independent senior review or difficult escalation;
- **local models**: cheap bounded support work where quality is sufficient.

This routing is a default, not a permanent product truth. Change it when measured capability/cost changes, while preserving the manager/worker principle.

Do not escalate by repeatedly rerunning the same weak worker. Escalate when the information state shows that a stronger capability or different approach is needed.

## 13. Cost discipline without arbitrary micro-budgets

Do not use fixed per-task dollar/token caps as the primary control mechanism. Small caps can create repeated low-value retries.

Control cost structurally:

- avoid redundant exploration;
- avoid same-state retries;
- keep contexts small;
- route routine work to cheaper capable models;
- use expensive models for judgment or genuinely difficult work;
- run expensive verification only at justified gates;
- stop when evidence is sufficient;
- bound worker runtime so large tasks are forced into durable increments rather than dying as one giant session.

Track cost/time as diagnostics when useful, but optimize the trajectory, not an arbitrary quota.

## 14. Durability and handoff

A coherent increment is complete only when its durable state is safely preserved according to the project's Git workflow.

Before completion:

- inspect the intended diff;
- exclude unrelated files;
- run proportional claim-based verification;
- update task/queue/decision/blocker/handoff state if required;
- commit/push when authorized;
- verify the durable state actually advanced.

If the whole parent task does not fit, checkpoint the coherent sub-increment rather than waiting for timeout. If blocked, record the exact blocker, evidence, and next condition. Do not fabricate progress or weaken acceptance criteria to keep an autonomous run alive.

A worker that performed substantial research but left no useful durable evidence has not completed a durable increment.

## 15. Runtime invariants for unattended development

Projects that run autonomous workers unattended must make the following behavior explicit in the runtime or supervisor, not rely only on prompt obedience:

1. **Bound each worker.** Configure a worker time boundary materially smaller than the total unattended run, with enough reserve for checkpoint/finalization. Exact minutes are project/runtime-specific; the principle is mandatory.
2. **Parent task != worker attempt.** Permit a large task to progress through multiple coherent Git checkpoints.
3. **Exact assignment.** The supervisor should pass the selected task and acceptance directly to the worker; the worker should not redo manager selection.
4. **Checkpoint before restart.** Dirty/partial work is recovered as the same increment and durably checkpointed when safe; a fresh worker must not rediscover it from zero.
5. **No same-state relaunch.** If HEAD/product/worktree/information state did not materially change, do not launch the same task again merely because retry budget remains.
6. **Mechanical bookkeeping where deterministic.** Queue promotion/status repair that can be proven from machine-readable dependency state should not require an LLM to reread the project.
7. **Activity is not progress.** Tool calls, files read, tests run, elapsed minutes, and model tokens are diagnostics only. The supervisor must evaluate durable/product/information state change.

If a runtime cannot implement an invariant mechanically, record the limitation and use the strongest available guard. Do not silently claim the invariant exists.

## 16. Milestone and release gates remain strong

Efficiency rules do not weaken product correctness.

Localized increments use localized evidence. Milestones and releases use broader acceptance appropriate to their risk.

Keep project-specific long-run simulations, compatibility checks, hidden-information guarantees, deterministic guarantees, security gates, and other critical invariants when they are part of the product acceptance contract.

## 17. Structural-fix propagation gate

A recurring/systemic failure is not fixed merely because one repository stops showing the symptom.

When a change addresses a **reusable or structural autonomous-development problem** (for example retry behavior, manager/worker boundaries, context loading, checkpointing, verification discipline, cost control, task sizing, or orchestration), classify it as `STRUCTURAL` unless there is clear evidence it is project-specific.

A structural fix enters state:

`LOCAL_FIX -> PROPAGATION_REQUIRED -> PROPAGATED -> VERIFIED`

It may be called globally/systemically `DONE` only after all applicable steps are complete:

1. **Canonical rule updated** in this repository.
2. **Shared bootstrap/template/runtime guidance updated** so future projects inherit the fix.
3. **Active adopter manifest reviewed** and every applicable active project is synchronized, or has a durable explicit exception with reason.
4. **Project entrypoints verified** so the updated rule is actually on the path used by future autonomous work; merely copying a dead document is insufficient.
5. **Version/adoption evidence updated** so stale projects can be detected without relying on conversation memory.
6. **Past experiment artifacts are not rewritten** unless the experiment protocol explicitly allows it; instead update the experiment framework for future runs.

If any applicable propagation step is missing, report the structural issue as `PROPAGATION_REQUIRED`, not fixed/DONE.

A project-local agent that discovers a reusable improvement must either propagate it under this gate or persist a durable upstream action item before claiming its own systemic root-cause work complete.

This gate is itself a root-cause invariant: **human discovery of a reusable lesson should be converted into shared machinery once, not repeatedly rediscovered project by project.**

## 18. Adoption rule for every new project

Every new autonomous-development repository must adopt this standard **before substantial implementation begins**.

Preferred pattern:

1. copy this file byte-for-byte into the project as `docs/AUTONOMOUS_DEVELOPMENT_STANDARD.md`;
2. preserve its `Standard-Version` marker and canonical Git blob SHA in the adopter lock/manifest evidence;
3. make `AGENTS.md`/equivalent say that the vendored standard is the common baseline;
4. add only project-specific product rules locally; do not summarize/rewrite the vendored canonical file;
5. adopt the runtime invariants from section 15 for unattended execution;
6. register the active project in the canonical adoption manifest when it becomes a maintained autonomous-development project;
7. do not fork the common rules casually; upstream reusable improvements to this canonical standard first, then sync active projects under section 17.

A project bootstrap agent must search for this canonical standard before inventing its own autonomous-development rules.

## 19. Root-cause escalation is a runtime invariant

Recurring failures must be recognized as a failure family, not handled as unrelated incidents.

Escalate immediately when any of these is true:

- the same normalized failure symptom/class occurs twice;
- three related failures occur in the same upper-level mechanism;
- the operator performs the same recovery action twice;
- one failure consumes at least 25% of the planned unattended run;
- the proposed fix is another local patch to a failure family already patched before.

When triggered:

1. stop same-family local retries/patches except emergency data-protection containment;
2. classify `symptom -> immediate cause -> mechanism -> systemic cause -> challenged assumption`;
3. inspect whether responsibilities/entrypoints/state stores can be removed or unified before adding machinery;
4. re-run SEARCH BEFORE BUILD for orchestration changes;
5. require a mechanical invariant or validator plus failure-injection acceptance before declaring the root issue fixed;
6. persist the normalized failure class/count and escalation state in durable repository state so a fresh supervisor can recognize recurrence.

A rule written only in a prompt/document is not considered mechanically enforced.

## 20. Control-plane integrity and single active entrypoint

Every active autonomous project must identify exactly one **canonical operator entrypoint** for unattended product work.

That entrypoint must assert, before launching a worker:

- expected repository identity;
- expected branch;
- expected runtime/agent family;
- expected Queue/plan source of truth;
- clean or explicitly recoverable worktree state;
- canonical standard version/blob lock.

Legacy runners may remain for history only if they fail closed with a message pointing to the canonical entrypoint. They must not silently bypass current invariants.

Runtime code that is generated by patching another script at launch time is prohibited for the canonical path. The code inspected by CI/review must be the code executed by the operator entrypoint, except for ordinary parameter/config substitution.

Project identity is a mechanical invariant: a Lemuria entrypoint must reject MFC identity/configuration and vice versa.

## 21. Synchronization must be proven, not declared

`SYNCED` is an evidence state, not a manual label.

At minimum, active adopter evidence must include:

1. exact `Standard-Version`;
2. exact canonical standard Git blob SHA, with the vendored project file byte-identical to that blob;
3. canonical operator entrypoint path;
4. project identity/branch/Queue assertions present on that entrypoint;
5. CI/static validation that covers the actual entrypoint and its runtime implementation;
6. applicable failure-injection checks for the invariants the runtime claims to enforce.

If byte identity or runtime evidence is missing, the adopter is `SYNC_PENDING`, not `SYNCED`.

This is itself an application of SEARCH BEFORE BUILD and structural propagation: **reuse one standard, execute one control path, and verify the wiring instead of trusting duplicated prose.**
