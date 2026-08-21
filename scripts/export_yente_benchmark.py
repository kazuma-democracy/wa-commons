from __future__ import annotations

import json
from pathlib import Path

from wa_commons.identity.benchmark_corpus import build_m12_corpus


def _identifiers(record) -> list[str]:
    values = []
    for prefix, value in [
        ("CORP", record.corporate_number),
        ("LEI", record.lei),
        ("EDINET", record.edinet_code),
        ("JPX", record.security_code),
    ]:
        if value:
            values.append(f"{prefix}:{value}")
    return values


def to_ftm(case_id: str, record) -> dict:
    props: dict[str, list[str]] = {"name": [record.name]}
    if record.jurisdiction:
        props["jurisdiction"] = [record.jurisdiction.lower()]
    ids = _identifiers(record)
    if ids:
        props["registrationNumber"] = ids
    if record.address:
        props["address"] = [record.address]
    return {
        "id": f"wa-right-{case_id}",
        "schema": "Company",
        "properties": props,
    }


def main() -> None:
    out = Path("artifacts/yente-benchmark")
    out.mkdir(parents=True, exist_ok=True)
    cases = build_m12_corpus()

    with (out / "candidates.ftm.json").open("w", encoding="utf-8") as fh:
        for case in cases:
            fh.write(json.dumps(to_ftm(case.case_id, case.right), ensure_ascii=False) + "\n")

    queries = []
    for case in cases:
        queries.append({
            "case_id": case.case_id,
            "case_type": case.case_type,
            "expected": case.expected,
            "provenance": case.provenance,
            "expected_candidate_id": f"wa-right-{case.case_id}",
            "query": to_ftm(case.case_id, case.left),
        })
    (out / "queries.json").write_text(
        json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "manifest.yml").write_text(
        Path("configs/yente-benchmark-manifest.yml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(json.dumps({"cases": len(cases), "candidates": len(cases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
