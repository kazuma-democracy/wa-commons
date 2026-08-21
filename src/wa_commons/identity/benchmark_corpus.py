from __future__ import annotations

from .benchmark import BenchmarkCase, BenchmarkRecord
from .source_verified_cases import build_source_verified_cases


def _r(i: int, name: str, *, corp: str = "", security: str = "", address: str = "東京都千代田区") -> BenchmarkRecord:
    return BenchmarkRecord(
        name=name,
        corporate_number=corp,
        security_code=security,
        jurisdiction="JP",
        address=address,
    )


def build_v01_corpus() -> list[BenchmarkCase]:
    """Deterministic 400-case synthetic Japanese ER calibration corpus."""
    cases: list[BenchmarkCase] = []

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

    for i in range(50):
        parent = f"輪ホールディングス{i:03d}"
        sub = f"輪ホールディングス{i:03d}サービス"
        cases.append(BenchmarkCase(
            f"parent-trap-{i:03d}", "parent_subsidiary_trap",
            _r(i, parent, corp=f"2{i:012d}"),
            _r(i, sub, corp=f"3{i:012d}"),
            "NON_MATCH", "synthetic_adversarial", "Parent/subsidiary identity must never collapse.",
        ))

    for i in range(50):
        name = f"共栄商事{i % 10:02d}株式会社"
        cases.append(BenchmarkCase(
            f"similar-nonmatch-{i:03d}", "similar_name_nonmatch",
            _r(i, name, address=f"北海道札幌市中央区{i+1}"),
            _r(i, name, address=f"沖縄県那覇市久茂地{i+1}"),
            "NON_MATCH", "synthetic_adversarial", "Same display name with strongly divergent address.",
        ))

    for i in range(50):
        corp = f"4{i:012d}"
        cases.append(BenchmarkCase(
            f"history-{i:03d}", "historical_rename_merger",
            _r(i, f"旧・環産業{i:03d}株式会社", corp=corp),
            _r(i, f"WA環境ソリューションズ{i:03d}株式会社", corp=corp),
            "MATCH", "synthetic_adversarial", "Name changed; legal-entity identifier remains aligned.",
        ))

    for i in range(50):
        cases.append(BenchmarkCase(
            f"incomplete-{i:03d}", "incomplete_record",
            BenchmarkRecord(name=f"未来システム{i:03d}"),
            BenchmarkRecord(name=f"未来システム{i:03d}株式会社"),
            "REVIEW", "synthetic_adversarial", "Name-only evidence is intentionally insufficient.",
        ))

    return cases


def build_m12_corpus() -> list[BenchmarkCase]:
    """M1.2 corpus: original synthetic fixtures plus source-verified Japanese cases."""
    return [*build_v01_corpus(), *build_source_verified_cases()]
