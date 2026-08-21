from __future__ import annotations

from .benchmark import BenchmarkCase, BenchmarkRecord


def _r(i: int, name: str, *, corp: str = "", security: str = "", address: str = "東京都千代田区") -> BenchmarkRecord:
    return BenchmarkRecord(
        name=name,
        corporate_number=corp,
        security_code=security,
        jurisdiction="JP",
        address=address,
    )


def build_v01_corpus() -> list[BenchmarkCase]:
    """Deterministic 400-case Japanese ER calibration corpus.

    v0.1 deliberately separates sourced identity facts from synthetic adversarial
    transformations. The generated cases are for matcher calibration and safety
    regression; they must not be published as claims about real companies.
    """
    cases: list[BenchmarkCase] = []

    # 100 easy exact identifier matches.
    for i in range(100):
        corp = f"1{i:012d}"
        sec = f"{1301 + i:04d}"
        name = f"和コモンズ検証企業{i:03d}株式会社"
        cases.append(BenchmarkCase(
            f"exact-{i:03d}", "easy_exact",
            _r(i, name, corp=corp, security=sec),
            _r(i, name.replace("株式会社", "（株）"), corp=corp, security=sec),
            "MATCH", "synthetic_adversarial", "Exact identifiers; legal-form variation only.",
        ))

    # 100 alias/transliteration-ish cases without strong IDs: similar Japanese
    # aliases + stable address. These exercise non-identifier review thresholds.
    for i in range(100):
        base = f"平和技研{i:03d}"
        address = f"東京都港区芝{i % 20 + 1}丁目"
        left_name = f"株式会社{base}"
        right_name = f"{base}（株）"
        cases.append(BenchmarkCase(
            f"alias-{i:03d}", "alias_transliteration",
            _r(i, left_name, address=address),
            _r(i, right_name, address=address),
            "MATCH", "synthetic_adversarial", "Name variant plus independently aligned address.",
        ))

    # 50 parent/subsidiary traps: deliberately similar names but conflicting IDs.
    for i in range(50):
        parent = f"輪ホールディングス{i:03d}"
        sub = f"輪ホールディングス{i:03d}サービス"
        cases.append(BenchmarkCase(
            f"parent-trap-{i:03d}", "parent_subsidiary_trap",
            _r(i, parent, corp=f"2{i:012d}"),
            _r(i, sub, corp=f"3{i:012d}"),
            "NON_MATCH", "synthetic_adversarial", "Parent/subsidiary identity must never collapse.",
        ))

    # 50 same/similar-name non-matches in different locations.
    for i in range(50):
        name = f"共栄商事{i % 10:02d}株式会社"
        cases.append(BenchmarkCase(
            f"similar-nonmatch-{i:03d}", "similar_name_nonmatch",
            _r(i, name, address=f"北海道札幌市中央区{i+1}"),
            _r(i, name, address=f"沖縄県那覇市久茂地{i+1}"),
            "NON_MATCH", "synthetic_adversarial", "Same display name with strongly divergent address.",
        ))

    # 50 rename/merger-shaped cases: strong ID continuity overrides changed name.
    for i in range(50):
        corp = f"4{i:012d}"
        cases.append(BenchmarkCase(
            f"history-{i:03d}", "historical_rename_merger",
            _r(i, f"旧・環産業{i:03d}株式会社", corp=corp),
            _r(i, f"WA環境ソリューションズ{i:03d}株式会社", corp=corp),
            "MATCH", "synthetic_adversarial", "Name changed; legal-entity identifier remains aligned.",
        ))

    # 50 deliberately incomplete records: insufficient for consequential auto-link.
    for i in range(50):
        cases.append(BenchmarkCase(
            f"incomplete-{i:03d}", "incomplete_record",
            BenchmarkRecord(name=f"未来システム{i:03d}"),
            BenchmarkRecord(name=f"未来システム{i:03d}株式会社"),
            "REVIEW", "synthetic_adversarial", "Name-only evidence is intentionally insufficient.",
        ))

    return cases
