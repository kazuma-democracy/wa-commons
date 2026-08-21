# M1.2b Pinned yente Benchmark v0.1

Status: **protocol implemented; measured CI results pending**.

Related issue: #26. Parent acceptance gate: #13.

## Scope

This increment measures OpenSanctions yente against the same 420-case WA Commons M1.2 corpus used by the transparent baseline:

- 400 synthetic adversarial cases;
- 20 source-verified Japanese cases.

It does **not** select the final matcher or production threshold. Threshold selection belongs to M1.2d (#28), after the alternative matcher comparison in #27.

## Pinned environment

- yente container: `ghcr.io/opensanctions/yente:5.5.0`
- index backend: `docker.elastic.co/elasticsearch/elasticsearch:9.4.2`
- matching algorithm: `logic-v2`
- dataset: local `wa_benchmark` only
- OpenSanctions production datasets: **not loaded**

The local-only dataset avoids mixing external screening data or its dataset licensing into this matcher benchmark.

## Reproduction

The GitHub Actions workflow `.github/workflows/yente-benchmark.yml` executes the complete run:

1. install the WA Commons package and run unit tests;
2. export all 420 candidate-side records as line-oriented FollowTheMoney `Company` entities;
3. write the corresponding query-side benchmark observations;
4. start the pinned Elasticsearch container;
5. run `yente reindex --force` against the local manifest;
6. start the pinned yente API;
7. POST the queries to `/match/wa_benchmark` using `logic-v2`;
8. preserve per-case paired score/rank and top results;
9. publish score summaries and measurement curves for both provenance classes.

Local reproduction uses the same steps, beginning with:

```sh
python scripts/export_yente_benchmark.py
docker compose -f docker-compose.yente-benchmark.yml up -d index
docker compose -f docker-compose.yente-benchmark.yml run --rm yente yente reindex --force
docker compose -f docker-compose.yente-benchmark.yml up -d yente
python scripts/run_yente_benchmark.py
```

## Adapter semantics

The benchmark adapter maps each record to a FollowTheMoney `Company` with the available subset of:

- `name`;
- `jurisdiction`;
- `address`;
- `registrationNumber`.

WA strong identifiers are namespaced before entering the generic registration-number field:

- `CORP:<Japanese corporate number>`;
- `LEI:<LEI>`;
- `EDINET:<EDINET code>`;
- `JPX:<security code>`.

This namespacing prevents unrelated identifier systems from being treated as the same raw namespace.

## Measurement policy

The runner records the raw paired yente score for every case and reports descriptive curves at score cuts 0.50, 0.60, 0.70, 0.80, 0.90 and 0.95.

Those cuts are **measurement points only**. They are not an adopted AUTO_LINK threshold. REVIEW cases are excluded from binary MATCH/NON_MATCH precision/recall calculations but remain in the raw output and score summaries.

Outputs:

- `artifacts/yente-benchmark/yente-report.json`;
- `artifacts/yente-benchmark/yente-rows.json`;
- `artifacts/yente-benchmark/queries.json`;
- `artifacts/yente-benchmark/candidates.ftm.json`.

## Acceptance still pending

This document must be updated with the actual CI measurements before #26 is closed. #13 remains open regardless of the M1.2b result.
