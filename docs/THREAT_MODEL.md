# WA Commons Threat Model v0.1

Status: **M1 bootstrap threat model**  
Related issue: #7

WA Commons can cause reputational, financial, political, and legal harm if it attributes the wrong facts to the wrong entity or automates an action on weak evidence. Therefore the threat model treats **false attribution and institutional capture** as first-class security problems, not merely data-quality bugs.

## Safety properties we must preserve

1. **Identity integrity** — evidence is attached to the correct legal entity.
2. **Evidence integrity** — source, date, content, and locator are not silently altered.
3. **Semantic integrity** — an allegation is not converted into a finding; a contract is not converted into weapons activity without evidence.
4. **Policy separation** — facts do not silently become a universal moral score.
5. **Authorization integrity** — research automation cannot escalate into consequential execution.
6. **Contestability** — affected claims can be challenged and corrections remain visible.
7. **Reproducibility** — a past decision can be regenerated from versioned evidence and policy.
8. **Availability without panic** — source outages or missing data degrade to UNKNOWN, not fabricated certainty.

## Threat table

| ID | Threat | Example | Impact | Likelihood | Detection | Mitigation | Residual risk | Deployment gate |
|---|---|---|---|---|---|---|---|---|
| T01 | Entity false positive | Same-name company is linked to a political donation or military contract | Critical | High | conflicting address/IDs; manual sampling; labeled match set | deterministic IDs first; multi-attribute matching; ambiguity queue; no name-only auto-link for consequential claims | Medium | **BLOCK** if consequential claims can publish from name-only matches |
| T02 | Parent/subsidiary conflation | Subsidiary contract is attributed to parent or vice versa | High | High | ownership graph; legal-entity identifiers | model relationship separately; never collapse group identity; policy must explicitly define propagation | Medium | **BLOCK** until relationship semantics exist |
| T03 | Source poisoning | Compromised page/API introduces false company record | Critical | Medium | hashes, cross-source comparison, sudden-change alerts | provenance; source trust tier; signatures where available; two-source confirmation for high-risk changes | Medium | Block real-money or public high-impact action on unverified anomaly |
| T04 | Source revision/disappearance | Government PDF changes or vanishes | High | High | hash/version change; retrieval failures | timestamp, locator, permitted archival copy/hash, immutable observation log | Medium | Must preserve enough provenance to explain old decision |
| T05 | Context stripping | MOD office-chair contract is labeled weapons activity | Critical | High | category-vs-object validation; reviewer audits | narrow predicates; contract subject classifier; separate `military_contract` from `weapons_activity`; SIPRI-style military-specific definition | Low/Medium | **BLOCK** universal contract→weapons rule |
| T06 | Allegation laundering | NGO complaint becomes “company committed abuse” | Critical | High | source type/status checks | encode allegation/procedure/finding separately; stronger predicate requires stronger evidence | Low/Medium | **BLOCK** generic violation boolean |
| T07 | Stale evidence | Company exited activity years ago but remains excluded | High | High | expiry dates; scheduled source recheck | effective dates; evidence expiry; revalidation queue; policy lookback windows | Medium | Must support EXPIRED before user-facing routing |
| T08 | Missing evidence interpreted as innocence | Company with poor disclosure is rated “clean” | High | High | coverage metrics | UNKNOWN distinct from CONFIRMED absence; source coverage score; no default PASS from missing records | Medium | **BLOCK** if absence-of-record automatically means safe |
| T09 | Missing evidence interpreted as guilt | Search failure produces WATCH/EXCLUDE | High | Medium | adapter health and completeness metrics | fail closed to UNKNOWN for evidence, not moral judgment | Low | No exclusion on ingestion failure alone |
| T10 | Model hallucination | LLM invents a contract, donation, or source | Critical | Medium | every claim requires source locator; deterministic validator | models may propose extraction only; no source = no evidence; schema validation | Low/Medium | **BLOCK** model-only factual claims |
| T11 | Prompt/tool injection from source text | Malicious webpage tells agent to alter rules or secrets | High | Medium | tool-call policy; content sandboxing | treat source text as untrusted data; separate extraction from agent authority; allowlist tools; no secrets in prompt context | Medium | Required before autonomous crawling |
| T12 | Policy capture | Maintainer/funder inserts ideology into core scoring | Critical | Medium | public diffs; governance review; profile comparison | no single mandatory moral score; user-defined policy profiles; decision logs; forkability | Medium | Major policy schema changes require public review |
| T13 | Data-source capture | One advocacy/corporate source dominates disputed area | High | Medium | source diversity metrics | source hierarchy; evidence contradiction model; disclose publisher/conflict | Medium | No opaque single-source blacklists |
| T14 | Coordinated false reporting | Group floods correction/accusation issues | Medium/High | Medium | anomaly/rate monitoring | submissions are leads, not evidence; authenticated moderation; source requirements; rate limits | Medium | Public challenge path may launch with moderation controls |
| T15 | Suppression via coordinated challenges | True evidence is mass-disputed to make it disappear | High | Medium | challenge provenance and duplicate detection | challenge does not delete evidence; DISPUTED remains visible; adjudication rules | Low/Medium | Never auto-delete on challenge volume |
| T16 | Defamation/reputational harm | Wrongly labels named company as war-profiteer or rights violator | Critical | Medium | legal/editorial review; false-positive audits | factual narrow language; no inflammatory labels; citations; correction workflow; uncertainty displayed | Medium | **BLOCK** public accusatory labels not grounded in explicit predicate/evidence |
| T17 | License violation | Project redistributes restricted commercial dataset | High | Medium | source registry/license CI/checklist | license metadata required; isolate restricted data; prefer primary/open sources; legal review | Low/Medium | **BLOCK** distribution when rights=unknown/restricted |
| T18 | Privacy leakage | Personal donor/address data exposed beyond lawful/public purpose | High | Medium | privacy review | minimize personal data; focus on organizations; avoid sensitive-trait inference; redact where not necessary | Medium | Personal-data datasets require explicit review |
| T19 | Secret/credential compromise | API/broker credentials leak | Critical | Medium | secret scanning, audit logs | no real-money credentials in M1; secret manager later; least privilege; rotation | Low in M1 | **BLOCK** real execution until credential architecture exists |
| T20 | Permission escalation | Research agent gets ability to trade/post/contact automatically | Critical | Medium | capability registry; audit | separate research and action identities; explicit grants; human approval; reversible low-risk defaults | Low/Medium | **BLOCK** high-impact autonomy without governance decision |
| T21 | Market manipulation / coordinated trading | Router causes concentrated buying/selling or becomes signal for manipulation | Critical | Low/Medium later | position/flow monitoring | paper mode first; diversification; rate/size caps; licensed partner/legal review; no coordinated pump narratives | Medium | **BLOCK** real-money scale until legal/market-abuse review |
| T22 | Financial misrepresentation | “Peace aligned” is marketed as higher-return/safer without evidence | High | Medium | copy/research review | separate values from financial claims; benchmark honestly; no guaranteed benefit claims | Low | Required before public investment product claims |
| T23 | Benchmark gaming | Chosen benchmark/time window makes paper results look good | High | Medium | preregister evaluation; alternate benchmarks | versioned methodology; out-of-sample periods; report tracking error, turnover, concentration and failures | Low/Medium | Paper evaluation must be reproducible |
| T24 | Feedback-loop bias | Companies with more public scrutiny accumulate more negative evidence | High | High | disclosure/coverage metrics | normalize by evidence coverage; never equate evidence count with wrongdoing; show source density | Medium | Scoring cannot use raw allegation counts without correction |
| T25 | Geographic/cultural bias | US/EU data availability makes non-Western firms systematically UNKNOWN or misjudged | High | High | coverage by jurisdiction/language | jurisdiction-specific sources; multilingual review; UNKNOWN; local forks/contributors | Medium/High | International claims must display coverage limits |
| T26 | Historical identity drift | Merger/rename causes old conduct to attach incorrectly to current entity | High | Medium | dated identifiers/ownership | time-bounded entity relationships; predecessor/successor links; policy defines inheritance | Medium | Must exist before long-history portfolio screen |
| T27 | Automated source breakage | Parser silently maps wrong columns after website change | High | High | schema/fixture tests; row-count/domain anomalies | pinned adapters; contract tests; change alerts; manual review of major diffs | Low/Medium | Autonomous refresh needs adapter-health gate |
| T28 | Denial of service / cost exhaustion | Attack floods expensive matching/model/API calls | Medium | Medium | usage/cost alerts | rate limits; cache; batch; quotas; cheap deterministic path first | Low | Required before public API |
| T29 | Audit-log tampering | Evidence/correction history rewritten | Critical | Low/Medium | Git/object hashes; append checks | append-oriented logs; immutable artifacts where practical; signed releases later | Low/Medium | Material decisions require durable history |
| T30 | Founder key-person risk | One maintainer disappears or controls all releases | High | Medium | governance health | documented process; multiple maintainers; reproducible builds/data; transfer procedure | Medium | Relevant before production ecosystem |

