from __future__ import annotations

import json
from pathlib import Path

from wa_commons.identity.benchmark import BenchmarkRecord
from wa_commons.identity.benchmark_corpus import build_v01_corpus

OUT = Path("artifacts/yente-benchmark")


def ftm_entity(entity_id: str, record: BenchmarkRecord) -> dict:
    props: dict[str, list[str]] = {"name": [record.name]}
    if record.corporate_number:
        props["registrationNumber"] = [record.corporate_number]
    if record.jurisdiction:
        props["jurisdiction"] = [record.jurisdiction.lower()]
    if record.address:
        props["address"] = [record.address]
    # These identifiers are useful to WA Commons but do not all map cleanly onto
    # standard FtM Company properties. Keep them out of the fuzzy benchmark query
    # rather than smuggling semantics into generic identifiers.
    return {"id": entity_id, "schema": "Company", "properties": props}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = build_v01_corpus()

    with (OUT / "candidates.ftm.json").open("w", encoding="utf-8") as fh:
        for case in cases:
            fh.write(json.dumps(ftm_entity(f"wa-er:{case.case_id}", case.right), ensure_ascii=False) + "\n")

    queries = []
    for case in cases:
        queries.append({
            "case_id": case.case_id,
            "case_type": case.case_type,
            "expected": case.expected,
            "expected_candidate_id": f"wa-er:{case.case_id}" if case.expected == "MATCH" else None,
            "query": {k: v for k, v in ftm_entity("query", case.left).items() if k != "id"},
            "provenance": case.provenance,
        })
    (OUT / "queries.json").write_text(json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (OUT / "manifest.yml").write_text(
        "datasets:\n"
        "  - name: wa_er\n"
        "    title: WA Commons Entity Resolution Benchmark\n"
        "    path: /data/candidates.ftm.json\n"
        "    version: '1'\n",
        encoding="utf-8",
    )
    print(f"exported {len(cases)} candidates and queries to {OUT}")


if __name__ == "__main__":
    main()
