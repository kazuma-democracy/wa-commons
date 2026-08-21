from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request

from jsonschema import Draft202012Validator

from wa_commons.evidence.mod_procurement import SOURCE_URL, observation_to_claim, parse_workbook


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "wa-commons-m1/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response, path.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)


def validate_claims(claims: list[dict]) -> None:
    schema_path = Path("schemas/evidence-claim.v0.1.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for claim in claims:
        validator.validate(claim)


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    snapshot = out / "04_buppin_k.xlsx"
    download(SOURCE_URL, snapshot)

    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    observations = parse_workbook(snapshot, retrieved_at=retrieved_at)
    claims = [claim for obs in observations if (claim := observation_to_claim(obs)) is not None]
    validate_claims(claims)

    report = {
        "source_url": SOURCE_URL,
        "retrieved_at": retrieved_at,
        "record_count": len(observations),
        "resolved_count": sum(obs.identity_decision == "AUTO_LINK" for obs in observations),
        "unresolved_count": sum(obs.identity_decision != "AUTO_LINK" for obs in observations),
        "claim_count": len(claims),
        "schema_validated_claim_count": len(claims),
        "civilian_guard_examples": [
            obs.subject for obs in observations
            if any(token in obs.subject for token in ("鉛筆", "ＰＰＣ", "PPC", "空調", "発送", "自動車修理"))
        ][:10],
        "semantic_rule": "MOD contract != weapons activity; subject text is preserved for downstream M1.4 classification",
    }
    (out / "observations.json").write_text(
        json.dumps([obs.to_dict() for obs in observations], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(observations) < 50:
        raise RuntimeError(f"expected at least 50 real MOD contract records, got {len(observations)}")
    if not report["civilian_guard_examples"]:
        raise RuntimeError("fixed snapshot did not preserve any clearly civilian procurement subject")
    if not claims:
        raise RuntimeError("no resolved contract claims were produced")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/mod-procurement-pilot")
