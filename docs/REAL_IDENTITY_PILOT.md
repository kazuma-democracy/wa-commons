# Real Identity Pilot — M1.1 closure run

This run exists to close #12 with real public data rather than fixtures.

## Official inputs

- JPX: TSE listed issues, month-end July 2026. JPX states the month-end list is replaced monthly and should be downloaded/saved when needed.
- EDINET: official fixed-link EDINET code list (`Edinetcode.zip`). The code list is available without the document API key.
- National Tax Agency: Japanese Corporate Number Publication Site. The July 31, 2026 full dataset is the authoritative validation source; live API validation is optional because it requires an application ID.
- GLEIF: public LEI API / Golden Copy. For Japanese corporate-number matching, only an exact `registeredAs` match from registration authority `RA001075` (National Tax Agency Corporate Number Publication Site) is accepted automatically.

## Security-code normalization

EDINET may represent a four-character TSE security code using a five-character form with a terminal `0` (for example `72030` for TSE code `7203`). The adapter normalizes this form only when the EDINET field is exactly five numeric characters ending in `0`. Alphanumeric TSE codes are never modified by this rule.

## Closure acceptance

The real run must report:

1. exactly 100 domestic TSE issuer entities generated from the pinned JPX snapshot;
2. EDINET match coverage;
3. Japanese corporate-number coverage;
4. LEI coverage using exact registry identifiers only;
5. unresolved and disputed counts;
6. source hashes/URLs and adapter version;
7. deterministic reproduction hash for the resulting entity payload.

No entity is linked by company name alone.