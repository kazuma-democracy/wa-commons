from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = "http://127.0.0.1:8000"
DATASET = "wa_er"
ALGORITHM = "logic-v2"
OUT = Path("artifacts/yente-benchmark")


def post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def collect_scores(queries: list[dict]) -> list[dict]:
    rows: list[dict] = []
    batch_size = 50
    for start in range(0, len(queries), batch_size):
        batch = queries[start:start + batch_size]
        body = {"queries": {f"q{i}": q["query"] for i, q in enumerate(batch)}}
        params = urllib.parse.urlencode({"algorithm": ALGORITHM, "limit": 5, "threshold": 0.0})
        data = post_json(f"{BASE}/match/{DATASET}?{params}", body)
        for i, meta in enumerate(batch):
            hits = data["responses"][f"q{i}"].get("results", [])
            top = hits[0] if hits else None
            expected_id = meta["expected_candidate_id"]
            expected_hit = next((h for h in hits if h.get("id") == expected_id), None) if expected_id else None
            rows.append({
                **{k: meta[k] for k in ("case_id", "case_type", "expected", "provenance")},
                "top_id": top.get("id") if top else None,
                "top_score": float(top.get("score", 0.0)) if top else 0.0,
                "expected_id": expected_id,
                "expected_score": float(expected_hit.get("score", 0.0)) if expected_hit else 0.0,
                "expected_rank": (hits.index(expected_hit) + 1) if expected_hit else None,
            })
    return rows


def metrics(rows: list[dict], threshold: float) -> dict:
    tp = fp = fn = tn = 0
    review = 0
    by_type = defaultdict(lambda: {"cases": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0, "auto_link": 0, "review": 0})
    for row in rows:
        # Auto-link only the top result. For MATCH cases it must also be the labeled
        # candidate. REVIEW is intentionally treated as non-auto-link ground truth.
        auto = row["top_id"] is not None and row["top_score"] >= threshold
        correct_auto = auto and row["expected"] == "MATCH" and row["top_id"] == row["expected_id"]
        positive = row["expected"] == "MATCH"
        if correct_auto:
            tp += 1
        elif auto:
            fp += 1
        elif positive:
            fn += 1
            review += 1
        else:
            tn += 1
            review += int(row["top_id"] is not None)
        b = by_type[row["case_type"]]
        b["cases"] += 1
        b["auto_link"] += int(auto)
        b["review"] += int(not auto and row["top_id"] is not None)
        if correct_auto:
            b["tp"] += 1
        elif auto:
            b["fp"] += 1
        elif positive:
            b["fn"] += 1
        else:
            b["tn"] += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    total = len(rows)
    return {
        "threshold": threshold, "cases": total, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall, "false_positive_rate": fpr,
        "manual_review_rate": review / total if total else 0.0,
        "by_type": dict(by_type),
    }


def choose_threshold(curve: list[dict]) -> dict:
    zero_fp = [m for m in curve if m["fp"] == 0]
    if not zero_fp:
        return max(curve, key=lambda m: (m["precision"], m["recall"], -m["threshold"]))
    # Safety gate: zero false positives first. Within that set maximize recall;
    # if tied, choose the lower threshold to avoid unnecessary review.
    return max(zero_fp, key=lambda m: (m["recall"], -m["threshold"]))


def main() -> None:
    queries = json.loads((OUT / "queries.json").read_text(encoding="utf-8"))
    rows = collect_scores(queries)
    observed = sorted({round(r["top_score"], 6) for r in rows} | {0.0, 1.0})
    # Each observed score is a meaningful decision boundary; add a tiny epsilon
    # above it so threshold transitions are represented without arbitrary grids.
    thresholds = sorted({0.0, 1.0} | set(observed) | {min(1.0, s + 1e-6) for s in observed})
    curve = [metrics(rows, t) for t in thresholds]
    chosen = choose_threshold(curve)
    report = {
        "matcher": "yente",
        "algorithm": ALGORITHM,
        "dataset": DATASET,
        "case_count": len(rows),
        "chosen": chosen,
        "threshold_curve": curve,
        "score_summary": {
            "min": min((r["top_score"] for r in rows), default=0.0),
            "max": max((r["top_score"] for r in rows), default=0.0),
        },
    }
    (OUT / "yente_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "yente_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "threshold_curve"}, ensure_ascii=False, indent=2))
    if chosen["fp"] != 0:
        raise SystemExit("no zero-false-positive threshold found")


if __name__ == "__main__":
    main()
