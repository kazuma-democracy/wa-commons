# M1.6 Evidence Cards v0.1

Status: **measured pilot**  
Issue: #17  
Card version: `evidence-card-v0.1`

## Scope

M1.6 renders human-readable WA Commons Evidence Cards from canonical `EvidenceClaim v0.1` data. The renderer is presentation-only: it does not create new factual claims, moral labels, policy rules, or action authority.

Each card exposes:

- canonical entity identity and identifiers;
- exact narrow claim category, predicate, value and effective period;
- source publisher, URL and locator;
- evidence date and retrieval date;
- adjudication status, confidence and concise reasoning;
- entity-resolution method and review state;
- append-oriented correction history;
- a public correction/challenge path tied to `claim_id`;
- an explicit boundary between evidence and any downstream user-policy evaluation.

## Fixed/versioned inputs

The pilot combines two already-versioned M1 inputs rather than hand-authoring card prose:

1. the pinned M1.3 Ministry of Defense procurement snapshot:
   - `https://www.mod.go.jp/j/budget/chotatsu/naikyoku/keiyaku/fy2026/04_buppin_k.xlsx`
   - expected SHA-256: `c1f37e838d66ffa7bc62c35c5d8830c75ed7b92b0befe0c380f0d79052c773e8`
   - fixed acquisition timestamp for deterministic regeneration: `2026-08-21T13:00:00Z`
2. `schemas/examples/evidence-claim.examples.json`, which is validated against the canonical schema and intentionally contains worked `UNKNOWN`, `DISPUTED`, political-finance, human-rights and correction-history examples.

The first 20 unique identity-resolved real suppliers from the fixed M1.3 snapshot are selected deterministically and converted through the existing M1.4 contract-subject classifier. No company is selected by a moral score or policy decision.

## Measured result

GitHub Actions run `32492466372` (`evidence-cards-pilot`, run #1) completed successfully.

| Measure | Result |
|---|---:|
| Real fixed-pilot entities | **20** |
| Canonical worked-example entities | **4** |
| Total cards | **24** |
| Unique entities | **24** |
| Targeted card tests | **6 passed** |
| Repeated regeneration semantic SHA | **stable** |

Adjudication statuses present:

- `CONFIRMED`
- `UNKNOWN`
- `DISPUTED`

Claim categories present:

- `military_contract`
- `political_finance`
- `human_rights`

The measured semantic SHA-256 of the generated card array is:

`ff1c0dc8f32ee36cbf1c70d3418bfb45be7e027693eb44f1a44303a41c5f25fa`

The workflow deletes its first generated output, regenerates the complete card set from the same inputs, and asserts the second semantic SHA equals the first. This passed in the measured run.

Artifact:

- name: `evidence-cards-pilot-v01`
- artifact ID: `9450291567`
- ZIP SHA-256: `ef13cc548ea57c0e3b7894cc8713a6357748c5753a0a006798b41ee2b7349255`

The artifact contains generated Markdown and JSON cards plus aggregate `cards.json` and `report.json`; the government workbook is only a transient, hash-verified input.

## Status semantics

The renderer does not reinterpret adjudication status.

- `CONFIRMED` means the exact narrow claim is supported under its recorded rule set. It is not a moral endorsement or condemnation.
- `UNKNOWN` is rendered with the explicit guard: insufficient evidence for this exact claim must **not** be presented as `clean` or `safe`.
- `DISPUTED` keeps the material identity/evidence conflict and review reason visible.
- `EXPIRED`, when present in future inputs, is rendered as requiring revalidation for the relevant time context.

The renderer contains no automatic mapping from these statuses to `PASS`, `WATCH`, or `EXCLUDE`.

## Correction demonstration

The canonical correction example is rendered with visible history:

`CONFIRMED → DISPUTED`

The underlying example records that a name-only match was later contradicted by stronger corporate-number/address evidence. The old state is not silently erased; the correction reason and evidence remain visible on the card.

## Policy separation

Some canonical worked examples intentionally contain `policy_context` so the UI boundary can be tested. The card shows such a decision only inside a section explicitly titled as a **separate downstream layer**.

The Evidence Card itself never changes the claim status or invents a policy decision. A configured example `EXCLUDE` remains visibly distinct from the evidence/adjudication fields.

## Challenge / correction path

Every generated card includes a correction/challenge route to the WA Commons GitHub issue tracker and instructs contributors to cite the exact `claim_id` and source locator. This creates a concrete contestability path without giving automated systems authority to overwrite evidence silently.

## Safety regressions

The targeted tests assert that:

- all required identity, claim, provenance, adjudication and review fields are exposed;
- `UNKNOWN` is not rendered as clean/safe;
- disputed identity and reasoning remain visible;
- correction history renders `CONFIRMED → DISPUTED` visibly;
- a downstream policy result remains separated from evidence;
- renderer-added inflammatory labels such as `bad company` or `war profiteer` are forbidden.

## Acceptance review

- cards generated from schema-backed data rather than hand-authored card prose: **PASS**
- at least 20 pilot entities: **PASS — 20 real fixed-snapshot entities; 24 total cards/entities including canonical worked examples**
- mixed statuses/categories: **PASS — 3 statuses, 3 categories**
- one corrected claim visibly demonstrates history: **PASS**
- another contributor can regenerate the same cards from versioned inputs: **PASS — repeated semantic SHA is identical in CI**
- exact source provenance and entity-resolution review state shown: **PASS**
- UNKNOWN and disputed cases remain visibly unresolved: **PASS**
- evidence remains separate from downstream user policy: **PASS**
