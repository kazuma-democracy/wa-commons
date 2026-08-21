from __future__ import annotations

import json
from pathlib import Path

from wa_commons.evidence.cards import card_from_claim, render_markdown


def _examples() -> list[dict]:
    return json.loads(Path("schemas/examples/evidence-claim.examples.json").read_text(encoding="utf-8"))


def test_card_exposes_required_identity_claim_source_and_review_fields():
    card = card_from_claim(_examples()[0]).to_dict()
    assert card["entity"]["canonical_name"] == "Example Company A"
    assert card["entity"]["identifiers"]
    assert card["claim"]["predicate"] == "was_awarded_contract_by"
    assert card["sources"][0]["publisher"] == "Japan Ministry of Defense"
    assert card["sources"][0]["url"].startswith("https://")
    assert card["sources"][0]["locator"]
    assert card["sources"][0]["evidence_date"]
    assert card["sources"][0]["retrieved_at"]
    assert card["adjudication"]["status"] == "CONFIRMED"
    assert card["entity_resolution"]["review_status"] == "not_required"
    assert card["challenge_path"]["url"].startswith("https://github.com/")
    assert card["policy_layer"]["separate_from_evidence"] is True


def test_unknown_is_not_rendered_as_clean_or_safe():
    card = card_from_claim(_examples()[2])
    text = render_markdown(card).lower()
    assert "unknown" in text
    assert "must not be rendered as clean or safe" in text


def test_disputed_identity_and_reason_remain_visible():
    card = card_from_claim(_examples()[3])
    text = render_markdown(card)
    assert "**DISPUTED**" in text
    assert "name-only" in text
    assert "disputed" in card.entity_resolution["review_status"]


def test_correction_history_is_rendered():
    card = card_from_claim(_examples()[3])
    text = render_markdown(card)
    assert "CONFIRMED → DISPUTED" in text
    assert "conflated two companies" in text


def test_policy_is_visibly_separate_even_when_example_has_decision():
    card = card_from_claim(_examples()[1]).to_dict()
    assert card["policy_layer"]["decision"] == "EXCLUDE"
    assert card["policy_layer"]["separate_from_evidence"] is True
    assert "separate downstream layer" in card["policy_layer"]["note"].lower()


def test_renderer_does_not_add_inflammatory_labels():
    for claim in _examples():
        text = render_markdown(card_from_claim(claim)).lower()
        assert "bad company" not in text
        assert "war profiteer" not in text
