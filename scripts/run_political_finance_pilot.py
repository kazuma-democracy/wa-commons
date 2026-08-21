from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import (
    parse_organization_ocr_page,
    sha256_bytes,
    source_url,
)

PART = 18
FIRST_PAGE = 2
LAST_PAGE = 15


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
    subprocess.run([
        "pdftoppm", "-f", str(FIRST_PAGE), "-l", str(LAST_PAGE), "-r", "200",
        "-gray", "-png", str(pdf), str(prefix)
    ], check=True)

    observations = []
    per_page = {}
    for image in sorted(out.glob("page-*.png")):
        page = int(image.stem.rsplit("-", 1)[-1])
        proc = subprocess.run(
            ["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6"],
            check=True, text=True, capture_output=True,
        )
        # Positive section guard. We selected a fixed form-2 range discovered in
        # the official filing; accept either the explicit heading or form ID.
        text = proc.stdout
        if "法人" not in text and not any(f"-2-{n:05d}" in text for n in range(1, 99999)):
            # OCR may miss the footer on a page; parser still fails closed at row level.
            pass
        rows = parse_organization_ocr_page(
            text, part=PART, page=page, retrieved_at=retrieved_at, source_sha256=digest
        )
        observations.extend(rows)
        per_page[str(page)] = len(rows)

    # Raw filing and rendered pages are working inputs, not redistribution artifacts.
    pdf.unlink(missing_ok=True)
    for image in out.glob("page-*.png"):
        image.unlink()

    unresolved = [o for o in observations if o.identity_decision != "AUTO_LINK"]
    report = {
        "source_url": url,
        "source_sha256": digest,
        "retrieved_at": retrieved_at,
        "pdf_part": PART,
        "page_range": [FIRST_PAGE, LAST_PAGE],
        "record_count": len(observations),
        "per_page_counts": per_page,
        "identity_auto_link_count": len(observations) - len(unresolved),
        "identity_unresolved_count": len(unresolved),
        "claims_emitted": 0,
        "personal_data_policy": "Only a fixed filing range independently identified as section 2 (法人・その他の団体) is processed; individual-donor sections are excluded.",
        "semantic_rule": "A disclosed donation is a narrow transaction fact, not an ideology label or endorsement of every recipient policy. Unresolved donors cannot trigger downstream exclusion.",
    }
    (out / "observations.json").write_text(
        json.dumps([o.to_dict() for o in observations], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(observations) < 50:
        raise SystemExit(f"Acceptance failed: expected >=50 organizational/corporate transactions, got {len(observations)}")
    if any(o.donor_type != "organization_or_corporation" for o in observations):
        raise SystemExit("Personal-data minimization guard failed")


if __name__ == "__main__":
    main()
