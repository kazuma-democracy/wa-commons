# M1.7 Deterministic reproduction and correction end to end v0.1

Status: **PASS — M1 exit demonstrated in a clean GitHub-hosted checkout**  
Issue: #18  
Reproduction version: `m1-reproduction-v0.1`

## Purpose

M1.7 closes the Reproducible Evidence Graph milestone by proving that the existing M1 identity, evidence, adjudication and Evidence Card layers can be regenerated from fixed/versioned inputs, and that correction, dispute, expiry and source-outage behavior propagate without silently creating policy decisions.

This is an evidence-research milestone only. It does **not** authorize real-money trading or any other consequential action.

## Clean reproduction environment

Measured GitHub Actions run: `32493640144` (`m1-reproduction`, run #2).

The workflow starts from a clean checkout on Ubuntu 24.04 and records the relevant runtime versions:

- Python: `3.11.16`
- Tesseract: `5.3.4`
- Poppler `pdftoppm`: `24.02.0`
- identity policy: `wa-conservative-v0.2`
- MOD adapter: `0.1`
- contract-subject rules: `contract-subject-v0.1`
- political-finance adapter: `0.1`

No model-assisted stage is used by the M1.7 reproduction graph. `model_assisted_stages` is therefore an explicit empty list rather than an unrecorded assumption.

## Fixed real source inputs

### 1. Japan Ministry of Defense procurement

- source: `https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/fy2026/04_buppin_k.xlsx`
- required SHA-256: `c1f37e838d66ffa7bc62c35c5d8830c75ed7b92b0befe0c380f0d79052c773e8`
- fixed retrieval timestamp used in semantic output: `2026-08-21T13:00:00Z`
- real observations: **88**
- deterministic canonical claims selected for the frozen graph: **10**

The claims reuse the existing strong-ID identity path and contract-subject rules. A MOD procurement record remains `military_contract` evidence; it is not automatically converted to `weapons_activity`.

### 2. Japanese political-finance filing

- source: `https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/contents/SS20241129/006710_215018.pdf`
- required SHA-256: `e8871ed2cb62729ec8a8c01028c3da2f797a6f65972abfb8dc4dcf757f11c8fe`
- bounded pages: **1–20** of part 18
- fixed retrieval timestamp used in semantic output: `2026-08-21T13:00:00Z`
- real OCR observations: **24**
- canonical claims emitted: **0**

Zero claims is the intended fail-closed result. The fixed filing exposes donor names but not a strong corporate identifier, and OCR extraction remains review-required. M1.7 verifies that name/OCR alone does not `AUTO_LINK` a donor and therefore cannot silently create a consequential claim or exclusion.

## Canonical graph result

The frozen graph contains:

- **2** real evidence adapters executed;
- **11** canonical entity IDs;
- **11** schema-valid canonical claims;
- regenerated Evidence Cards for those claims;
- source hashes, locators and adapter/rule versions;
- explicit correction, expiry and outage demonstrations.

Canonical graph SHA-256:

`0a4f9ed031eaa534e116dca9c441e08054be49047b4404832a14a48094cf2e15`

The workflow deletes the first generated graph, reruns the entire real-source pipeline, and requires the second canonical graph hash to equal the first. Both runs produced the exact same SHA above.

## Correction propagation

Controlled correction claim: `wc:claim:example-correction-001`.

- before: `CONFIRMED`
- after: `DISPUTED`
- correction-history entries retained: **1**
- pre-correction Evidence Card SHA-256: `de6c60f68630d021e31b4324b50368c57115b08d5a5127e0287f01e30da5cf7a`
- post-correction Evidence Card SHA-256: `c702050b567c5a7d8428a28006030a6bd1f246a2ce7525259dac7db4a1bf045b`

The original state is not silently deleted. The correction is appended and the dependent Evidence Card changes deterministically.

## Expiry propagation

A copy of a real schema-backed `CONFIRMED` contract-subject claim is used only as a controlled expiry fixture:

- before: `CONFIRMED`
- after: `EXPIRED`
- policy context after expiry: `null`

This proves that stale/revalidation state can propagate to the human-readable output without inventing a PASS/WATCH/EXCLUDE decision.

## Source-outage behavior

A controlled political-finance source outage produces:

- adapter health: `unavailable`
- evidence status: `UNKNOWN`
- policy decision: `NONE`

A missing or unreachable source therefore cannot create PASS or EXCLUDE by itself.

## Executable threat-model gates

All M1.7 gates passed:

- name-only consequential auto-link blocked;
- MOD contract does not automatically become `weapons_activity`;
- missing source does not create PASS/EXCLUDE;
- correction history remains visible;
- `EXPIRED` propagation is supported;
- no model-only/source-less evidence stage is hidden in the reproduction graph.

Targeted regression tests: **6 passed**.

## Artifact

Derived artifact only:

- name: `m1-reproduction-v01`
- artifact ID: `9450802091`
- artifact ZIP SHA-256: `8dbb9b06a34f5277d701bb7b72a729a14382d8c64c4d560b4370d149d131a0d2`

The artifact contains `canonical-graph.json` and `report.json`. Raw upstream XLSX/PDF files and rendered OCR page images are transient and are not redistributed while source reuse terms remain `review_required`.

## Third-party reproduction

From a clean checkout on a compatible Ubuntu environment:

```bash
python -m pip install -e '.[dev]'
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-jpn
python -m pytest -q tests/test_m1_reproduction.py
python scripts/run_m1_reproduction.py
```

Then inspect:

- `artifacts/m1-reproduction/canonical-graph.json`
- `artifacts/m1-reproduction/report.json`

For the recorded source and tool versions, `report.json` must contain:

`canonical_graph_sha256 = 0a4f9ed031eaa534e116dca9c441e08054be49047b4404832a14a48094cf2e15`

A changed upstream source hash, changed explicitly versioned rule, or changed OCR/runtime version is treated as a new reproducibility context and must not be silently presented as identical deterministic history.

## M1 conclusion

With M1.1–M1.7 now measured and the M1.7 clean reproduction workflow passing, **M1 — Reproducible Evidence Graph is complete**.

The next project stage may move to M2 user-policy evaluation and Peace Capital paper portfolios. Real-money execution remains prohibited by the existing pre-real-money gates.
