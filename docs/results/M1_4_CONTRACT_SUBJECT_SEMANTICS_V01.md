# M1.4 Contract-Subject Evidence Semantics v0.1

Status: **implementation candidate; real-snapshot CI measurement pending**.

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

## Labeled fixtures

`tests/fixtures/contract_subject_labels.json` contains 21 labeled cases covering all four categories, including deliberate conflicts:

- clearly military-specific weapon/platform language;
- clearly civilian examples copied from the M1.3 fixed MOD snapshot;
- dual-use information/communications/sensor examples;
- vague unmatched examples;
- mixed military + dual-use and civilian + dual-use examples that must become `UNKNOWN`.

The CI runner publishes a full 4x4 confusion matrix and error rows. Any labeled error fails the M1.4 workflow.

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

## Real-snapshot gate

`.github/workflows/contract-subject-semantics.yml` re-downloads the same fixed FY2026 April competitive goods/services XLSX used by M1.3 and requires:

- at least 50 parsed real records;
- zero errors on the labeled fixture set;
- at least one real `CIVILIAN` classification;
- at least one real `UNKNOWN` review item, guarding against an overconfident classifier;
- classification claims only for suppliers that passed the M1.3 identity-resolution gate;
- every generated classification claim validates against the canonical EvidenceClaim schema.

The workflow publishes the classification distribution, review-queue burden, confusion matrix and classified rows for inspection.
