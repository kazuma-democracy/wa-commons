# WA Commons Development Roadmap

This roadmap turns the project goals in [`GOALS.md`](GOALS.md) into an implementation sequence.

WA Commons is **exit-criteria driven**. Dates may be added for planning, but phases are not considered complete because a calendar deadline passed.

## North Star

Build useful, voluntary software where repeated use can create a measurable peace-positive economic or practical signal.

The first proof vehicle is **Experiment 001 — Peace Capital**.

---

## Phase 0 — Public foundation

### Purpose
Make the project understandable, challengeable, and contributable before building a large system.

### Deliverables
- [x] Publish README and manifesto.
- [x] Publish governance, security, and contribution principles.
- [x] Publish Experiment 001 scope.
- [x] Open first contribution issues.
- [x] Establish reuse-before-invention policy.
- [ ] Publish short / medium / long-term goals.
- [ ] Audit Japanese/English terminology.
- [ ] Complete first ideological-bias red-team.
- [ ] Establish a lightweight decision-log convention.

### Exit condition
A newcomer can understand the mission, identify what is uncertain, challenge a claim, and make a useful contribution without private onboarding.

### Current issues
- #8 Red-team manifesto/governance.
- #9 Review Japanese/English framing.

---

## Phase 1 — Evidence foundation

### Purpose
Prove that consequential company classifications can be reproduced from versioned evidence rather than opaque model judgment.

### Workstream 1A — Evidence schema
- Define minimal evidence object.
- Separate observation, evidence, inference, policy, action, and outcome.
- Support `CONFIRMED`, `DISPUTED`, `UNKNOWN`, `EXPIRED`.
- Preserve correction history rather than silently rewriting it.

**Issue:** #2

### Workstream 1B — Source registry
- Inventory public/licensed data sources.
- Record publisher, scope, access, cadence, license/terms, identifiers, history, evidentiary strength, and limitations.
- Prefer primary/public sources where possible.
- Adopt / watch / reject each candidate explicitly.

**Issue:** #4

### Workstream 1C — Entity resolution
- Review existing OSS before writing a matcher.
- Test Japanese company names, aliases, subsidiaries, parent ownership, ticker/legal-name differences, and historical names.
- Choose or adapt the smallest sufficient reusable stack.

**Issue:** #3

### Workstream 1D — Threat model
- Data poisoning.
- Source compromise/disappearance.
- False entity matches.
- Coordinated manipulation.
- Defamation / unsupported accusation risk.
- Model/tool compromise.
- Permission escalation.
- Privacy leakage.

**Issue:** #7

### Milestone M1 — Reproducible Evidence Graph
For a small fixed company universe, every material claim can be regenerated from a versioned source registry and evidence schema, with disputes visible.

### Gate to Phase 2
Do not build portfolio recommendations until M1 exists.

---

## Phase 2 — User policy and classification engine

### Purpose
Let different users apply different peace-related values to a shared evidence layer without creating one official WA Commons moral score.

### Workstream 2A — Policy language
Define a small human-readable and machine-readable policy format covering:
- exclusions vs preferences;
- thresholds;
- `UNKNOWN` and `DISPUTED` handling;
- policy versioning;
- shareable/forkable profiles.

**Issue:** #5

### Workstream 2B — Deterministic classification
Implement:

```text
Evidence Graph + User Policy
             ↓
      PASS / WATCH / EXCLUDE
```

Requirements:
- no classification without an explicit rule;
- every outcome explains which rule fired;
- policy and evidence versions are recorded;
- the same inputs reproduce the same result;
- LLMs may assist extraction/review but must not become the hidden source of truth.

### Workstream 2C — Evidence cards
For each consequential classification show:
- entity;
- relevant claim;
- source/provenance;
- evidence/retrieval dates;
- status and confidence;
- policy rule;
- why the rule fired;
- challenge/correction path.

### Milestone M2 — Explainable company screener
A non-developer can choose a policy and understand why each company is PASS / WATCH / EXCLUDE.

### Gate to Phase 3
At least two meaningfully different policy profiles must work against the same evidence layer.

---

## Phase 3 — Peace Capital paper portfolio

### Purpose
Test whether the product remains financially useful after value constraints are applied.

### Workstream 3A — Evaluation specification
Before implementation, define:
- benchmark;
- diversification/concentration metrics;
- tracking difference/error;
- turnover;
- estimated costs;
- sector/factor drift;
- policy-threshold sensitivity;
- versioned reproducibility.

**Issue:** #6

### Workstream 3B — Portfolio construction
Use mature portfolio libraries where possible. Do not invent an optimizer unless the OSS review demonstrates a gap.

Initial scope:
- fixed investment universe;
- paper only;
- configurable exclusions/preferences;
- ordinary risk/diversification constraints;
- no claim of guaranteed or superior returns.

### Workstream 3C — User-facing report
Show:
- selected policy;
- excluded/watch companies and reasons;
- resulting portfolio;
- benchmark comparison;
- concentration and risk trade-offs;
- what changed because of the policy;
- unresolved/unknown evidence.

### Milestone M3 — Peace Capital v0
A user can create a reproducible paper portfolio aligned with their own policy and see the financial trade-offs honestly.

### Gate to Phase 4
Demonstrate at least one concrete non-ideological user benefit such as research time saved, easier customization, clearer evidence, or lower decision friction.

