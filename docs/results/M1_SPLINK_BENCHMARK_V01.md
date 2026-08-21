# M1.2c Splink Benchmark v0.1

Status: **measured in CI; issue #27 acceptance candidate**.

Related issue: #27. Parent acceptance gate: #13.

## Scope

This increment compares one reuse-first alternative matcher, Splink, against the existing WA conservative baseline on the identical 420-case M1.2 corpus:

- 400 synthetic adversarial cases;
- 20 source-verified Japanese cases.

It does **not** choose the final production matcher or threshold. That decision remains M1.2d (#28).

## Why Splink

Splink is an open-source probabilistic record-linkage framework with a DuckDB backend, explicit comparison features, blocking rules, inspectable model parameters, and reproducible batch linkage. It is meaningfully different from yente's search/matching API and therefore provides a useful alternative benchmark without inventing another matcher.

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

## Pinned measured environment

First successful CI measurement:

- Splink: `4.0.16`
- DuckDB: `1.5.5`
- Python: `3.11.16`
- link type: `link_only`
- prior match probability: `1/420`
- u estimation: 100,000 random pairs, seed `20260821`
- m estimation: unsupervised EM blocks on corporate number, security code, address and name

## Measured results

### Splink — all 420 cases

At descriptive score cut `0.50`:

- precision: **100.0%**
- recall: **40.16%**
- false-positive rate: **0.0%**
- TP / FP / FN / TN: **102 / 0 / 152 / 110**

At `0.70` through `0.95`, precision and FPR remain 100% / 0%, but recall falls slightly to **39.37%**.

The score distribution is strongly polarized:

- 318 / 420 cases below 0.10;
- 0 cases from 0.10 to below 0.50;
- 2 cases from 0.50 to below 0.90;
- 100 cases at or above 0.90.

This is not evidence that 0.50 is a production threshold; it is only a description of this fitted model on this corpus.

### Splink — source-verified 20 cases

At descriptive score cuts `0.50` and `0.60`:

- precision: **100.0%**
- recall: **50.0%**
- false-positive rate: **0.0%**
- TP / FP / FN / TN: **2 / 0 / 2 / 10**

At `0.70` and above, all four known MATCH cases fall below the cut: recall becomes **0%** while FPR remains 0%.

For the four source-verified MATCH cases, observed probabilities ranged from approximately **0.0053** to **0.6474**. The ten source-verified NON_MATCH cases all remained below **0.045**. This shows useful separation for the negative examples but weak and inconsistent recovery of real historical-name continuity in this small subset.

### Splink — synthetic 400 cases

At `0.50`:

- precision: **100.0%**
- recall: **40.0%**
- false-positive rate: **0.0%**
- TP / FP / FN / TN: **100 / 0 / 150 / 100**

The 400 synthetic cases split almost completely into 100 very high scores and 300 very low scores. The case-type report is preserved in the machine-readable artifact so #28 can inspect which fixture shapes drive that separation without retuning this run.

## Training limitation observed in CI

The first successful run emitted Splink warnings that some comparison levels were not observed during parameter estimation. The affected warnings included levels for name, LEI, EDINET code, jurisdiction, security code and address. Splink therefore used default values for some untrained m/u parameters during prediction.

This is a material result, not a warning to hide. The 420-case M1.2 corpus is suitable as a safety benchmark but is too small and structurally sparse to fully estimate every probabilistic comparison level. The final report now records this limitation explicitly.

## Comparison with M1.2b yente

Raw Splink probabilities and yente scores are **not calibrated to the same scale**, so equal numeric cuts must not be treated as equivalent operating thresholds. The useful comparison is behavioral:

| Matcher/run | Observed behavior on this M1.2 corpus |
| --- | --- |
| yente 5.5.0 / logic-v2 | More MATCH coverage, but high false-positive exposure on adversarial similar-name cases. At its descriptive 0.70 cut: precision 75.1%, recall 60.6%, FPR 46.4% overall. |
| Splink 4.0.16 / this unsupervised model | Strong false-positive suppression at the shown cuts, but much lower MATCH coverage. At descriptive 0.50: precision 100%, recall 40.2%, FPR 0%. |
| `wa-conservative-v0.1` | Fixed safety rules achieve zero benchmark errors, with 25.2% REVIEW and 14.3% DISPUTED. This result is optimistic because much of the synthetic corpus was deliberately designed around those explicit safety invariants. |

On the 20 source-verified cases specifically, yente at its 0.70 measurement point returned 80% precision / 100% recall / 10% FPR, while Splink at its 0.50 measurement point returned 100% precision / 50% recall / 0% FPR. These points illustrate the different failure modes; they do not establish interchangeable thresholds.

## Reproducibility and implementation complexity

### WA conservative baseline

- lowest runtime and dependency complexity;
- pure, transparent rules with explicit conflict handling;
- easy to audit and reproduce;
- limited ability to discover fuzzy candidates outside those rules.

### yente

- highest operational complexity in this comparison;
- requires a service, Elasticsearch, FollowTheMoney adaptation and indexing;
- useful search/matching API and candidate retrieval behavior;
- score-only automatic linking is unsafe on this corpus.

### Splink

- middle operational complexity: Python package + DuckDB, no separate service;
- batch experiments are straightforward and model parameters are inspectable;
- probabilistic training adds conceptual/configuration complexity;
- small or sparse calibration data can leave comparison levels untrained and dependent on defaults;
- this unsupervised v0.1 fit is conservative on false positives but misses many true links.

## Outputs and reproduction

The workflow `.github/workflows/splink-benchmark.yml` installs the pinned Splink version, runs the project test suite, executes `scripts/run_splink_benchmark.py`, and uploads:

- `artifacts/splink-benchmark/splink-report.json`;
- `artifacts/splink-benchmark/splink-rows.json`.

The report includes per-case probabilities, environment metadata, training metadata and limitations, case-type/provenance splits, descriptive measurement curves, and the unchanged `wa-conservative-v0.1` baseline.

## M1.2c conclusion

M1.2c has identified a genuinely different alternative failure mode without selecting a winner:

- yente favors coverage but produces unacceptable false positives if its score is treated naively;
- this Splink fit suppresses false positives but loses too much recall, especially on real rename/continuity cases;
- the transparent baseline remains the safest benchmark on this deliberately safety-shaped corpus, but its apparent perfection must not be mistaken for independent production validation.

No final matcher or AUTO_LINK/REVIEW threshold is selected here. That synthesis belongs to #28. Parent issue #13 remains open.
