# WA Commons

**和をつくる。輪をひろげる。環をめぐらせる。話をつなぐ。**

WA Commons is an open-source experiment from Japan to build technology that makes peaceful choices easier, useful, and economically attractive.

> **Peace should not depend on goodwill alone.**
> People should be able to use a service because it is useful to them — and, as a side effect, move money, attention, transactions, and opportunity toward less violent and more accountable systems.

## Why “WA”?

WA carries several meanings in Japanese:

- **和 — harmony / peace**
- **輪 — circle / connection**
- **環 — cycle / ecosystem**
- **話 — dialogue / conversation**

“Commons” means this should not belong to one company, party, ideology, or founder. The core rules, evidence, code, experiments, successes, and failures should be inspectable and improvable by anyone.

## What we are trying to build

WA Commons explores **peace-positive infrastructure**: tools that people adopt for ordinary reasons — better choices, lower friction, useful information, financial utility — while the system structurally rewards peaceful, transparent, rights-respecting behavior.

We are not trying to build an AI that decides what is morally correct for everyone.

We are building infrastructure that lets users choose their own values, shows the evidence behind every judgment, and automates only bounded, reversible, auditable actions.

## Project direction

WA Commons is organized around three horizons:

- **Short term:** prove one useful, reproducible product loop with **Peace Capital v0** — evidence-driven screening, user-defined policies, and an explainable paper portfolio.
- **Medium term:** extract a reusable **Peace Router** so the same evidence/policy/audit layer can serve a second voluntary economic domain.
- **Long term:** grow into internationally reusable, open peace-incentive infrastructure with bounded maintenance agents and community-owned implementations.

The project is **exit-criteria driven rather than calendar driven**. We do not advance because time passed; we advance when the current claims are demonstrated.

See:

- [`GOALS.md`](GOALS.md) — short-, medium-, and long-term objectives and success criteria.
- [`ROADMAP.md`](ROADMAP.md) — phased development roadmap and hard gates.
- [`MANIFESTO.md`](MANIFESTO.md) — project philosophy.

## Design principles

1. **User benefit first** — a peace-oriented service that harms its users will not spread.
2. **Evidence, not labels** — decisions should trace back to public evidence and explicit rules.
3. **User-defined values** — no central authority decides one mandatory definition of “good.”
4. **Weak authority, extreme persistence** — agents may be tireless, but their permissions stay narrow.
5. **No covert persuasion** — no fake grassroots activity, hidden political manipulation, or impersonation.
6. **Human control for high-impact actions** — large, irreversible, legal, financial, or safety-critical actions require review.
7. **Reversibility by default** — autonomous actions should be small and recoverable.
8. **Open logs and contestability** — evidence, confidence, reasons, and appeals belong in the system design.
9. **Reuse before invention** — prefer proven open-source components and public standards.
10. **Publish failures** — negative results are part of the commons.

## Experiment 001 — Peace Capital

Our first experiment asks:

> **Can software help people invest according to their own peace-related values without treating financial performance as irrelevant?**

The initial prototype will not autonomously trade real money.

It will:

1. collect public evidence about companies;
2. classify specific, auditable activities rather than vague political labels;
3. let each user choose exclusion and preference rules;
4. construct an investable universe that satisfies those rules;
5. compare candidate portfolios on ordinary financial dimensions;
6. explain every exclusion with sources and confidence;
7. run in paper-trading / research mode first.

Possible evidence categories include military and weapons exposure, political finance, conflict-linked supply chains, human-rights controversies, and positive peace-related activities. The schema and thresholds are open research questions, not predetermined doctrine.

See [`experiments/peace-capital/README.md`](experiments/peace-capital/README.md).

## Immediate development target

The next milestone is **M1 — Reproducible Evidence Graph**.

Current priority issues:

- **#2** minimal evidence schema;
- **#3** reusable OSS for entity resolution;
- **#4** public data-source registry;
- **#7** threat model.

Portfolio recommendation work is intentionally gated behind this evidence foundation.

## The longer-term idea

If the experiment works, the same evidence and routing layer could support other voluntary services:

- investment;
- purchasing;
- banking and finance;
- procurement;
- donations;
- civic and institutional maintenance agents.

The long-term hypothesis is simple:

> **When peaceful behavior becomes economically useful, peace gains a persistent incentive rather than relying only on persuasion.**

## Join the experiment

You do not need to agree on politics to contribute.

We need people who can challenge assumptions as much as people who can write code.

Useful contributions include:

- finding reliable public datasets;
- verifying evidence and provenance;
- entity resolution and corporate ownership research;
- finance and portfolio construction;
- legal and compliance review;
- UX and accessibility;
- Japanese/English translation;
- adversarial review and bias testing;
- privacy and security;
- documenting failed approaches;
- proposing new peace-positive experiments.

Start with the open issues or use the contribution templates to propose a small, verifiable task.

## Status

**Day 0 / public experiment.**

We are deliberately publishing before we know the final answer. The reasoning, discarded ideas, design changes, and failures are part of the project.

## License

Proposed initial licensing:

- Code: **Apache License 2.0**
- Documentation and public research: **CC BY 4.0**

Data sources retain their original licenses and terms. Dataset licensing must be tracked source by source.
