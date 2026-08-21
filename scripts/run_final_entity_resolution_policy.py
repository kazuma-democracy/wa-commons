from __future__ import annotations

import json
from pathlib import Path

from wa_commons.identity.benchmark import evaluate
from wa_commons.identity.benchmark_corpus import build_m12_corpus
from wa_commons.identity.policy import (
    POLICY_VERSION,
    SPLINK_REVIEW_SCORE,
    SPLINK_VERSION,
    YENTE_ALGORITHM,
    YENTE_REVIEW_SCORE,
    YENTE_VERSION,
    final_policy_match,
)


def main() -> None:
    cases = build_m12_corpus()
    evaluation = evaluate(cases, matcher=final_policy_match)
    rows = evaluation.pop("rows")

    report = {
        "policy_version": POLICY_VERSION,
        "cases": len(cases),
        "automatic_link_rule": "aligned strong identifier required; any strong identifier conflict => DISPUTED",
        "fuzzy_auto_link": False,
        "candidate_routing": {
            "yente": {
                "version": YENTE_VERSION,
                "algorithm": YENTE_ALGORITHM,
                "review_score": YENTE_REVIEW_SCORE,
            },
            "splink": {
                "version": SPLINK_VERSION,
                "review_score": SPLINK_REVIEW_SCORE,
            },
        },
        "evaluation": evaluation,
        "note": "Fuzzy score thresholds route candidates to REVIEW only and never permit AUTO_LINK in M1.",
    }

    out = Path("artifacts/entity-resolution-final")
    out.mkdir(parents=True, exist_ok=True)
    (out / "final-policy-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "final-policy-rows.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
