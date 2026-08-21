from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .models import EntityRecord, Identifier, SourceRef
from .normalize import normalize_security_code


@dataclass(frozen=True)
class JpxColumns:
    code: str = "コード"
    name: str = "銘柄名"
    market: str = "市場・商品区分"


def entity_id_from_tse_code(code: str) -> str:
    return f"wa:org:jp:tse:{normalize_security_code(code)}"


def from_jpx_row(
    row: Mapping[str, object],
    source: SourceRef,
    columns: JpxColumns = JpxColumns(),
) -> EntityRecord:
    code = normalize_security_code(row[columns.code])
    name = str(row[columns.name]).strip()
    return EntityRecord(
        entity_id=entity_id_from_tse_code(code),
        canonical_name=name,
        identifiers=[Identifier("JPX_SECURITY_CODE", code, source)],
    )
