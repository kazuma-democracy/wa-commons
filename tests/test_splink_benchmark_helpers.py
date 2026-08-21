from wa_commons.identity.benchmark import BenchmarkRecord
from wa_commons.identity.benchmark_corpus import build_m12_corpus
from wa_commons.identity.splink_benchmark import (
    build_link_tables,
    probability_bands,
    provenance_class,
    record_to_row,
    score_rows,
)


def test_record_to_row_preserves_identifier_namespaces_and_nulls():
    row = record_to_row(
        "L",
        "case-1",
        BenchmarkRecord(
            name="株式会社テスト",
            corporate_number="123",
            security_code="9999",
            jurisdiction="JP",
        ),
    )
    assert row["unique_id"] == "L:case-1"
    assert row["corporate_number"] == "123"
    assert row["security_code"] == "9999"
    assert row["lei"] is None
    assert row["edinet_code"] is None


def test_build_link_tables_uses_identical_m12_corpus_size():
    cases = build_m12_corpus()
    left, right = build_link_tables(cases)
    assert len(cases) == 420
    assert len(left) == len(right) == 420
    assert len({row["unique_id"] for row in left}) == 420
    assert len({row["unique_id"] for row in right}) == 420


def test_score_rows_excludes_review_from_binary_metrics():
    rows = [
        {"expected": "MATCH", "paired_score": 0.9},
        {"expected": "NON_MATCH", "paired_score": 0.8},
        {"expected": "REVIEW", "paired_score": 1.0},
    ]
    report = score_rows(rows, 0.7)
    assert report["considered"] == 2
    assert report["tp"] == 1
    assert report["fp"] == 1


def test_probability_bands_are_descriptive_only():
    report = probability_bands([
        {"paired_score": 0.01},
        {"paired_score": 0.2},
        {"paired_score": 0.7},
        {"paired_score": 0.95},
    ])
    assert report["counts"] == {
        "lt_0_10": 1,
        "0_10_to_lt_0_50": 1,
        "0_50_to_lt_0_90": 1,
        "gte_0_90": 1,
    }
    assert "not" in report["note"]


def test_provenance_class_separates_sourced_and_synthetic():
    assert provenance_class("source_verified|publisher=JPX") == "source_verified"
    assert provenance_class("synthetic_adversarial") == "synthetic_adversarial"
