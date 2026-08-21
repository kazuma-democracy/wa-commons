from wa_commons.identity.benchmark import BenchmarkRecord
from wa_commons.identity.benchmark_corpus import build_m12_corpus

from scripts.export_yente_benchmark import to_ftm


def test_m12_corpus_exports_420_company_candidates():
    cases = build_m12_corpus()
    assert len(cases) == 420
    entities = [to_ftm(case.case_id, case.right) for case in cases]
    assert len({entity["id"] for entity in entities}) == 420
    assert all(entity["schema"] == "Company" for entity in entities)
    assert all(entity["properties"]["name"] for entity in entities)


def test_strong_ids_are_namespaced_in_registration_number():
    record = BenchmarkRecord(
        name="検証株式会社",
        corporate_number="1234567890123",
        lei="ABCDEF12345678901234",
        edinet_code="E01234",
        security_code="7203",
        jurisdiction="JP",
    )
    entity = to_ftm("example", record)
    assert entity["properties"]["registrationNumber"] == [
        "CORP:1234567890123",
        "LEI:ABCDEF12345678901234",
        "EDINET:E01234",
        "JPX:7203",
    ]


def test_incomplete_record_does_not_gain_identifiers_during_export():
    entity = to_ftm("incomplete", BenchmarkRecord(name="名称のみ株式会社", jurisdiction="JP"))
    assert "registrationNumber" not in entity["properties"]
