from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from wa_commons.identity.enrich import enrich_entity_batch, strong_id
from wa_commons.identity.jpx import from_jpx_row
from wa_commons.identity.jpx_snapshot import domestic_company_rows, read_jpx_rows
from wa_commons.identity.models import SourceRef

JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
EDINET_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
NTA_PAGE = "https://www.houjin-bangou.nta.go.jp/download/zenken/index.html"
GLEIF_API = "https://api.gleif.org/api/v1/lei-records"


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=180) as resp, path.open("wb") as out:
        final_url = resp.geturl()
        content_type = resp.headers.get("Content-Type", "")
        print(f"download {url} -> {final_url} [{content_type}]")
        while chunk := resp.read(1024 * 1024):
            out.write(chunk)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def read_edinet_zip(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise RuntimeError("EDINET code-list zip contained no CSV")
        raw = zf.read(names[0])
    for enc in ("cp932", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            return list(csv.DictReader(io.StringIO(text)))
        except UnicodeDecodeError:
            pass
    raise RuntimeError("could not decode EDINET code-list CSV")


def _zip_url_from_anchor(anchor) -> str | None:
    candidates = [str(v) for v in anchor.attrs.values() if isinstance(v, str)]
    candidates.append(str(anchor))
    for candidate in candidates:
        direct = re.search(r"https?://[^\s'\"<>]+\.zip(?:\?[^\s'\"<>]*)?", candidate)
        if direct:
            return direct.group(0)
        relative = re.search(r"[A-Za-z0-9_./%?=&-]+\.zip(?:\?[^\s'\"<>]*)?", candidate)
        if relative:
            return urllib.parse.urljoin(NTA_PAGE, relative.group(0))
    href = anchor.get("href")
    if href and not str(href).lower().startswith("javascript:"):
        return urllib.parse.urljoin(NTA_PAGE, str(href))
    return None


def find_nta_unicode_nationwide_url() -> str:
    req = urllib.request.Request(NTA_PAGE, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read()
    soup = BeautifulSoup(html, "html.parser")
    heading = next((h for h in soup.find_all(["h2", "h3"]) if "CSV形式・Unicode" in h.get_text(" ", strip=True)), None)
    if heading is None:
        raise RuntimeError("NTA Unicode section not found")
    node = heading
    inspected: list[str] = []
    while True:
        node = node.find_next()
        if node is None or (node.name in {"h2", "h3"} and node is not heading):
            break
        if node.name == "a" and "zip" in node.get_text(" ", strip=True).lower():
            inspected.append(str(node)[:500])
            url = _zip_url_from_anchor(node)
            if url:
                print(f"NTA nationwide Unicode candidate: {url}")
                return url
    raise RuntimeError(f"NTA nationwide Unicode zip URL not found; anchors={inspected[:3]}")


def nta_rows_for_targets(zip_path: Path, targets: set[str]) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    with zipfile.ZipFile(zip_path) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        for name in csv_names:
            with zf.open(name) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                for row in csv.reader(text):
                    hit = next((v for v in row if v in targets), None)
                    if not hit:
                        continue
                    official_name = row[6] if len(row) > 6 else ""
                    address = "".join(row[i] for i in (9, 10, 11) if len(row) > i)
                    found[hit] = {"法人番号": hit, "商号又は名称": official_name, "国内所在地（都道府県市区町村）": address}
                    if len(found) == len(targets):
                        return list(found.values())
    return list(found.values())


def gleif_rows_for_targets(targets: set[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for number in sorted(targets):
        query = urllib.parse.urlencode({"filter[entity.registeredAs]": number})
        req = urllib.request.Request(f"{GLEIF_API}?{query}", headers={"User-Agent": "wa-commons-m1/0.1", "Accept": "application/vnd.api+json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.load(resp)
        except Exception:
            continue
        for item in payload.get("data", []):
            attrs = item.get("attributes", {})
            entity = attrs.get("entity", {})
            reg = entity.get("registeredAs")
            authority = entity.get("registrationAuthority", {})
            if reg != number or authority.get("id") != "RA001075":
                continue
            lei = attrs.get("lei") or item.get("id")
            if lei:
                out.append({"LEI": lei, "Entity.RegistrationAuthority.RegistrationAuthorityEntityID": number})
    return out


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    jpx_path = out / "jpx_data_j.xls"
    edinet_zip = out / "Edinetcode.zip"
    download(JPX_URL, jpx_path)
    download(EDINET_URL, edinet_zip)

    jpx_rows = sorted(domestic_company_rows(read_jpx_rows(jpx_path)), key=lambda r: str(r.get("コード", "")))[:100]
    if len(jpx_rows) != 100:
        raise RuntimeError(f"expected 100 domestic JPX issuers, got {len(jpx_rows)}")

    jpx_source = SourceRef("JPX", jpx_path.name, "2026-07-31", JPX_URL, now, "0.3")
    entities = [from_jpx_row(row, jpx_source) for row in jpx_rows]
    edinet_rows = read_edinet_zip(edinet_zip)
    edinet_source = SourceRef("EDINET", edinet_zip.name, "2026-08-21", EDINET_URL, now, "0.2")
    entities = enrich_entity_batch(entities, edinet_rows=edinet_rows, edinet_source=edinet_source)

    corp_numbers = {n for e in entities if (n := strong_id(e, "JP_CORPORATE_NUMBER"))}
    print(f"EDINET yielded {len(corp_numbers)} unique corporate numbers for 100 issuers")

    nta_url = find_nta_unicode_nationwide_url()
    nta_zip = out / "nta_all_unicode.zip"
    download(nta_url, nta_zip)
    if not zipfile.is_zipfile(nta_zip):
        preview = nta_zip.read_bytes()[:500]
        raise RuntimeError(f"NTA download was not a zip: url={nta_url!r} preview={preview!r}")
    nta_rows = nta_rows_for_targets(nta_zip, corp_numbers)
    nta_source = SourceRef("NTA", nta_zip.name, "2026-07-31", nta_url, now, "0.1")

    gleif_rows = gleif_rows_for_targets(corp_numbers)
    gleif_source = SourceRef("GLEIF", "api-v1", "2026-08-21", GLEIF_API, now, "0.1")
    entities = enrich_entity_batch(
        entities,
        edinet_rows=edinet_rows,
        edinet_source=edinet_source,
        nta_rows=nta_rows,
        nta_source=nta_source,
        gleif_rows=gleif_rows,
        gleif_source=gleif_source,
    )

    def has(e, scheme):
        return strong_id(e, scheme) is not None

    canonical = [e.to_dict() for e in entities]
    stable_blob = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    report = {
        "generated_at": now,
        "entity_count": len(entities),
        "edinet_count": sum(has(e, "EDINET_CODE") for e in entities),
        "corporate_number_count": sum(has(e, "JP_CORPORATE_NUMBER") for e in entities),
        "nta_validated_count": len({r["法人番号"] for r in nta_rows}),
        "lei_count": sum(has(e, "LEI") for e in entities),
        "disputed_count": sum(e.review_state == "DISPUTED" for e in entities),
        "unresolved_corporate_number_count": sum(not has(e, "JP_CORPORATE_NUMBER") for e in entities),
        "entity_payload_sha256": hashlib.sha256(stable_blob).hexdigest(),
        "sources": {
            "jpx": {"url": JPX_URL, "sha256": sha256(jpx_path)},
            "edinet": {"url": EDINET_URL, "sha256": sha256(edinet_zip)},
            "nta": {"url": nta_url, "sha256": sha256(nta_zip)},
            "gleif": {"url": GLEIF_API, "registration_authority": "RA001075"},
        },
    }
    (out / "entities.json").write_text(json.dumps(canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/real-identity-pilot")
