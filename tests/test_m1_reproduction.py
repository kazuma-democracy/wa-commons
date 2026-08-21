from copy import deepcopy

from wa_commons.evidence.reproduction import (
    apply_status_transition,
    build_canonical_graph,
    canonical_sha256,
    card_status,
    outage_result,
)


def base_claim(status="confirmed"):
    return {
        "schema_version": "0.1",
        "claim_id": "wc:claim:test-reproduction-001",
        "subject": {
            "entity_id": "jp:corporate-number:1234567890123",
            "entity_type": "company",
            "canonical_name": "Reproduction Test Co.",
            "jurisdiction": "JP",
            "identifiers": [{"scheme": "corporate_number", "value": "1234567890123", "issuer": "NTA"}],
            "entity_resolution": {
                "method": "deterministic_identifier",
                "confidence": 1.0,
                "review_status": "not_required",
                "match_evidence": ["strong ID"],
            },
        },
        "claim": {
            "category": "military_contract",
            "predicate": "received_contract_from_japan_ministry_of_defense",
            "value": {"contract_subject": "office chair"},
            "effective_from": "2026-04-01",
            "effective_to": "2026-04-01",
        },
        "evidence": [{
            "evidence_id": "wc:evidence:test-reproduction-001",
            "source_id": "jp-mod-procurement",
            "source_url": "https://www.mod.go.jp/example",
            "publisher": "Japan Ministry of Defense",
            "source_type": "official_contract",
            "publication_date": None,
            "evidence_date": "2026-04-01",
            "retrieved_at": "2026-08-21T13:00:00Z",
            "support": "supports",
            "locator": "sheet=x;row=1",
            "content_sha256": "a" * 64,
            "license_status": "review_required",
            "notes": "Narrow contract fact only.",
        }],
        "adjudication": {
            "status": status,
            "confidence": 1.0,
            "reasoning_summary": "Source-published strong identifier.",
            "method": {"type": "deterministic_rule", "version": "test-v1", "model": None},
            "rule_set_version": "test-v1",
            "decided_at": "2026-08-21T13:00:00Z",
            "reviewer": None,
        },
        "policy_context": None,
        "correction_history": [],
        "provenance": {
            "created_at": "2026-08-21T13:00:00Z",
            "updated_at": "2026-08-21T13:00:00Z",
            "created_by": "test",
            "dataset_version": "test-v1",
        },
    }


def test_correction_is_append_only_and_propagates_to_card():
    original = base_claim()
    corrected = apply_status_transition(
        original,
        new_status="disputed",
        reason="Contradictory strong identifier shows this was a different legal entity.",
        changed_at="2026-08-21T14:00:00Z",
        evidence_refs=["wc:evidence:contradiction-001"],
    )
    assert original["adjudication"]["status"] == "confirmed"
    assert original["correction_history"] == []
    assert corrected["adjudication"]["status"] == "disputed"
    assert corrected["correction_history"][0]["previous_status"] == "confirmed"
    assert corrected["correction_history"][0]["new_status"] == "disputed"
    assert card_status(corrected) == "DISPUTED"


def test_expiry_propagates_without_policy_decision():
    expired = apply_status_transition(
        base_claim(),
        new_status="expired",
        reason="Evidence exceeded its configured revalidation horizon.",
        changed_at="2027-08-21T00:00:00Z",
    )
    assert card_status(expired) == "EXPIRED"
    assert expired["policy_context"] is None


def test_source_outage_never_creates_pass_or_exclude():
    result = outage_result(source_id="jp-mod-procurement", checked_at="2026-08-21T14:00:00Z", reason="HTTP 503")
    assert result["evidence_status"] == "UNKNOWN"
    assert result["policy_decision"] == "NONE"


def test_mod_contract_does_not_become_weapons_activity():
    claim = base_claim()
    assert claim["claim"]["category"] == "military_contract"
    assert claim["claim"]["category"] != "weapons_activity"
    assert claim["policy_context"] is None


def test_graph_hash_is_order_independent_for_versioned_inputs():
    claim_a = base_claim()
    claim_b = deepcopy(claim_a)
    claim_b["claim_id"] = "wc:claim:test-reproduction-002"
    claim_b["subject"]["entity_id"] = "jp:corporate-number:9999999999999"
    claim_b["subject"]["canonical_name"] = "Second Test Co."
    kwargs = dict(
        observation_summaries=[{"source_id": "z", "observation_id": "2"}, {"source_id": "a", "observation_id": "1"}],
        adapter_runs=[{"adapter": "z"}, {"adapter": "a"}],
        correction_demo={"after": "DISPUTED"},
        expiry_demo={"after": "EXPIRED"},
        outage_demo={"evidence_status": "UNKNOWN", "policy_decision": "NONE"},
        tool_versions={"python": "3.11"},
    )
    graph1 = build_canonical_graph(claims=[claim_a, claim_b], **kwargs)
    graph2 = build_canonical_graph(claims=[claim_b, claim_a], **kwargs)
    assert canonical_sha256(graph1) == canonical_sha256(graph2)


def test_no_model_assisted_stage_is_hidden_in_reproduction_graph():
    graph = build_canonical_graph(
        claims=[base_claim()],
        observation_summaries=[],
        adapter_runs=[],
        correction_demo={},
        expiry_demo={},
        outage_demo={},
        tool_versions={},
    )
    assert graph["model_assisted_stages"] == []
