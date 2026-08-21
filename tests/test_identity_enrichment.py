from wa_commons.identity.enrich import (
    build_edinet_security_index,
    build_gleif_registration_index,
    enrich_entity_batch,
)
from wa_commons.identity.jpx import from_jpx_row
from wa_commons.identity.models import SourceRef


def src(name: str) -> SourceRef:
    return SourceRef(
        source=name,
        source_key="fixture",
        snapshot="2026-08-21",
        url=f"https://example.test/{name}",
        retrieved_at="2026-08-21T00:00:00Z",
    )


def entity(code="7203", name="Example Motors"):
    return from_jpx_row(
        {"コード": code, "銘柄名": name, "市場・商品区分": "プライム（内国株式）"},
        src("jpx"),
    )


def test_edinet_security_code_bridges_to_corporate_number_without_name_match():
    edinet = [
        {
            "証券コード": "7203",
            "ＥＤＩＮＥＴコード": "E00001",
            "法人番号": "1111111111111",
            "提出者名": "A deliberately different display name",
        }
    ]
    nta = [{"法人番号": "1111111111111", "商号又は名称": "Example Motors株式会社"}]
    gleif = [
        {
            "LEI": "549300EXAMPLE0000001",
            "Entity.RegistrationAuthority.RegistrationAuthorityEntityID": "1111111111111",
        }
    ]
    [result] = enrich_entity_batch(
        [entity()],
        edinet_rows=edinet,
        edinet_source=src("edinet"),
        nta_rows=nta,
        nta_source=src("nta"),
        gleif_rows=gleif,
        gleif_source=src("gleif"),
    )
    ids = result.identifier_map()
    assert ids["JPX_SECURITY_CODE"] == {"7203"}
    assert ids["EDINET_CODE"] == {"E00001"}
    assert ids["JP_CORPORATE_NUMBER"] == {"1111111111111"}
    assert ids["LEI"] == {"549300EXAMPLE0000001"}
    assert "Example Motors株式会社" in result.aliases


def test_duplicate_edinet_security_code_is_not_auto_linked():
    rows = [
        {"証券コード": "7203", "ＥＤＩＮＥＴコード": "E00001", "法人番号": "1111111111111"},
        {"証券コード": "7203", "ＥＤＩＮＥＴコード": "E00002", "法人番号": "2222222222222"},
    ]
    assert "7203" not in build_edinet_security_index(rows)


def test_duplicate_gleif_registration_id_is_not_auto_linked():
    rows = [
        {"LEI": "LEI1", "Entity.RegistrationAuthority.RegistrationAuthorityEntityID": "1111111111111"},
        {"LEI": "LEI2", "Entity.RegistrationAuthority.RegistrationAuthorityEntityID": "1111111111111"},
    ]
    assert "1111111111111" not in build_gleif_registration_index(rows)


def test_name_only_match_cannot_enrich():
    edinet = [
        {
            "証券コード": "9999",
            "ＥＤＩＮＥＴコード": "E99999",
            "法人番号": "9999999999999",
            "提出者名": "Example Motors",
        }
    ]
    [result] = enrich_entity_batch(
        [entity()],
        edinet_rows=edinet,
        edinet_source=src("edinet"),
    )
    assert "EDINET_CODE" not in result.identifier_map()
    assert "JP_CORPORATE_NUMBER" not in result.identifier_map()
