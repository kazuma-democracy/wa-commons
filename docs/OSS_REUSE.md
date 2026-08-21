# Reuse-First Policy

WA Commons should not build infrastructure that mature open-source projects already solve.

Before writing a major subsystem, create a short reuse review covering:

- existing OSS candidates;
- license;
- maintenance activity;
- deployment model;
- API/data model fit;
- security history;
- localization needs;
- why adaptation is insufficient, if proposing new code.

Likely categories to investigate first include:

- durable workflow engines;
- agent orchestration;
- entity resolution and knowledge graphs;
- civic participation platforms;
- policy/rules-as-code engines;
- provenance/audit standards;
- change detection and web ingestion;
- portfolio optimization libraries.

A new subsystem should be considered a last resort, not a default.
