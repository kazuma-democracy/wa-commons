from wa_commons.identity.benchmark import BenchmarkRecord, conservative_baseline, evaluate
from wa_commons.identity.benchmark_corpus import build_m12_corpus, build_v01_corpus
from wa_commons.identity.source_verified_cases import build_source_verified_cases


def test_corpus_has_required_400_case_shape():
    cases = build_v01_corpus()
    assert len(cases) == 400
    counts = {}
    for case in cases:
        counts[case.case_type] = counts.get(case.case_type, 0) + 1
    assert counts == {
        "easy_exact": 100,
        "alias_transliteration": 100,
        "parent_subsidiary_trap": 50,
        "similar_name_nonmatch": 50,
        "historical_rename_merger": 50,
        "incomplete_record": 50,
    }


def test_source_verified_subset_has_required_shape_and_provenance():
    cases = build_source_verified_cases()
    assert len(cases) >= 20
    case_types = {case.case_type for case in cases}
    assert {
        "historical_rename_merger",
        "parent_subsidiary_trap",
        "similar_name_nonmatch",
        "incomplete_record",
    }.issubset(case_types)
    for case in cases:
        assert case.provenance.startswith("source_verified|")
        assert "publisher=" in case.provenance
        assert "url=https://" in case.provenance
        assert "locator=" in case.provenance
        assert "retrieved=" in case.provenance


def test_combined_report_separates_sourced_and_synthetic_cases():
    report = evaluate(build_m12_corpus())
    assert report["cases"] >= 420
    assert report["by_provenance"]["synthetic_adversarial"]["cases"] == 400
    assert report["by_provenance"]["source_verified"]["cases"] >= 20


def test_name_only_match_never_auto_links():
    result = conservative_baseline(
        BenchmarkRecord(name="未来システム株式会社"),
        BenchmarkRecord(name="未来システム（株）"),
    )
    assert result.decision == "REVIEW"


def test_conflicting_strong_id_forces_dispute():
    result = conservative_baseline(
        BenchmarkRecord(name="同名株式会社", corporate_number="1111111111111"),
        BenchmarkRecord(name="同名株式会社", corporate_number="2222222222222"),
    )
    assert result.decision == "DISPUTED"


def test_exact_strong_id_auto_links_despite_rename():
    result = conservative_baseline(
        BenchmarkRecord(name="旧社名株式会社", corporate_number="1111111111111"),
        BenchmarkRecord(name="新社名株式会社", corporate_number="1111111111111"),
    )
    assert result.decision == "AUTO_LINK"


def test_baseline_has_zero_false_positive_on_v01_adversarial_corpus():
    report = evaluate(build_v01_corpus())
    assert report["cases"] == 400
    assert report["fp"] == 0
    assert report["precision"] == 1.0


def test_source_incomplete_cases_never_auto_link():
    for case in build_source_verified_cases():
        if case.case_type != "incomplete_record":
            continue
        result = conservative_baseline(case.left, case.right)
        assert result.decision != "AUTO_LINK"
