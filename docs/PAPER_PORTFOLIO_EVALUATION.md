# Peace Capital Paper Portfolio Evaluation v0.1

Status: **implementation specification**  
Related issue: #6

## Purpose

This document fixes the financial evaluation contract **before** Peace Capital portfolio construction is implemented.

The objective is not to prove that a value-constrained portfolio outperforms. The objective is to measure, honestly and reproducibly, what changes when a user's policy is applied to an investable universe.

A conforming implementation must be able to answer:

- what benchmark was used;
- what information was knowable at each decision time;
- what the policy changed;
- how much diversification was lost or gained;
- how far the result drifted from the benchmark;
- how much trading the policy/constructor required;
- what estimated trading costs do to results;
- which sector/factor exposures changed;
- how sensitive the output is to policy thresholds;
- whether another contributor can reproduce the same numbers from pinned inputs.

This specification is paper-research only. It grants no real-money trading authority.

---

## 1. Evaluation unit

One evaluation run is identified by a fully versioned tuple:

```text
Evidence Graph
+ User Policy
+ Policy Evaluator
+ Portfolio Constructor + config
+ Benchmark snapshot
+ Market-data snapshot
+ Sector taxonomy
+ Factor dataset
+ Evaluation method
+ Evaluation period
+ Code commit
= one reproducible paper evaluation
```

Changing any material member of that tuple creates a new run. Historical results must not be silently recomputed under newer inputs and presented as if unchanged.

---

## 2. Benchmark selection

### 2.1 Primary rule

The benchmark must represent the **unconstrained investment opportunity set** the candidate portfolio is intended to approximate.

The benchmark is part of the preregistered method, not something selected after results are known.

For the first Japanese-equity Peace Capital implementation, the constructor issue must choose one broad, investable Japan-equity benchmark and pin its exact identifier/provider/licensing terms before producing headline results. This specification intentionally does not pretend that a benchmark dataset has already been licensed.

### 2.2 Required benchmark properties

Every run records:

- `benchmark_id` and human-readable name;
- total-return or price-return variant;
- currency;
- point-in-time constituents and weights;
- weighting method;
- snapshot hash/version;
- source/provider and license status in the run manifest.

**Point-in-time membership is mandatory.** Reconstructing old periods using today's constituents is prohibited because it creates survivorship bias.

### 2.3 Return variant

Use total return when a legally usable, reproducible total-return series is available. If only price return is legally/reproducibly available, label the run as price return and compare candidate and benchmark on the same basis. Never mix return bases.

### 2.4 Alternative benchmarks

A secondary benchmark may be reported as a robustness check, but:

1. the primary benchmark is chosen before evaluating outcomes;
2. switching the headline benchmark after seeing performance is prohibited;
3. every alternative is separately identified and versioned.

No silent benchmark substitution is allowed when a source becomes unavailable.

---

## 3. Time and information integrity

### 3.1 Calendar

Baseline v0.1 convention:

- timezone: `Asia/Tokyo`;
- returns: daily;
- annualization constant: 252 trading days;
- scheduled rebalance: monthly, first trading day;
- minimum decision lag: 1 trading day.

The portfolio constructor may eventually use a slower schedule, but any change is a new constructor/config version and must not rewrite prior results.

### 3.2 As-known-at-cutoff rule

A decision at date `t` may use only data/evidence whose availability timestamp is at or before the configured cutoff for that decision.

Example:

```text
Evidence published after market close on 2026-06-30
must not affect a portfolio assumed tradable at the same close.
```

At least one trading-day decision lag is required in v0.1. Implementations may choose a longer lag but must record it.

This applies to:

- evidence/adjudication state;
- policy version;
- benchmark membership/weights;
- market prices/returns;
- sector classification;
- factor exposures.

Future information must never leak backward into a historical screen.

---

## 4. Universe, coverage, and missing data

### 4.1 Unmapped entities

If a benchmark security cannot be mapped safely to a WA Commons legal entity, it remains **unscreened**, not automatically excluded and not automatically treated as clean.

The baseline rule is:

```text
unmapped entity -> keep in financial universe + report as unscreened
```

Every rebalance reports:

- benchmark count;
- safely mapped count/weight;
- unmapped count/weight;
- policy `EXCLUDE` count/weight;
- `WATCH` count/weight;
- unresolved/unknown evidence count/weight where available.

### 4.2 Missing returns

If required portfolio or benchmark return data are missing for a held security/date and no preregistered corporate-action treatment explains the gap, the evaluation is **BLOCKED**. Do not replace missing returns with zero.

A later implementation must specify corporate actions, delistings, mergers and cash proceeds explicitly before long-history headline tests.

### 4.3 Missing sector/factor data

Missing sector/factor fields must not be zero-filled.

Sector analysis requires an `UNKNOWN` bucket.

Factor drift is reported only with explicit coverage. Baseline minimum exposure coverage is 90% of both portfolio and benchmark weight for a factor/date. Below that threshold, the factor result is `INSUFFICIENT_COVERAGE`, not zero drift.

---

## 5. Portfolio and benchmark return convention

