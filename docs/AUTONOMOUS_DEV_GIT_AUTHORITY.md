# Autonomous Development Git Authority

Status: proposed repo policy
Date: 2026-08-26 JST

This repository adopts the project-wide unattended Git authority pattern defined in `kazuma-democracy/autonomous-dev-oss-lab` at `docs/UNATTENDED_GIT_AUTHORITY.md`.

## Purpose

Allow autonomous coding/review agents to make bounded progress without repeated human approval while keeping high-risk Git/GitHub actions fail-closed.

## Allowed for the active unattended session

Only for an explicitly designated non-default working branch, after re-reading repository identity and remote HEAD:

- create Git blobs/trees/commits;
- fast-forward update that designated branch with `force=false`;
- add bounded Issue/PR evidence comments for the active task;
- read/request independent review and record its result.

Before every remote branch update verify:

1. repository is `kazuma-democracy/wa-commons`;
2. target is the task-designated working branch;
3. target is not `main`/`master`;
4. remote HEAD equals the expected parent SHA;
5. update is fast-forward and `force=false`;
6. required tests/verification have passed;
7. no unrelated files are included.

If any gate is unknown or mismatched, stop and request `AUTH`/`RESPEC`.

## Always require explicit human authority

- update/push to `main` or `master`;
- force push/history rewrite;
- merge/auto-merge;
- branch deletion;
- repository settings, branch protection, rulesets;
- secrets/auth/account changes;
- billing/spend changes;
- release/deployment publication unless separately authorized;
- destructive reset/clean/stash/discard of unknown work;
- widening this authority contract during the same task that relies on it.

## Post-write proof

After every permitted branch update, re-fetch the remote HEAD, verify the intended SHA, record durable evidence, and name the next agent/action when a handoff is required.

A local commit, model self-report, transport ACK, or API success alone is not project PASS.

Target: `ROUTINE_COURIER = 0` after initial setup.
