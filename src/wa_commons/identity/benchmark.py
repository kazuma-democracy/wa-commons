from __future__ import annotations

from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from typing import Iterable, Literal

from .normalize import normalize_name, normalize_security_code

Expected = Literal["MATCH", "NON_MATCH", "REVIEW"]
Decision = Literal["AUTO_LINK", "NON_MATCH", "REVIEW", "DISPUTED"]

STRONG_ID_FIELDS = ("corporate_number", "lei", "edinet_code", "security_code")


@dataclass(frozen=True)
class BenchmarkRecord:
    name: str
    corporate_number: str = ""
    lei: str = ""
    edinet_code: str = ""
    security_code: str = ""
    jurisdiction: str = "JP"
    address: str = ""


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    case_type: str
    left: BenchmarkRecord
    right: BenchmarkRecord
    expected: Expected
    provenance: str
    note: str = ""


@dataclass(frozen=True)
class MatchResult:
    decision: Decision
    score: float
    aligned_attributes: tuple[str, ...]
    conflicting_attributes: tuple[str, ...]
    matcher: str


def _norm_id(field: str, value: str) -> str:
    value = str(value or "").strip()
    if field == "security_code":
        return normalize_security_code(value)
    return value.upper()


def _strong_id_comparison(left: BenchmarkRecord, right: BenchmarkRecord) -> tuple[list[str], list[str]]:
    aligned: list[str] = []
    conflicts: list[str] = []
    for field in STRONG_ID_FIELDS:
        a = _norm_id(field, getattr(left, field))
        b = _norm_id(field, getattr(right, field))
        if not a or not b:
            continue
        if a == b:
            aligned.append(field)
        else:
            conflicts.append(field)
    return aligned, conflicts


def conservative_baseline(left: BenchmarkRecord, right: BenchmarkRecord) -> MatchResult:
    """Transparent safety baseline for threshold calibration.

    This is intentionally not a production fuzzy matcher. It exists as a simple,
    auditable comparison point for yente/Splink-style matchers.
    """
    strong_aligned, strong_conflicts = _strong_id_comparison(left, right)
    if strong_conflicts:
        return MatchResult("DISPUTED", 0.0, tuple(strong_aligned), tuple(strong_conflicts), "wa-conservative-v0.1")
    if strong_aligned:
        return MatchResult("AUTO_LINK", 1.0, tuple(strong_aligned), (), "wa-conservative-v0.1")

    aligned: list[str] = []
    conflicts: list[str] = []
    name_score = SequenceMatcher(None, normalize_name(left.name), normalize_name(right.name)).ratio()
    if name_score >= 0.94:
        aligned.append("name")

    if left.jurisdiction and right.jurisdiction:
        if left.jurisdiction.upper() == right.jurisdiction.upper():
            aligned.append("jurisdiction")
        else:
            conflicts.append("jurisdiction")

    if left.address and right.address:
        address_score = SequenceMatcher(None, normalize_name(left.address), normalize_name(right.address)).ratio()
        if address_score >= 0.90:
            aligned.append("address")
        elif address_score < 0.45:
            conflicts.append("address")

    if conflicts:
        return MatchResult("REVIEW", name_score, tuple(aligned), tuple(conflicts), "wa-conservative-v0.1")

    # Consequential name-only links never auto-link. A broad attribute such as
    # jurisdiction is not enough corroboration: require a more entity-specific
    # aligned attribute (address in v0.1) unless an exact strong ID already matched.
    substantive_corroboration = "address" in aligned
    if name_score >= 0.94 and substantive_corroboration:
        return MatchResult("AUTO_LINK", name_score, tuple(aligned), (), "wa-conservative-v0.1")
    if name_score >= 0.72:
        return MatchResult("REVIEW", name_score, tuple(aligned), (), "wa-conservative-v0.1")
    return MatchResult("NON_MATCH", name_score, tuple(aligned), (), "wa-conservative-v0.1")


def expected_positive(case: BenchmarkCase) -> bool:
    return case.expected == "MATCH"


def predicted_positive(result: MatchResult) -> bool:
    return result.decision == "AUTO_LINK"


def evaluate(cases: Iterable[BenchmarkCase], matcher=conservative_baseline) -> dict:
    rows = []
    tp = fp = fn = tn = review = disputed = 0
    by_type: dict[str, dict[str, int]] = {}

    for case in cases:
        result = matcher(case.left, case.right)
        actual = expected_positive(case)
        predicted = predicted_positive(result)
        if result.decision == "REVIEW":
            review += 1
        if result.decision == "DISPUTED":
            disputed += 1
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1

        bucket = by_type.setdefault(case.case_type, {"cases": 0, "auto_link": 0, "review": 0, "disputed": 0, "errors": 0})
        bucket["cases"] += 1
        bucket["auto_link"] += int(result.decision == "AUTO_LINK")
        bucket["review"] += int(result.decision == "REVIEW")
        bucket["disputed"] += int(result.decision == "DISPUTED")
        bucket["errors"] += int((predicted and not actual) or (not predicted and actual))
        rows.append({"case_id": case.case_id, "expected": case.expected, "result": asdict(result)})

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    false_positive_rate = fp / (fp + tn) if fp + tn else 0.0
    total = tp + fp + fn + tn
    return {
        "cases": total,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
        "manual_review_rate": review / total if total else 0.0,
        "disputed_rate": disputed / total if total else 0.0,
        "by_type": by_type,
        "rows": rows,
    }
