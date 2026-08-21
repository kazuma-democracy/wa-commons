from __future__ import annotations

import json
from pathlib import Path

from wa_commons.identity.benchmark import evaluate
from wa_commons.identity.benchmark_corpus import build_v01_corpus


def main() -> None:
    out = Path("artifacts/entity-resolution-benchmark")
    out.mkdir(parents=True, exist_ok=True)
    cases = build_v01_corpus()
    report = evaluate(cases)
    summary = {k: v for k, v in report.items() if k != "rows"}
    (out / "report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "rows.json").write_text(json.dumps(report["rows"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
