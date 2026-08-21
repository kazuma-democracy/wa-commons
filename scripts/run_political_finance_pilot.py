from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.request

from wa_commons.evidence.political_finance import parse_organization_tsv_page, sha256_bytes, source_url

PART = 18
FIRST_PAGE = 1
LAST_PAGE = 60


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
        "pdftoppm", "-f", str(FIRST_PAGE), "-l", str(LAST_PAGE), "-r", "250",
        "-gray", "-png", str(pdf), str(prefix)
    ], check=True)

    observations = []
    per_page: dict[str, int] = {}
    for image in sorted(out.glob("page-*.png")):
        page = int(image.stem.rsplit("-", 1)[-1])
        proc = subprocess.run(
            ["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6", "tsv"],
            check=True, text=True, capture_output=True,
        )
        rows = parse_organization_tsv_page(
            proc.stdout, part=PART, page=page, retrieved_at=retrieved_at, source_sha256=digest
        )
        observations.extend(rows)
        per_page[str(page)] = len(rows)

    # Official raw PDF and rendered page images are working inputs only. The CI
    # artifact contains derived review-required observations and the report.
    pdf.unlink(missing_ok=True)
    for image in out.glob("page-*.png"):
        image.unlink()

    unresolved = [o for o in observations if o.identity_decision != "AUTO_LINK"]
    review_required = [o for o in observations if o.extraction_review_required]
    report = {
        "source_url": url,
        "source_sha256": digest,
        "retrieved_at": retrieved_at,
        "snapshot": "MIAC 2023 annual political-finance report, Kokumin Seiji Kyokai, part 18",
        "pdf_part": PART,
        "page_range": [FIRST_PAGE, LAST_PAGE],
        "record_count": len(observations),
        "per_page_counts": per_page,
        "reporting_year": 2023,
        "identity_auto_link_count": len(observations) - len(unresolved),
        "identity_unresolved_count": len(unresolved),
        "ocr_review_required_count": len(review_required),
        "claims_emitted": 0,
        "personal_data_policy": "Only the fixed source part independently identified as filing section 2 (法人・その他の団体) is processed. Individual-donor section data is excluded.",
        "identity_rule": "OCR/printed name alone never AUTO_LINKs under wa-conservative-v0.2. Strong identifier plus extraction review is required before claim emission.",
        "semantic_rule": "A disclosed donation is a narrow transaction fact, not an ideology label or endorsement of every recipient policy. UNKNOWN/DISPUTED identity cannot trigger exclusion.",
    }
    (out / "observations.json").write_text(
        json.dumps([o.to_dict() for o in observations], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(observations) < 50:
        raise SystemExit(f"Acceptance failed: expected >=50 organizational/corporate transaction observations, got {len(observations)}")
    if any(o.donor_type != "organization_or_corporation" for o in observations):
        raise SystemExit("Personal-data minimization guard failed")
    if any(o.identity_decision == "AUTO_LINK" for o in observations):
        raise SystemExit("Unexpected name-only auto-link in real OCR sample")
    if any(not o.extraction_review_required for o in observations):
        raise SystemExit("OCR observation escaped review gate")


if __name__ == "__main__":
    main()