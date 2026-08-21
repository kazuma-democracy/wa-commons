from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class SourceRef:
    source: str
    source_key: str
    snapshot: str
    url: str
    retrieved_at: str
    adapter_version: str = "0.1"


@dataclass(frozen=True)
class Identifier:
    scheme: str
    value: str
    source: SourceRef


@dataclass
class EntityRecord:
    entity_id: str
    canonical_name: str
    jurisdiction: str = "JP"
    aliases: list[str] = field(default_factory=list)
    identifiers: list[Identifier] = field(default_factory=list)
    addresses: list[str] = field(default_factory=list)
    review_state: str = "CONFIRMED"
    review_reason: str | None = None

    def identifier_map(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for identifier in self.identifiers:
            out.setdefault(identifier.scheme, set()).add(identifier.value)
        return out

    def to_dict(self) -> dict:
        return asdict(self)


def find_conflicting_strong_ids(records: Iterable[EntityRecord]) -> list[tuple[str, str, str]]:
    """Return (scheme, value_a, value_b) for per-entity strong-ID conflicts."""
    strong = {"JP_CORPORATE_NUMBER", "LEI", "EDINET_CODE"}
    conflicts: list[tuple[str, str, str]] = []
    for record in records:
        by_scheme = record.identifier_map()
        for scheme in strong:
            values = sorted(by_scheme.get(scheme, set()))
            if len(values) > 1:
                conflicts.append((scheme, values[0], values[1]))
    return conflicts
