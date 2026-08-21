from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from wa_commons.policy import evaluate_claim

ROOT = Path(__file__).resolve().parents[1]


def load_policies() -> list[dict]:
    schema = json.loads((ROOT / "schemas" / "user-policy.v0.1.schema.json").read_text(encoding="utf-8"))
    policies = json.loads((ROOT / "schemas" / "examples" / "user-policy.examples.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for policy in policies:
        validator.validate(policy)
    return policies


def military_specific_claim(status: str = "confirmed", confidence: float = 0.98) -> dict:
    return {
        "claim_id": "wc:claim:test-military-specific",
        "subject": {"entity_id": "wc:entity:test-a", "jurisdiction": "JP"},
        "claim": {
            "category": "military_contract",
            "predicate": "contract_subject_classification",
            "value": {"classification": "military_specific"},
        },
        "evidence": [{"source_id": "jp-mod-procurement"}],
        "adjudication": {"status": status, "confidence": confidence},
    }


def test_examples_validate_and_are_not_official() -> None:
    policies = load_policies()
    assert len(policies) >= 3
    assert all(p["origin"]["official_status"] == "not_official" for p in policies)
    assert all(p["default_decision"] == "NONE" for p in policies)


def test_same_confirmed_evidence_can_produce_different_user_decisions() -> None:
    strict, narrow, transparency = load_policies()
    claim = military_specific_claim()
    assert evaluate_claim(strict, claim).decision == "EXCLUDE"
    assert evaluate_claim(narrow, claim).decision == "NONE"
    assert evaluate_claim(transparency, claim).decision == "WATCH"


def test_unknown_never_becomes_exclude_from_category_match() -> None:
    strict = load_policies()[0]
    result = evaluate_claim(strict, military_specific_claim(status="unknown", confidence=0.0))
    assert result.decision == "WATCH"
    assert result.matched_rule_ids == ()


def test_disputed_never_becomes_exclude_from_category_match() -> None:
    strict = load_policies()[0]
    result = evaluate_claim(strict, military_specific_claim(status="disputed"))
    assert result.decision == "WATCH"
    assert result.matched_rule_ids == ()


def test_expired_never_becomes_exclude_from_category_match() -> None:
    strict = load_policies()[0]
    result = evaluate_claim(strict, military_specific_claim(status="expired"))
    assert result.decision == "WATCH"
    assert result.matched_rule_ids == ()


def test_non_match_is_none_not_clean_or_safe_pass() -> None:
    strict = load_policies()[0]
    claim = military_specific_claim()
    claim["claim"]["value"]["classification"] = "civilian"
    result = evaluate_claim(strict, claim)
    assert result.decision == "NONE"
    assert "safe or clean" in result.reasoning


def test_preferences_are_separate_from_exclusion_decision() -> None:
    transparency = load_policies()[2]
    claim = military_specific_claim()
    claim["claim"]["category"] = "human_rights"
    claim["claim"]["predicate"] = "was_named_in_public_allegation"
    claim["claim"]["value"] = "allegation"
    result = evaluate_claim(transparency, claim)
    assert result.decision == "NONE"
    assert result.preference_signals == ({"rule_id": "soft-avoid-unresolved-human-rights", "direction": "avoid", "weight": 0.35},)


def test_profile_version_changes_result_identity_without_mutating_evidence() -> None:
    strict = load_policies()[0]
    claim = military_specific_claim()
    original = deepcopy(claim)
    result = evaluate_claim(strict, claim)
    assert claim == original
    assert result.profile_id == strict["profile_id"]
    assert result.profile_version == strict["profile_version"]
