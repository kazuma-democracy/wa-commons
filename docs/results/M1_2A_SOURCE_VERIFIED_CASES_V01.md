# M1.2a Source-Verified Japanese Entity-Resolution Cases v0.1

Status: implementation candidate for issue #25.

## Scope

This increment adds a small factual Japanese subset to the existing 400-case synthetic adversarial entity-resolution corpus. It does **not** run yente, compare another matcher, or calibrate final production thresholds.

The combined M1.2 benchmark now keeps two provenance classes visibly separate:

- `synthetic_adversarial` — generated safety/calibration fixtures;
- `source_verified` — cases grounded in public official company or JPX material, with benchmark transformations explicitly noted.

## Source-verified subset

The v0.1 subset contains 20 cases across four safety-relevant shapes:

| Case type | Cases | Purpose |
| --- | ---: | --- |
| historical rename / continuity | 4 | Same listed legal entity across documented company-name changes |
| parent/subsidiary trap | 6 | Related group companies must remain separate legal entities |
| similar-name non-match | 4 | Overlapping Japanese names must not override conflicting listed identifiers |
| incomplete/review-only | 6 | Real sourced entities with identifiers deliberately removed from the benchmark observation |

Total: **20 source-verified cases** plus the unchanged **400 synthetic adversarial cases**.

## Public sources

### ZOZO

Official company announcement:

`https://corp.zozo.com/news/20181001-5984/`

The announcement records the 2018-10-01 change from 株式会社スタートトゥデイ to 株式会社ZOZO. The benchmark uses security code `3092` as the aligned listed-company identifier.

### LINE Yahoo / Z Holdings

Official corporate history:

`https://www.lycorp.co.jp/ja/company/history/z-holdings/`

The history records the 2019 transition from ヤフー株式会社 to Zホールディングス株式会社 and the later 2023 reorganization/name change to LINEヤフー株式会社. The benchmark uses security code `4689` as the listed-company continuity identifier.

### SoftBank Group / SoftBank Corp

Official SoftBank Group segment description:

`https://group.softbank/segments/softbank`

The source describes the SoftBank business segment centered on ソフトバンク株式会社 and its subsidiaries inside the wider SoftBank Group. The benchmark pairs listed identifiers `9984` and `9434` to ensure related group companies do not collapse into one identity.

### JPX-listed similar-name issuers

JPX stock search:

`https://www2.jpx.co.jp/tseHpFront/StockSearch.do`

The v0.1 subset includes distinct listed issuer pairs identified by separate security codes:

- 日本電気株式会社 `6701` vs 日本電気硝子株式会社 `5214`;
- 大和ハウス工業株式会社 `1925` vs 大和工業株式会社 `5444`;
- 三菱商事株式会社 `8058` vs 三菱食品株式会社 `7451`;
- 東京建物株式会社 `8804` vs 東京鐵鋼株式会社 `5445`.

These cases establish identity non-equivalence only; they make no inference about corporate relationships.

## Provenance convention

M1.2a intentionally avoids a schema migration. Each sourced case uses the existing `BenchmarkCase.provenance` field with a machine-readable prefix and key/value segments:

`source_verified|publisher=...|url=...|locator=...|retrieved=2026-08-21|note=...`

This keeps the increment small while making sourced and synthetic cases separable in reports. A later evidence-graph schema may replace this benchmark-local representation if needed.

## Benchmark transformations

Some cases deliberately vary spelling, legal-form abbreviations, English names, or remove identifiers. These transformations are regression fixtures, not additional factual assertions. Their provenance notes say so explicitly.

In particular, incomplete cases are built from real sourced entities but deliberately remove strong identifiers. They are expected to remain `REVIEW` and must never become consequential `AUTO_LINK` decisions from name alone.

## Reporting change

`evaluate()` now reports `by_provenance` alongside `by_type`, and row output includes both the provenance class and full provenance string. The benchmark runner uses the combined M1.2 corpus while `build_v01_corpus()` remains the unchanged 400-case synthetic baseline for regression compatibility.

## Limits

This is a small safety subset, not a statistically representative sample of Japanese corporate identity ambiguity. It does not estimate real-world frequencies. It is deliberately insufficient for final threshold selection.

Issue #13 must remain open. Next work is #26: run a pinned yente benchmark on the same combined corpus.