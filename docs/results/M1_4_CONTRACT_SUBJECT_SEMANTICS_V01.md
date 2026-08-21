# M1.4 Contract-Subject Evidence Semantics v0.1

Status: **PASS for issue #15 acceptance on the fixed M1.3 snapshot**.

Related issue: #15.

## Purpose

M1.4 classifies only the exact procurement subject text retained by M1.3. It does not infer meaning from the fact that the contracting authority is the Japan Ministry of Defense and it does not produce PASS/WATCH/EXCLUDE.

Rule version: `contract-subject-v0.1`.

Target categories:

- `MILITARY_SPECIFIC` — the subject explicitly names a narrowly military weapon/platform or military-specific control term;
- `DUAL_USE` — the subject explicitly names technology/services with substantial ordinary civilian and military uses;
- `CIVILIAN` — the subject explicitly names ordinary civilian goods/services;
- `UNKNOWN` — no sufficiently specific rule matches, or category signals conflict.

## Conservative rule policy

The deterministic classifier accepts **only contract subject text**. Contracting authority, supplier reputation, sector, political context and downstream policy are not features.

Examples of narrow military-specific tokens include `誘導弾`, `ミサイル`, `弾薬`, `小銃`, `魚雷`, `戦車`, `射撃統制`, and `火器管制`.

Examples of dual-use tokens include `情報システム`, `通信`, `ネットワーク`, `サイバー`, `衛星`, `ドローン`, `燃料`, `測定器`, and `センサ`.

Examples of ordinary civilian tokens include `鉛筆`, `PPC`, `空調`, `清掃`, `発送`, `印刷`, and `自動車修理`.

If more than one category family matches the same subject, the classifier does **not** choose a priority winner. It returns `UNKNOWN`, confidence `0.0`, and `review_required=true`.

Unmatched text follows the same fail-safe path to `UNKNOWN`.

## Labeled fixture measurement

`tests/fixtures/contract_subject_labels.json` contains 21 labeled cases covering all four categories, including deliberate conflicts:

- clearly military-specific weapon/platform language;
- clearly civilian examples copied from the M1.3 fixed MOD snapshot;
- dual-use information/communications/sensor examples;
- vague unmatched examples;
- mixed military + dual-use and civilian + dual-use examples that must become `UNKNOWN`.

Measured confusion matrix on CI run `contract-subject-semantics #1`:

| Expected \\ Actual | MILITARY_SPECIFIC | DUAL_USE | CIVILIAN | UNKNOWN |
|---|---:|---:|---:|---:|
| MILITARY_SPECIFIC | 5 | 0 | 0 | 0 |
| DUAL_USE | 0 | 5 | 0 | 0 |
| CIVILIAN | 0 | 0 | 6 | 0 |
| UNKNOWN | 0 | 0 | 0 | 5 |

Fixture errors: **0 / 21**.

This is a regression/behavior fixture, not an independent estimate of production accuracy. It proves the configured rules behave as labeled; it does not justify expanding the vocabulary without separate sourced review.

## Real fixed-snapshot measurement

Source: the same FY2026 April competitive goods/services XLSX used by M1.3.

Measured on 2026-08-21:

- records: **88**;
- `MILITARY_SPECIFIC`: **0**;
- `DUAL_USE`: **4**;
- `CIVILIAN`: **17**;
- `UNKNOWN`: **67**;
- review queue: **67 / 88 = 76.14%**;
- identity-resolved derived claims: **86**;
- schema-validated derived claims: **86 / 86**.

The zero `MILITARY_SPECIFIC` result must **not** be interpreted as proof that the Ministry of Defense had no military-specific procurement in April. It means only that this fixed disclosure contained no subject text that crossed the deliberately narrow `contract-subject-v0.1` military-specific rule gate.

Likewise, the 76.14% UNKNOWN rate is an explicit limitation of v0.1 rather than a reason to silently loosen rules. Reducing that review burden requires additional labeled/source-reviewed examples and a new versioned rule change.

## Error / failure review

Observed failure risk is currently dominated by **under-classification**, not false military attribution:

1. many real subjects are too specific, abbreviated, administrative, or domain-dependent for the narrow token list and therefore remain UNKNOWN;
2. category collisions are intentionally UNKNOWN rather than resolved by precedence;
3. the current labeled fixture set is small and partly designed from known behavior, so its zero-error result should not be treated as calibrated production accuracy;
4. no model-assisted fallback is enabled in v0.1; this avoids opaque confidence but leaves manual review burden high;
5. no conclusion about absence of military activity may be drawn from an UNKNOWN or unmatched result.

The main safety benefit is that the classifier cannot turn the words `Japan Ministry of Defense` into a military-specific classification by itself.

## Derived EvidenceClaims

An identity-resolved M1.3 observation can produce one narrow derived claim:

- category: `military_contract`;
- predicate: `contract_subject_classification`;
- original contract subject retained verbatim;
- original source locator retained;
- matched rule terms retained;
- classification and review flag retained;
- `rule_set_version=contract-subject-v0.1`;
- `policy_context=null`.

`UNKNOWN` claims use adjudication status `unknown` and remain reviewable. Other deterministic categories use `confirmed` for the narrow statement that the configured rule classified the recorded subject that way. The classifier does not create a separate generic `weapons_activity` accusation.

## Acceptance verification

`.github/workflows/contract-subject-semantics.yml` re-downloads the same fixed FY2026 April competitive goods/services XLSX used by M1.3 and verifies:

- at least 50 parsed real records;
- zero errors on the labeled fixture set;
- all four target categories represented in labeled fixtures;
- at least one real `CIVILIAN` classification;
- at least one real `UNKNOWN` review item, guarding against an overconfident classifier;
- classification claims only for suppliers that passed the M1.3 identity-resolution gate;
- every generated classification claim validates against the canonical EvidenceClaim schema;
- contracting authority is not a classifier feature;
- no user-policy decision is produced.

Artifact from the first successful measured run: `contract-subject-semantics-v01`, artifact ID `9448070491`, uploaded zip SHA-256 `758ad2cdf55713dcedb261660f283a90ea145b392dd4f6d24a845c8d5cd1d222`.
