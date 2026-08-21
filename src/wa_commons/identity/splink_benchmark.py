from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Iterable

from .benchmark import BenchmarkCase, BenchmarkRecord, evaluate

SCORE_CUTS = (0.50, 0.60, 0.70, 0.80, 0.90, 0.95)


def provenance_class(value: str) -> str:
    if value.startswith("source_verified|"):
        return "source_verified"
    if value == "synthetic_adversarial":
        return "synthetic_adversarial"
    return "other"


def record_to_row(side: str, case_id: str, record: BenchmarkRecord) -> dict:
    """Convert one benchmark observation into a table row for Splink.

    Empty strings become NULL so missing identifiers never compare as equal.
    The benchmark keeps identifier systems in separate columns instead of
    collapsing them into one generic identifier namespace.
    """

    def value_or_none(value: str) -> str | None:
        value = str(value or "").strip()
        return value or None

    return {
        "unique_id": f"{side}:{case_id}",
        "name": value_or_none(record.name),
        "corporate_number": value_or_none(record.corporate_number),
        "lei": value_or_none(record.lei),
        "edinet_code": value_or_none(record.edinet_code),
        "security_code": value_or_none(record.security_code),
        "jurisdiction": value_or_none(record.jurisdiction),
        "address": value_or_none(record.address),
    }


def build_link_tables(cases: Iterable[BenchmarkCase]) -> tuple[list[dict], list[dict]]:
    left: list[dict] = []
    right: list[dict] = []
    for case in cases:
        left.append(record_to_row("L", case.case_id, case.left))
        right.append(record_to_row("R", case.case_id, case.right))
    return left, right


def score_rows(rows: list[dict], cut: float) -> dict:
    tp = fp = fn = tn = 0
    considered = 0
    for row in rows:
        if row["expected"] == "REVIEW":
            continue
        considered += 1
        actual = row["expected"] == "MATCH"
        predicted = row["paired_score"] >= cut
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    false_positive_rate = fp / (fp + tn) if fp + tn else 0.0
    return {
        "cut": cut,
        "considered": considered,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
    }


def summarize_scores(rows: list[dict]) -> dict:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["expected"]].append(float(row["paired_score"]))
    output = {}
    for key, values in grouped.items():
        values = sorted(values)
        output[key] = {
            "count": len(values),
            "min": values[0] if values else None,
            "max": values[-1] if values else None,
            "mean": sum(values) / len(values) if values else None,
            "median": values[len(values) // 2] if values else None,
        }
    return output


def probability_bands(rows: list[dict]) -> dict:
    """Descriptive probability bands, not production decision thresholds."""
    counts = {
        "lt_0_10": 0,
        "0_10_to_lt_0_50": 0,
        "0_50_to_lt_0_90": 0,
        "gte_0_90": 0,
    }
    for row in rows:
        score = float(row["paired_score"])
        if score < 0.10:
            counts["lt_0_10"] += 1
        elif score < 0.50:
            counts["0_10_to_lt_0_50"] += 1
        elif score < 0.90:
            counts["0_50_to_lt_0_90"] += 1
        else:
            counts["gte_0_90"] += 1
    total = len(rows)
    return {
        "counts": counts,
        "fractions": {key: value / total if total else 0.0 for key, value in counts.items()},
        "note": "Bands describe score concentration only and are not AUTO_LINK/REVIEW thresholds.",
    }


def baseline_summary(cases: list[BenchmarkCase]) -> dict:
    """Evaluate the existing fixed WA conservative baseline without retuning it."""

    def clean(report: dict) -> dict:
        report = dict(report)
        report.pop("rows", None)
        return report

    overall = clean(evaluate(cases))
    by_provenance = {}
    for pclass in sorted({provenance_class(case.provenance) for case in cases}):
        subset = [case for case in cases if provenance_class(case.provenance) == pclass]
        by_provenance[pclass] = clean(evaluate(subset))
    overall["by_provenance_metrics"] = by_provenance
    return overall
