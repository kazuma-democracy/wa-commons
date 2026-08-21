# WA Commons Evidence Model v0.1

Related issue: #2

The evidence model is designed to prevent one dangerous shortcut:

> **observation → moral label**

WA Commons instead requires:

```text
Observation
   ↓
Evidence Claim
   ↓
Adjudication
   ↓
User Policy
   ↓
PASS / WATCH / EXCLUDE / NONE
   ↓
Research or authorized action
```

## Layer 1 — Observation

An observation is what a source actually says or records.

Examples:

- a government contract record names supplier X and contract subject Y;
- a political-finance report lists donor X, recipient Y and amount Z;
- a company filing reports revenue for a defence segment;
- an OECD NCP record says a specific instance was submitted and later concluded;
- a regulator officially lists an entity under a defined legal framework.

Observation does not contain WA Commons ideology.

## Layer 2 — Evidence Claim

A claim is a narrow normalized proposition connected to one or more observations.

Good:

- `received_contract_from = Japan Ministry of Defense`
- `contract_subject = office furniture`
- `reported_arms_revenue = 1200000000 USD`
- `reported_donation_to = X`
- `was_named_in_public_allegation = Y`
- `was_officially_listed_under = Z`

Bad:

- `bad_company = true`
- `war_profiteer = true`
- `supports_country_X = true` based only on ordinary business presence
- `human_rights_abuser = true` based only on a complaint

## Layer 3 — Adjudication

Adjudication answers: **how strongly does the available evidence support this exact claim?**

Statuses:

- `confirmed` — evidence supports the narrow claim under the current rule set;
- `disputed` — material evidence or identity resolution conflicts;
- `unknown` — insufficient evidence to decide;
- `expired` — evidence is outside its validity/lookback context or needs revalidation.

Confidence is not a moral score. It represents confidence in the factual/adjudicated claim.

## Layer 4 — User Policy

A user policy decides what a confirmed/disputed/unknown claim means for that user.

Two users can lawfully reach different decisions from the same evidence graph.

Example:

```text
Claim: Company A has 2% military-specific revenue.

User profile 1:
  exclude if military revenue > 0%
  → EXCLUDE

User profile 2:
  exclude only controversial weapons
  → PASS or NONE

User profile 3:
  military evidence is informational only
  → WATCH
```

The evidence is shared. The values are not forced.

## Layer 5 — Action Authority

A policy result does not automatically authorize an action.

M1/M2 examples:

- produce an evidence card: allowed;
- generate a paper portfolio: allowed;
- notify that evidence changed: allowed when configured;
- execute a real trade: **not allowed in v0**;
- post a public accusation automatically: **not allowed**.

## Source semantics

### Government contract

A contract proves the narrow procurement relationship. The contract subject determines whether it is military-specific, dual-use, or ordinary civilian procurement.

### Political donation

A reported donation proves a disclosed financial transaction when identity is resolved. It does not prove agreement with every policy of the recipient.

### Complaint / allegation

A complaint proves that an allegation was made. A later proceeding or finding is a separate claim.

### Specialist estimate

A SIPRI-style arms-revenue estimate should be stored as an attributed estimate with methodology/source, not transformed into an unqualified company self-report.

### Negative search result

Failure to find evidence is not evidence of absence unless the source has defined comprehensive coverage for the relevant claim.

## Corrections

Corrections are append-oriented:

1. retain old claim/evidence version;
2. add contradictory/new evidence;
3. change adjudication status;
4. add correction reason;
5. re-evaluate dependent policy outputs.

Do not silently erase an error; the correction process is part of project credibility.

## Machine/LLM role

Models may:

- extract candidate structured facts from documents;
- propose entity matches;
- summarize evidence;
- flag conflicts;
- queue records for review.

Models may not create a consequential factual claim without a retrievable source and locator. `model confidence` never substitutes for evidence provenance.

## Schema

Canonical bootstrap schema:

- [`schemas/evidence-claim.v0.1.schema.json`](../schemas/evidence-claim.v0.1.schema.json)
- [`schemas/examples/evidence-claim.examples.json`](../schemas/examples/evidence-claim.examples.json)

The examples intentionally include:

- a defence-ministry contract that does **not** imply weapons activity;
- a political-finance transaction separated from user policy;
- an unresolved allegation kept at `UNKNOWN/WATCH`;
- a false entity match corrected from `confirmed` to `disputed`.
