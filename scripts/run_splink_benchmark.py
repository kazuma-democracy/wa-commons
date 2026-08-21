from __future__ import annotations

import json
import platform
from pathlib import Path

import duckdb
import pandas as pd
import splink
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

from wa_commons.identity.benchmark_corpus import build_m12_corpus
from wa_commons.identity.splink_benchmark import (
    SCORE_CUTS,
    baseline_summary,
    build_link_tables,
    probability_bands,
    provenance_class,
    score_rows,
    summarize_scores,
)

SPLINK_VERSION = "4.0.16"


def make_linker(cases):
    left_rows, right_rows = build_link_tables(cases)
    left = pd.DataFrame(left_rows)
    right = pd.DataFrame(right_rows)

    settings = SettingsCreator(
        link_type="link_only",
        unique_id_column_name="unique_id",
        probability_two_random_records_match=1 / 420,
        blocking_rules_to_generate_predictions=[
            block_on("jurisdiction"),
            block_on("corporate_number"),
            block_on("lei"),
            block_on("edinet_code"),
            block_on("security_code"),
            block_on("address"),
            block_on("name"),
        ],
        comparisons=[
            cl.NameComparison("name"),
            cl.ExactMatch("corporate_number"),
            cl.ExactMatch("lei"),
            cl.ExactMatch("edinet_code"),
            cl.ExactMatch("security_code"),
            cl.ExactMatch("jurisdiction"),
            cl.NameComparison("address"),
        ],
        retain_intermediate_calculation_columns=True,
    )
    linker = Linker(
        [left, right],
        settings,
        db_api=DuckDBAPI(),
        input_table_aliases=["wa_left", "wa_right"],
        set_up_basic_logging=False,
    )
    return linker


def train_unsupervised(linker) -> list[dict]:
    """Estimate parameters without using WA benchmark truth labels."""
    training = []
    linker.training.estimate_u_using_random_sampling(max_pairs=100_000, seed=20260821)
    training.append({"stage": "u_random_sampling", "max_pairs": 100_000, "seed": 20260821})

    # Use high-signal observed attributes as unsupervised EM blocks. These rules
    # select comparison pairs only; they do not inspect MATCH/NON_MATCH labels.
    for column in ("corporate_number", "security_code", "address", "name"):
        try:
            linker.training.estimate_parameters_using_expectation_maximisation(block_on(column))
            training.append({"stage": "em", "block_on": column, "status": "ok"})
        except Exception as exc:  # preserve training limitations as evidence
            training.append({"stage": "em", "block_on": column, "status": "skipped", "reason": str(exc)})
    return training


def paired_rows(cases, predictions: pd.DataFrame) -> list[dict]:
    by_case = {case.case_id: case for case in cases}
    rows = []
    for case_id, case in by_case.items():
        left_id = f"L:{case_id}"
        right_id = f"R:{case_id}"
        pair = predictions[
            (predictions["unique_id_l"] == left_id)
            & (predictions["unique_id_r"] == right_id)
        ]
        score = float(pair.iloc[0]["match_probability"]) if len(pair) else 0.0
        weight = float(pair.iloc[0]["match_weight"]) if len(pair) else None
        rows.append({
            "case_id": case_id,
            "case_type": case.case_type,
            "expected": case.expected,
            "provenance_class": provenance_class(case.provenance),
            "paired_score": score,
            "match_weight": weight,
            "pair_present": bool(len(pair)),
        })
    return rows


def report_for(rows: list[dict]) -> dict:
    return {
        "cases": len(rows),
        "score_summary": summarize_scores(rows),
        "curves": [score_rows(rows, cut) for cut in SCORE_CUTS],
        "probability_bands": probability_bands(rows),
    }


def main() -> None:
    if splink.__version__ != SPLINK_VERSION:
        raise RuntimeError(f"Expected Splink {SPLINK_VERSION}, got {splink.__version__}")

    cases = build_m12_corpus()
    linker = make_linker(cases)
    training = train_unsupervised(linker)
    predictions = linker.inference.predict(threshold_match_probability=0.0).as_pandas_dataframe()
    rows = paired_rows(cases, predictions)

    by_provenance = {}
    for pclass in sorted({row["provenance_class"] for row in rows}):
        by_provenance[pclass] = report_for([row for row in rows if row["provenance_class"] == pclass])

    report = {
        "matcher": "splink",
        "splink_version": splink.__version__,
        "backend": "duckdb",
        "duckdb_version": duckdb.__version__,
        "python_version": platform.python_version(),
        "link_type": "link_only",
        "parameter_estimation": "unsupervised; benchmark truth labels not used for training",
        "probability_two_random_records_match": 1 / 420,
        "training": training,
        **report_for(rows),
        "by_provenance": by_provenance,
        "wa_conservative_v0_1": baseline_summary(cases),
        "note": "Score cuts are descriptive measurement points only; M1.2c does not choose a production matcher or threshold.",
    }

    out = Path("artifacts/splink-benchmark")
    out.mkdir(parents=True, exist_ok=True)
    (out / "splink-rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "splink-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
