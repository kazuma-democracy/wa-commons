from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import source_url


def main() -> None:
    out = Path("artifacts/political-finance-pilot")
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / "source.pdf"
    req = urllib.request.Request(source_url(18), headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        pdf.write_bytes(response.read())
    prefix = out / "page"
    subprocess.run(["pdftoppm", "-f", "2", "-l", "2", "-r", "250", "-gray", "-png", str(pdf), str(prefix)], check=True)
    image = next(out.glob("page-*.png"))
    proc = subprocess.run(["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6", "tsv"], check=True, text=True, capture_output=True)
    reader = csv.DictReader(StringIO(proc.stdout), delimiter="\t")
    words = []
    for row in reader:
        text = row.get("text", "").strip()
        if text:
            words.append({k: row[k] for k in ("block_num", "par_num", "line_num", "left", "top", "width", "height", "conf", "text")})
    for row in words[:300]:
        print(row)
    raise SystemExit("bounded TSV diagnostic")


if __name__ == "__main__":
    main()
