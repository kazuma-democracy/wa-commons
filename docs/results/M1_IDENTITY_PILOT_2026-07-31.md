# M1.1 Real Identity Pilot — 2026-07-31 JPX snapshot

Status: first successful official-data run completed on 2026-08-21.

## Result

The fixed pilot contains 100 domestic TSE-listed issuers selected deterministically by security code from the JPX 2026-07-31 snapshot.

| Metric | Result |
| --- | ---: |
| JPX entities | 100 / 100 |
| EDINET exact security-code links | 100 / 100 |
| Japanese corporate numbers | 100 / 100 |
| Corporate numbers validated against NTA full data | 100 / 100 |
| Exact LEI links | 7 / 100 |
| DISPUTED identity records | 0 |
| Unresolved corporate numbers | 0 |

LEI absence is not treated as an identity failure. LEIs are attached only when the GLEIF record's `registeredAs` exactly equals the Japanese corporate number and `registeredAt.id` is `RA001075` (Japan's National Tax Agency Corporate Number Publication Site).

## Important implementation findings

### EDINET metadata/header layout

`EdinetcodeDlInfo.csv` starts with a download-metadata row. The actual field header is the second row. The official columns include `ＥＤＩＮＥＴコード`, `証券コード`, and `提出者法人番号`.

### Five-character securities code

EDINET uses the full five-character securities code including the security-type reserve character. Ordinary shares therefore map as:

- `72030` → JPX issuer code `7203`
- `130A0` → JPX issuer code `130A`

The trailing reserve code is stripped only for the five-character ordinary-share form. Company-name similarity remains forbidden as an automatic strong-ID bridge.

### NTA validation

The nationwide Unicode full dataset is downloaded through the official NTA form POST, using the page's CSRF token and the nationwide Unicode file number. The run used file number `27660`, corresponding to the 2026-07-31 nationwide Unicode snapshot.

Only the 100 target corporate numbers are retained after streaming the full dataset.

## Source fingerprints from successful run

- JPX snapshot SHA-256: `6e401867d9ddf2524e4752f08fd3e3e434cd308c6d423839ca6e24fc7b1e1653`
- EDINET code-list SHA-256: `58c29c60c5466c79b962d0a4d77b3ee2e6ccb4ddabbe5727a8f010d917cdee1b`
- NTA nationwide Unicode ZIP SHA-256: `69d3c3a694863cdea4adfb57140b2f09703babb4d84e764d816f7ae4070be55a`
- Semantic entity payload SHA-256: `589bd90eb2bc4a090cc1d73ebabdabab06ae3b12282a3ec38062d78e3399d61f`

The semantic payload hash excludes run-time retrieval timestamps but retains entity identities, names, aliases, identifiers, source snapshot references, review state, and source keys.

## Safety result

No company was linked by name alone. No strong-ID conflicts appeared in this pilot. A conflict in corporate number, EDINET code, or LEI remains a `DISPUTED` identity and cannot silently merge.

## Reproduction

GitHub Actions workflow: `.github/workflows/real-identity-pilot.yml`

The workflow downloads the official sources, executes the identity pipeline, checks coverage gates, prints `report.json`, and uploads `report.json` plus `entities.json` as an artifact.

A second execution is used to verify that the semantic payload hash is stable for the same source state before Issue #12 is closed.
