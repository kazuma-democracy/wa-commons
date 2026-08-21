# JPX Pilot Runbook

## Purpose

Generate the fixed M1.1 pilot universe of Japanese listed issuers from a versioned JPX source snapshot.

## Source of truth

Production runs should start from the official JPX listed-issues file. Keep the original downloaded file unchanged and record:

- JPX source URL;
- snapshot/effective date;
- retrieval timestamp;
- SHA-256 of the original source;
- any conversion step required before ingestion.

WA Commons currently supports CSV and XLSX directly. JPX may publish legacy XLS; if so, convert it to XLSX or CSV for ingestion **without deleting the original file or original-file hash**.

A public mirror may be used only as a development/reproducibility fixture and must never be silently presented as the authoritative current JPX snapshot.

## Generate the pilot

```bash
python -m pip install -e .
wa-commons build-jpx-pilot \
  data/raw/jpx/data_j.csv \
  data/derived/jpx/pilot-100.json \
  --snapshot 2026-07-31 \
  --source-url 'https://www.jpx.co.jp/markets/statistics-equities/misc/01.html' \
  --retrieved-at '2026-08-21T00:00:00Z' \
  --limit 100
```

The builder:

1. reads the snapshot;
2. keeps rows whose market/product category contains `内国株式`;
3. excludes ETF/ETN, PRO Market and other non-domestic-equity rows;
4. sorts by JPX security code;
5. selects the requested fixed pilot size;
6. creates stable v0 IDs such as `wa:org:jp:tse:7203`;
7. writes source provenance and SHA-256 in the manifest.

## Reproduction rule

Given the same input bytes and the same adapter version, deterministic fields and ordering must be identical.

Do not fetch live data during the reproduction test. Live fetching belongs to a separate acquisition step; the evidence graph is built from frozen snapshots.

## Next enrichment passes

After JPX pilot generation:

1. resolve National Tax Agency corporate numbers;
2. add EDINET filer codes where available;
3. add LEIs where available;
4. emit conflicts as review/dispute records;
5. never collapse parent and subsidiary entities.

API credentials are external configuration and must never be committed.

## Current development fixture

During initial implementation, a public mirror containing a 2026-04-30 JPX-style snapshot was used only to verify the column layout and filtering assumptions. It is not the production source of truth. Production/acceptance data must be regenerated from an archived official JPX snapshot before #12 is closed.
