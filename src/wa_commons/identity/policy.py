from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .benchmark import BenchmarkRecord, MatchResult, STRONG_ID_FIELDS
from .normalize import normalize_name, normalize_security_code

POLICY_VERSION = "wa-conservative-v0.2"
YENTE_VERSION = "5.5.0"
YENTE_ALGORITHM = "logic-v2"
YENTE_REVIEW_SCORE = 0.70
SPLINK_VERSION = "4.0.16"
SPLINK_REVIEW_SCORE = 0.50


@dataclass(frozen=True)
class ResolutionPolicy:
    version: str = POLICY_VERSION
    auto_link_requires_strong_id: bool = True
    name_only_auto_link: bool = False
    yente_version: str = YENTE_VERSION
    yente_algorithm: str = YENTE_ALGORITHM
    yente_review_score: float = YENTE_REVIEW_SCORE
    splink_version: str = SPLINK_VERSION
    splink_review_score: float = SPLINK_REVIEW_SCORE


def _norm_id(field: str, value: str) -> str:
    value = str(value or "").strip()
    if field == "security_code":
        return normalize_security_code(value)
    return value.upper()


def strong_id_evidence(left: BenchmarkRecord, right: BenchmarkRecord) -> tuple[list[str], list[str]]:
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


def final_policy_match(left: BenchmarkRecord, right: BenchmarkRecord) -> MatchResult:
    """M1.2 final identity-decision policy.

    Fuzzy scores are deliberately absent from this decision function. yente and
    Splink may rank or surface candidates for review, but cannot create an
    AUTO_LINK in M1. A consequential identity link requires an aligned strong
    identifier and no conflicting strong identifier.
    """
    strong_aligned, strong_conflicts = strong_id_evidence(left, right)
    if strong_conflicts:
        return MatchResult(
            "DISPUTED",
            0.0,
            tuple(strong_aligned),
            tuple(strong_conflicts),
            POLICY_VERSION,
        )
    if strong_aligned:
        return MatchResult(
            "AUTO_LINK",
            1.0,
            tuple(strong_aligned),
            (),
            POLICY_VERSION,
        )

    aligned: list[str] = []
    conflicts: list[str] = []
    name_score = SequenceMatcher(None, normalize_name(left.name), normalize_name(right.name)).ratio()
    if name_score >= 0.72:
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

    # Non-identifier evidence can surface a candidate but cannot establish
    # identity automatically in the M1 policy.
    if name_score >= 0.72 or "address" in aligned or conflicts:
        return MatchResult(
            "REVIEW",
            name_score,
            tuple(aligned),
            tuple(conflicts),
            POLICY_VERSION,
        )
    return MatchResult("NON_MATCH", name_score, tuple(aligned), tuple(conflicts), POLICY_VERSION)


def fuzzy_review_candidate(*, yente_score: float | None = None, splink_score: float | None = None) -> bool:
    """Return whether fuzzy evidence is strong enough to enter review.

    These calibrated measurement points are review-routing thresholds only.
    Neither threshold permits AUTO_LINK.
    """
    return bool(
        (yente_score is not None and yente_score >= YENTE_REVIEW_SCORE)
        or (splink_score is not None and splink_score >= SPLINK_REVIEW_SCORE)
    )
