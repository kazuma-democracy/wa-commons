from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from wa_commons.identity.enrich import build_edinet_security_index
from wa_commons.identity.jpx_snapshot import domestic_company_rows, read_jpx_rows

JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
EDINET_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
NTA_PAGE = "https://www.houjin-bangou.nta.go.jp/download/zenken/index.html"


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=180) as resp, path.open("wb") as out:
        print(f"download {url} -> {resp.geturl()} [{resp.headers.get('Content-Type', '')}]")
        while chunk := resp.read(1024 * 1024):
            out.write(chunk)


def read_edinet_zip(path: Path) -> tuple[list[dict[str, str]], str]:
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise RuntimeError(f"EDINET zip files={zf.namelist()}")
        raw = zf.read(names[0])
    for enc in ("cp932", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            reader = csv.DictReader(io.StringIO(text))
            return list(reader), names[0]
        except UnicodeDecodeError:
            continue
    raise RuntimeError("could not decode EDINET CSV")


def inspect_nta_anchors() -> list[str]:
    req = urllib.request.Request(NTA_PAGE, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        soup = BeautifulSoup(resp.read(), "html.parser")
    heading = next((h for h in soup.find_all(["h2", "h3"]) if "CSV形式・Unicode" in h.get_text(" ", strip=True)), None)
    if heading is None:
        return ["NO UNICODE HEADING"]
    out = []
    node = heading
    while len(out) < 5:
        node = node.find_next()
        if node is None or (node.name in {"h2", "h3"} and node is not heading):
            break
        if node.name == "a" and "zip" in node.get_text(" ", strip=True).lower():
            out.append(str(node))
    return out


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    jpx_path = out / "jpx_data_j.xls"
    edinet_zip = out / "Edinetcode.zip"
    download(JPX_URL, jpx_path)
    download(EDINET_URL, edinet_zip)

    jpx_rows = sorted(domestic_company_rows(read_jpx_rows(jpx_path)), key=lambda r: str(r.get("コード", "")))[:100]
    print("JPX_COUNT", len(jpx_rows))
    print("JPX_FIRST", json.dumps(jpx_rows[0], ensure_ascii=False, default=str))

    edinet_rows, edinet_name = read_edinet_zip(edinet_zip)
    print("EDINET_FILE", edinet_name)
    print("EDINET_COUNT", len(edinet_rows))
    print("EDINET_KEYS", json.dumps(list(edinet_rows[0].keys()) if edinet_rows else [], ensure_ascii=False))
    print("EDINET_FIRST", json.dumps(edinet_rows[0] if edinet_rows else {}, ensure_ascii=False))
    idx = build_edinet_security_index(edinet_rows)
    print("EDINET_INDEX_SIZE", len(idx))
    print("EDINET_1301", json.dumps(idx.get("1301", {}), ensure_ascii=False))

    print("NTA_ANCHORS", json.dumps(inspect_nta_anchors(), ensure_ascii=False))
    raise RuntimeError("diagnostic run complete; use logged official formats to finalize parser")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/real-identity-pilot")
