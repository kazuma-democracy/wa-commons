from __future__ import annotations

from dataclasses import replace

from .models import EntityRecord, Identifier
from .normalize import normalize_name

STRONG_SCHEMES = {"JP_CORPORATE_NUMBER", "LEI", "EDINET_CODE"}


def merge_identifiers(base: EntityRecord, incoming: list[Identifier]) -> EntityRecord:
    existing = {(i.scheme, i.value) for i in base.identifiers}
    merged = list(base.identifiers)
    for identifier in incoming:
        if (identifier.scheme, identifier.value) not in existing:
            merged.append(identifier)
            existing.add((identifier.scheme, identifier.value))

    by_scheme: dict[str, set[str]] = {}
    for identifier in merged:
        if identifier.scheme in STRONG_SCHEMES:
            by_scheme.setdefault(identifier.scheme, set()).add(identifier.value)
    conflicts = {k: v for k, v in by_scheme.items() if len(v) > 1}
    if conflicts:
        detail = "; ".join(f"{k}={sorted(v)}" for k, v in sorted(conflicts.items()))
        return replace(
            base,
            identifiers=merged,
            review_state="DISPUTED",
            review_reason=f"strong identifier conflict: {detail}",
        )
    return replace(base, identifiers=merged)


def name_candidate(a: str, b: str) -> bool:
    """Candidate generation only. A True result is never sufficient to auto-link."""
    return bool(a and b and normalize_name(a) == normalize_name(b))
