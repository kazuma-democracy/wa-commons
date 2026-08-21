from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import platform
import subprocess
import urllib.request

from jsonschema import Draft202012Validator

from wa_commons.evidence.cards import card_from_claim
from wa_commons.evidence.contract_subject import RULE_VERSION, classification_claim, classify_contract_subject
from wa_commons.evidence.mod_procurement import ADAPTER_VERSION as MOD_ADAPTER_VERSION
from wa_commons.evidence.mod_procurement import SOURCE_URL as MOD_SOURCE_URL
from wa_commons.evidence.mod_procurement import parse_workbook, sha256
from wa_commons.evidence.political_finance import ADAPTER_VERSION as PF_ADAPTER_VERSION
from wa_commons.evidence.political_finance import IDENTITY_POLICY_VERSION, parse_organization_tsv_page, sha256_bytes, source_url
from wa_commons.evidence.reproduction import apply_status_transition, build_canonical_graph, canonical_sha256, outage_result

EXPECTED_MOD_SHA256 = "c1f37e838d66ffa7bc62c35c5d8830c75ed7b92b0befe0c380f0d79052c773e8"
EXPECTED_PF_SHA256 = "e8871ed2cb62729ec8a8c01028c3da2f797a6f65972abfb8dc4dcf757f11c8fe"
FIXED_RETRIEVED_AT = "2026-08-21T13:00:00Z"
FIXED_CORRECTION_AT = "2026-08-21T14:00:00Z"
FIXED_EXPIRY_AT = "2027-08-21T00:00:00Z"
PF_PART = 18
PF_FIRST_PAGE = 1
PF_LAST_PAGE = 20
REAL_MOD_ENTITY_TARGET = 10


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def command_version(args: list[str]) -> str:
    proc = subprocess.run(args, check=True, text=True, capture_output=True)
    text = (proc.stdout or proc.stderr).strip().splitlines()
    return text[0] if text else "unknown"


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "artifacts" / "m1-reproduction"
    work = out / "work"
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)

    schema = json.loads((root / "schemas" / "evidence-claim.v0.1.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    examples = json.loads((root / "schemas" / "examples" / "evidence-claim.examples.json").read_text(encoding="utf-8"))
    for claim in examples:
        validator.validate(claim)

    # Adapter 1: fixed Ministry of Defense procurement workbook.
    mod_path = work / "mod.xlsx"
    mod_path.write_bytes(download(MOD_SOURCE_URL))
    mod_sha = sha256(mod_path)
    if mod_sha != EXPECTED_MOD_SHA256:
        raise SystemExit(f"Pinned MOD source changed: expected {EXPECTED_MOD_SHA256}, got {mod_sha}")
    mod_observations = parse_workbook(mod_path, retrieved_at=FIXED_RETRIEVED_AT)

    real_claims: list[dict] = []
    seen_entities: set[str] = set()
    for obs in mod_observations:
        if not obs.entity_id or obs.entity_id in seen_entities:
            continue
        claim = classification_claim(obs, classify_contract_subject(obs.subject))
        if claim is None:
            continue
        validator.validate(claim)
        real_claims.append(claim)
        seen_entities.add(obs.entity_id)
        if len(real_claims) >= REAL_MOD_ENTITY_TARGET:
            break
    if len(real_claims) < REAL_MOD_ENTITY_TARGET:
        raise SystemExit(f"Expected {REAL_MOD_ENTITY_TARGET} deterministic real MOD entities, got {len(real_claims)}")

    # Adapter 2: fixed official political-finance filing, bounded to 20 pages.
    # OCR observations are intentionally review-required and therefore do not
    # silently become entity-linked claims.
    pf_url = source_url(PF_PART)
    pf_bytes = download(pf_url)
    pf_sha = sha256_bytes(pf_bytes)
    if pf_sha != EXPECTED_PF_SHA256:
        raise SystemExit(f"Pinned political-finance source changed: expected {EXPECTED_PF_SHA256}, got {pf_sha}")
    pf_pdf = work / "political-finance.pdf"
    pf_pdf.write_bytes(pf_bytes)
    prefix = work / "pf-page"
    subprocess.run([
        "pdftoppm", "-f", str(PF_FIRST_PAGE), "-l", str(PF_LAST_PAGE), "-r", "250",
        "-gray", "-png", str(pf_pdf), str(prefix)
    ], check=True)
    pf_observations = []
    for image in sorted(work.glob("pf-page-*.png")):
        page = int(image.stem.rsplit("-", 1)[-1])
        proc = subprocess.run(
            ["tesseract", str(image), "stdout", "-l", "jpn", "--psm", "6", "tsv"],
            check=True, text=True, capture_output=True,
        )
        pf_observations.extend(parse_organization_tsv_page(
            proc.stdout,
            part=PF_PART,
            page=page,
            retrieved_at=FIXED_RETRIEVED_AT,
            source_sha256=pf_sha,
        ))
    if not pf_observations:
        raise SystemExit("Political-finance adapter produced no bounded real observations")
    if any(o.identity_decision == "AUTO_LINK" for o in pf_observations):
        raise SystemExit("Threat-model gate failed: OCR/name-only political donor auto-linked")
    if any(not o.extraction_review_required for o in pf_observations):
        raise SystemExit("Threat-model gate failed: OCR political-finance observation escaped review")

    # Controlled correction fixture: use the canonical correction example, render
    # its earlier state and its final DISPUTED state, proving dependent card output
    # changes while history is preserved.
    corrected_example = next(c for c in examples if c["claim_id"] == "wc:claim:example-correction-001")
    before_correction = deepcopy(corrected_example)
    before_correction["adjudication"]["status"] = "confirmed"
    before_correction["adjudication"]["reasoning_summary"] = "Controlled pre-correction fixture state."
    before_correction["adjudication"]["decided_at"] = "2026-08-21T05:16:00Z"
    before_correction["correction_history"] = []
    before_correction["subject"]["entity_resolution"]["review_status"] = "machine_only"
    before_correction["policy_context"] = None
    validator.validate(before_correction)
    validator.validate(corrected_example)
    correction_demo = {
        "claim_id": corrected_example["claim_id"],
        "before_status": card_from_claim(before_correction).adjudication["status"],
        "after_status": card_from_claim(corrected_example).adjudication["status"],
        "before_card_sha256": canonical_sha256(card_from_claim(before_correction).to_dict()),
        "after_card_sha256": canonical_sha256(card_from_claim(corrected_example).to_dict()),
        "history_entries": len(corrected_example["correction_history"]),
    }
    if correction_demo["before_status"] != "CONFIRMED" or correction_demo["after_status"] != "DISPUTED":
        raise SystemExit("Correction propagation gate failed")
    if correction_demo["before_card_sha256"] == correction_demo["after_card_sha256"]:
        raise SystemExit("Dependent evidence card did not change after correction")

    # Controlled expiry transition on a schema-backed real claim copy. This is a
    # demonstration only and is not presented as the current status of the company.
    expiry_fixture = apply_status_transition(
        real_claims[0],
        new_status="expired",
        reason="Controlled M1.7 fixture: evidence exceeded a hypothetical revalidation horizon.",
        changed_at=FIXED_EXPIRY_AT,
    )
    validator.validate(expiry_fixture)
    expiry_demo = {
        "base_claim_id": real_claims[0]["claim_id"],
        "before_status": card_from_claim(real_claims[0]).adjudication["status"],
        "after_status": card_from_claim(expiry_fixture).adjudication["status"],
        "policy_context": expiry_fixture.get("policy_context"),
    }
    if expiry_demo["after_status"] != "EXPIRED" or expiry_demo["policy_context"] is not None:
        raise SystemExit("Expiry propagation/policy-separation gate failed")

    outage_demo = outage_result(
        source_id="jp-political-finance",
        checked_at=FIXED_CORRECTION_AT,
        reason="Controlled M1.7 source-outage fixture",
    )
    if outage_demo["evidence_status"] != "UNKNOWN" or outage_demo["policy_decision"] != "NONE":
        raise SystemExit("Source outage created a policy decision")

    # The final canonical graph contains deterministic real MOD claims and the
    # corrected schema example. Political-finance OCR stays an observation-layer
    # adapter result because its identity/review gate intentionally blocks claims.
    final_claims = real_claims + [corrected_example]
    for claim in final_claims:
        validator.validate(claim)

    observation_summaries = [
        {
            "source_id": "jp-mod-procurement",
            "observation_id": o.observation_id,
            "entity_id": o.entity_id,
            "identity_decision": o.identity_decision,
            "source_sha256": o.source_sha256,
        }
        for o in mod_observations[:20]
    ] + [
        {
            "source_id": "jp-political-finance",
            "observation_id": o.observation_id,
            "entity_id": o.entity_id,
            "identity_decision": o.identity_decision,
            "source_sha256": o.source_sha256,
            "review_required": o.extraction_review_required,
        }
        for o in pf_observations[:20]
    ]

    tool_versions = {
        "python": platform.python_version(),
        "tesseract": command_version(["tesseract", "--version"]),
        "pdftoppm": command_version(["pdftoppm", "-v"]),
    }
    adapter_runs = [
        {
            "adapter": "jp-mod-procurement",
            "adapter_version": MOD_ADAPTER_VERSION,
            "rule_version": RULE_VERSION,
            "identity_policy_version": IDENTITY_POLICY_VERSION,
            "source_url": MOD_SOURCE_URL,
            "source_sha256": mod_sha,
            "fixed_retrieved_at": FIXED_RETRIEVED_AT,
            "observation_count": len(mod_observations),
            "canonical_claim_count": len(real_claims),
        },
        {
            "adapter": "jp-political-finance",
            "adapter_version": PF_ADAPTER_VERSION,
            "identity_policy_version": IDENTITY_POLICY_VERSION,
            "source_url": pf_url,
            "source_sha256": pf_sha,
            "fixed_retrieved_at": FIXED_RETRIEVED_AT,
            "page_range": [PF_FIRST_PAGE, PF_LAST_PAGE],
            "observation_count": len(pf_observations),
            "canonical_claim_count": 0,
            "claim_gate": "review-required OCR/name-only observations cannot emit claims",
        },
    ]

    graph = build_canonical_graph(
        claims=final_claims,
        observation_summaries=observation_summaries,
        adapter_runs=adapter_runs,
        correction_demo=correction_demo,
        expiry_demo=expiry_demo,
        outage_demo=outage_demo,
        tool_versions=tool_versions,
    )
    graph_sha = canonical_sha256(graph)
    report = {
        "m1_status": "PASS",
        "reproduction_version": graph["reproduction_version"],
        "canonical_graph_sha256": graph_sha,
        "canonical_entity_count": len(graph["entity_ids"]),
        "canonical_claim_count": len(graph["claims"]),
        "adapter_count": len(graph["adapter_runs"]),
        "model_assisted_stages": graph["model_assisted_stages"],
        "correction_demo": correction_demo,
        "expiry_demo": expiry_demo,
        "outage_demo": outage_demo,
        "tool_versions": tool_versions,
        "threat_model_gates": {
            "name_only_auto_link_blocked": True,
            "mod_contract_not_weapons_activity": all(c["claim"]["category"] != "weapons_activity" for c in real_claims),
            "missing_source_no_pass_exclude": outage_demo["policy_decision"] == "NONE",
            "correction_history_visible": correction_demo["history_entries"] > 0,
            "expired_supported": expiry_demo["after_status"] == "EXPIRED",
            "model_only_evidence_absent": graph["model_assisted_stages"] == [],
        },
    }
    if not all(report["threat_model_gates"].values()):
        raise SystemExit(f"Threat-model gate failed: {report['threat_model_gates']}")

    (out / "canonical-graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    # Raw upstream files and rendered OCR pages are transient. The artifact only
    # needs the derived graph/report while redistribution terms remain review-required.
    for path in work.glob("*"):
        path.unlink(missing_ok=True)
    work.rmdir()


if __name__ == "__main__":
    main()
