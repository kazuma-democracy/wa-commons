# M1.2 Entity Resolution Benchmark v0.1

Status: benchmark harness + adversarial corpus foundation.

This is **not yet the final M1.2 acceptance report**. It establishes a reproducible safety benchmark before a pinned yente/Splink comparison is run.

## Corpus shape

The deterministic v0.1 corpus contains 400 labeled pairwise cases:

| Case type | Count | Purpose |
| --- | ---: | --- |
| easy exact | 100 | Exact strong identifiers with harmless legal-form variation |
| alias / transliteration-shaped | 100 | Name variation plus a second independently aligned attribute |
| parent/subsidiary traps | 50 | Similar corporate-family names must not collapse identity |
| same/similar-name non-matches | 50 | Same display name with strongly divergent location evidence |
| historical rename/merger-shaped | 50 | Changed name with continuing strong legal identifier |
| incomplete records | 50 | Name-only evidence must remain review-only |

## Provenance warning

v0.1 adversarial cases are explicitly marked `synthetic_adversarial`. They are matcher calibration fixtures, not factual claims about real companies.

The final M1.2 corpus must add source-verified Japanese historical rename, merger, parent/subsidiary, and duplicate-name cases with provenance. Synthetic fixtures remain useful for regression testing but must not be presented as empirical real-world frequency estimates.

## Transparent baseline

`wa-conservative-v0.1` is deliberately simple and auditable. It is not intended to replace yente, Splink, Dedupe, or another mature entity-resolution system.

Safety invariants:

- exact aligned strong identifier -> `AUTO_LINK` unless another strong identifier conflicts;
- conflicting strong identifier -> `DISPUTED`;
- name-only match -> never `AUTO_LINK`;
- without a strong identifier, automatic linking requires the name plus at least one independent aligned attribute;
- parent/subsidiary identity is never collapsed merely because names are similar.

## Reuse-first matcher evaluation

WA Commons will reuse yente's own validation approach rather than inventing a separate black-box scoring framework. Current yente includes `contrib/validation_report`, which runs labeled fixtures through the live `/match/<dataset>` API and records scores and expected-ID recall.

For the final M1.2 benchmark we will:

1. export the WA Commons labeled corpus as FollowTheMoney-compatible entities;
2. index the candidate side into a pinned self-hosted yente instance;
3. run the query side through yente's `/match` API using a pinned algorithm/version;
4. compare against `wa-conservative-v0.1` and at least one practical alternative/baseline;
5. calibrate the auto-link threshold from labeled results, emphasizing false-positive avoidance;
6. publish precision, recall, false-positive rate, manual-review rate, and metrics by case type.

## Exit rule

Issue #13 must remain open until:

- the source-verified Japanese subset exists;
- yente is actually executed against the WA corpus;
- at least one alternative/baseline is measured;
- thresholds are selected from measured curves, not guessed;
- false-positive and review tradeoffs are published.
