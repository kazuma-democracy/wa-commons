from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import urllib.request

from pypdf import PdfReader

from wa_commons.evidence.political_finance import source_url


def main() -> None:
    out = Path("artifacts/political-finance-probe")
    out.mkdir(parents=True, exist_ok=True)
    report = []
    for part in (1,):
        url = source_url(part)
        req = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
            reader = PdfReader(BytesIO(data))
            texts = [(p.extract_text() or "") for p in reader.pages]
            joined = "\n".join(texts)
            report.append({"part": part, "url": url, "pages": len(reader.pages), "bytes": len(data), "text_chars": len(joined), "sample": joined[:10000]})
        except Exception as exc:
            report.append({"part": part, "url": url, "error": f"{type(exc).__name__}: {exc}"})
    (out / "probe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not any(row.get("text_chars", 0) > 500 for row in report):
        raise SystemExit("No usable PDF text layer found; deterministic text extraction cannot proceed without an explicit OCR stage.")


if __name__ == "__main__":
    main()
