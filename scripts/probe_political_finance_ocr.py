from __future__ import annotations

import json
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import source_url


def main() -> None:
    out = Path("artifacts/political-finance-ocr-probe")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    # Bounded boundary search: only the first two pages of three widely spaced
    # parts. This locates the organization/corporation section without OCRing
    # thousands of pages or retaining personal-donor data as an artifact.
    for part in (2, 10, 20):
        pdf = out / f"part{part:02d}.pdf"
        req = urllib.request.Request(source_url(part), headers={"User-Agent": "wa-commons-m1/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            pdf.write_bytes(r.read())
        prefix = out / f"p{part:02d}"
        subprocess.run(["pdftoppm", "-f", "1", "-l", "2", "-r", "140", "-gray", "-png", str(pdf), str(prefix)], check=True)
        for image in sorted(out.glob(f"p{part:02d}-*.png")):
            proc = subprocess.run(["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6"], check=True, text=True, capture_output=True)
            rows.append({"part": part, "image": image.name, "text": proc.stdout[:8000]})
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
