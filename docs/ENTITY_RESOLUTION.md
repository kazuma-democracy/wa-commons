# Entity Resolution for WA Commons

Status: **M1 design decision, v0.1**

Related issue: #3

## Decision

Use a **tiered entity-resolution pipeline** rather than one fuzzy matcher:

1. **Deterministic identifiers first** — LEI, corporate number, EDINET code, ISIN, ticker + exchange, or source-native IDs.
2. **Normalize and model entities with FollowTheMoney-compatible concepts** where useful.
3. **Use yente as the primary fuzzy/multi-attribute matching service** for records without a reliable exact identifier.
4. **Require human review in the ambiguity band** and for consequential classifications.
5. Keep **Splink/Dedupe as evaluation or batch-linkage alternatives**, not the first production dependency.

The key principle is that entity resolution is itself evidence. A high-scoring name match must never silently become an identity fact.

## Why this matters

WA Commons may join records such as:

- a Japanese issuer name in EDINET;
- a Ministry of Defense supplier name;
- a donor name in a political-finance filing;
- a parent/subsidiary name in an international dataset;
- an English transliteration used by an NGO or intergovernmental report.

A false match can wrongly attribute military activity, political finance, or a human-rights allegation to the wrong company. Therefore the cost of false positives is unusually high.

## Candidate comparison

| Candidate | Role | License / data caveat | Strengths | Weaknesses | WA Commons decision |
|---|---|---|---|---|---|
| **OpenSanctions yente** | Entity matching API | Software is MIT; OpenSanctions dataset has separate non-commercial/commercial terms | Query-by-example; multi-attribute matching; built for people/companies; self-hostable; active project; integrates with FollowTheMoney | Matching quality depends on available descriptors; hosted OpenSanctions data/API licensing is separate from code | **ADOPT for v0 matcher**, using our own/compatible datasets where needed |
| **FollowTheMoney** | Entity + relationship data model/toolkit | MIT software | Rich company/person/ownership/relationship model; lineage-oriented ecosystem; pairs naturally with yente | More expressive than the minimal WA schema; adopting it wholesale could overcomplicate M1 | **ADOPT concepts / adapter**, do not replace WA evidence schema |
| **Splink** | Probabilistic record linkage | OSS; verify exact current package/license before production pin | Strong for large batch linkage, explainable comparison weights, scalable backends | More tuning/data-engineering overhead; not specifically a screening API | **WATCH / benchmark** for batch Japanese datasets |
| **Dedupe** | Active-learning entity resolution | MIT software | Mature deduplication/linkage patterns; trainable | Interactive/training workflow adds operational burden; not a ready-made evidence graph | **WATCH / benchmark** |
| Custom name matcher | Bespoke | Our code | Full control | Reinvents normalization, scoring, review workflows; high false-positive risk | **REJECT for M1** |

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
- exchange + ticker;
- source-native IDs;
- parent/subsidiary relationships with dates.

Names are never sufficient when a stronger identifier is available.

## Resolution algorithm v0

```text
source record
   ↓
normalize strings/identifiers
   ↓
exact identifier match?
   ├─ yes → deterministic match (confidence 1.0 unless identifier conflict)
   └─ no
       ↓
construct multi-attribute query
       ↓
      yente
       ↓
score + conflicting-attribute checks
       ↓
 ┌──────────────┬───────────────────────┬────────────────┐
 │ high + clean │ ambiguity band        │ low/conflicting│
 │ auto-link*   │ human review required │ unresolved     │
 └──────────────┴───────────────────────┴────────────────┘
```

`*` Auto-link does not imply auto-publication of a consequential claim. The downstream evidence rule can still require human review.

## Initial conservative thresholds

The exact score scale must be calibrated on a labeled test set; do not hard-code these numbers as universal truth.

For the first evaluation corpus:

- deterministic identifier: accept unless conflicting identifiers exist;
- high fuzzy score with **at least two independent aligned attributes**: candidate for automatic link;
- name-only match: never auto-link a consequential claim;
- conflicting jurisdiction, corporate number, LEI, or address: force `disputed`/manual review;
- parent and subsidiary: keep distinct entities; relationships must not collapse identity.

## Japanese-specific test cases

M1 evaluation must include:

- 株式会社 prefix/suffix variation;
- full-width / half-width characters;
- old/new kanji and punctuation variation;
- English legal name vs Japanese name;
- common abbreviations;
- holding company vs operating subsidiary;
- mergers and historical names;
- duplicate company names in different prefectures/jurisdictions;
- ticker reuse or market changes;
- transliteration ambiguity.

## Evaluation set

Before production use, build a labeled corpus with at least:

- 100 easy exact matches;
- 100 alias/transliteration matches;
- 50 parent/subsidiary traps;
- 50 same/similar-name non-matches;
- 50 historical rename/merger cases;
- 50 deliberately incomplete records.

Report precision, recall, false-positive rate, and the size of the manual-review queue separately. For WA Commons, **false-positive precision is more important than maximizing automatic match rate**.

## Provenance requirement

Every link stores:

- matcher + version;
- input fields;
- candidate ID;
- score/confidence;
- matching attributes;
- conflicting attributes;
- review status;
- review timestamp/person if applicable.

A later matcher upgrade must not silently rewrite history. Reconciliation changes should create a correction record.

## Licensing rule

Open-source software licensing and dataset licensing are separate questions. yente and FollowTheMoney being MIT does **not** make every dataset used with them unrestricted. Each source in `docs/SOURCE_REGISTRY.md` keeps its own license/terms status.
