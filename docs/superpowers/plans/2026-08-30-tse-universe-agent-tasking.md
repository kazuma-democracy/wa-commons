# Canonical TSE Universe and Agent Tasking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the canonical TSE domestic listed-company universe the direct scale target after the 100-company regression cohort, separate benchmark selection from coverage, and make every near-term M3 task independently assignable to a strong autonomous worker.

**Architecture:** Preserve the completed M1/M2 contracts and scale them by source-defined universe rather than by an artificial benchmark-sized intermediate cohort. Keep benchmark selection/mapping and market-return ingestion as separate financial-evaluation paths that join the TSE-wide evidence/policy path only at the final paper-evaluation integration issue.

**Tech Stack:** GitHub Issues, Markdown roadmap/goals, existing Python identity/evidence/policy implementation and CI.

**Spec:** `docs/superpowers/specs/2026-08-30-tse-universe-agent-tasking-design.md`

## Global Constraints

- Existing M1 identity/evidence semantics remain unchanged.
- Policy v0.1 remains `EXCLUDE / WATCH / NONE`; `NONE` is never PASS.
- TSE canonical v0.1 scope is domestic Prime/Standard/Growth companies from a pinned official JPX snapshot.
- TOKYO PRO Market and non-company investment products remain outside canonical v0.1.
- Benchmark selection remains preregistered before observed portfolio performance.
- No real-money trading capability is introduced.
- Each implementation worker receives one exact Issue, not a roadmap phase.

---

### Task 1: Canonical TSE universe enumeration

**Files:**
- Consume existing JPX identity/universe implementation paths identified by the worker from #46.
- Create/modify only the generator, tests, result artifact/report and CI needed by #46.

**Interfaces:**
- Consumes: pinned official JPX listed-company snapshot.
- Produces: deterministic canonical TSE universe artifact + manifest required by #53.

- [ ] Read #46, `AGENTS.md`, the current JPX pilot/runbook, and only the source/tests directly needed to locate the existing JPX parsing path.
- [ ] Write failing scope/determinism tests proving Prime/Standard/Growth domestic companies are retained and explicitly excluded product categories are not silently included.
- [ ] Run only those targeted tests and confirm the new universe behavior is not yet implemented.
- [ ] Extend the existing JPX path minimally to emit the pinned canonical universe and manifest.
- [ ] Re-run targeted tests; compare counts to the pinned source and prove deterministic semantic output.
- [ ] Publish the measured result report, inspect the diff for unrelated changes, and preserve a bounded PR/checkpoint.

### Task 2: TSE identity enrichment

**Files:**
- Reuse existing M1 identity adapters/resolver and tests.
- Add only the full-universe orchestration/artifact/report required by #53.

**Interfaces:**
- Consumes: #46 canonical TSE universe artifact.
- Produces: deterministic TSE identity artifact keyed by canonical JPX identifiers.

- [ ] Read #53 plus existing M1 identity implementation/result contracts.
- [ ] Add a failing regression proving every #46 row survives into mapped/unresolved/disputed output and name-only AUTO_LINK remains impossible.
- [ ] Run the targeted identity regression.
- [ ] Reuse the existing JPX/EDINET/NTA/GLEIF spine across all #46 rows; do not add a new resolver framework.
- [ ] Verify mapped/unresolved/disputed counts, semantic determinism and source hashes.
- [ ] Publish result evidence and a bounded PR/checkpoint; if source-format drift blocks an adapter, stop with the exact reproducible failure.

### Task 3: Scale evidence coverage to TSE

**Files:**
- Reuse the completed #42 coverage generator/state model.
- Extend only the universe input and report/artifact paths needed by #54.

**Interfaces:**
- Consumes: #42 coverage semantics and #53 TSE identity artifact.
- Produces: deterministic TSE-wide evidence-coverage artifact required by #55.

- [ ] Read #54, #42 output contracts and existing integrated adapter interfaces.
- [ ] Add a failing test proving every TSE identity receives an explicit applicable coverage state and missing/unintegrated data cannot become a positive classification.
- [ ] Run targeted coverage tests.
- [ ] Generalize the existing #42 generator to #53 without adding or repairing source adapters.
- [ ] Verify deterministic output, state counts and source/category coverage statistics.
- [ ] Publish result evidence and stop on adapter/license blockers rather than weakening semantics.

### Task 4: Scale policy screening to TSE

**Files:**
- Reuse completed #43 company-level screening aggregation/evaluator.
- Extend only batch input/output/reporting required by #55.

**Interfaces:**
- Consumes: #54 TSE coverage/evidence artifact and current policy profiles.
- Produces: deterministic TSE-wide per-profile screening artifact required by #51.