---

## Phase 4 — Product utility validation

### Purpose
Test the central adoption hypothesis: people must have a reason to use the product beyond supporting the mission.

### Workstream 4A — Pilot users
Recruit a small pilot group with diverse policy preferences.

Measure:
- time saved versus manual research;
- comprehension of evidence cards;
- correction/dispute rate;
- policy customization usage;
- repeated usage intent;
- portfolio trade-offs users consider acceptable/unacceptable.

### Workstream 4B — Adversarial evaluation
- False-positive hunt.
- False-negative hunt.
- Political/ideological bias review.
- Entity-resolution stress tests.
- Source-license audit.
- Accessibility and UX review.

### Workstream 4C — Publish negative results
If exclusions cause unacceptable concentration, evidence is too weak, or users do not find the tool useful, publish the finding rather than hiding it.

### Milestone M4 — Utility proof
There is evidence that at least one target user group wants the product for a practical reason.

### Kill / pivot rule
If no meaningful user benefit survives honest testing, do not proceed to financial execution. Reuse the Evidence Graph elsewhere or change the experiment.

---

## Phase 5 — Peace Router core

### Purpose
Extract the reusable infrastructure so Peace Capital becomes one client rather than the whole project.

### Core components
- Evidence Graph.
- Entity identity layer.
- User policy language.
- Explainable routing/ranking engine.
- Provenance and audit log.
- Appeals/corrections model.
- Domain adapter interface.

### Architecture target

```text
Sources
   ↓
Evidence + Identity
   ↓
User Policy
   ↓
Peace Router
   ↓
┌────────────┬─────────────┬──────────────┐
│ Investment │ Purchasing  │ Future domain│
└────────────┴─────────────┴──────────────┘
```

### Milestone M5 — Domain-independent router
A second domain can reuse the core without duplicating the evidence/policy/audit stack.

---

## Phase 6 — Second economic experiment

### Purpose
Test whether the mechanism generalizes beyond investing.

The domain is selected based on evidence, not preference. Candidates include:
- product/service purchasing;
- procurement/vendor choice;
- banking or financial-product comparison;
- donations;
- another voluntary economic decision.

### Selection criteria
1. Direct user benefit exists.
2. Repeated use could create a peace-positive externality.
3. Participation is voluntary.
4. Evidence and rules are auditable.
5. A large share can be built from existing OSS/data.
6. The system can be tested without granting dangerous authority.

### Milestone M6 — Two-domain proof
The same Peace Router core serves two different decision domains.

---

## Phase 7 — Bounded autonomous maintenance

### Purpose
Add the agent capability that motivated WA Commons: persistence without broad authority.

### Agent jobs
- scheduled source re-checking;
- change detection;
- evidence expiry;
- revalidation;
- reopening unresolved evidence;
- detecting broken data sources;
- proposing entity merges/splits;
- preparing human review packets;
- applying reversible low-risk updates where explicitly authorized.

### Required guardrails
- least privilege;
- explicit action authority;
- rate limits;
- audit logs;
- reversible defaults;
- human approval for consequential financial/legal/political actions;
- no covert persuasion or impersonation.

### Milestone M7 — Relentless but weak agent
The system can maintain its evidence layer for an extended period with low human effort while remaining bounded and auditable.

---

## Phase 8 — Internationalization and ecosystem

### Purpose
Make the infrastructure usable beyond one country's politics, datasets, and assumptions.

### Workstreams
- multilingual documentation and UI;
- country/domain source adapters;
- local policy profiles;
- portable schemas and APIs;
- community-maintained data connectors;
- governance for disputes across jurisdictions;
- independent downstream implementations.

### Milestone M8 — Forkable commons
At least one independent group can operate or fork a compatible implementation without founder involvement.

---

## Phase 9 — Long-horizon peace infrastructure

This phase is intentionally exploratory. Candidates include:
- additional Peace Router domains;
- public-interest maintenance agents;
- commitment/evidence/resource/authority graphs;
- narrow ephemeral institutions with explicit budgets, permissions, expiry, and shutdown rules;
- interoperability standards for evidence, policy, audit, and agent authority.

The project should only enter these areas when earlier phases demonstrate user utility, safety, and governance capacity.

---

# Dependency order

```text
Phase 0 Public foundation
        ↓
Phase 1 Evidence foundation
        ↓
Phase 2 User policy + classification
        ↓
Phase 3 Peace Capital paper portfolio
        ↓
Phase 4 Utility validation
        ↓
Phase 5 Peace Router core
        ↓
Phase 6 Second domain
        ↓
Phase 7 Bounded autonomous maintenance
        ↓
Phase 8 International ecosystem
        ↓
Phase 9 Long-horizon infrastructure
```

## Hard gates

WA Commons should **not**:
- add real-money autonomous trading before evidence, reproducibility, threat modeling, and user-utility validation;
- generalize into many domains before Experiment 001 teaches us what the reusable core actually is;
- build custom infrastructure before an OSS reuse review;
- hide disputed evidence to make the product look cleaner;
- grant agents broad authority merely because the software is technically capable of it.

## Immediate next milestone

**M1 — Reproducible Evidence Graph.**

The current highest-priority issues are #2, #3, #4, and #7. They establish the evidence schema, reusable entity-resolution stack, source registry, and threat model required before portfolio work begins.