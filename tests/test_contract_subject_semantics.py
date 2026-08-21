from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from wa_commons.evidence.contract_subject import RULE_VERSION, classification_claim, classify_contract_subject
from wa_commons.evidence.mod_procurement import ProcurementObservation

FIXTURE = Path("tests/fixtures/contract_subject_labels.json")


def _observation(subject: str, authority: str = "Japan Ministry of Defense") -> ProcurementObservation:
    return ProcurementObservation(
        observation_id="wc:obs:test:1",
        subject=subject,
        supplier_name="Example Co., Ltd.",
        supplier_address="Tokyo",
        corporate_number="1234567890123",
        contract_date="2026-04-01",
        contract_amount_jpy=1000,
        planned_price_jpy=1200,
        contracting_authority=authority,
        source_url="https://example.invalid/source.xlsx",
        source_page_url="https://example.invalid/",
        source_locator="sheet=test;row=1",
        retrieved_at="2026-08-21T12:00:00Z",
        source_sha256="a" * 64,
        identity_decision="AUTO_LINK",
        entity_id="jp:corporate-number:1234567890123",
    )


def test_labeled_fixture_set() -> None:
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert {case["expected"] for case in cases} == {"MILITARY_SPECIFIC", "DUAL_USE", "CIVILIAN", "UNKNOWN"}
    errors = []
    for case in cases:
        actual = classify_contract_subject(case["subject"]).category
        if actual != case["expected"]:
            errors.append((case["id"], case["expected"], actual))
    assert not errors, errors


def test_contracting_authority_name_is_not_a_feature() -> None:
    subject = "鉛筆 HB 一式"
    a = classify_contract_subject(subject)
    b = classify_contract_subject(subject)
    assert a == b
    assert a.category == "CIVILIAN"
    # The classifier API accepts only subject text: changing authority on the
    # observation cannot alter classification.
    assert _observation(subject, "Japan Ministry of Defense").subject == _observation(subject, "Civil Agency").subject


def test_conflicting_signals_fail_to_unknown() -> None:
    result = classify_contract_subject("小銃関連情報システム保守役務")
    assert result.category == "UNKNOWN"
    assert result.review_required is True
    assert "小銃" in result.matched_terms
    assert "情報システム" in result.matched_terms


def test_derived_claim_records_rule_and_no_policy_decision() -> None:
    obs = _observation("記念館等空調設備補修役務一式")
    result = classify_contract_subject(obs.subject)
    claim = classification_claim(obs, result)
    assert claim is not None
    assert claim["claim"]["value"]["contract_subject"] == obs.subject
    assert claim["evidence"][0]["locator"] == obs.source_locator
    assert claim["adjudication"]["rule_set_version"] == RULE_VERSION
    assert claim["adjudication"]["method"]["version"] == RULE_VERSION
    assert claim["policy_context"] is None
    assert claim["claim"]["category"] == "military_contract"
    assert claim["claim"]["predicate"] == "contract_subject_classification"

    schema = json.loads(Path("schemas/evidence-claim.v0.1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(claim)


def test_unknown_claim_is_reviewable_not_consequential() -> None:
    obs = _observation("特殊役務一式")
    result = classify_contract_subject(obs.subject)
    claim = classification_claim(obs, result)
    assert claim is not None
    assert result.category == "UNKNOWN"
    assert claim["adjudication"]["status"] == "unknown"
    assert claim["claim"]["value"]["review_required"] is True
    assert claim["policy_context"] is None