- [ ] Read #55, #43 output contracts and policy evaluator tests.
- [ ] Add a failing scaling regression covering EXCLUDE/WATCH/NONE plus UNKNOWN/DISPUTED/EXPIRED/no-evidence behavior.
- [ ] Run targeted tests.
- [ ] Apply the existing #43 semantics to all #54 entities and current example profiles.
- [ ] Verify every non-NONE result traces to rule/evidence references and semantic hashes reproduce.
- [ ] Publish result evidence and bounded PR/checkpoint.

### Task 5: Benchmark research and constructor decision

**Files:**
- Follow #45 and #47 exact documentation/result paths selected by those workers.

**Interfaces:**
- #45 produces one adopted benchmark decision or explicit blocker.
- #47 consumes #45 and produces one constructor design/config contract for #49.

- [ ] Complete #45 without inspecting portfolio performance; record provider, identifier, return variant, point-in-time availability and rights assumptions.
- [ ] After #45 is durable, complete #47 as an OSS-first decision task; do not implement the constructor or run headline returns.
- [ ] Ensure both tasks leave ADOPT/WATCH/REJECT evidence and explicit blockers where applicable.

### Task 6: Constructor implementation

**Files:**
- Modify only the constructor/config/test paths required by #49.

**Interfaces:**
- Consumes: #47 constructor contract.
- Produces: deterministic target-weight constructor used by #51.

- [ ] Write fixed-fixture tests for weights, constraints, WATCH/NONE handling and infeasible cases.
- [ ] Confirm failing tests.
- [ ] Implement only the adopted #47 constructor and versioned config.
- [ ] Verify numerical invariants and fail-closed infeasibility behavior.
- [ ] Publish a bounded PR/checkpoint with no market download/backtest/broker functionality.

### Task 7: Benchmark snapshot and TSE mapping

**Files:**
- Implement only benchmark constituent/weight ingestion and mapping required by #50.

**Interfaces:**
- Consumes: #45 benchmark decision and #53 canonical TSE identity artifact.
- Produces: pinned mapped benchmark snapshot required by #56 and #51.

- [ ] Add failing fixtures for point-in-time constituent/weight parsing, weight reconciliation and unresolved identity mapping.
- [ ] Run targeted tests.
- [ ] Ingest the pinned benchmark snapshot and map using strong identifiers/existing identity rules.
- [ ] Verify weight reconciliation, unresolved/disputed count/weight and deterministic semantic output.
- [ ] Publish provider/license metadata and a bounded PR/checkpoint; do not ingest return history.

### Task 8: Bounded market-return ingestion

**Files:**
- Implement only normalized return/corporate-action ingestion required by #56.

**Interfaces:**
- Consumes: #50 mapped benchmark snapshot and M3.1 evaluation contract.
- Produces: pinned bounded market-return snapshot required by #51.

- [ ] Add failing tests for no-look-ahead behavior, required corporate-action treatment and unexplained missing-return BLOCK behavior.
- [ ] Run targeted tests.
- [ ] Implement the minimum provider ingestion/normalization needed for the explicitly bounded first evaluation period.
- [ ] Verify normalized return determinism and missing-return fail-closed behavior.
- [ ] Publish provider/license/hash evidence and a bounded PR/checkpoint; do not broaden the period.

### Task 9: First paper evaluation integration

**Files:**
- Modify/create only the integration runner, manifest, result report and targeted integration tests required by #51.

**Interfaces:**
- Consumes: #44, #49, #50, #55, #56 plus M3.1 specification.
- Produces: first reproducible Peace Capital paper evaluation or explicit BLOCK result.

- [ ] Add an integration fixture proving incompatible/missing prerequisites BLOCK before methodology execution.
- [ ] Run the fixture and confirm failure before integration exists.
- [ ] Wire only versioned completed outputs; do not redesign any upstream method.
- [ ] Run the preregistered metrics for one bounded evaluation period.
- [ ] Clean-rerun and verify target weights/metrics within pinned tolerance plus complete provenance from exclusion to policy/evidence/source.
- [ ] Publish negative results/limitations with equal prominence, inspect the final diff, and preserve the milestone PR/checkpoint.

### Task 10: Future-phase decomposition gate

**Files:**
- `ROADMAP.md`
- New GitHub Issues created only when a future workstream is ready to execute.

**Interfaces:**
- Consumes: measured M3/utility evidence.
- Produces: Issue-sized contracts for Phase 4+ rather than roadmap-sized worker prompts.

- [ ] Before assigning any Phase 4–9 work, apply the `Agent-sized task contract` checklist in `ROADMAP.md`.
- [ ] Split research, design, data/rights, implementation and acceptance when they can fail independently.
- [ ] Ensure each new Issue names exact inputs, output, DoD, stop/block conditions and out-of-scope work.
- [ ] Do not assign “do Phase 4”, “build Peace Router”, “internationalize”, or similarly broad prompts directly to any autonomous model.