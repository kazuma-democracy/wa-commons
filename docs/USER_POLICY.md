# WA Commons User Policy v0.1

Status: **proposal for M2 / Peace Capital paper research**  
Related issue: #5

## Purpose

A WA Commons user policy converts adjudicated factual claims into **that user's** research decisions. It does not change the evidence graph and it does not define an official WA Commons ideology.

```text
shared Evidence Claim + adjudication
             ↓
versioned user policy
             ↓
      EXCLUDE / WATCH / NONE
             +
      soft preference signals
             ↓
future paper-portfolio research
```

`PASS` is intentionally not emitted by policy v0.1. A rule failing to match is not proof that an entity is clean, safe, peaceful, or free of relevant activity. `NONE` means only: **this profile produced no exclusion/watch decision from this exact claim**.

## Exclusions versus preferences

### Exclusions

An exclusion rule is a hard routing instruction for a sufficiently supported factual claim. In v0.1 it can produce:

- `EXCLUDE` — this user does not want the matched confirmed evidence in the eligible universe;
- `WATCH` — surface the matched confirmed evidence but do not exclude it.

Rules match narrow evidence fields such as category, predicate, jurisdiction, source, confidence and a restricted condition over claim values. They do not match free-form moral labels.

### Preferences

A preference is deliberately separate from exclusion. It emits a signal:

- `prefer` or `avoid`;
- weight `0 < weight <= 1`.

A preference does **not** itself produce `EXCLUDE`. M2 portfolio code may later use these signals for bounded paper-portfolio weighting after a separate methodology is defined.

## Uncertainty is handled before exclusion rules

Each profile explicitly chooses `WATCH` or `NONE` for:

- `UNKNOWN`;
- `DISPUTED`;
- `EXPIRED`.

An uncertain claim never becomes `EXCLUDE` merely because its category would have matched a hard exclusion rule. This preserves M1's rule that missing, contradictory or stale evidence is not silently converted into guilt.

## Thresholds

Rules may set `min_confidence` from 0 to 1. Conditions use a restricted set of deterministic operators (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `exists`) and only whitelisted fields under `claim.value` plus `adjudication.confidence`.

This is intentionally less expressive than arbitrary code. The policy language should remain inspectable, reproducible and safe to share.

## Versioning and reproduction

Every policy contains:

- `profile_id` — stable identity of the policy family;
- `profile_version` — explicit version of its current rules;
- origin metadata and optional `forked_from`;
- all uncertainty, exclusion and preference rules needed to evaluate it.

A reproducible paper result must record both the Evidence Graph version/hash and `(profile_id, profile_version)`. Changing a threshold or rule requires a new profile version rather than silently rewriting historical results.

## Sharing and forking without an official ideology

Every v0.1 profile must state:

```json
"official_status": "not_official"
```

Profiles may be authored by a user, community or as examples and may record `forked_from`. WA Commons can distribute example profiles to exercise the engine, but those examples are not endorsements or canonical moral rankings.

## Example profiles

`schemas/examples/user-policy.examples.json` contains three intentionally different examples:

1. **Strict military-specific activity avoidance** — excludes a confirmed `military_specific` contract-subject classification, while routing uncertainty to WATCH.
2. **Narrow controversial-weapons focus** — ordinary military-contract evidence does not match; exclusion is reserved for a narrower `controversial_weapons` category.
3. **Transparency-first informational profile** — military-contract and political-finance evidence are WATCH-only; human-rights evidence can emit a soft avoid preference rather than a hard exclusion.

The same confirmed military-specific claim therefore legitimately evaluates to `EXCLUDE`, `NONE`, or `WATCH` depending on the selected user profile. The shared evidence remains unchanged.

## Action boundary

Policy evaluation is research logic only. It does not authorize:

- real-money trades;
- automatic public accusations;
- contacting an entity;
- deleting or rewriting evidence.

Those remain separate authorization/governance questions.

## Machine-readable artifacts

- schema: `schemas/user-policy.v0.1.schema.json`
- examples: `schemas/examples/user-policy.examples.json`
- deterministic evaluator: `src/wa_commons/policy/evaluator.py`
- regression tests: `tests/test_user_policy.py`
