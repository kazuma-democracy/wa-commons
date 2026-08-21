from wa_commons.identity.jpx import entity_id_from_tse_code, from_jpx_row
from wa_commons.identity.merge import merge_identifiers, name_candidate
from wa_commons.identity.models import Identifier, SourceRef
from wa_commons.identity.normalize import normalize_name, normalize_security_code


def src(name="fixture"):
    return SourceRef(
        name,
        "1",
        "2026-07-31",
        "https://example.test",
        "2026-08-21T00:00:00Z",
    )


def test_japanese_name_normalization_is_comparison_only():
    assert normalize_name("トヨタ自動車株式会社") == normalize_name("トヨタ自動車（株）")
    assert name_candidate("株式会社ABC", "ＡＢＣ") is True


def test_security_code_normalization():
    assert normalize_security_code(7203.0) == "7203"
    assert entity_id_from_tse_code("7203") == "wa:org:jp:tse:7203"


def test_jpx_row_builds_canonical_record():
    record = from_jpx_row(
        {"コード": 7203, "銘柄名": "トヨタ自動車", "市場・商品区分": "プライム"},
        src("jpx"),
    )
    assert record.entity_id == "wa:org:jp:tse:7203"
    assert record.identifiers[0].scheme == "JPX_SECURITY_CODE"


def test_conflicting_corporate_numbers_force_dispute():
    base = from_jpx_row(
        {"コード": 7203, "銘柄名": "Example", "市場・商品区分": "プライム"},
        src("jpx"),
    )
    one = Identifier("JP_CORPORATE_NUMBER", "1234567890123", src("nta"))
    two = Identifier("JP_CORPORATE_NUMBER", "9999999999999", src("nta"))
    record = merge_identifiers(base, [one, two])
    assert record.review_state == "DISPUTED"
    assert "strong identifier conflict" in record.review_reason
