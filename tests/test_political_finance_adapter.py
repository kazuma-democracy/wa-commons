from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from wa_commons.evidence.political_finance import (
    PoliticalFinanceObservation,
    conservative_identity_resolution,
    observation_to_claim,
    parse_organization_ocr_page,
)


def test_same_or_similar_names_never_auto_link_without_strong_id():
    assert conservative_identity_resolution("東和株式会社") == ("UNRESOLVED", None)
    assert conservative_identity_resolution("株式会社東和") == ("UNRESOLVED", None)
    assert conservative_identity_resolution("東和株式会社") == conservative_identity_resolution("東和株式会社")


def test_strong_id_routes_through_m1_policy():
    decision, entity_id = conservative_identity_resolution("テスト株式会社", corporate_number="1234567890123")
    assert decision == "AUTO_LINK"
    assert entity_id == "jp:corporate-number:1234567890123"


def test_section2_parser_rejects_uncertain_rows_and_carries_donor():
    text = """
(その 7) 寄附の内訳 寄附者の区分 2. 法人・その他の団体
株式会社テスト | 60000 | 5 | 4 | 28 | 東京都 | 山田太郎
/ | 60000 | 5 | 5 | 28 | / | /
壊れたOCR | ??? | 5 | xx | yy | 不明
00-2-00001
"""
    rows = parse_organization_ocr_page(text, part=18, page=2, retrieved_at="2026-08-21T00:00:00Z", source_sha256="a" * 64)
    assert len(rows) == 2
    assert rows[0].donor_name == "株式会社テスト"
    assert rows[1].donor_name == "株式会社テスト"
    assert rows[0].amount_jpy == rows[1].amount_jpy == 60000
    assert all(r.identity_decision == "UNRESOLVED" for r in rows)


def test_unresolved_observation_cannot_become_claim():
    obs = PoliticalFinanceObservation(
        observation_id="wc:obs:test:1", donor_name="同名株式会社", recipient="一般財団法人国民政治協会",
        amount_jpy=100000, reporting_year=2023, filing_id="00-2-00001",
        source_url="https://example.invalid/report.pdf", source_locator="pdf_part=18;page=2",
        retrieved_at="2026-08-21T00:00:00Z", source_sha256="b" * 64,
    )
    assert observation_to_claim(obs) is None


def test_resolved_claim_is_narrow_schema_valid_and_not_ideology():
    obs = PoliticalFinanceObservation(
        observation_id="wc:obs:test:2", donor_name="テスト株式会社", recipient="一般財団法人国民政治協会",
        amount_jpy=100000, reporting_year=2023, filing_id="00-2-00001",
        source_url="https://example.invalid/report.pdf", source_locator="pdf_part=18;page=2",
        retrieved_at="2026-08-21T00:00:00Z", source_sha256="c" * 64,
        corporate_number="1234567890123", identity_decision="AUTO_LINK",
        entity_id="jp:corporate-number:1234567890123",
    )
    claim = observation_to_claim(obs)
    assert claim is not None
    assert claim["claim"]["category"] == "political_finance"
    assert claim["policy_context"] is None
    serialized = json.dumps(claim, ensure_ascii=False).lower()
    assert "left-wing" not in serialized and "right-wing" not in serialized
    schema = json.loads(Path("schemas/evidence-claim.v0.1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(claim)
