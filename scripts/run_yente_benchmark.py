from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ALGORITHM = "logic-v2"
SCORE_CUTS = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]


def provenance_class(value: str) -> str:
    if value.startswith("source_verified|"):
        return "source_verified"
    if value == "synthetic_adversarial":
        return "synthetic_adversarial"
    return "other"


def post_match(batch: list[dict]) -> dict:
    queries = {}
    for item in batch:
        q = dict(item["query"])
        q["id"] = f"wa-left-{item['case_id']}"
        queries[item["case_id"]] = q
    params = urllib.parse.urlencode({"algorithm": ALGORITHM, "threshold": 0.0, "limit": 50})
    req = urllib.request.Request(
        f"{BASE}/match/wa_benchmark?{params}",
        data=json.dumps({"queries": queries}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def score_rows(rows: list[dict], cut: float) -> dict:
    tp = fp = fn = tn = 0
    considered = 0
    for row in rows:
        if row["expected"] == "REVIEW":
            continue
        considered += 1
        actual = row["expected"] == "MATCH"
        pred = row["paired_score"] >= cut
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
        elif not pred and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "cut": cut,
        "considered": considered,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fpr,
    }


def summarize_scores(rows: list[dict]) -> dict:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["expected"]].append(row["paired_score"])
    out = {}
    for key, vals in grouped.items():
        vals = sorted(vals)
        out[key] = {
            "count": len(vals),
            "min": vals[0] if vals else None,
            "max": vals[-1] if vals else None,
            "mean": sum(vals) / len(vals) if vals else None,
            "median": vals[len(vals) // 2] if vals else None,
        }
    return out


def main() -> None:
    out = Path("artifacts/yente-benchmark")
    items = json.loads((out / "queries.json").read_text(encoding="utf-8"))
    rows = []
    for i in range(0, len(items), 20):
        batch = items[i:i + 20]
        data = post_match(batch)
        responses = data.get("responses", {})
        for item in batch:
            response = responses[item["case_id"]]
            results = response.get("results", [])
            expected_id = item["expected_candidate_id"]
            paired = next((r for r in results if r.get("id") == expected_id), None)
            rows.append({
                "case_id": item["case_id"],
                "case_type": item["case_type"],
                "expected": item["expected"],
                "provenance_class": provenance_class(item["provenance"]),
                "expected_candidate_id": expected_id,
                "paired_score": float(paired.get("score", 0.0)) if paired else 0.0,
                "paired_rank": next((j + 1 for j, r in enumerate(results) if r.get("id") == expected_id), None),
                "top_results": [
                    {"id": r.get("id"), "score": r.get("score"), "match": r.get("match")}
                    for r in results[:10]
                ],
            })

    by_provenance = {}
    for pclass in sorted({r["provenance_class"] for r in rows}):
        subset = [r for r in rows if r["provenance_class"] == pclass]
        by_provenance[pclass] = {
            "cases": len(subset),
            "score_summary": summarize_scores(subset),
            "curves": [score_rows(subset, cut) for cut in SCORE_CUTS],
        }

    report = {
        "matcher": "yente",
        "yente_version": "5.5.0",
        "index_backend": "elasticsearch:9.4.2",
        "algorithm": ALGORITHM,
        "dataset": "wa_benchmark",
        "cases": len(rows),
        "score_summary": summarize_scores(rows),
        "curves": [score_rows(rows, cut) for cut in SCORE_CUTS],
        "by_provenance": by_provenance,
        "note": "Score cuts are measurement points only; M1.2b does not select a production threshold.",
    }
    (out / "yente-rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "yente-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
