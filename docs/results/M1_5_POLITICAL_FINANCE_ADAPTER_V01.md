# M1.5 Japanese political-finance evidence adapter v0.1

Status: **measured pilot**  
Issue: #16  
Adapter version: `0.1`  
Identity policy: `wa-conservative-v0.2`

## Scope

M1.5 adds a conservative adapter for published Japanese political-finance reports. The pilot deliberately records **narrow disclosed transaction observations**, not political ideology, corruption, influence, endorsement, or a downstream portfolio decision.

The fixed source is the Ministry of Internal Affairs and Communications (Japan) 2023 annual political-finance report for `一般財団法人国民政治協会`, publication set dated 2024-11-29. The production pilot uses part 18, independently located during bounded source inspection as the filing section for `法人・その他の団体`.

- source ID: `jp-political-finance`
- fixed source URL: `https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/contents/SS20241129/006710_215018.pdf`
- snapshot version: `soumu-SS20241129-kokumin-seiji-kyokai-r5`
- source SHA-256: `e8871ed2cb62729ec8a8c01028c3da2f797a6f65972abfb8dc4dcf757f11c8fe`
- fixed page range: PDF pages 1-60 of part 18
- reporting period: 2023

The report is primarily scanned/image content. M1.5 therefore renders only the fixed page range and uses Tesseract TSV coordinates to recover conservative donor/amount row candidates. Plain OCR separators are not trusted because the table grid is not reproduced consistently in text output.

## Measured result

GitHub Actions run `32491024723` (`political-finance-pilot`, run #9) completed successfully.

| Measure | Result |
|---|---:|
| Fixed organizational/corporate transaction observations | **52** |
| Identity `AUTO_LINK` | **0** |
| Identity unresolved | **52** |
| OCR extraction review required | **52** |
| EvidenceClaims emitted from the real OCR sample | **0** |
| Targeted tests | **6 passed** |

The 52 observations satisfy the issue requirement for a fixed sample of at least 50 disclosed organizational/corporate transactions. Each observation records the donor name as OCR-extracted, recipient, amount, reporting year, filing/report identifier or fixed part/page fallback, source URL, retrieval timestamp, source hash, and a locator of the form `pdf_part=18;page=<page>;ocr_top=<coordinate>`.

The CI artifact contains only derived review-required `observations.json` and `report.json`. The official PDF and rendered page images are transient working inputs and are not redistributed by the workflow while reuse terms remain `review_required`.

Artifact:

- name: `political-finance-pilot-v01`
- artifact ID: `9449807279`
- ZIP SHA-256: `4e970e77afbfffdde4e191b06282cdfe94efdb79e234f6d3d858c46c986a39a5`

## Identity and claim gate

The political-finance filing normally supplies printed names/addresses rather than a strong corporate identifier. M1.5 therefore reuses the M1 identity policy rather than weakening it for this source:

1. a printed/OCR donor name alone never `AUTO_LINK`s;
2. same/similar names remain unresolved without a strong identifier;
3. a separately verified 13-digit Japanese corporate number is routed through `wa-conservative-v0.2`;
4. OCR-derived observations remain `extraction_review_required=true` even if a strong identifier is later supplied;
5. `observation_to_claim` emits an EvidenceClaim only after both strong-ID resolution and extraction review.

Consequently, **0 real-sample claims is an intentional safety result, not a failed extraction**. The source supplied enough narrow transaction observations to exercise the adapter, but it did not supply the strong identifiers required for safe automatic donor linkage. An unresolved or disputed donor cannot trigger exclusion.

A reviewed/resolved fixture exercises the documented observation-to-EvidenceClaim transformation and validates it against `schemas/evidence-claim.v0.1.schema.json`. The resulting claim uses category `political_finance`, predicate `reported_political_donation`, preserves filing/source provenance, and keeps `policy_context=null`.

## Semantic boundary

A disclosed donation supports only the narrow fact represented by the filing. M1.5 does **not** infer that the donor:

- agrees with every policy or statement of the recipient;
- has a left/right or other political ideology;
- exerted influence or received a benefit;
- engaged in corruption or wrongdoing;
- should be `PASS`, `WATCH`, or `EXCLUDE`.

Those conclusions require different evidence and, where applicable, explicit downstream user policy.

## Personal-data minimization

M1.5 focuses on corporate/organizational donors. During bounded source discovery, filing form sections were distinguished before the production sample was fixed. Individual-donor sections (`*-1-*`) are not processed by the production pilot. Part 18 was selected for the `法人・その他の団体` section (`*-2-*`).

## Tests and failure modes

The targeted suite covers:

- same/similar donor names remain unresolved without a strong identifier;
- strong identifiers route through the existing M1 identity policy;
- TSV geometry extracts donor/amount columns and handles continuation rows;
- merged table/OCR artifacts with impossible digit runs or amounts are rejected before integer conversion;
- unresolved or unreviewed OCR observations cannot become claims;
- a reviewed + strongly resolved fixture produces a narrow schema-valid claim without ideology labels.

An earlier real run exposed a merged OCR artifact containing thousands of digits in the amount region. The parser now rejects oversized digit runs and amounts above the explicit pilot bound rather than trying to repair or guess them. This failure is preserved as a regression test.

## Limitations

This pilot is deliberately conservative and is **not a completeness or production-accuracy estimate**. Many real rows are missed because uncertain OCR/table reconstructions are dropped rather than guessed. The 52 extracted observations are sufficient to test the M1.5 pipeline, but no conclusion should be drawn from omitted rows.

OCR donor names and amounts require source review before claim publication. Future work can reduce review burden with better source-native structured data, stronger identifiers, or separately measured extraction improvements, but must not relax the M1 identity rule silently.

## Acceptance review

- fixed sample >=50 organizational/corporate transactions: **PASS (52)**
- reproducible extraction from fixed source set: **PASS** — pinned report part/page range, URL, snapshot version and source hash
- same/similar-name ambiguity fixture: **PASS**
- claim provenance and filing locator: **PASS** in the reviewed/resolved claim transformation; unresolved real observations are intentionally held pre-claim
- no direct political ideology label: **PASS**
- M1 identity layer used; name-only ambiguity unresolved: **PASS**
- UNKNOWN/DISPUTED identity cannot trigger exclusion: **PASS**
- personal-data minimization: **PASS** — production pilot excludes individual-donor sections
