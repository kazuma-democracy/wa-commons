from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from wa_commons.evidence.political_finance import (
    PoliticalFinanceObservation,
    conservative_identity_resolution,
    observation_to_claim,
    parse_organization_tsv_page,
)


def _tsv(*rows: tuple[int, int, int, int, int, str]) -> str:
    header = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"
    values = ["1\t1\t0\t0\t0\t0\t0\t0\t3000\t2000\t-1\t"]
    word_num = 1
    for line, left, top, width, height, text in rows:
        values.append(f"5\t1\t1\t1\t{line}\t{word_num}\t{left}\t{top}\t{width}\t{height}\t90\t{text}")
        word_num += 1
    return header + "\n" + "\n".join(values) + "\n"


def test_same_or_similar_names_never_auto_link_without_strong_id():
    assert conservative_identity_resolution("東和株式会社") == ("UNRESOLVED", None)
    assert conservative_identity_resolution("株式会社東和") == ("UNRESOLVED", None)


def test_strong_id_routes_through_m1_policy():
    decision, entity_id = conservative_identity_resolution("テスト株式会社", corporate_number="1234567890123")
    assert decision == "AUTO_LINK"
    assert entity_id == "jp:corporate-number:1234567890123"


def test_geometry_parser_uses_columns_and_carries_continuation():
    tsv = _tsv(
        (1, 210, 600, 150, 40, "株式会社テスト"),
        (1, 930, 600, 160, 40, "60000|"),
        (2, 210, 700, 20, 40, "/"),
        (2, 930, 700, 160, 40, "60000|"),
        (3, 210, 800, 150, 40, "壊れたOCR"),
        (3, 930, 800, 160, 40, "???"),
        (9, 2600, 1850, 200, 30, "00-2-00001"),
    )
    rows = parse_organization_tsv_page(tsv, part=18, page=2, retrieved_at="2026-08-21T00:00:00Z", source_sha256="a" * 64)
    assert len(rows) == 2
    assert rows[0].donor_name == "株式会社テスト"
    assert rows[1].donor_name == "株式会社テスト"
    assert rows[0].amount_jpy == rows[1].amount_jpy == 60000
    assert all(r.identity_decision == "UNRESOLVED" for r in rows)
    assert all(r.extraction_review_required for r in rows)


def test_geometry_parser_rejects_merged_or_impossible_amount_cells():
    tsv = _tsv(
        (1, 210, 600, 150, 40, "株式会社正常"),
        (1, 930, 600, 160, 40, "60000|"),
        (2, 210, 700, 150, 40, "株式会社巨大ノイズ"),
        (2, 930, 700, 180, 40, "12345678901234567890"),
        (3, 210, 800, 150, 40, "株式会社上限超過"),
        (3, 930, 800, 180, 40, "1000000001"),
    )
    rows = parse_organization_tsv_page(tsv, part=18, page=2, retrieved_at="2026-08-21T00:00:00Z", source_sha256="e" * 64)
    assert len(rows) == 1
    assert rows[0].donor_name == "株式会社正常"
    assert rows[0].amount_jpy == 60000


def test_unresolved_or_unreviewed_observation_cannot_become_claim():
    unresolved = PoliticalFinanceObservation(
        observation_id="wc:obs:test:1", donor_name="同名株式会社", recipient="一般財団法人国民政治協会",
        amount_jpy=100000, reporting_year=2023, filing_id="00-2-00001",
        source_url="https://example.invalid/report.pdf", source_locator="pdf_part=18;page=2",
        retrieved_at="2026-08-21T00:00:00Z", source_sha256="b" * 64,
    )
    assert observation_to_claim(unresolved) is None
    unreviewed = PoliticalFinanceObservation(
        observation_id="wc:obs:test:2", donor_name="テスト株式会社", recipient="一般財団法人国民政治協会",
        amount_jpy=100000, reporting_year=2023, filing_id="00-2-00001",
        source_url="https://example.invalid/report.pdf", source_locator="pdf_part=18;page=2",
        retrieved_at="2026-08-21T00:00:00Z", source_sha256="c" * 64,
        corporate_number="1234567890123", identity_decision="AUTO_LINK", entity_id="jp:corporate-number:1234567890123",
    )
    assert observation_to_claim(unreviewed) is None


def test_reviewed_resolved_claim_is_narrow_schema_valid_and_not_ideology():
    obs = PoliticalFinanceObservation(
        observation_id="wc:obs:test:3", donor_name="テスト株式会社", recipient="一般財団法人国民政治協会",
        amount_jpy=100000, reporting_year=2023, filing_id="00-2-00001",
        source_url="https://example.invalid/report.pdf", source_locator="pdf_part=18;page=2;ocr_top=600",
        retrieved_at="2026-08-21T00:00:00Z", source_sha256="d" * 64,
        extraction_review_required=False, corporate_number="1234567890123", identity_decision="AUTO_LINK",
        entity_id="jp:corporate-number:1234567890123",
    )
    claim = observation_to_claim(obs)
    assert claim is not None
    assert claim["claim"]["category"] == "political_finance"
    assert claim["policy_context"] is None
    assert "ocr_top=600" in claim["evidence"][0]["locator"]
    serialized = json.dumps(claim, ensure_ascii=False).lower()
    assert "left-wing" not in serialized and "right-wing" not in serialized
    schema = json.loads(Path("schemas/evidence-claim.v0.1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(claim)