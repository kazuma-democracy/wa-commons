from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from wa_commons.evidence.cards import card_from_claim

REPRODUCTION_VERSION = "m1-reproduction-v0.1"


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def apply_status_transition(
    claim: dict[str, Any],
    *,
    new_status: str,
    reason: str,
    changed_at: str,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Append a deterministic adjudication transition without deleting history."""
    if new_status not in {"confirmed", "disputed", "unknown", "expired"}:
        raise ValueError(f"unsupported adjudication status: {new_status}")
    result = deepcopy(claim)
    previous = result["adjudication"]["status"]
    history = result.setdefault("correction_history", [])
    history.append({
        "changed_at": changed_at,
        "previous_status": previous,
        "new_status": new_status,
        "reason": reason,
        "evidence_refs": list(evidence_refs or []),
    })
    result["adjudication"]["status"] = new_status
    result["adjudication"]["reasoning_summary"] = reason
    result["adjudication"]["decided_at"] = changed_at
    result["provenance"]["updated_at"] = changed_at
    return result


def outage_result(*, source_id: str, checked_at: str, reason: str) -> dict[str, Any]:
    """Represent source unavailability without inventing evidence or policy certainty."""
    return {
        "source_id": source_id,
        "checked_at": checked_at,
        "adapter_health": "unavailable",
        "evidence_status": "UNKNOWN",
        "policy_decision": "NONE",
        "reason": reason,
    }


def card_status(claim: dict[str, Any]) -> str:
    return card_from_claim(claim).adjudication["status"]


def build_canonical_graph(
    *,
    claims: list[dict[str, Any]],
    observation_summaries: list[dict[str, Any]],
    adapter_runs: list[dict[str, Any]],
    correction_demo: dict[str, Any],
    expiry_demo: dict[str, Any],
    outage_demo: dict[str, Any],
    tool_versions: dict[str, str],
) -> dict[str, Any]:
    """Build a stable, versioned semantic graph manifest for M1 reproduction."""
    ordered_claims = sorted(deepcopy(claims), key=lambda c: c["claim_id"])
    entity_ids = sorted({c["subject"]["entity_id"] for c in ordered_claims})
    cards = [card_from_claim(c).to_dict() for c in ordered_claims]
    cards.sort(key=lambda c: c["claim_id"])
    observations = sorted(deepcopy(observation_summaries), key=lambda o: (o["source_id"], o["observation_id"]))
    runs = sorted(deepcopy(adapter_runs), key=lambda r: r["adapter"])
    return {
        "reproduction_version": REPRODUCTION_VERSION,
        "entity_ids": entity_ids,
        "claims": ordered_claims,
        "cards": cards,
        "observation_summaries": observations,
        "adapter_runs": runs,
        "correction_demo": deepcopy(correction_demo),
        "expiry_demo": deepcopy(expiry_demo),
        "outage_demo": deepcopy(outage_demo),
        "tool_versions": dict(sorted(tool_versions.items())),
        "model_assisted_stages": [],
    }
