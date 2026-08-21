# Technical and Governance Principles

## Core separation

WA Commons should keep these layers distinct:

1. **Observation** — what public/authorized sources say.
2. **Evidence** — normalized claims with provenance and timestamps.
3. **Inference** — what can reasonably be derived from evidence.
4. **Policy** — what a user chooses to allow, avoid, or prefer.
5. **Action** — what the agent is authorized to do.
6. **Outcome** — what actually happened after the action.

## Required fields for consequential judgments

- entity ID;
- claim;
- evidence source;
- evidence date;
- retrieval date;
- confidence;
- rule/policy version;
- reasoning summary;
- status: confirmed / disputed / unknown / expired;
- appeal or correction path.

## Autonomous-action rule

Default autonomous actions should be:

- low impact;
- reversible;
- within explicit user permission;
- logged;
- rate limited;
- independently reviewable.

High-impact financial, legal, political, physical, or safety-critical actions require human approval unless a future governance process explicitly establishes stronger safeguards.