For daily simple returns `r[i,t]` and start-of-period/post-rebalance weights `w[i,t-1]`:

```text
R_p,t = sum_i(w_p,i,t-1 * r_i,t)
R_b,t = sum_i(w_b,i,t-1 * r_i,t)
active_t = R_p,t - R_b,t
```

Between scheduled rebalances, weights drift with realized returns rather than being magically reset each day.

Gross performance is calculated before the configured transaction-cost deduction. Net performance applies the cost model in Section 8.

All weights must sum to 1 within numerical tolerance after any documented cash treatment.

---

## 6. Diversification and concentration

At every rebalance and for period summaries report:

### 6.1 Holding count

Number of securities with weight greater than `1e-8`.

### 6.2 Maximum weight

```text
max_i(w_i)
```

### 6.3 Top-10 weight

Sum of the ten largest weights (or all holdings if fewer than ten).

### 6.4 Herfindahl-Hirschman Index (HHI)

```text
HHI = sum_i(w_i^2)
```

### 6.5 Effective number of holdings

```text
effective_n = 1 / HHI
```

### 6.6 Active share

Against benchmark weights over the union of names:

```text
active_share = 0.5 * sum_i(abs(w_p,i - w_b,i))
```

These measures must be shown for candidate and benchmark where meaningful. Do not describe a portfolio as adequately diversified from holding count alone.

---

## 7. Performance and tracking

### 7.1 Cumulative return

```text
cumulative_return = product_t(1 + R_t) - 1
```

### 7.2 Annualized geometric return

For `N` daily observations:

```text
annualized_return = product_t(1 + R_t)^(252 / N) - 1
```

If the observation period is too short for annualization to be meaningful, still compute mechanically but label the period length prominently.

### 7.3 Annualized volatility

```text
volatility = sample_std(R_t) * sqrt(252)
```

### 7.4 Tracking difference

Headline tracking difference is the annualized geometric return difference:

```text
tracking_difference = annualized_return_portfolio
                    - annualized_return_benchmark
```

Gross and net tracking difference are both reported.

### 7.5 Tracking error

```text
tracking_error = sample_std(R_p,t - R_b,t) * sqrt(252)
```

Use sample standard deviation (`ddof=1`) when at least two daily active returns exist.

No claim that a lower/higher tracking error is intrinsically good is encoded in the engine; it is a trade-off measure.

---

## 8. Turnover and estimated transaction costs

### 8.1 Turnover

At each rebalance compare **pre-trade drifted weights** to new target weights over the union of names:

```text
turnover_t = 0.5 * sum_i(abs(w_target,i - w_pretrade,i))
```

This is one-way portfolio turnover. Report:

- each rebalance turnover;
- total turnover over the evaluation;
- annualized turnover = total turnover * 252 / number_of_daily_return_observations.

Do not compare the new target only with the previous target; that understates trading after market drift.

### 8.2 Baseline cost model

v0.1 uses a transparent linear scenario model rather than pretending to estimate market impact precisely.

Headline assumption:

```text
10 bps per 100% one-way turnover
```

Required scenarios:

- 0 bps;
- 10 bps (headline);
- 25 bps;
- 50 bps.

At a rebalance:

```text
cost_fraction_t = turnover_t * cost_bps / 10,000
```

The cost is deducted from portfolio value on the rebalance execution date according to the implementation's fixed timing convention.

These are **estimated research costs**, not broker quotes. Taxes, borrow fees, FX costs and market impact are not silently included. If relevant later, each must become an explicit versioned cost component.

---

## 9. Sector drift

Use a pinned sector taxonomy/version.

For sector `s`:

```text
sector_drift_s = portfolio_sector_weight_s - benchmark_sector_weight_s
```

Required outputs at each rebalance:

- portfolio and benchmark weight by sector;
- signed difference by sector;
- maximum absolute sector difference;
- half-L1 sector distance:

```text
sector_distance = 0.5 * sum_s(abs(sector_drift_s))
```

Unknown sector assignments are included as an explicit `UNKNOWN` sector. They are not dropped and weights are not renormalized around them.

---

## 10. Factor drift

The evaluator consumes factor exposures; Issue #6 does **not** choose or invent a proprietary factor model.

Any implementation must record:

- factor dataset/provider;
- factor definitions;
- version/date;
- snapshot hash where legally possible;
- coverage by portfolio and benchmark weight.

For factor `f`:

```text
exposure_portfolio_f = weighted mean of valid security exposures
exposure_benchmark_f = weighted mean of valid security exposures
factor_drift_f = exposure_portfolio_f - exposure_benchmark_f
```

Weights are renormalized **only across securities with valid exposure for that factor**, and the original valid-weight coverage is reported beside the result.

Baseline minimum coverage is 90% for both sides. Otherwise output `INSUFFICIENT_COVERAGE`.

Missing factor exposure is never assumed to be zero.

---

## 11. Policy-threshold sensitivity

Sensitivity analysis tests whether apparently attractive/unattractive results depend on a knife-edge policy setting.

### 11.1 Confidence thresholds

