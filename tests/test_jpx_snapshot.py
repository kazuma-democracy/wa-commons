from pathlib import Path

from wa_commons.identity.jpx_snapshot import build_pilot, domestic_company_rows, read_jpx_rows


def _write_fixture(path: Path) -> None:
    lines = ["日付,コード,銘柄名,市場・商品区分,33業種コード,33業種区分,17業種コード,17業種区分,規模コード,規模区分"]
    # Mixed non-company rows that must be ignored.
    lines.append("20260430,1305,TEST ETF,ETF・ETN,-,-,-,-,-,-")
    lines.append("20260430,131A,TEST PRO,PRO Market,5250,情報・通信業,10,情報通信・サービスその他,-,-")
    for i in range(1, 106):
        code = 2000 + i
        market = "プライム（内国株式）" if i % 2 else "スタンダード（内国株式）"
        lines.append(f"20260430,{code},テスト企業{i},{market},2050,建設業,3,建設・資材,-,-")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def test_domestic_filter_excludes_etf_and_pro_market(tmp_path):
    fixture = tmp_path / "data_j.csv"
    _write_fixture(fixture)
    rows = domestic_company_rows(read_jpx_rows(fixture))
    assert len(rows) == 105
    assert all("内国株式" in row["市場・商品区分"] for row in rows)


def test_build_pilot_is_deterministic_and_limited_to_100(tmp_path):
    fixture = tmp_path / "data_j.csv"
    _write_fixture(fixture)
    kwargs = dict(
        snapshot="2026-04-30",
        source_url="https://www.jpx.co.jp/example/data_j.xls",
        retrieved_at="2026-08-21T00:00:00Z",
        limit=100,
    )
    one = build_pilot(fixture, **kwargs)
    two = build_pilot(fixture, **kwargs)
    assert one == two
    assert one["manifest"]["entity_count"] == 100
    assert len(one["manifest"]["source_sha256"]) == 64
    assert one["entities"][0]["entity_id"] == "wa:org:jp:tse:2001"
    assert one["entities"][-1]["entity_id"] == "wa:org:jp:tse:2100"
