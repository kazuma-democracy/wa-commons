from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import parse_organization_ocr_page, sha256_bytes, source_url

PART = 18
FIRST_PAGE = 2
LAST_PAGE = 3


def main() -> None:
    out = Path("artifacts/political-finance-pilot")
    out.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    url = source_url(PART)
    req = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        pdf_bytes = response.read()
    digest = sha256_bytes(pdf_bytes)
    pdf = out / "source.pdf"
    pdf.write_bytes(pdf_bytes)
    prefix = out / "page"
    subprocess.run(["pdftoppm", "-f", str(FIRST_PAGE), "-l", str(LAST_PAGE), "-r", "200", "-gray", "-png", str(pdf), str(prefix)], check=True)
    observations = []
    for image in sorted(out.glob("page-*.png")):
        page = int(image.stem.rsplit("-", 1)[-1])
        proc = subprocess.run(["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6"], check=True, text=True, capture_output=True)
        print(f"--- OCR PAGE {page} ---\n{proc.stdout[:12000]}\n--- END OCR PAGE {page} ---")
        observations.extend(parse_organization_ocr_page(proc.stdout, part=PART, page=page, retrieved_at=retrieved_at, source_sha256=digest))
    print(json.dumps({"record_count": len(observations)}, ensure_ascii=False))
    raise SystemExit("bounded diagnostic run")


if __name__ == "__main__":
    main()
