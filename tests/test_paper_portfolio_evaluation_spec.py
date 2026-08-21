from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "paper-portfolio-evaluation.v0.1.schema.json"
EXAMPLE = ROOT / "schemas" / "examples" / "paper-portfolio-evaluation.example.json"
DOC = ROOT / "docs" / "PAPER_PORTFOLIO_EVALUATION.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_validates_against_schema():
    schema = load(SCHEMA)
    example = load(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)


def test_point_in_time_and_lookahead_controls_are_mandatory():
    example = load(EXAMPLE)
    assert example["benchmark"]["constituent_membership"] == "point_in_time"
    assert example["data_integrity"]["survivorship_bias_control"] == "point_in_time_constituents"
    assert example["data_integrity"]["knowledge_mode"] == "as_known_at_cutoff"
    assert example["calendar"]["decision_lag_trading_days"] >= 1


def test_missing_data_does_not_become_false_certainty():
    example = load(EXAMPLE)
    assert example["data_integrity"]["missing_return_policy"] == "BLOCK"
    assert example["data_integrity"]["unmapped_entity_policy"] == "keep_unscreened_and_report"
    assert example["data_integrity"]["missing_factor_policy"] == "report_insufficient_coverage"
    assert example["metrics"]["factor_drift"]["zero_fill_missing"] is False
    assert example["metrics"]["sector_drift"]["unknown_bucket_required"] is True


def test_tracking_and_turnover_formulas_are_pinned():
    example = load(EXAMPLE)
    perf = example["metrics"]["performance"]
    assert perf["tracking_difference_method"] == "annualized_geometric_return_difference"
    assert perf["tracking_error_method"] == "sample_std_daily_active_return_sqrt_252"
    assert example["metrics"]["turnover"]["method"] == "half_l1_pretrade_to_target"


def test_cost_scenarios_are_fixed_and_gross_net_required():
    example = load(EXAMPLE)
    costs = example["costs"]
    assert costs["headline_bps"] == 10
    assert costs["scenario_bps"] == [0, 10, 25, 50]
    assert costs["application"] == "one_way_turnover_times_bps"
    assert costs["report_gross_and_net"] is True


def test_sensitivity_is_not_performance_optimization():
    example = load(EXAMPLE)
    sensitivity = example["sensitivity"]
    assert sensitivity["confidence_delta_grid"] == [-0.1, -0.05, 0.0, 0.05, 0.1]
    assert sensitivity["quantitative_multiplier_grid"] == [0.5, 0.75, 1.0, 1.25, 1.5]
    assert sensitivity["same_non_policy_inputs"] is True


def test_reproduction_manifest_pins_evidence_policy_constructor_and_market_inputs():
    required = set(load(EXAMPLE)["reproducibility"]["required_run_provenance"])
    must_have = {
        "code_commit_sha",
        "evidence_graph_sha256",
        "policy_profile_id",
        "policy_profile_version",
        "policy_profile_sha256",
        "policy_evaluator_version",
        "portfolio_constructor_id",
        "portfolio_constructor_version",
        "portfolio_constructor_config_sha256",
        "benchmark_snapshot_sha256",
        "market_data_snapshot_sha256",
        "evaluation_config_sha256",
    }
    assert must_have <= required


def test_document_keeps_real_money_out_of_scope_and_requires_negative_results():
    text = DOC.read_text(encoding="utf-8")
    assert "real-money trading" in text
    assert "negative results" in text
    assert "Point-in-time membership is mandatory" in text
    assert "as-known-at-cutoff" in text
    assert "Do not replace missing returns with zero" in text
