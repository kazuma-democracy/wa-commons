# Entity Resolution for WA Commons

Status: **M1.2 final decision — `wa-conservative-v0.2`**

Related issues: #13, #28

## Decision

WA Commons uses a **tiered entity-resolution pipeline** in which fuzzy matchers generate candidates but do not establish consequential identity facts by score alone.

1. **Deterministic strong identifiers first** — Japanese corporate number, LEI, EDINET code, JPX security code, and future source-native identifiers with explicit namespaces.
2. **Explicit conflict checks** precede any automatic link.
3. **yente 5.5.0 / logic-v2** is the primary fuzzy candidate-generation service for M1.
4. **Splink 4.0.16 / DuckDB** remains an evaluation and batch-linkage signal.
5. **`wa-conservative-v0.2` is the identity-decision policy.**
6. Human review is required whenever no aligned strong identifier establishes identity.
7. A later policy change requires a new version and must not silently rewrite historical decisions.

The key principle is that entity resolution is itself evidence. A high-scoring name match must never silently become an identity fact.

## Why this matters

WA Commons may join records such as:

- a Japanese issuer name in EDINET;
- a Ministry of Defense supplier name;
- a donor name in a political-finance filing;
- a parent/subsidiary name in an international dataset;
- an English transliteration used by an NGO or intergovernmental report.

A false match can wrongly attribute military activity, political finance, or a human-rights allegation to the wrong company. Therefore false-positive avoidance has priority over automatic-link recall.

## Measured matcher decision

The M1.2 labeled corpus contains 420 cases: 400 synthetic adversarial cases and 20 source-verified Japanese cases.

| Component | Measured behavior | M1 role |
| --- | --- | --- |
| `wa-conservative-v0.2` | 0 benchmark false-positive AUTO_LINKs; 60.63% automatic-link recall; high review burden | **Identity decision policy** |
| yente `5.5.0`, `logic-v2` | At descriptive 0.70: 75.12% precision / 60.63% recall / 46.36% FPR overall; 80% / 100% / 10% on sourced subset | **Primary fuzzy candidate generator; score never auto-links** |
| Splink `4.0.16`, DuckDB | At descriptive 0.50: 100% precision / 40.16% recall / 0% FPR overall; sparse training left some comparison levels on defaults | **Secondary/batch signal; score never auto-links** |

Full measurements and limitations are in:

- `docs/results/M1_YENTE_BENCHMARK_V01.md`;
- `docs/results/M1_SPLINK_BENCHMARK_V01.md`;
- `docs/results/M1_2_FINAL_ENTITY_RESOLUTION_DECISION.md`.

## Final M1 resolution algorithm

```text
source record
   ↓
normalize strings / preserve identifier namespaces
   ↓
compare strong identifiers
   ├─ any observed strong-ID conflict → DISPUTED → human review
   ├─ one or more strong IDs align, no conflict → AUTO_LINK
   └─ no aligned strong ID
        ↓
   fuzzy candidate generation / attribute comparison
        ├─ yente >= 0.70 → REVIEW candidate
        ├─ Splink >= 0.50 → REVIEW candidate
        ├─ plausible name/address evidence → REVIEW
        └─ insufficient evidence → NON_MATCH
```

Fuzzy routing points are matcher-specific measurement points, not shared probabilities and not production identity thresholds.

## Hard safety invariants

- **Name-only consequential matches never AUTO_LINK.**
- An AUTO_LINK in M1 requires at least one aligned strong identifier and no conflicting strong identifier.
- A conflicting Japanese corporate number, LEI, EDINET code, or JPX security code forces `DISPUTED` / manual review.
- A yente or Splink score can never override a strong-ID conflict.
- Parent and subsidiary entities remain distinct; relationship similarity does not collapse identity.
- AUTO_LINK does not imply automatic publication of a consequential downstream claim.

## Calibrated review-routing points

### yente

Pinned configuration:

- version: `5.5.0`;
- algorithm: `logic-v2`;
- local WA dataset for the benchmark;
- review-routing point: `0.70`.

The sourced benchmark showed one false positive at score `0.8` while all four documented historical-continuity positives scored `0.85`. Raising the score to `0.90` removed the false positive but also removed every known positive. Therefore yente has no accepted score-only AUTO_LINK threshold in M1. The `0.70` point is used only to surface review candidates.

### Splink

Pinned configuration:

- version: `4.0.16`;
- DuckDB backend;
- `link_only`;
- M1.2c unsupervised parameter-estimation configuration;
- review-routing point: `0.50`.

At `0.50`, the sourced subset had 100% precision and 50% recall; at `0.70` and above none of the four sourced continuity positives were recovered. The CI run also observed untrained comparison levels that used defaults. Splink therefore remains review/batch evidence rather than an identity authority in M1.

## Final policy benchmark outcome

`wa-conservative-v0.2` deliberately sends no-ID name/address matches to review instead of auto-linking them.

Combined 420 cases:

- TP 154;
- FP 0;
- FN 100;
- TN 166;
- precision 100%;
- recall 60.63%;
- false-positive rate 0%;
- REVIEW 206 / 420 = 49.05%;
- DISPUTED 60 / 420 = 14.29%.

The review burden is intentionally high for M1. Reducing it requires new independently sourced labeled data and a new versioned policy, not an undocumented threshold change.

## Required identity fields

Every entity should support, where available:

- canonical name;
- aliases and transliterations;
- jurisdiction;
- legal form;
- address;
- LEI;
- Japanese corporate number;
- EDINET code;
- ISIN;
- exchange + ticker/security code;
- source-native IDs;
- parent/subsidiary relationships with dates.

Names are never sufficient when a stronger identifier is available.

## Provenance requirement

Every link stores:

- decision-policy version;
- fuzzy matcher + version/config if used;
- input fields;
- candidate ID;
- score/confidence signals;
- aligned attributes;
- conflicting attributes;
- decision/review status;
- source provenance;
- review timestamp/person if applicable;
- correction history.

A later matcher upgrade must not silently rewrite history. Reconciliation changes should create a correction record.

## Licensing rule

Open-source software licensing and dataset licensing are separate questions. yente and FollowTheMoney being open-source does **not** make every dataset used with them unrestricted. Each source in `docs/SOURCE_REGISTRY.md` keeps its own license/terms status.
