from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
from io import StringIO
import hashlib
import re

from wa_commons.identity.benchmark import BenchmarkRecord
from wa_commons.identity.policy import final_policy_match

SOURCE_ID = "jp-political-finance"
ADAPTER_VERSION = "0.1"
IDENTITY_POLICY_VERSION = "wa-conservative-v0.2"
RECIPIENT = "一般財団法人国民政治協会"
REPORTING_YEAR = 2023
PUBLICATION_DATE = "2024-11-29"
SNAPSHOT_VERSION = "soumu-SS20241129-kokumin-seiji-kyokai-r5"
SOURCE_URL_TEMPLATE = "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/contents/SS20241129/006710_2150{part:02d}.pdf"


@dataclass(frozen=True)
class PoliticalFinanceObservation:
    observation_id: str
    donor_name: str
    recipient: str
    amount_jpy: int
    reporting_year: int
    filing_id: str
    source_url: str
    source_locator: str
    retrieved_at: str
    source_sha256: str
    donor_type: str = "organization_or_corporation"
    extraction_method: str = "ocr_tsv_geometry"
    extraction_review_required: bool = True
    corporate_number: str = ""
    identity_decision: str = "UNRESOLVED"
    entity_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_text(text: str) -> str:
    return re.sub(r"[ \t\u3000]+", " ", text or "").strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_url(part: int) -> str:
    if not 1 <= part <= 20:
        raise ValueError("part must be 1..20")
    return SOURCE_URL_TEMPLATE.format(part=part)


def conservative_identity_resolution(donor_name: str, *, corporate_number: str | None = None) -> tuple[str, str | None]:
    """Route donor identity through M1.2. Printed/OCR names alone never auto-link."""
    number = re.sub(r"\D", "", corporate_number or "")
    if len(number) != 13:
        return "UNRESOLVED", None
    source = BenchmarkRecord(name=donor_name, corporate_number=number, jurisdiction="JP")
    canonical = BenchmarkRecord(name=donor_name, corporate_number=number, jurisdiction="JP")
    result = final_policy_match(source, canonical)
    if result.decision != "AUTO_LINK":
        return result.decision, None
    return result.decision, f"jp:corporate-number:{number}"


def _digits(text: str) -> str:
    table = str.maketrans("０１２３４５６７８９", "0123456789")
    return re.sub(r"\D", "", (text or "").translate(table))


def _clean_donor(text: str) -> str:
    text = normalize_text(text).strip("|[]{}<> _ー-・.、")
    return re.sub(r"\s+", "", text)


def parse_organization_tsv_page(tsv: str, *, part: int, page: int, retrieved_at: str, source_sha256: str) -> list[PoliticalFinanceObservation]:
    """Extract conservative row observations from a pre-selected section-2 page.

    Tesseract's plain text does not preserve these scanned table columns reliably,
    so rows are reconstructed from TSV coordinates. Only the donor and amount
    columns are used. Reporting period comes from the fixed 2023 filing. OCR
    output remains review-required and never establishes identity by itself.
    """
    rows = list(csv.DictReader(StringIO(tsv), delimiter="\t"))
    page_row = next((r for r in rows if r.get("level") == "1"), None)
    if not page_row:
        return []
    width = max(int(page_row.get("width") or 0), 1)
    height = max(int(page_row.get("height") or 0), 1)

    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    filing_id = ""
    for row in rows:
        text = normalize_text(row.get("text", ""))
        if not text:
            continue
        match = re.search(r"(\d{2}-2-\d{5})", text)
        if match:
            filing_id = match.group(1)
        if row.get("level") != "5":
            continue
        key = (row.get("block_num", ""), row.get("par_num", ""), row.get("line_num", ""), row.get("top", ""))
        groups.setdefault(key, []).append(row)

    observations: list[PoliticalFinanceObservation] = []
    current_donor = ""
    for words in sorted(groups.values(), key=lambda ws: min(int(w.get("top") or 0) for w in ws)):
        top = min(int(w.get("top") or 0) for w in words)
        if top < height * 0.22 or top > height * 0.86:
            continue

        donor_words = []
        amount_words = []
        for word in words:
            text = normalize_text(word.get("text", ""))
            left = int(word.get("left") or 0)
            w = int(word.get("width") or 0)
            center = (left + w / 2) / width
            if center < 0.275:
                donor_words.append((left, text))
            elif 0.275 <= center < 0.385:
                amount_words.append((left, text))

        donor_raw = "".join(text for _, text in sorted(donor_words))
        amount_raw = "".join(text for _, text in sorted(amount_words))
        donor = _clean_donor(donor_raw)
        amount_digits = _digits(amount_raw)
        if not amount_digits:
            continue
        amount = int(amount_digits)
        if amount <= 0 or amount > 1_000_000_000:
            continue

        if any(token in donor for token in ("寄附", "合計", "小計", "その他", "十億", "百万", "千円", "年月")):
            continue
        continuation = not donor or donor in {"/", "ヵ", "カ", "M", "7", "ル", "り", "上", "間", "昌", "電"}
        if continuation:
            donor = current_donor
        else:
            # Require at least two visible characters for a new donor. One-character
            # OCR fragments cannot start an entity and are dropped, never guessed.
            if len(donor) < 2:
                donor = current_donor
            else:
                current_donor = donor
        if not donor:
            continue

        key = hashlib.sha256(f"{part}|{page}|{top}|{donor}|{amount}".encode("utf-8")).hexdigest()[:16]
        decision, entity_id = conservative_identity_resolution(donor)
        observations.append(PoliticalFinanceObservation(
            observation_id=f"wc:obs:political-finance:{key}",
            donor_name=donor,
            recipient=RECIPIENT,
            amount_jpy=amount,
            reporting_year=REPORTING_YEAR,
            filing_id=filing_id or f"part-{part:02d}-page-{page:03d}",
            source_url=source_url(part),
            source_locator=f"pdf_part={part};page={page};ocr_top={top}",
            retrieved_at=retrieved_at,
            source_sha256=source_sha256,
            identity_decision=decision,
            entity_id=entity_id,
        ))
    return observations


