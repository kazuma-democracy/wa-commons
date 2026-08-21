# M1.1 Identity Spine — implementation note

Status: implementation in progress.

## Source order

The canonical Japanese company identity spine resolves identifiers in this order:

1. JPX listed-security code / issuer metadata;
2. National Tax Agency corporate number;
3. EDINET filer code;
4. GLEIF LEI where available.

A source identifier is evidence for identity, not a moral or policy classification.

## External-access constraints

- JPX publishes a current TSE-listed-issues list and a downloadable company/security dataset. Source snapshots must be versioned before transformation.
- The National Tax Agency Corporate Number Web API is REST-based and requires an application ID. The API can search by corporate number, name, or update period and can return history depending on request parameters.
- EDINET API Version 2 requires an API key.
- GLEIF provides public LEI data and API/download access; adapters must tolerate additive API fields and preserve source-native identifiers.

API credentials are never committed. M1.1 must also work from local frozen source snapshots so a third party can reproduce the identity graph without live services.

## Canonical ID rule

WA Commons entity IDs are internal opaque IDs and must not be derived from a mutable company name.

For v0, an issuer discovered from JPX receives a deterministic ID from its stable namespace + source key, for example:

`wa:org:jp:tse:7203`

This does **not** imply that ticker/security code and legal entity are permanently identical. Corporate reorganizations, multiple securities, mergers, and spin-offs must be represented explicitly and can supersede a previous mapping.

## Merge rule

Two source records may be merged automatically only when one of these is true:

1. an exact strong identifier links them (e.g. corporate number, LEI, EDINET code mapped through an authoritative source); or
2. multiple non-name attributes agree under a versioned deterministic rule and no strong identifier conflicts.

Name-only matching can propose candidates but cannot publish a consequential link.

## Conflict rule

If strong identifiers conflict, do not pick a winner silently. Emit a review record with `DISPUTED` state and keep both source records addressable.

## Parent/subsidiary rule

Parent and subsidiary companies remain different entities. Ownership is a relationship edge, not an identity merge.

## Reproducibility

Every generated entity dataset must record:

- source name;
- source snapshot date/version;
- retrieval timestamp;
- source URL;
- source file hash where practical;
- adapter version;
- normalization-rule version.

The first pilot target remains at least 100 Japanese listed issuers.