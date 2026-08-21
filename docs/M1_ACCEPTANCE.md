# M1 — Reproducible Evidence Graph Acceptance

## Goal

A third party can start from the same source records and rules and reproduce the same narrow factual claims, entity links, adjudication statuses, and correction history.

M1 is the foundation for Peace Capital. It is **not** a real-money trading milestone.

## Current acceptance checklist

### A. Evidence schema

- [x] Facts are separated from user policy.
- [x] Source URL, publisher, date, retrieval time, and locator are first-class fields.
- [x] `CONFIRMED / DISPUTED / UNKNOWN / EXPIRED` can be represented.
- [x] Entity-resolution confidence/review state is recorded.
- [x] Correction history is append-oriented.
- [x] License status is recorded per evidence item.
- [x] Three worked examples plus a correction example exist.

Artifacts:

- `schemas/evidence-claim.v0.1.schema.json`
- `schemas/examples/evidence-claim.examples.json`
- `docs/EVIDENCE_MODEL.md`

### B. Entity resolution

- [x] Reuse-first OSS comparison exists.
- [x] Deterministic identifiers are preferred to fuzzy matching.
- [x] Primary v0 fuzzy matcher selected: yente.
- [x] FollowTheMoney-compatible modeling is selected as an interoperability target, not a replacement for the evidence schema.
- [x] Name-only consequential matches are forbidden.
- [x] Japanese-specific ambiguity cases are defined.
- [x] M1.1 real 100-company identity spine implemented and reproduced twice.
- [x] JPX → EDINET → corporate number → NTA exact-link chain demonstrated at 100/100 coverage in the pilot.
- [x] GLEIF exact-ID enrichment demonstrated without making LEI presence mandatory.
- [ ] Build labeled Japanese entity-resolution evaluation corpus.
- [ ] Calibrate thresholds and publish precision/recall/false-positive metrics.

Artifacts:

- `docs/ENTITY_RESOLUTION.md`
- `docs/results/M1_IDENTITY_PILOT_2026-07-31.md`

### C. Source registry

- [x] At least 10 candidate sources are documented.
- [x] Identity, military/arms, political-finance, human-rights and contextual-risk sources are represented.
- [x] Each source records evidence scope and main limitations.
- [x] License/terms uncertainty is explicit rather than guessed away.
- [x] First integration order is defined.
- [x] First identity-spine adapters implemented for JPX, EDINET, NTA and GLEIF.
- [x] Source hashes/identifiers are recorded in the real pilot result.
- [ ] Pin exact terms/license URLs for each future evidence source selected for redistribution/ingestion.

Artifact: `docs/SOURCE_REGISTRY.md`

### D. Threat model

- [x] False entity match is treated as a critical safety threat.
- [x] Parent/subsidiary conflation is covered.
- [x] Data poisoning, stale evidence, source disappearance, model hallucination and prompt injection are covered.
- [x] Political/funder capture and coordinated challenge/report attacks are covered.
- [x] Defamation, privacy, licensing and financial-automation risk are covered.
- [x] M1 blockers and pre-real-money gates are explicit.
- [x] Strong-ID conflicts automatically become `DISPUTED` in identity-layer regression tests.
- [x] Name-only automatic linking is blocked by regression tests.
- [ ] Convert evidence-adapter-specific high-priority threats into executable regression tests as adapters are implemented.

Artifact: `docs/THREAT_MODEL.md`

## M1 implementation sequence

### M1.1 — Identity spine — DONE

Implemented and verified using:

1. JPX listed-company metadata;
2. EDINET filer identifiers and submitter corporate numbers;
3. Japanese Corporate Number Publication Site full data;
4. GLEIF LEI where an exact Japanese registration ID exists.

Result: 100/100 pilot issuers received EDINET and corporate-number links; 100/100 corporate numbers were independently found in the NTA full dataset; 7 exact LEIs were attached; 0 entities were disputed or unresolved. Two executions produced the same semantic payload SHA-256.

See `docs/results/M1_IDENTITY_PILOT_2026-07-31.md`.

### M1.2 — Entity matcher benchmark

Create the labeled Japanese corpus defined in `ENTITY_RESOLUTION.md`, then benchmark:

- deterministic identifier resolution;
- yente;
- at least one alternative/baseline where practical.

Output: precision/recall/false-positive report and calibrated review thresholds.

### M1.3 — First evidence adapter: Ministry of Defense procurement

Extract narrow contract facts only:

- supplier;
- contracting authority;
- date;
- amount where published;
- contract subject;
- source locator.

Do **not** map contracts directly to weapons activity.

### M1.4 — Contract-subject semantics

Classify contract subject into evidence categories such as:

- military-specific goods/services;
- dual-use/ambiguous;
- ordinary civilian procurement;
- unknown.

Every classification must retain source text/locator and confidence.

### M1.5 — Political-finance adapter

Extract disclosed transaction facts, resolve donor entities conservatively, and preserve filing/page/row provenance.

### M1.6 — Evidence card

For a fixed pilot universe, render a human-readable card containing:

- entity identity;
- exact claim;
- source;
- evidence/adjudication status;
- confidence;
- date/expiry;
- correction/challenge path.

### M1.7 — Reproduction test

Freeze a small dataset/version. A clean checkout must regenerate the same evidence output deterministically, except for explicitly versioned model-assisted stages.

## M1 exit condition

M1 is complete when all of the following are true:

1. a fixed pilot universe is represented by stable canonical entity IDs;
2. every consequential entity link is deterministic or passes calibrated review rules;
3. at least two real evidence adapters are implemented;
4. every published claim has source provenance and a reproducible rule path;
5. correction/dispute/expiry behavior is demonstrated end-to-end;
6. a third party can regenerate the same versioned evidence graph from documented inputs;
7. threat-model blockers are enforced by tests or workflow gates.

M1.1 is now complete. M1 overall remains open until M1.2–M1.7 satisfy the remaining exit conditions.

Only then should WA Commons move the center of gravity to M2 user-policy evaluation and Peace Capital paper portfolios.
