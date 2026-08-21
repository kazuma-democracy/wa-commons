# M1.1 Identity Enrichment

## Objective

Attach strong legal/regulatory identifiers to the JPX issuer spine without using company-name similarity as an automatic identity bridge.

## v0 bridge order

```text
JPX security code
    ↓ exact security-code bridge
EDINET code list
    ├─ EDINET code
    └─ Japanese corporate number
             ↓ exact corporate-number validation
        National Tax Agency snapshot/API
             ↓ exact registration-authority ID bridge where available
        GLEIF LEI data
             └─ LEI
```

This order is intentional. A normalized company name may generate a manual-review candidate, but name-only similarity never attaches a strong identifier automatically.

## Source roles

### EDINET code list

Primary crosswalk for listed issuers because the code list can expose the security code together with the EDINET filer code and corporate number. Duplicate rows for the same security code are treated as ambiguous and excluded from automatic linking.

### National Tax Agency corporate-number data

Used to validate an already-known corporate number and to capture the official legal name/address where redistribution terms permit. It is not linked to a JPX issuer by name alone.

The live Corporate Number Web-API requires an application ID. For reproducible M1 tests, frozen source snapshots are preferred.

### GLEIF LEI data

LEI is attached only when the GLEIF registration-authority entity ID exactly matches the already-established Japanese corporate number. If multiple LEIs share the same registration ID in an input snapshot, the automatic bridge is disabled for that ID and the case must be reviewed.

## Ambiguity rules

Automatic enrichment stops when:

- an EDINET security code is duplicated in the selected snapshot;
- a strong identifier conflicts with a strong identifier already attached to the entity;
- a GLEIF registration ID maps to multiple LEIs;
- the only available agreement is a company-name match.

Strong-ID conflicts are represented by `review_state = DISPUTED`; they are not silently overwritten.

## Reproducibility

Each source is supplied as a frozen snapshot plus `SourceRef` metadata:

- source/publisher;
- source key/version;
- snapshot date;
- canonical source URL;
- retrieval timestamp;
- adapter version.

Source file hashes should be stored alongside the pilot manifest.

## Next acceptance step for #12

1. archive an official current JPX snapshot;
2. build a fixed pilot of at least 100 domestic listed issuers;
3. load the matching EDINET code-list snapshot;
4. attach EDINET code and corporate number by exact security code;
5. validate corporate numbers against an NTA snapshot where available;
6. attach LEI by exact corporate-number/registration-ID bridge where available;
7. publish enrichment coverage and unresolved/disputed counts;
8. regenerate the same output from the same frozen inputs.
