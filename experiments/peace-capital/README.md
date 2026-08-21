# Experiment 001 — Peace Capital

## Research question

Can an evidence-driven agent help a user avoid activities they personally reject while preserving ordinary investment goals such as diversification, risk control, cost awareness, and expected return?

## Non-goals for v0

- No autonomous real-money trading.
- No universal moral score.
- No opaque blacklist.
- No unsupported political labels.
- No claim that an investment is financially superior merely because it matches a value preference.

## Proposed pipeline

```text
Public / licensed sources
        ↓
Source adapters
        ↓
Entity resolution
        ↓
Evidence Graph
        ↓
User Policy
        ↓
PASS / WATCH / EXCLUDE
        ↓
Investable universe
        ↓
Portfolio research / paper trading
        ↓
Explainable report
```

## Candidate evidence classes

These are hypotheses to evaluate, not settled rules:

- military/weapons revenue and contracts;
- controversial weapons;
- political donations and political-finance relationships;
- conflict-linked supply chains;
- documented human-rights controversies;
- positive peace-building or public-benefit activities.

Each class must define objective evidence requirements before implementation.

## What would make this useful to a normal user?

The prototype should measure:

- research time saved;
- number of companies automatically resolved and checked;
- false-positive / disputed rate;
- diversification after user exclusions;
- benchmark tracking difference;
- portfolio cost and turnover;
- clarity of explanations.

## First milestone

Take a small, fixed universe of companies and produce a reproducible evidence report and paper portfolio from version-controlled rules.
