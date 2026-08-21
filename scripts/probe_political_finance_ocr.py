from __future__ import annotations

import json
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import source_url


def main() -> None:
    out = Path("artifacts/political-finance-ocr-probe")
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / "part01.pdf"
    req = urllib.request.Request(source_url(1), headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        pdf.write_bytes(r.read())
    # Bound the experiment: inspect only the end of part 1 to locate the
    # transition from individual donors to organizations/corporations.
    prefix = out / "page"
    subprocess.run(["pdftoppm", "-f", "95", "-l", "112", "-r", "150", "-gray", "-png", str(pdf), str(prefix)], check=True)
    rows = []
    for image in sorted(out.glob("page-*.png")):
        proc = subprocess.run(["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6"], check=True, text=True, capture_output=True)
        rows.append({"image": image.name, "text": proc.stdout[:12000]})
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    (out / "ocr-sample.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
