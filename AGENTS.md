# AGENTS.md — WA Commons

## Mission

Build WA Commons as useful, voluntary, auditable peace-positive software. The current first proof vehicle is Experiment 001 — Peace Capital.

## Shared autonomous-development baseline

This repository adopts `docs/AUTONOMOUS_DEVELOPMENT_STANDARD.md`, copied byte-for-byte from `kazuma-democracy/autonomous-dev-oss-lab` Standard-Version `1.2`, canonical blob `4db21e5dc666f472f193ea3a990922c9681d5066`.

Project-specific rules may be stricter but may not silently weaken the shared standard.

## Source of truth

For current product work use this order:

1. `ROADMAP.md` for milestone/dependency order and current phase status.
2. The exact selected GitHub Issue for scope and Definition of Done.
3. Current implementation/tests/data and directly referenced docs.
4. Older plans/history only where not superseded.

Do not infer task readiness from conversation history. Verify the current Issue and its dependencies first.

## Current bounded work discipline

- Work on exactly one selected Issue/increment at a time.
- Respect explicit dependency order. For the current M2 path this is `#42 -> #43 -> #44`.
- Do not start a dependent Issue before its predecessor is durably complete.
- Adjacent discoveries become concise Issue/backlog evidence; they do not expand the selected increment.
- Prefer USE / BORROW / ADAPT over BUILD. Do not add another scheduler, supervisor, task database, orchestration framework, or retry layer merely to automate the project.

## Evidence and policy safety

- Evidence, inference, user policy, action and outcome remain separate layers.
- Missing evidence must never become clean/safe/PASS.
- Preserve `UNKNOWN`, `DISPUTED`, `EXPIRED`, unresolved identity, no-match and not-integrated states distinctly where applicable.
- No hidden moral score.
- No consequential classification without an explicit versioned rule and traceable evidence.
- Prefer primary/public sources; record licensing/terms constraints before redistribution or ingestion.
- Do not make real-money trading decisions or execute trades. Peace Capital remains paper/research work until later explicit gates authorize otherwise.

## Verification

Use claim-based, proportional verification from the shared standard. For small bounded changes, run the smallest targeted tests that falsify the changed claims; do not run broad suites merely for reassurance. Milestone/release gates may require broader evidence as defined by `ROADMAP.md` or the selected Issue.

## Git and durability

- Default active product branch is `main` unless the exact assigned work establishes another reviewed branch.
- Never force-push or rewrite history for autonomous work.
- Do not discard unknown dirty work.
- Before completion inspect the diff, exclude unrelated changes, run proportional verification, and leave the repository in a durable reviewable state.
- A coding agent should normally open a PR or otherwise preserve a bounded Git checkpoint rather than accumulating oversized unreviewed work.

## Autonomous runtime status

The shared rules are re-adopted on current `main`, but a single canonical unattended runtime/entrypoint has not yet been production-verified. Do not claim WA Commons `SYNCED` until control-lock/entrypoint/runtime evidence satisfies the canonical adoption manifest.
