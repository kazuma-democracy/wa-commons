# M1.3 Ministry of Defense Procurement Adapter v0.1

Status: **implementation candidate; CI must verify the fixed official snapshot before issue #14 closes**.

Related issue: #14.

## Fixed source snapshot

Publisher: Japan Ministry of Defense (Minister's Secretariat / internal bureaus procurement disclosure).

Registry page:

`https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/index.html`

Pinned source file:

`https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/fy2026/04_buppin_k.xlsx`

Snapshot ID: `fy2026-04-buppin-competitive`.

The corresponding official PDF is the April FY2026 disclosure for competitive procurement of goods/services. It contains source-published Japanese corporate numbers, contract dates, supplier names/addresses, planned prices, contract amounts and exact subject text.

## Safety semantics

This adapter implements one narrow proposition only:

`received_contract_from_japan_ministry_of_defense`

A MOD contract is **not** converted into `weapons_activity`, `military_specific`, `EXCLUDE`, or any other policy result.

The exact contract subject is preserved verbatim for the separate M1.4 subject-semantics task. This is important because the fixed snapshot contains clearly ordinary procurement such as pencils, PPC paper, air-conditioning repair, document shipping and automobile repair alongside other MOD work.

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

Tests validate the generated object against `schemas/evidence-claim.v0.1.schema.json`.

## Acceptance gate

`.github/workflows/mod-procurement-pilot.yml` downloads the fixed official XLSX, runs the targeted adapter tests, parses the real snapshot, and requires:

- at least 50 real contract observations;
- at least one resolved EvidenceClaim;
- preservation of at least one clearly civilian subject;
- name-only fixture remains unresolved;
- civilian fixture remains a `military_contract` fact and never becomes `weapons_activity`;
- generated claims validate against the canonical EvidenceClaim schema.

The workflow uploads observations, claims and the run report but deliberately does **not** upload the raw government workbook while source reuse/redistribution terms remain marked `review_required`.
