from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Mapping

from .merge import merge_identifiers
from .models import EntityRecord, Identifier, SourceRef
from .normalize import normalize_security_code


def _first(row: Mapping[str, object], names: Iterable[str]) -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def read_csv_rows(path: str | Path, *, encoding: str = "utf-8-sig") -> list[dict[str, str]]:
    with open(path, newline="", encoding=encoding) as fh:
        return list(csv.DictReader(fh))


def normalize_edinet_security_code(value: object) -> str:
    """Map EDINET's five-character security code to JPX's four-character issuer code.

    The Japanese securities-code system appends a one-character security-type reserve
    code to the four-character issuer code. Ordinary shares use terminal ``0``.
    Examples: 72030 -> 7203 and 130A0 -> 130A.
    """
    text = str(value).strip().upper()
    if text.endswith(".0"):
        text = text[:-2]
    if len(text) == 5 and text.endswith("0") and text[:4].isalnum():
        text = text[:4]
    return normalize_security_code(text)


def build_edinet_security_index(rows: Iterable[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    out: dict[str, Mapping[str, object]] = {}
    duplicates: set[str] = set()
    for row in rows:
        raw = _first(row, ("証券コード", "Security Code", "security_code"))
        if not raw:
            continue
        code = normalize_edinet_security_code(raw)
        if code in out:
            duplicates.add(code)
        else:
            out[code] = row
    for code in duplicates:
        out.pop(code, None)
    return out


def enrich_from_edinet(entity: EntityRecord, edinet_row: Mapping[str, object], source: SourceRef) -> EntityRecord:
    incoming: list[Identifier] = []
    edinet_code = _first(edinet_row, ("ＥＤＩＮＥＴコード", "EDINETコード", "EDINET Code", "edinet_code"))
    corporate_number = _first(edinet_row, ("提出者法人番号", "法人番号", "Corporate Number", "corporate_number"))
    if edinet_code:
        incoming.append(Identifier("EDINET_CODE", edinet_code, source))
    if corporate_number:
        incoming.append(Identifier("JP_CORPORATE_NUMBER", corporate_number, source))
    return merge_identifiers(entity, incoming)


def build_nta_corporate_index(rows: Iterable[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    out: dict[str, Mapping[str, object]] = {}
    for row in rows:
        number = _first(row, ("法人番号", "corporateNumber", "corporate_number"))
        if number:
            out[number] = row
    return out


def validate_with_nta(entity: EntityRecord, nta_row: Mapping[str, object], source: SourceRef) -> EntityRecord:
    number = _first(nta_row, ("法人番号", "corporateNumber", "corporate_number"))
    if not number:
        return entity
    result = merge_identifiers(entity, [Identifier("JP_CORPORATE_NUMBER", number, source)])
    official_name = _first(nta_row, ("商号又は名称", "name", "corporate_name"))
    address = _first(nta_row, ("国内所在地（都道府県市区町村）", "address", "location"))
    aliases = list(result.aliases)
    if official_name and official_name != result.canonical_name and official_name not in aliases:
        aliases.append(official_name)
    addresses = list(result.addresses)
    if address and address not in addresses:
        addresses.append(address)
    return replace(result, aliases=aliases, addresses=addresses)


def build_gleif_registration_index(rows: Iterable[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    out: dict[str, Mapping[str, object]] = {}
    duplicates: set[str] = set()
    for row in rows:
        reg_id = _first(row, ("Entity.RegistrationAuthority.RegistrationAuthorityEntityID", "registration_authority_entity_id", "registrationAuthorityEntityId"))
        if not reg_id:
            continue
        if reg_id in out:
            duplicates.add(reg_id)
        else:
            out[reg_id] = row
    for reg_id in duplicates:
        out.pop(reg_id, None)
    return out


def enrich_from_gleif(entity: EntityRecord, gleif_row: Mapping[str, object], source: SourceRef) -> EntityRecord:
    lei = _first(gleif_row, ("LEI", "lei"))
    if not lei:
        return entity
    return merge_identifiers(entity, [Identifier("LEI", lei, source)])


def strong_id(entity: EntityRecord, scheme: str) -> str | None:
    values = sorted({i.value for i in entity.identifiers if i.scheme == scheme})
    return values[0] if len(values) == 1 else None


def enrich_entity_batch(
    entities: Iterable[EntityRecord],
    *,
    edinet_rows: Iterable[Mapping[str, object]],
    edinet_source: SourceRef,
    nta_rows: Iterable[Mapping[str, object]] = (),
    nta_source: SourceRef | None = None,
    gleif_rows: Iterable[Mapping[str, object]] = (),
    gleif_source: SourceRef | None = None,
) -> list[EntityRecord]:
    edinet_by_security = build_edinet_security_index(edinet_rows)
    nta_by_corporate = build_nta_corporate_index(nta_rows)
    gleif_by_registration = build_gleif_registration_index(gleif_rows)

    output: list[EntityRecord] = []
    for entity in entities:
        result = entity
        security = strong_id(result, "JPX_SECURITY_CODE")
        if security and security in edinet_by_security:
            result = enrich_from_edinet(result, edinet_by_security[security], edinet_source)

        corporate_number = strong_id(result, "JP_CORPORATE_NUMBER")
        if corporate_number and nta_source and corporate_number in nta_by_corporate:
            result = validate_with_nta(result, nta_by_corporate[corporate_number], nta_source)

        corporate_number = strong_id(result, "JP_CORPORATE_NUMBER")
        if corporate_number and gleif_source and corporate_number in gleif_by_registration:
            result = enrich_from_gleif(result, gleif_by_registration[corporate_number], gleif_source)

        output.append(result)
    return output
