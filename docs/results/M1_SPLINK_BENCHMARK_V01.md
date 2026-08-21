# M1.2c Splink Benchmark v0.1

Status: **protocol implemented; measured CI results pending**.

Related issue: #27. Parent acceptance gate: #13.

## Scope

This increment compares one reuse-first alternative matcher, Splink, against the existing WA conservative baseline on the identical 420-case M1.2 corpus:

- 400 synthetic adversarial cases;
- 20 source-verified Japanese cases.

It does **not** choose the final production matcher or threshold. That decision remains M1.2d (#28).

## Why Splink

Splink is a mature open-source probabilistic record-linkage framework with a DuckDB backend, explicit comparison features, blocking rules, inspectable model parameters, and reproducible batch linkage. It is meaningfully different from yente's search/matching API and therefore provides a useful alternative benchmark without inventing another matcher.

Pinned version: `splink==4.0.16`.

## Apples-to-apples policy

The same `build_m12_corpus()` cases are used. Each WA observation maps directly to separate Splink columns for:

- name;
- Japanese corporate number;
- LEI;
- EDINET code;
- JPX security code;
- jurisdiction;
- address.

Missing identifiers are NULL, not empty strings, so missing-on-both-sides cannot become accidental evidence of equality.

The benchmark truth labels (`MATCH`, `NON_MATCH`, `REVIEW`) are **not used to train Splink**. They are used only after inference to measure the paired case score.

## Model/training protocol

- link type: `link_only`;
- backend: DuckDB;
- prior probability: `1/420`;
- u probabilities: random-pair sampling with a fixed seed;
- m probabilities: unsupervised expectation-maximisation blocks on available high-signal observed attributes;
- prediction candidate blocking includes jurisdiction and exact high-signal attributes so every intended WA case pair remains observable.

If an EM block is not estimable, the runner preserves that skipped stage and error message in the report instead of silently changing the model.

## Outputs

The workflow `.github/workflows/splink-benchmark.yml` writes:

- `artifacts/splink-benchmark/splink-report.json`;
- `artifacts/splink-benchmark/splink-rows.json`.

The report includes:

- raw paired Splink match probability per case;
- measurement curves at 0.50/0.60/0.70/0.80/0.90/0.95;
- source-verified and synthetic-adversarial splits;
- descriptive probability-band counts;
- the unchanged `wa-conservative-v0.1` baseline metrics;
- runtime/version and training metadata.

The measurement cuts and probability bands are descriptive only. They are not adopted AUTO_LINK or REVIEW thresholds.

## Acceptance still pending

This document must be updated with measured CI results, reproducibility notes, and an implementation-complexity comparison before #27 is closed. #13 remains open regardless of the M1.2c result.