For every numeric `min_confidence` used by a profile, run a clipped grid around the base threshold:

```text
base + {-0.10, -0.05, 0.00, +0.05, +0.10}
clipped to [0, 1]
```

If duplicate clipped values result, run each unique value once.

### 11.2 Quantitative claim thresholds

For any numeric claim-value threshold used to decide exclusion/preference, run:

```text
base * {0.50, 0.75, 1.00, 1.25, 1.50}
```

Zero or signed thresholds that make multiplicative sensitivity nonsensical must use a preregistered additive grid instead; that grid becomes part of the evaluation config.

### 11.3 Isolation rule

During one sensitivity sweep, **all non-policy inputs remain identical**:

- same Evidence Graph snapshot;
- same benchmark;
- same market data;
- same constructor and constraints;
- same period;
- same cost assumptions.

Required sensitivity outputs:

- eligible security count;
- excluded benchmark weight;
- WATCH benchmark weight;
- active share;
- tracking error;
- turnover;
- net tracking difference.

Sensitivity is not a search procedure for picking the best-performing threshold. The base policy remains the user's preregistered policy.

---

## 12. Reproducibility manifest

Every run must emit a machine-readable manifest containing at least:

- evaluation specification/version;
- Git commit SHA of evaluation code;
- Evidence Graph SHA-256;
- policy profile ID/version and policy file SHA-256;
- policy evaluator version;
- portfolio constructor ID/version;
- portfolio constructor config SHA-256;
- benchmark snapshot SHA-256;
- market-data snapshot SHA-256;
- sector taxonomy ID/version;
- factor dataset ID/version/SHA-256;
- evaluation config SHA-256;
- period start/end;
- runtime/package versions sufficient to reproduce numerical behavior;
- hashes/identifiers of derived target weights and final metrics.

Where licensing prevents redistribution of raw market/index/factor data, the manifest still records provider-native version identifiers and local content hashes so an authorized third party can verify they possess the same inputs.

A clean rerun with the same canonical inputs/config must reproduce the same target weights and evaluation metrics within declared floating-point tolerance. The implementation issue must pin that tolerance rather than inventing it ad hoc per run.

---

## 13. Required report

Every headline paper evaluation report must include:

1. benchmark and evaluation period;
2. evidence + policy + constructor versions;
3. coverage/unmapped benchmark weight;
4. excluded and WATCH benchmark weight and reasons;
5. gross and net cumulative/annualized returns;
6. gross and net tracking difference;
7. tracking error;
8. holding count, max weight, top-10 weight, HHI, effective N, active share;
9. turnover and all required cost scenarios;
10. sector drift;
11. factor drift and factor-data coverage;
12. policy-threshold sensitivity;
13. data gaps, blocked intervals, unresolved evidence and other limitations;
14. any negative/unfavorable result with the same prominence as favorable results.

The report must not call `NONE` evidence “clean”, and must not market historical outperformance as guaranteed, safer, or caused by peace alignment without a separate valid causal analysis.

---

## 14. Benchmark-gaming safeguards

To address Threat Model T23:

- primary benchmark is fixed before outcome inspection;
- evaluation period is fixed before outcome inspection;
- method/config is versioned;
- failures and negative results remain publishable;
- alternate benchmarks are robustness checks, not replacements for an inconvenient primary result;
- threshold sensitivity is reported, not optimized for return;
- point-in-time membership prevents current-constituent survivorship bias;
- as-known-at-cutoff evidence prevents look-ahead bias.

---

## 15. Out of scope for Issue #6

This issue does **not** implement:

- a portfolio optimizer;
- actual benchmark or market-data licensing/ingestion;
- factor-model construction;
- real-money trading;
- broker integration;
- tax advice;
- a claim that policy-constrained investing outperforms.

Those require later bounded issues. This specification defines how candidate paper portfolios will be evaluated once such a constructor exists.

---

## 16. Implementation acceptance checklist

A future portfolio implementation conforms to v0.1 only if all are true:

- [ ] primary benchmark and period are preregistered and versioned;
- [ ] point-in-time constituents/weights are used;
- [ ] only as-known-at-cutoff evidence/data affect each rebalance;
- [ ] unmapped entities remain unscreened and their weight is reported;
- [ ] missing returns fail closed rather than becoming zero;
- [ ] candidate and benchmark return bases match;
- [ ] concentration metrics use the formulas in this document;
- [ ] tracking difference and tracking error use the formulas in this document;
- [ ] turnover uses pre-trade drifted weights;
- [ ] gross and 0/10/25/50-bps net results are reported;
- [ ] sector drift includes UNKNOWN;
- [ ] factor drift reports coverage and never zero-fills missing exposures;
- [ ] threshold sensitivity holds all non-policy inputs fixed;
- [ ] the full run provenance tuple is recorded;
- [ ] a clean rerun reproduces weights and metrics within pinned tolerance;
- [ ] negative results and limitations are not hidden;
- [ ] no real-money authority is granted.

Machine-readable method contract: `schemas/paper-portfolio-evaluation.v0.1.schema.json`.
