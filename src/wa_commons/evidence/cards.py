from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from typing import Any

CARD_VERSION = "evidence-card-v0.1"
CHALLENGE_URL = "https://github.com/kazuma-democracy/wa-commons/issues/new"
FORBIDDEN_SUMMARY_LABELS = ("bad company", "war profiteer")


def _json_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class EvidenceCard:
    card_version: str
    claim_id: str
    entity: dict[str, Any]
    claim: dict[str, Any]
    sources: list[dict[str, Any]]
    adjudication: dict[str, Any]
    entity_resolution: dict[str, Any]
    correction_history: list[dict[str, Any]]
    policy_layer: dict[str, Any]
    challenge_path: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def card_from_claim(claim: dict[str, Any]) -> EvidenceCard:
    subject = claim["subject"]
    adjudication = claim["adjudication"]
    evidence = claim.get("evidence", [])
    policy = claim.get("policy_context")
    status = str(adjudication["status"]).upper()

    status_note = "Evidence status only; this is not a user-policy decision."
    if status == "UNKNOWN":
        status_note = "UNKNOWN means insufficient evidence for this exact claim; it must not be rendered as clean or safe."
    elif status == "DISPUTED":
        status_note = "DISPUTED means material identity/evidence conflict remains visible and unresolved."
    elif status == "EXPIRED":
        status_note = "EXPIRED means the evidence requires revalidation for the relevant time context."

    sources = []
    for item in evidence:
        sources.append({
            "publisher": item.get("publisher"),
            "url": item.get("source_url"),
            "locator": item.get("locator"),
            "evidence_date": item.get("evidence_date"),
            "retrieved_at": item.get("retrieved_at"),
            "support": item.get("support"),
            "source_type": item.get("source_type"),
        })

    policy_layer = {
        "separate_from_evidence": True,
        "decision": policy.get("decision") if policy else None,
        "profile_id": policy.get("policy_profile_id") if policy else None,
        "decision_reason": policy.get("decision_reason") if policy else None,
        "note": "Policy is a separate downstream layer. The evidence card itself does not assign PASS/WATCH/EXCLUDE.",
    }

    return EvidenceCard(
        card_version=CARD_VERSION,
        claim_id=claim["claim_id"],
        entity={
            "entity_id": subject["entity_id"],
            "canonical_name": subject["canonical_name"],
            "jurisdiction": subject.get("jurisdiction"),
            "identifiers": subject.get("identifiers", []),
        },
        claim={
            "category": claim["claim"]["category"],
            "predicate": claim["claim"]["predicate"],
            "value": claim["claim"].get("value"),
            "effective_from": claim["claim"].get("effective_from"),
            "effective_to": claim["claim"].get("effective_to"),
        },
        sources=sources,
        adjudication={
            "status": status,
            "confidence": adjudication.get("confidence"),
            "reasoning_summary": adjudication.get("reasoning_summary"),
            "status_note": status_note,
        },
        entity_resolution={
            "method": subject["entity_resolution"].get("method"),
            "confidence": subject["entity_resolution"].get("confidence"),
            "review_status": subject["entity_resolution"].get("review_status"),
            "match_evidence": subject["entity_resolution"].get("match_evidence", []),
        },
        correction_history=claim.get("correction_history", []),
        policy_layer=policy_layer,
        challenge_path={
            "url": CHALLENGE_URL,
            "instruction": f"Open a correction/challenge issue and cite claim_id={claim['claim_id']} plus the source locator.",
        },
    )


def render_markdown(card: EvidenceCard) -> str:
    c = card.to_dict()
    lines = [
        f"# Evidence Card — {c['entity']['canonical_name']}",
        "",
        f"- Card version: `{c['card_version']}`",
        f"- Claim ID: `{c['claim_id']}`",
        f"- Entity ID: `{c['entity']['entity_id']}`",
        f"- Jurisdiction: `{c['entity'].get('jurisdiction') or 'unknown'}`",
        f"- Adjudication: **{c['adjudication']['status']}**",
        f"- Confidence: `{c['adjudication']['confidence']}`",
        "",
        "## Canonical identity",
        "",
    ]
    identifiers = c["entity"].get("identifiers", [])
    if identifiers:
        for identifier in identifiers:
            lines.append(f"- `{identifier.get('scheme')}`: `{identifier.get('value')}` ({identifier.get('issuer') or 'issuer unknown'})")
    else:
        lines.append("- No strong identifier recorded in this claim.")

    lines.extend([
        "",
        "## Exact narrow claim",
        "",
        f"- Category: `{c['claim']['category']}`",
        f"- Predicate: `{c['claim']['predicate']}`",
        f"- Value: `{_json_value(c['claim']['value'])}`",
        f"- Effective from: `{c['claim'].get('effective_from') or 'unknown'}`",
        f"- Effective to: `{c['claim'].get('effective_to') or 'open/unknown'}`",
        "",
        "## Evidence provenance",
        "",
    ])
    for i, source in enumerate(c["sources"], start=1):
        lines.extend([
            f"### Source {i}",
            f"- Publisher: {source.get('publisher') or 'unknown'}",
            f"- URL: {source.get('url') or 'unknown'}",
            f"- Locator: `{source.get('locator') or 'unknown'}`",
            f"- Evidence date: `{source.get('evidence_date') or 'unknown'}`",
            f"- Retrieved at: `{source.get('retrieved_at') or 'unknown'}`",
            f"- Source type/support: `{source.get('source_type') or 'unknown'}` / `{source.get('support') or 'unknown'}`",
            "",
        ])

    lines.extend([
        "## Adjudication",
        "",
        f"- Status: **{c['adjudication']['status']}**",
        f"- Confidence: `{c['adjudication']['confidence']}`",
        f"- Reason: {c['adjudication']['reasoning_summary']}",
        f"- Interpretation guard: {c['adjudication']['status_note']}",
        "",
        "## Entity-resolution review",
        "",
        f"- Method: `{c['entity_resolution']['method']}`",
        f"- Confidence: `{c['entity_resolution']['confidence']}`",
        f"- Review state: **{c['entity_resolution']['review_status']}**",
        f"- Match evidence: `{_json_value(c['entity_resolution']['match_evidence'])}`",
        "",
        "## Correction history",
        "",
    ])
    if c["correction_history"]:
        for item in c["correction_history"]:
            lines.append(
                f"- `{item.get('changed_at')}`: **{str(item.get('previous_status')).upper()} → {str(item.get('new_status')).upper()}** — {item.get('reason')}"
            )
    else:
        lines.append("- No correction recorded for this claim version.")

    lines.extend([
        "",
        "## User policy — separate downstream layer",
        "",
        f"- Evidence/policy separated: `{c['policy_layer']['separate_from_evidence']}`",
        f"- Example/configured policy decision: `{c['policy_layer']['decision'] or 'NONE'}`",
        f"- Policy profile: `{c['policy_layer']['profile_id'] or 'none'}`",
        f"- Note: {c['policy_layer']['note']}",
        "",
        "## Challenge / correction",
        "",
        f"- {c['challenge_path']['instruction']}",
        f"- Path: {c['challenge_path']['url']}",
        "",
    ])
    rendered = "\n".join(lines)
    lowered = rendered.lower()
    if any(label in lowered for label in FORBIDDEN_SUMMARY_LABELS):
        raise ValueError("Inflammatory summary label detected in evidence card")
    return rendered
