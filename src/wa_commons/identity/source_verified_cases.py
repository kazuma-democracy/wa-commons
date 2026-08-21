from __future__ import annotations

from .benchmark import BenchmarkCase, BenchmarkRecord


JPX_STOCK_SEARCH = "https://www2.jpx.co.jp/tseHpFront/StockSearch.do"
ZOZO_RENAME = "https://corp.zozo.com/news/20181001-5984/"
LY_HISTORY = "https://www.lycorp.co.jp/ja/company/history/z-holdings/"
SOFTBANK_SEGMENT = "https://group.softbank/segments/softbank"


def _prov(publisher: str, url: str, locator: str, note: str = "") -> str:
    parts = [
        "source_verified",
        f"publisher={publisher}",
        f"url={url}",
        f"locator={locator}",
        "retrieved=2026-08-21",
    ]
    if note:
        parts.append(f"note={note}")
    return "|".join(parts)


def _stock(name: str, code: str = "") -> BenchmarkRecord:
    return BenchmarkRecord(name=name, security_code=code, jurisdiction="JP")


def build_source_verified_cases() -> list[BenchmarkCase]:
    """Small factual Japanese subset for M1.2 calibration.

    Facts come from official company/JPX public material. Some cases deliberately
    remove identifiers or vary legal-form spelling to exercise review behavior;
    those transformations are noted and must not be mistaken for additional
    claims about the source.
    """
    cases: list[BenchmarkCase] = []

    # Historical legal-entity continuity: official company histories document the
    # rename. The listed security code supplies a stable market identifier.
    cases.extend([
        BenchmarkCase(
            "src-history-zozo-01", "historical_rename_merger",
            _stock("株式会社スタートトゥデイ", "3092"),
            _stock("株式会社ZOZO", "3092"),
            "MATCH",
            _prov("ZOZO", ZOZO_RENAME, "2018-10-01 company-name change; security code 3092 cross-checked in JPX", "official rename announcement"),
            "Official rename; same listed security code.",
        ),
        BenchmarkCase(
            "src-history-zozo-02", "historical_rename_merger",
            _stock("START TODAY CO., LTD.", "3092"),
            _stock("ZOZO, Inc.", "3092"),
            "MATCH",
            _prov("ZOZO", ZOZO_RENAME, "2018-10-01 rename", "English-name variant derived from the same legal-entity history"),
            "English-name representation of the documented rename.",
        ),
        BenchmarkCase(
            "src-history-ly-01", "historical_rename_merger",
            _stock("ヤフー株式会社", "4689"),
            _stock("Zホールディングス株式会社", "4689"),
            "MATCH",
            _prov("LINE Yahoo", LY_HISTORY, "2019-10 Yahoo Japan -> Z Holdings", "official corporate history"),
            "Official history records the holding-company transition and rename.",
        ),
        BenchmarkCase(
            "src-history-ly-02", "historical_rename_merger",
            _stock("Zホールディングス株式会社", "4689"),
            _stock("LINEヤフー株式会社", "4689"),
            "MATCH",
            _prov("LINE Yahoo", LY_HISTORY, "2023-10 Z Holdings -> LINE Yahoo", "official corporate history"),
            "Official history records the 2023 group reorganization and rename.",
        ),
    ])

    # Parent/subsidiary trap: SoftBank Group's official segment material treats
    # SoftBank Corp and its subsidiaries as a business segment of the group. The
    # two listed issuers remain separate legal entities and must not collapse.
    for suffix, left_name, right_name in [
        ("01", "ソフトバンクグループ株式会社", "ソフトバンク株式会社"),
        ("02", "ソフトバンクグループ（株）", "ソフトバンク（株）"),
        ("03", "SoftBank Group Corp.", "SoftBank Corp."),
        ("04", "ソフトバンクグループ", "ソフトバンク"),
        ("05", "SoftBank Group", "SoftBank"),
        ("06", "ＳｏｆｔＢａｎｋ Ｇｒｏｕｐ", "ＳｏｆｔＢａｎｋ"),
    ]:
        cases.append(BenchmarkCase(
            f"src-parent-softbank-{suffix}", "parent_subsidiary_trap",
            _stock(left_name, "9984"),
            _stock(right_name, "9434"),
            "NON_MATCH",
            _prov("SoftBank Group", SOFTBANK_SEGMENT, "SoftBank business segment; JPX codes 9984 and 9434", "name variants are benchmark transformations"),
            "Related group companies are distinct listed legal entities.",
        ))

    # Similar-name non-matches. JPX-listed security codes are intentionally
    # different; similar display names must never override conflicting IDs.
    similar_pairs = [
        ("nec-glass", "日本電気株式会社", "6701", "日本電気硝子株式会社", "5214"),
        ("daiwa", "大和ハウス工業株式会社", "1925", "大和工業株式会社", "5444"),
        ("mitsubishi", "三菱商事株式会社", "8058", "三菱食品株式会社", "7451"),
        ("tokyo", "東京建物株式会社", "8804", "東京鐵鋼株式会社", "5445"),
    ]
    for key, left_name, left_code, right_name, right_code in similar_pairs:
        cases.append(BenchmarkCase(
            f"src-similar-{key}", "similar_name_nonmatch",
            _stock(left_name, left_code),
            _stock(right_name, right_code),
            "NON_MATCH",
            _prov("Japan Exchange Group", JPX_STOCK_SEARCH, f"listed issuer security codes {left_code} vs {right_code}", "identity fact is code-level; no relationship inference"),
            "Distinct listed issuers with superficially overlapping Japanese names.",
        ))

    # Real entities with deliberately incomplete benchmark observations. These are
    # review-only because the benchmark transformation removes strong IDs.
    incomplete = [
        ("zozo", "株式会社ZOZO", "ZOZO（株）", ZOZO_RENAME, "ZOZO"),
        ("ly", "LINEヤフー株式会社", "LINEヤフー（株）", LY_HISTORY, "LINE Yahoo"),
        ("sbg", "ソフトバンクグループ株式会社", "ソフトバンクグループ（株）", SOFTBANK_SEGMENT, "SoftBank Group"),
        ("sb", "ソフトバンク株式会社", "ソフトバンク（株）", SOFTBANK_SEGMENT, "SoftBank Group"),
        ("starttoday", "株式会社スタートトゥデイ", "スタートトゥデイ", ZOZO_RENAME, "ZOZO"),
        ("zhd", "Zホールディングス株式会社", "Zホールディングス（株）", LY_HISTORY, "LINE Yahoo"),
    ]
    for key, left_name, right_name, url, publisher in incomplete:
        cases.append(BenchmarkCase(
            f"src-incomplete-{key}", "incomplete_record",
            BenchmarkRecord(name=left_name, jurisdiction="JP"),
            BenchmarkRecord(name=right_name, jurisdiction="JP"),
            "REVIEW",
            _prov(publisher, url, "official entity/history page; identifiers deliberately omitted in benchmark transformation", "review-only transformation"),
            "Real sourced entity, but name-only benchmark observations are intentionally insufficient.",
        ))

    return cases
