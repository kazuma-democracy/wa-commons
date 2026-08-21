# M1.3 Ministry of Defense Procurement Adapter v0.1

Status: **PASS — fixed official snapshot parsed and validated in GitHub Actions on 2026-08-21**.

Related issue: #14.

## Fixed source snapshot

Publisher: Japan Ministry of Defense (Minister's Secretariat / internal bureaus procurement disclosure).

Registry page:

`https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/index.html`

Pinned source file:

`https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/fy2026/04_buppin_k.xlsx`

Snapshot ID: `fy2026-04-buppin-competitive`.

Measured source SHA-256:

`c1f37e838d66ffa7bc62c35c5d8830c75ed7b92b0befe0c380f0d79052c773e8`

The corresponding official PDF is the April FY2026 disclosure for competitive procurement of goods/services. The source contains Japanese corporate numbers, contract dates, supplier names/addresses, planned prices, contract amounts and exact subject text.

## Measured run

GitHub Actions run `32484157919` successfully downloaded and parsed the pinned official XLSX.

- real contract observations: **88**
- identity `AUTO_LINK`: **86**
- unresolved observations: **2**
- generated EvidenceClaims: **86**
- EvidenceClaims validated against the canonical v0.1 schema: **86 / 86**
- targeted adapter tests: **4 / 4 passed**

The two unresolved observations remain in the observation output and do not become confirmed claims.

## Safety semantics

This adapter implements one narrow proposition only:

`received_contract_from_japan_ministry_of_defense`

A MOD contract is **not** converted into `weapons_activity`, `military_specific`, `EXCLUDE`, or any other policy result.

The exact contract subject is preserved verbatim for the separate M1.4 subject-semantics task. The real fixed snapshot itself proves why this separation is necessary. Civilian guard examples detected in the measured run include:

- `鉛筆 ＨＢ外２８５件（単価契約）一式`
- `紙（ＰＰＣ用 Ａ４）外３件（単価契約）一式`
- `記念館等空調設備補修役務一式`
- `広報資料発送役務（単価契約）一式`
- `自動車修理等役務（トヨタ車）（単価契約）一式`
- `自動車修理等役務（日産車）（単価契約）一式`

These records remain ordinary `military_contract` observations at this layer; the adapter does not infer weapons activity from the contracting authority.

## Identity resolution

Supplier identity goes through the M1.2 `wa-conservative-v0.2` decision layer.

- a valid source-published 13-digit Japanese corporate number is treated as a strong identifier and can produce `AUTO_LINK`;
- missing/malformed corporate number remains `UNRESOLVED`;
- supplier name alone never creates a consequential identity link;
- unresolved observations are retained but are not transformed into confirmed EvidenceClaims.

The entity key produced for a resolved supplier is `jp:corporate-number:<13-digit-number>`.

## Observation fields

Each parsed observation retains:

- exact contract subject/title;
- supplier name and address as published;
- Japanese corporate number where published;
- contract date;
- contract amount where published;
- planned price where published;
- contracting authority text;
- official source URL and registry-page URL;
- workbook sheet + row locator;
- retrieval timestamp;
- SHA-256 of the downloaded source snapshot;
- adapter and snapshot versions;
- identity decision and resolved entity ID when applicable.

Canonical claim/evidence IDs use a deterministic SHA-256-derived ASCII key, while the human-readable Japanese sheet/row locator is preserved separately in evidence provenance.

## Observation → EvidenceClaim transformation

Only `AUTO_LINK` observations become claims.

The claim uses:

- category: `military_contract`;
- predicate: `received_contract_from_japan_ministry_of_defense`;
- source type: `official_contract`;
- identity method: `deterministic_identifier`;
- policy context: `null`;
- exact subject text inside the claim value;
- `license_status=review_required` pending a separate redistribution-rights determination.

The CI runner validates **every real generated claim**, not only the fixture, against `schemas/evidence-claim.v0.1.schema.json`.

## Acceptance result

Issue #14 acceptance is satisfied by the measured run:

- >=50 real records: **PASS (88)**;
- entity resolution through the M1 identity layer: **PASS**;
- ambiguous/failed identity remains unresolved: **PASS (2 retained unresolved)**;
- no contract → `EXCLUDE` or contract → `weapons_activity` inference: **PASS**;
- clearly civilian procurement regression coverage: **PASS**;
- output validates against EvidenceClaim: **PASS (86 / 86)**.

The workflow uploads derived observations, claims and the run report but deliberately does **not** upload the raw government workbook while source reuse/redistribution terms remain marked `review_required`.

Artifact from the measured run: `mod-procurement-pilot-v01`, artifact ID `9447194405`. The raw official workbook is not included in that artifact.
