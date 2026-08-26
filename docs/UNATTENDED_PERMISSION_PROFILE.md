# Unattended Permission Profile Mapping

Status: PROPOSED REPO ADOPTION
Date: 2026-08-26 JST

Canonical authority design lives in `kazuma-democracy/autonomous-dev-oss-lab`:

- `docs/UNATTENDED_GIT_AUTHORITY.md`
- `docs/UNATTENDED_PERMISSION_PROFILE.md`

WA Commons adopts the same fail-closed model for autonomous development.

## WA Commons runtime behavior

- routine in-scope reads/tests/edits on an explicitly designated working branch should not require repeated human approval;
- Git object creation and fast-forward update of that designated non-default branch may be session/profile allowed only after repository/branch/current-parent/force=false checks;
- bounded Issue/PR evidence comments for the active task may be session/profile allowed;
- `main`/`master`, force push, merge, settings/rulesets, secrets/auth, billing, release/deployment, branch deletion, and destructive cleanup always require explicit human authority;
- repository-specific publication/community/governance rules remain stricter where applicable.

## Runtime implementation

Do not guess Codex or Claude Code config syntax. The local agent must inspect the installed version, current config, and supported permission/approval mechanisms, then implement the narrowest rules that satisfy the canonical contract.

If branch-conditional permission cannot be expressed safely, keep remote branch mutation behind explicit approval rather than using a broad permanent `Always allow`.

## Acceptance

- routine bounded development reaches a durable working-branch commit without repeated human permission prompts;
- dangerous/default-branch operations still stop;
- exact effective runtime configuration and version are recorded as evidence;
- `ROUTINE_COURIER = 0` after initial setup for routine development work.