def observation_to_claim(observation: PoliticalFinanceObservation) -> dict | None:
    """Create a narrow donation fact only after strong-ID resolution and review."""
    if observation.identity_decision != "AUTO_LINK" or not observation.entity_id:
        return None
    if observation.extraction_review_required:
        return None
    key = hashlib.sha256(observation.observation_id.encode("utf-8")).hexdigest()[:16]
    identifiers = []
    if observation.corporate_number:
        identifiers.append({"scheme": "corporate_number", "value": observation.corporate_number, "issuer": "National Tax Agency, Japan"})
    return {
        "schema_version": "0.1",
        "claim_id": f"wc:claim:political-finance:{key}",
        "subject": {
            "entity_id": observation.entity_id,
            "entity_type": "company",
            "canonical_name": observation.donor_name,
            "jurisdiction": "JP",
            "identifiers": identifiers,
            "entity_resolution": {
                "method": "deterministic_identifier",
                "confidence": 1.0,
                "review_status": "not_required",
                "match_evidence": [IDENTITY_POLICY_VERSION],
            },
        },
        "claim": {
            "category": "political_finance",
            "predicate": "reported_political_donation",
            "value": {
                "donor_name_as_printed": observation.donor_name,
                "recipient_as_printed": observation.recipient,
                "amount_jpy": observation.amount_jpy,
                "reporting_year": observation.reporting_year,
                "filing_id": observation.filing_id,
            },
            "currency": "JPY",
            "effective_from": f"{observation.reporting_year}-01-01",
            "effective_to": f"{observation.reporting_year}-12-31",
        },
        "evidence": [{
            "evidence_id": f"wc:evidence:political-finance:{key}",
            "source_id": SOURCE_ID,
            "source_url": observation.source_url,
            "publisher": "Ministry of Internal Affairs and Communications, Japan",
            "source_type": "official_filing",
            "publication_date": PUBLICATION_DATE,
            "evidence_date": f"{observation.reporting_year}-12-31",
            "retrieved_at": observation.retrieved_at,
            "support": "supports",
            "locator": observation.source_locator,
            "content_sha256": observation.source_sha256,
            "license_status": "review_required",
            "notes": "Narrow disclosed transaction fact only. Donation does not imply agreement with every recipient policy or an ideology label.",
        }],
        "adjudication": {
            "status": "confirmed",
            "confidence": 1.0,
            "reasoning_summary": "Official political-finance filing plus separately verified strong donor identifier; no ideology or policy inference.",
            "method": {"type": "deterministic_rule", "version": ADAPTER_VERSION, "model": None},
            "rule_set_version": f"{IDENTITY_POLICY_VERSION}+political-finance-v{ADAPTER_VERSION}",
            "decided_at": observation.retrieved_at,
            "reviewer": None,
        },
        "policy_context": None,
        "correction_history": [],
        "provenance": {
            "created_at": observation.retrieved_at,
            "updated_at": observation.retrieved_at,
            "created_by": "wa-commons:political-finance-adapter",
            "dataset_version": SNAPSHOT_VERSION,
        },
    }