## Threat actors

WA Commons should assume pressure from multiple directions, not one political side:

- companies seeking removal of accurate unfavorable records;
- campaigners seeking inclusion on weaker-than-required evidence;
- political organizations seeking partisan capture;
- market participants seeking trading advantage;
- trolls seeking reputational damage;
- malicious data publishers;
- compromised upstream software/dependencies;
- well-intentioned contributors making confident mistakes;
- maintainers/funders with undisclosed conflicts.

## Trust boundaries

```text
Internet/public sources       UNTRUSTED CONTENT
          ↓
source adapters               LIMITED / TESTED
          ↓
raw observations              IMMUTABLE-ISH + HASHED
          ↓
entity resolution             PROBABILISTIC, REVIEWABLE
          ↓
evidence adjudication         VERSIONED RULES
          ↓
user policy                   USER CONTROLLED
          ↓
research output               EXPLAINABLE
          ↓
consequential action          DENIED BY DEFAULT
```

An LLM never crosses a trust boundary merely because its confidence is high.

## M1 blocking conditions

M1 is **not complete** if any of the following is true:

- consequential claims can be attached by name-only fuzzy match with no review path;
- source URL/date/locator is optional;
- `UNKNOWN`, `DISPUTED`, and `EXPIRED` cannot be represented;
- allegation and finding are represented with the same predicate;
- evidence deletion is the normal correction mechanism;
- dataset/source licensing is not tracked;
- a MOD contract automatically maps to `weapons_activity`;
- model output can create evidence without a source;
- parent/subsidiary identity is collapsed by default;
- evidence absence automatically produces PASS.

## Pre-real-money gates

Even after M1, real-money execution remains prohibited until all are satisfied:

1. reproducible evidence pipeline;
2. calibrated entity-resolution false-positive rate;
3. published threat-model review;
4. reproducible paper portfolio and benchmark methodology;
5. user-benefit validation that does not rely on ideological motivation;
6. financial-regulatory/legal review for target jurisdiction;
7. credential/authorization architecture;
8. size/rate/risk controls and emergency stop;
9. explicit governance approval.

## Incident handling principle

When a harmful classification is discovered:

1. stop downstream propagation where necessary;
2. preserve the original evidence and decision history;
3. mark the claim `DISPUTED` or corrected rather than silently deleting it;
4. publish the correction reason and affected versions;
5. re-run dependent outputs;
6. determine root cause: source, matcher, extraction, rule, policy, or action;
7. add a regression fixture/test before restoring automation.
