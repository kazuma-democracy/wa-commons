from wa_commons.identity.benchmark import BenchmarkRecord, conservative_baseline, evaluate
from wa_commons.identity.benchmark_corpus import build_v01_corpus


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
