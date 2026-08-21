from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request

from jsonschema import Draft202012Validator

from wa_commons.evidence.cards import card_from_claim, render_markdown
from wa_commons.evidence.contract_subject import classification_claim, classify_contract_subject
from wa_commons.evidence.mod_procurement import SOURCE_URL, parse_workbook, sha256

EXPECTED_MOD_SHA256 = "c1f37e838d66ffa7bc62c35c5d8830c75ed7b92b0befe0c380f0d79052c773e8"
FIXED_RETRIEVED_AT = "2026-08-21T13:00:00Z"
REAL_ENTITY_TARGET = 20


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "artifacts" / "evidence-cards-pilot"
    cards_dir = out / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    schema = json.loads((root / "schemas" / "evidence-claim.v0.1.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    examples = json.loads((root / "schemas" / "examples" / "evidence-claim.examples.json").read_text(encoding="utf-8"))

    source_path = out / "mod-source.xlsx"
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        source_path.write_bytes(response.read())
    actual_sha = sha256(source_path)
    if actual_sha != EXPECTED_MOD_SHA256:
        raise SystemExit(f"Pinned MOD source changed: expected {EXPECTED_MOD_SHA256}, got {actual_sha}")

    observations = parse_workbook(source_path, retrieved_at=FIXED_RETRIEVED_AT)
    source_path.unlink(missing_ok=True)

    # Select one deterministic contract-subject claim per unique resolved real entity.
    real_claims = []
    seen_entities: set[str] = set()
    for observation in observations:
        if not observation.entity_id or observation.entity_id in seen_entities:
            continue
        classification = classify_contract_subject(observation.subject)
        claim = classification_claim(observation, classification)
        if claim is None:
            continue
        validator.validate(claim)
        real_claims.append(claim)
        seen_entities.add(observation.entity_id)
        if len(real_claims) >= REAL_ENTITY_TARGET:
            break

    if len(real_claims) < REAL_ENTITY_TARGET:
        raise SystemExit(f"Expected {REAL_ENTITY_TARGET} unique resolved real entities, got {len(real_claims)}")

    # Canonical schema examples deliberately provide UNKNOWN, DISPUTED, political-
    # finance, human-rights and correction-history cases without inventing prose in
    # the renderer. They remain visibly marked as worked examples in their sources.
    for claim in examples:
        validator.validate(claim)
    all_claims = real_claims + examples

    cards = []
    for claim in all_claims:
        card = card_from_claim(claim)
        card_dict = card.to_dict()
        cards.append(card_dict)
        safe_name = claim["claim_id"].replace(":", "_").replace("/", "_")
        (cards_dir / f"{safe_name}.md").write_text(render_markdown(card), encoding="utf-8")
        (cards_dir / f"{safe_name}.json").write_text(
            json.dumps(card_dict, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )

    statuses = sorted({c["adjudication"]["status"] for c in cards})
    categories = sorted({c["claim"]["category"] for c in cards})
    unique_entities = sorted({c["entity"]["entity_id"] for c in cards})
    corrected = [c["claim_id"] for c in cards if c["correction_history"]]
    unresolved_semantics = [c for c in cards if c["adjudication"]["status"] == "UNKNOWN"]
    disputed = [c for c in cards if c["adjudication"]["status"] == "DISPUTED"]

    semantic_sha = canonical_sha256(cards)
    report = {
        "card_version": "evidence-card-v0.1",
        "input_schema": "schemas/evidence-claim.v0.1.schema.json",
        "versioned_inputs": [
            "schemas/examples/evidence-claim.examples.json",
            SOURCE_URL,
        ],
        "fixed_mod_source_sha256": actual_sha,
        "fixed_retrieved_at": FIXED_RETRIEVED_AT,
        "real_pilot_entities": len(real_claims),
        "total_cards": len(cards),
        "unique_entities": len(unique_entities),
        "statuses": statuses,
        "categories": categories,
        "corrected_claims": corrected,
        "unknown_cards": len(unresolved_semantics),
        "disputed_cards": len(disputed),
        "semantic_sha256": semantic_sha,
        "policy_separation": all(c["policy_layer"]["separate_from_evidence"] for c in cards),
    }
    (out / "cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(real_claims) < 20 or len(unique_entities) < 20:
        raise SystemExit("Acceptance failed: fewer than 20 pilot entities")
    if len(statuses) < 3 or not {"CONFIRMED", "UNKNOWN", "DISPUTED"}.issubset(statuses):
        raise SystemExit(f"Acceptance failed: mixed statuses missing: {statuses}")
    if len(categories) < 3:
        raise SystemExit(f"Acceptance failed: mixed categories missing: {categories}")
    if not corrected:
        raise SystemExit("Acceptance failed: no visible correction history")
    if not report["policy_separation"]:
        raise SystemExit("Acceptance failed: evidence/policy separation missing")


if __name__ == "__main__":
    main()
