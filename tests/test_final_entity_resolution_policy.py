from wa_commons.identity.benchmark import BenchmarkRecord, evaluate
from wa_commons.identity.benchmark_corpus import build_m12_corpus
from wa_commons.identity.policy import (
    POLICY_VERSION,
    SPLINK_REVIEW_SCORE,
    YENTE_REVIEW_SCORE,
    final_policy_match,
    fuzzy_review_candidate,
)


def test_strong_id_match_auto_links() -> None:
    result = final_policy_match(
        BenchmarkRecord(name="旧社名", corporate_number="123"),
        BenchmarkRecord(name="新社名", corporate_number="123"),
    )
    assert result.matcher == POLICY_VERSION
    assert result.decision == "AUTO_LINK"


def test_conflicting_strong_id_forces_disputed() -> None:
    result = final_policy_match(
        BenchmarkRecord(name="同じ会社名", security_code="1111"),
        BenchmarkRecord(name="同じ会社名", security_code="2222"),
    )
    assert result.decision == "DISPUTED"


def test_name_and_address_without_strong_id_never_auto_link() -> None:
    result = final_policy_match(
        BenchmarkRecord(name="株式会社平和技研", address="東京都港区芝1丁目"),
        BenchmarkRecord(name="平和技研（株）", address="東京都港区芝1丁目"),
    )
    assert result.decision == "REVIEW"


def test_fuzzy_thresholds_only_route_to_review() -> None:
    assert fuzzy_review_candidate(yente_score=YENTE_REVIEW_SCORE)
    assert fuzzy_review_candidate(splink_score=SPLINK_REVIEW_SCORE)
    assert not fuzzy_review_candidate(yente_score=YENTE_REVIEW_SCORE - 0.01, splink_score=SPLINK_REVIEW_SCORE - 0.01)


def test_final_policy_expected_m12_metrics() -> None:
    report = evaluate(build_m12_corpus(), matcher=final_policy_match)
    assert report["cases"] == 420
    assert report["tp"] == 154
    assert report["fp"] == 0
    assert report["fn"] == 100
    assert report["tn"] == 166
    assert report["precision"] == 1.0
    assert report["false_positive_rate"] == 0.0
    assert report["manual_review_rate"] == 206 / 420
    assert report["disputed_rate"] == 60 / 420

    sourced = report["by_provenance"]["source_verified"]
    assert sourced["cases"] == 20
    assert sourced["auto_link"] == 4
    assert sourced["review"] == 6
    assert sourced["disputed"] == 10
    assert sourced["errors"] == 0
