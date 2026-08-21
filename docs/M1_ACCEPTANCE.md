# M1 — Reproducible Evidence Graph Acceptance

Status: **DONE — measured clean reproduction completed 2026-08-21**

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
- [x] Labeled Japanese entity-resolution evaluation corpus built and exercised.
- [x] Thresholds calibrated and precision/recall/false-positive metrics published.

Artifacts:

- `docs/ENTITY_RESOLUTION.md`
- `docs/results/M1_IDENTITY_PILOT_2026-07-31.md`
- `docs/results/M1_ENTITY_RESOLUTION_BENCHMARK_V01.md`
- `docs/results/M1_YENTE_BENCHMARK_V01.md`
- `docs/results/M1_SPLINK_BENCHMARK_V01.md`
- `docs/results/M1_2_FINAL_ENTITY_RESOLUTION_DECISION.md`

### C. Source registry

- [x] At least 10 candidate sources are documented.
- [x] Identity, military/arms, political-finance, human-rights and contextual-risk sources are represented.
- [x] Each source records evidence scope and main limitations.
- [x] License/terms uncertainty is explicit rather than guessed away.
- [x] First integration order is defined.
- [x] First identity-spine adapters implemented for JPX, EDINET, NTA and GLEIF.
- [x] Source hashes/identifiers are recorded in the real pilot result.
- [ ] Pin exact terms/license URLs for each future evidence source selected for redistribution/ingestion.

The remaining unchecked item is an ongoing source-onboarding requirement for future sources, not a claim that redistribution rights have been cleared. Current M1 evidence workflows keep uncertain reuse status as `review_required` and do not redistribute the raw MOD workbook or political-finance PDF in CI artifacts.

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
- [x] Evidence-adapter-specific high-priority threats are executable regression/workflow gates.

Artifacts:

- `docs/THREAT_MODEL.md`
- `tests/test_m1_reproduction.py`
- `.github/workflows/m1-reproduction.yml`

## M1 implementation sequence

### M1.1 — Identity spine — DONE

Implemented and verified using:

1. JPX listed-company metadata;
2. EDINET filer identifiers and submitter corporate numbers;
3. Japanese Corporate Number Publication Site full data;
4. GLEIF LEI where an exact Japanese registration ID exists.

Result: 100/100 pilot issuers received EDINET and corporate-number links; 100/100 corporate numbers were independently found in the NTA full dataset; 7 exact LEIs were attached; 0 entities were disputed or unresolved. Two executions produced the same semantic payload SHA-256.

See `docs/results/M1_IDENTITY_PILOT_2026-07-31.md`.

### M1.2 — Entity matcher benchmark — DONE

The labeled Japanese benchmark and source-verified cases were used to calibrate the conservative resolution policy. Consequential name-only matches remain review-only; strong-ID conflicts become `DISPUTED`.

See `docs/results/M1_2_FINAL_ENTITY_RESOLUTION_DECISION.md` and the benchmark reports in `docs/results/`.

### M1.3 — First evidence adapter: Ministry of Defense procurement — DONE

The fixed official procurement snapshot is parsed into narrow contract observations and schema-valid claims after conservative identity resolution. Contracts do **not** map directly to weapons activity.

See `docs/results/M1_3_MOD_PROCUREMENT_ADAPTER_V01.md`.

### M1.4 — Contract-subject semantics — DONE

Contract subjects are classified independently as military-specific, dual-use, ordinary civilian procurement or unknown, retaining exact subject/provenance and routing ambiguous cases to review.

See `docs/results/M1_4_CONTRACT_SUBJECT_SEMANTICS_V01.md`.

### M1.5 — Political-finance adapter — DONE

The fixed organizational/corporate filing section is processed conservatively. OCR/name-only donor observations remain unresolved and review-required unless a strong identifier and review are supplied; the real sample therefore correctly emitted zero claims.

See `docs/results/M1_5_POLITICAL_FINANCE_ADAPTER_V01.md`.

### M1.6 — Evidence card — DONE

Human-readable cards are generated from schema-backed claims and expose identity, exact narrow claim, provenance, adjudication, entity-resolution review state, correction history, challenge path, and a visible evidence/policy boundary.

See `docs/results/M1_6_EVIDENCE_CARDS_V01.md`.

### M1.7 — Reproduction test — DONE

A clean GitHub-hosted checkout executes two real evidence adapters against fixed source hashes, regenerates a frozen 11-entity/11-claim canonical graph and Evidence Cards, demonstrates `CONFIRMED → DISPUTED` correction propagation, demonstrates `CONFIRMED → EXPIRED`, and proves a source outage degrades to `UNKNOWN / NONE` rather than PASS/EXCLUDE.

The complete real-source pipeline is deleted and rerun in the same CI job. Both executions produced canonical graph SHA-256:

`0a4f9ed031eaa534e116dca9c441e08054be49047b4404832a14a48094cf2e15`

See `docs/results/M1_7_REPRODUCTION_V01.md`.

## M1 exit condition

All seven M1 exit conditions are now satisfied:

1. **PASS** — a fixed pilot universe is represented by stable canonical entity IDs;
2. **PASS** — consequential entity links are deterministic or routed through calibrated conservative review rules;
3. **PASS** — two real evidence adapters are executed end to end;
4. **PASS** — canonical claims retain source provenance and a versioned reproducible rule path;
5. **PASS** — correction, dispute and expiry behavior is demonstrated end to end;
6. **PASS** — a third party can regenerate the versioned graph from documented inputs in a clean environment;
7. **PASS** — M1 threat-model blockers are enforced by regression tests/workflow gates.

**M1 — Reproducible Evidence Graph is complete as of 2026-08-21.**

The project may now shift its center of gravity to M2 user-policy evaluation and Peace Capital paper portfolios. This milestone does not relax the pre-real-money gates in `docs/THREAT_MODEL.md`; real-money execution remains prohibited.
