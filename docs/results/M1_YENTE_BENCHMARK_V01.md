# M1.2b Pinned yente Benchmark v0.1

Status: **PASS — reproducible measured run completed in GitHub Actions on 2026-08-21**.

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

The successful run indexed exactly **420 entities** and completed all **420 match cases**. The repository test suite also passed with **22 tests** in the same workflow.

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

## Measured results

REVIEW cases remain in raw output and score summaries but are excluded from binary MATCH/NON_MATCH precision/recall calculations. Score cuts below are measurement points only.

### Combined corpus

| Score cut | Precision | Recall | False-positive rate | TP | FP | FN | TN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.50 | 0.7333 | 0.6063 | 0.5091 | 154 | 56 | 100 | 54 |
| 0.60 | 0.7440 | 0.6063 | 0.4818 | 154 | 53 | 100 | 57 |
| 0.70 | 0.7512 | 0.6063 | 0.4636 | 154 | 51 | 100 | 59 |
| 0.80 | 0.7512 | 0.6063 | 0.4636 | 154 | 51 | 100 | 59 |
| 0.90 | 0.7500 | 0.5906 | 0.4545 | 150 | 50 | 104 | 60 |
| 0.95 | 0.7500 | 0.5906 | 0.4545 | 150 | 50 | 104 | 60 |

Paired-score summaries:

- MATCH: 254 cases, mean `0.6039`, median `1.0`, range `0.0–1.0`;
- NON_MATCH: 110 cases, mean `0.4893`, median `0.5625`, range `0.0–1.0`;
- REVIEW: 56 cases, paired score `0.0` in this run.

### Source-verified subset

| Score cut | Precision | Recall | False-positive rate | TP | FP | FN | TN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.50 | 0.4000 | 1.0000 | 0.6000 | 4 | 6 | 0 | 4 |
| 0.60 | 0.5714 | 1.0000 | 0.3000 | 4 | 3 | 0 | 7 |
| 0.70 | 0.8000 | 1.0000 | 0.1000 | 4 | 1 | 0 | 9 |
| 0.80 | 0.8000 | 1.0000 | 0.1000 | 4 | 1 | 0 | 9 |
| 0.90 | 1.0000 | 0.0000 | 0.0000 | 0 | 0 | 4 | 10 |
| 0.95 | 1.0000 | 0.0000 | 0.0000 | 0 | 0 | 4 | 10 |

All four source-verified MATCH cases scored exactly `0.85`. The ten source-verified NON_MATCH cases ranged from `0.0` to `0.8`. The six source-verified REVIEW/name-only observations scored `0.0`.

### Synthetic adversarial subset

At score cuts from 0.50 through 0.95, the synthetic subset remained poor as a score-only binary classifier: precision stayed `0.75`, recall `0.60`, and false-positive rate `0.50` (150 TP, 50 FP, 100 FN, 50 TN). This reflects intentionally difficult structural traps in the synthetic corpus and is useful evidence against treating a single yente score as sufficient identity proof.

## Interpretation without threshold selection

The run establishes three facts relevant to later M1.2d work:

1. **yente runs reproducibly on the WA corpus and produces useful continuous scores.** It is therefore a valid candidate component for comparison.
2. **A score alone is not safe enough for consequential automatic identity linking.** High-scoring false positives remain, especially in adversarial parent/subsidiary and similar-identity shapes.
3. **Simply raising the cutoff does not solve the problem.** In the source-verified subset, moving from 0.8 to 0.9 removes the observed false positive but also rejects every known positive rename/continuity case because those positives score 0.85.

These findings reinforce the existing WA Commons architecture: deterministic strong identifiers and explicit conflict checks remain separate from fuzzy matcher scoring, and ambiguous cases require review. This is a measurement finding, **not** the final matcher/threshold decision.

## Raw artifacts

The successful GitHub Actions run uploaded `yente-benchmark-v01` containing:

- `yente-report.json`;
- `yente-rows.json`;
- `queries.json`;
- `candidates.ftm.json`.

The artifact preserves the per-case paired score/rank and top returned candidates so #27 and #28 can compare systems on the same evidence rather than reconstructing summary metrics.

## M1.2b conclusion

Issue #26 acceptance is satisfied:

- pinned self-hosted yente actually executed;
- all 420 candidates were indexed and queried;
- raw per-case output was preserved;
- synthetic and source-verified results were reported separately;
- the run is reproducible from a documented workflow;
- no production threshold was adopted.

Parent #13 remains open. The next bounded task is #27, one alternative matcher comparison on the identical corpus.
