from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request

from jsonschema import Draft202012Validator

from wa_commons.evidence.contract_subject import RULE_VERSION, classification_claim, classify_contract_subject
from wa_commons.evidence.mod_procurement import SOURCE_URL, parse_workbook

FIXTURE_PATH = Path("tests/fixtures/contract_subject_labels.json")
SCHEMA_PATH = Path("schemas/evidence-claim.v0.1.schema.json")
CATEGORIES = ("MILITARY_SPECIFIC", "DUAL_USE", "CIVILIAN", "UNKNOWN")


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response, path.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)


def evaluate_fixture() -> dict:
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    matrix = {expected: {actual: 0 for actual in CATEGORIES} for expected in CATEGORIES}
    errors = []
    rows = []
    for case in cases:
        result = classify_contract_subject(case["subject"])
        expected = case["expected"]
        matrix[expected][result.category] += 1
        row = {
            "id": case["id"],
            "subject": case["subject"],
            "expected": expected,
            "actual": result.category,
            "matched_terms": list(result.matched_terms),
            "review_required": result.review_required,
        }
        rows.append(row)
        if expected != result.category:
            errors.append(row)
    return {
        "case_count": len(cases),
        "confusion_matrix": matrix,
        "error_count": len(errors),
        "errors": errors,
        "rows": rows,
    }


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    snapshot = out / "04_buppin_k.xlsx"
    download(SOURCE_URL, snapshot)

    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    observations = parse_workbook(snapshot, retrieved_at=retrieved_at)
    fixture = evaluate_fixture()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    category_counts: Counter[str] = Counter()
    review_rows = []
    classified_rows = []
    claims = []
    for obs in observations:
        result = classify_contract_subject(obs.subject)
        category_counts[result.category] += 1
        row = {
            "observation_id": obs.observation_id,
            "subject": obs.subject,
            "locator": obs.source_locator,
            "identity_decision": obs.identity_decision,
            "category": result.category,
            "confidence": result.confidence,
            "matched_terms": list(result.matched_terms),
            "review_required": result.review_required,
            "rule_version": result.rule_version,
        }
        classified_rows.append(row)
        if result.review_required:
            review_rows.append(row)
        claim = classification_claim(obs, result)
        if claim is not None:
            validator.validate(claim)
            claims.append(claim)

    report = {
        "rule_version": RULE_VERSION,
        "source_url": SOURCE_URL,
        "retrieved_at": retrieved_at,
        "record_count": len(observations),
        "category_counts": {category: category_counts.get(category, 0) for category in CATEGORIES},
        "review_queue_count": len(review_rows),
        "review_queue_rate": len(review_rows) / len(observations) if observations else 0.0,
        "derived_claim_count": len(claims),
        "schema_validated_claim_count": len(claims),
        "fixture_case_count": fixture["case_count"],
        "fixture_error_count": fixture["error_count"],
        "fixture_confusion_matrix": fixture["confusion_matrix"],
        "authority_feature_used": False,
        "policy_decisions_created": False,
        "safety_rule": "classification uses exact subject text only; ambiguous/conflicting/unmatched cases become UNKNOWN/review",
    }

    (out / "classified-observations.json").write_text(json.dumps(classified_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "review-queue.json").write_text(json.dumps(review_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "classification-claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "fixture-evaluation.json").write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(observations) < 50:
        raise RuntimeError(f"expected at least 50 real records, got {len(observations)}")
    if fixture["error_count"]:
        raise RuntimeError(f"labeled fixture errors: {fixture['errors']}")
    if not category_counts["CIVILIAN"]:
        raise RuntimeError("real snapshot produced no CIVILIAN classifications")
    if not review_rows:
        raise RuntimeError("real snapshot produced no UNKNOWN/review cases; rules may be overconfident")
    if len(claims) != sum(obs.identity_decision == "AUTO_LINK" for obs in observations):
        raise RuntimeError("derived claim count did not preserve M1.3 identity-resolution gate")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/contract-subject-semantics")
