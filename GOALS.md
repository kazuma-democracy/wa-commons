# WA Commons Goals

WA Commons exists to test one core hypothesis:

> **Can useful software make peace-positive choices economically easier and more attractive, so that repeated ordinary use creates persistent incentives for less violent, more transparent, and more rights-respecting behavior?**

The project advances by evidence and exit criteria, not by dates alone. A phase is complete only when its claims can be demonstrated.

## Short-term goal — prove one useful product loop

### Objective
Build **Peace Capital v0**, a research and paper-trading product that helps a user apply their own peace-related values to investment research without pretending ordinary financial goals do not matter.

### What must exist
- A versioned Evidence Graph for a small, fixed company universe.
- Public source registry with provenance, update cadence, license/terms, and limitations.
- Reusable entity-resolution layer selected through an OSS review.
- Explicit user policy format separating exclusions from preferences.
- Evidence statuses including `CONFIRMED`, `DISPUTED`, `UNKNOWN`, and `EXPIRED`.
- Reproducible PASS / WATCH / EXCLUDE decisions generated only from user policy + evidence.
- Human-readable evidence cards explaining every consequential classification.
- A paper portfolio compared with a normal benchmark on diversification, concentration, tracking error/difference, turnover, and estimated costs.
- Threat model and ideological-bias red-team review.
- A minimal public interface or report that a non-developer can understand.

### User benefit we must prove
At least one benefit must be demonstrated independently of agreement with the mission:
- research time saved;
- clearer evidence than manual research;
- easier portfolio customization;
- useful risk/constraint visibility;
- lower decision friction.

### Exit criteria
Short-term is complete when:
1. another contributor can reproduce a company classification from versioned evidence and policy;
2. disputed evidence can be challenged and visibly corrected without erasing history;
3. a user can create at least one policy profile and receive an explainable paper portfolio;
4. the portfolio trade-offs versus a benchmark are measured honestly;
5. no real-money autonomous trading is required for the demo;
6. at least one external contributor can make a useful contribution without private onboarding.

### Explicit non-goals
- No universal WA Commons moral score.
- No opaque blacklist.
- No claim that peace-aligned investing necessarily outperforms.
- No autonomous real-money execution.
- No attempt to cover every company, country, or ethical issue in v0.

---

## Medium-term goal — turn Peace Capital into a reusable Peace Router

### Objective
Generalize the successful parts of Experiment 001 into an open **Peace Router**: a reusable evidence-and-policy layer that can rank or route voluntary choices while preserving direct user utility.

### What must exist
- Stable Evidence Graph and entity identity layer.
- Versioned user-policy language that can be forked and shared without becoming an official ideology.
- Explainable ranking/routing API.
- Appeals/correction workflow and immutable or append-oriented decision history.
- Scheduled evidence re-checking, expiry, and change detection.
- Bounded agent maintenance: low-risk automation only, with human review queues for consequential changes.
- At least two policy profiles that disagree meaningfully while using the same evidence infrastructure.
- At least one second domain prototype beyond investment, chosen by evidence of user benefit.

Candidate second domains include purchasing, procurement, banking/finance comparison, donations, or another voluntary economic decision. Selection is not predetermined.

### User benefit we must prove
The routing layer must make an ordinary task better — faster, cheaper, clearer, safer, or more configurable — rather than merely adding a moral score.

### Peace-positive effect we must measure
We should be able to estimate a real behavioral or economic signal such as:
- value of assets screened/routed;
- purchases or transactions redirected;
- number of decisions where a user selected a higher peace-policy match without sacrificing a stated primary constraint;
- number of verified evidence corrections;
- adoption of the open evidence/policy standards by downstream projects.

These are signals, not proof that the system caused peace.

### Exit criteria
Medium-term is complete when:
1. Peace Capital is only one client of a shared routing core;
2. a second domain uses the same evidence/policy/audit primitives;
3. users can choose or author materially different policies;
4. automated maintenance can keep evidence current without granting agents broad authority;
5. measured user utility is positive for a meaningful pilot group;
6. independent contributors or downstream projects can reuse the core without founder involvement.

---

## Long-term goal — build open peace-incentive infrastructure

### Objective
Make WA Commons an internationally reusable public technology layer for creating systems where **peace-positive behavior can gain practical and economic advantages without coercion or centralized moral authority**.

The long-term project is not one app. It is a commons of interoperable components, standards, evidence, policy profiles, and bounded agents.

### Long-term capabilities
- International, multilingual evidence connectors maintained by communities closest to the data.
- Portable policy profiles reflecting different communities and legal contexts.
- Peace Router integrations across investment, purchasing, procurement, finance, and other voluntary economic systems where useful.
- Bounded maintenance agents that monitor changes, revalidate evidence, reopen unresolved issues, and request human decisions when authority is exceeded.
- Public standards for provenance, contestability, uncertainty, policy versioning, and agent authority.
- Ephemeral public-interest agents/institutions that can be created for narrowly scoped problems with explicit budgets, permissions, expiry, audit logs, and shutdown conditions.
- Independent forks and regional implementations that do not require agreement with the original maintainers.

### Long-term success signals
WA Commons should be considered successful only if some combination of these becomes true:
- people use products built on it because they are genuinely useful;
- peaceful/transparent organizations can attribute real economic opportunity to the routing ecosystem;
- users retain control of their own values rather than accepting a central score;
- evidence corrections and dissent remain possible at scale;
- third parties operate compatible implementations without asking permission;
- the project can outlive its founder and resist capture by a single party, company, donor, government, or ideology.

### What WA Commons must never become
- a centralized political blacklist;
- a covert persuasion or astroturfing system;
- an autonomous authority that punishes people or organizations;
- a mechanism that hides uncertainty behind AI confidence;
- a financial system that sacrifices users while claiming moral superiority;
- an organization whose survival depends on one founder's permanent attention.

---

## Strategic sequence

```text
Evidence you can inspect
        ↓
Policies users control
        ↓
Useful recommendations
        ↓
Measured user benefit
        ↓
Repeated voluntary adoption
        ↓
Economic / practical peace-positive signal
        ↓
Reusable Peace Router
        ↓
Bounded autonomous maintenance
        ↓
International public infrastructure
```

The sequence matters. WA Commons should not skip evidence, user utility, and contestability in pursuit of scale.