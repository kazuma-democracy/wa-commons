# Canonical TSE Universe and Agent-Sized Tasking Design

Date: 2026-08-30
Status: proposed with roadmap respec branch

## Problem

The prior M3 roadmap coupled two different concerns:

1. expanding WA Commons company identity/evidence coverage; and
2. selecting a financial benchmark for Peace Capital evaluation.

That produced an unnecessary conceptual stage of `100-company cohort -> benchmark universe -> broader TSE universe`. The benchmark-universe stage is useful for financial comparison, but it is not required as an intermediate technical scaling step.

The task audit also found two integration gaps:

- there was no explicit TSE-wide evidence-coverage task between identity expansion and portfolio evaluation;
- there was no explicit TSE-wide policy-screening task before the first portfolio evaluation.

Finally, the former #50 combined benchmark membership/weight ingestion, market returns and corporate-action behavior, which contains independent data/licensing failure modes and is too broad for a single autonomous worker increment.

## Design decision

### 1. Separate product universe from benchmark

The canonical Japan-equity company universe is a pinned official JPX snapshot of domestic companies listed on TSE Prime, Standard and Growth.

The 100-company cohort remains a regression/explainability fixture only.

The benchmark is a versioned financial-evaluation view/subset mapped onto the canonical TSE identities. Benchmark membership must not determine which companies WA Commons is capable of identifying or screening.

```text
100-company regression cohort
        |
        | contracts proven
        v
canonical TSE company universe
        |
        +--> TSE identity graph
        |      |
        |      +--> TSE evidence coverage
        |             |
        |             +--> TSE policy screening
        |
        +--> pinned benchmark mapping
                 |
                 +--> market-return snapshot
                         |
                         +--> paper evaluation
```

### 2. Canonical TSE v0.1 boundary

Include:
- domestic companies on TSE Prime;
- domestic companies on TSE Standard;
- domestic companies on TSE Growth.

Exclude from canonical v0.1:
- TOKYO PRO Market;
- ETFs;
- ETNs;
- REITs and other non-company investment products;
- hand-picked additions.

The exact company count is never hard-coded. The pinned official JPX snapshot defines it; “roughly 3,700” is descriptive only.

### 3. Task decomposition

The TSE scale path is deliberately split by independently reviewable artifacts:

- #46: enumerate canonical TSE company universe from one pinned JPX snapshot;
- #53: apply existing JPX/EDINET/NTA/GLEIF identity spine to every #46 row;
- #54: reuse completed #42 coverage semantics and existing evidence adapters across #53;
- #55: reuse completed #43 policy-screening semantics across #54.

The financial path remains separate:

- #45: choose benchmark before return inspection;
- #47: select/define constructor using OSS-first review;
- #49: implement constructor;
- #50: ingest/map benchmark constituents and weights onto #53 identities;
- #56: ingest bounded return/corporate-action data for #50;
- #51: integrate only completed versioned outputs.

### 4. Autonomous-worker contract

A roadmap workstream is not itself a worker task. A Sonnet-class or Luna MAX-class autonomous worker receives one exact Issue.

An Issue is agent-ready only when it has:

- one durable primary outcome;
- completed/versioned prerequisites;
- one dominant uncertainty/failure family;
- explicit inputs and outputs;
- finite reproducible Definition of Done;
- explicit stop/block behavior;
- explicit out-of-scope boundary;
- proportional verification requirements;
- a context footprint limited to the issue, referenced contracts and relevant code/tests;
- a durable handoff format if unfinished.

Research selection, data-rights investigation, ingestion, algorithm design, implementation and end-to-end acceptance must be separate whenever one can fail without invalidating the others.

## Safety invariants

- Missing evidence is never PASS/clean/safe.
- Policy v0.1 outputs `EXCLUDE / WATCH / NONE`; `NONE` is not PASS.
- Name-only consequential entity matches never AUTO_LINK.
- Benchmark selection is fixed before portfolio performance is inspected.
- Benchmark membership does not define evidence scrutiny coverage.
- TSE expansion adds rows, not looser identity or evidence semantics.
- No task may silently substitute a source, benchmark, identity match or methodology when a prerequisite fails.
- Real-money trading remains prohibited.

## Acceptance

This design is accepted when repository durable state shows:

1. `ROADMAP.md` defines direct `100 -> canonical TSE` expansion and benchmark-as-view semantics;
2. `GOALS.md` is consistent with `EXCLUDE / WATCH / NONE` and broad TSE identity coverage;
3. #46 is narrowed to canonical TSE enumeration;
4. a separate TSE identity-enrichment issue exists;
5. separate TSE evidence-coverage and policy-screening issues exist;
6. benchmark mapping and market-return ingestion are separate issues;
7. #51 depends on all required versioned upstream artifacts;
8. the roadmap contains an explicit agent-sized task readiness checklist and marks phases 4–9 as not directly assignable until decomposed.