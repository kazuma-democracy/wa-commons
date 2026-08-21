# M1.2 Final Entity-Resolution Decision

Status: **FINAL for M1 — acceptance report for #28 and parent #13**

Date: 2026-08-21

## Decision

WA Commons adopts **`wa-conservative-v0.2` as the identity-decision policy**.

Fuzzy matchers are retained as reusable candidate-generation and review-routing tools, not as authorities that can establish a consequential identity link by score alone.

Versioned configuration:

- decision policy: `wa-conservative-v0.2`;
- yente: `5.5.0`, algorithm `logic-v2`, local WA dataset;
- yente review-routing measurement point: `0.70`;
- Splink: `4.0.16`, DuckDB backend, the M1.2c unsupervised configuration;
- Splink review-routing measurement point: `0.50`;
- **no fuzzy score permits AUTO_LINK in M1**.

The score points above are calibrated routing points for human review. They are not interchangeable probabilities and are not identity thresholds.

## Final decision rules

1. If one or more strong identifiers align and no observed strong identifier conflicts, return `AUTO_LINK`.
2. If any observed strong identifier conflicts, return `DISPUTED` and require review. A fuzzy score can never override the conflict.
3. Without an aligned strong identifier, name/address/jurisdiction similarity can only return `REVIEW` or `NON_MATCH`.
4. Name-only evidence never returns `AUTO_LINK`.
5. Parent and subsidiary entities remain distinct even when their names are very similar.
6. yente `>=0.70` or Splink `>=0.50` may route a candidate to review, but neither score changes rule 1–5.
7. Consequential downstream publication remains a separate decision even after identity AUTO_LINK.

Strong identifiers in M1 are Japanese corporate number, LEI, EDINET code, and JPX security code. Identifier namespace is preserved; values from different systems are never compared as though they were the same identifier type.

## Why the fuzzy scores are review-only

### yente 5.5.0 / logic-v2

On the identical 420-case corpus, the descriptive `0.70` point produced:

- precision: `75.12%`;
- recall: `60.63%`;
- false-positive rate: `46.36%`.

On the 20 source-verified cases it produced `80%` precision, `100%` recall, and `10%` false-positive rate. The observed Japanese Electric / Nippon Electric Glass similar-name non-match scored `0.8`, while all four source-verified historical continuity positives scored `0.85`. Raising the cut to `0.90` removed that observed false positive but also removed all four real positives. Therefore no score-only yente AUTO_LINK threshold is supported by the measurements.

`0.70` is retained only as a review-routing point because it preserved all four source-verified positives in this corpus while still reducing the candidate set relative to lower cuts.

### Splink 4.0.16

At the descriptive `0.50` point:

- precision: `100%`;
- recall: `40.16%`;
- false-positive rate: `0%`.

On the source-verified subset it produced `100%` precision, `50%` recall, and `0%` FPR. At `0.70` and above it recovered none of the four real continuity positives. In addition, the CI run reported unobserved comparison levels and default m/u values for several features, demonstrating that this 420-case corpus is too sparse to fully fit every probabilistic parameter.

Therefore Splink is useful as a second, inspectable batch signal, but its M1.2 fit is not accepted as an identity authority. `0.50` is retained only as a review-routing point.

## `wa-conservative-v0.2` measured outcome

The final policy deliberately removes the v0.1 rule that could AUTO_LINK a no-ID record from high name similarity plus aligned address. That evidence now goes to `REVIEW`.

### Combined 420 cases

- TP: **154**
- FP: **0**
- FN: **100**
- TN: **166**
- precision: **100%**
- recall: **60.63%**
- false-positive rate: **0%**
- REVIEW: **206 / 420 = 49.05%**
- DISPUTED: **60 / 420 = 14.29%**

This is intentionally conservative. The 100 additional false negatives are the synthetic alias/name+address MATCH cases which no longer qualify for automatic identity without a strong identifier. They remain reviewable candidates rather than being discarded.

### Source-verified 20 cases

- four documented historical-continuity cases: `AUTO_LINK` via aligned JPX code;
- six deliberately ID-stripped name-only cases: `REVIEW`;
- six SoftBank Group / SoftBank parent-subsidiary traps: `DISPUTED` via conflicting JPX codes;
- four similar-name distinct issuers: `DISPUTED` via conflicting JPX codes;
- benchmark errors for consequential AUTO_LINK decisions: **0**.

The source-verified subset is small, so this is an acceptance result for the M1 policy, not evidence of universal production accuracy.

### Synthetic 400 cases

Expected behavior under v0.2:

- 100 easy exact: `AUTO_LINK`;
- 100 alias/name+address matches without strong IDs: `REVIEW`;
- 50 parent/subsidiary traps with conflicting IDs: `DISPUTED`;
- 50 same-name / divergent-address non-matches: `REVIEW`;
- 50 historical rename cases with aligned corporate number: `AUTO_LINK`;
- 50 incomplete/name-only records: `REVIEW`.

The synthetic corpus was intentionally shaped around safety invariants, so its strong baseline performance must not be interpreted as independent proof of generalization.

## Manual-review burden

The policy accepts a high review burden in M1: roughly half the benchmark observations are routed to `REVIEW`, in addition to explicit `DISPUTED` cases. This is a deliberate trade-off because WA Commons can attach consequential evidence such as procurement, political-finance, conflict, or human-rights records to an entity. A false identity link can contaminate every downstream claim.

Later milestones may reduce review load only with new independently sourced labels and a new versioned policy. The M1.2 thresholds must not be silently loosened.

## Known failure modes

- legal-name changes with no surviving strong identifier require review;
- transliteration and alias-only matches require review even when obvious to a human;
- stale or erroneous source identifiers can cause a false deterministic link unless provenance/correction handling catches the source error;
- identifiers can be reused or change semantics over time, so source/date context remains necessary;
- the present source-verified subset is small;
- yente has high score-only false-positive exposure on similar names;
- the measured Splink fit misses many true links and used defaults for some untrained comparison levels;
- fuzzy match scores are matcher-specific and must not be compared as a shared probability scale.

## Reproducibility and auditability

The policy implementation lives in `src/wa_commons/identity/policy.py`. Tests pin the core safety invariants and the expected 420-case metrics. Earlier yente and Splink workflows preserve raw per-case scores and environment metadata. A future matcher or threshold change must create a new policy version and must not rewrite historical decisions silently.

Every persisted entity link should retain matcher/policy version, input identifiers and attributes, candidate ID, fuzzy signals if used, aligned/conflicting attributes, decision, provenance, and review/correction history.

## M1.2 acceptance conclusion

The parent #13 acceptance criteria are satisfied:

- thresholds and routing points are grounded in labeled measurements;
- name-only consequential matches never auto-link;
- automatic links require an aligned strong identifier in M1;
- conflicting strong identifiers force `DISPUTED` / manual review;
- yente and Splink were both run reproducibly on the same 420-case corpus;
- metrics and failure modes are documented with source-verified and synthetic subsets separated;
- the final strategy is versioned and testable.

M1.2 is therefore complete when #28 is merged. This report does not begin M1.3 evidence-adapter work.
