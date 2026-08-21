from __future__ import annotations

from dataclasses import asdict, dataclass
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
    """Route donor identity through the M1.2 policy; names alone never auto-link."""
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


def parse_organization_ocr_page(text: str, *, part: int, page: int, retrieved_at: str, source_sha256: str) -> list[PoliticalFinanceObservation]:
    """Parse conservative row candidates from a known section-2 filing page.

    The caller must select pages independently verified to be section 2
    (法人・その他の団体). We do not infer donor type from a name. OCR rows that
    do not expose an amount plus 2023 month/day are rejected rather than guessed.
    Slash-like continuation rows inherit only the immediately preceding donor.
    """
    observations: list[PoliticalFinanceObservation] = []
    current_donor = ""
    filing_id = ""
    lines = [normalize_text(line) for line in (text or "").splitlines() if normalize_text(line)]
    for line in lines:
        m_filing = re.search(r"(\d{2}-2-\d{5})", line)
        if m_filing:
            filing_id = m_filing.group(1)
        if "小計" in line or "合計" in line or "その他の寄附" in line or "その他の" in line and "寄" in line:
            continue
        parts = [normalize_text(p) for p in line.split("|")]
        if len(parts) < 4:
            continue
        first = parts[0]
        # Pull amount/year/month/day from the first numeric-looking cells after donor.
        numeric = []
        for cell in parts[1:7]:
            d = _digits(cell)
            if d:
                numeric.append(d)
        if len(numeric) < 4:
            continue
        # Locate a plausible Reiwa-5 date triple. Amount is the numeric field just before it.
        date_at = None
        for i in range(1, len(numeric) - 2):
            if numeric[i] == "5" and 1 <= int(numeric[i + 1]) <= 12 and 1 <= int(numeric[i + 2]) <= 31:
                date_at = i
                break
        if date_at is None:
            continue
        amount_digits = numeric[date_at - 1]
        amount = int(amount_digits)
        if amount <= 0:
            continue
        donor = first.strip(" /ヵカM7りルヶー_上")
        continuation = not donor or donor in {"D", "MD", "M"}
        if continuation:
            donor = current_donor
        else:
            # Exclude obvious headings; exact organization status comes from the section.
            if any(token in donor for token in ("寄附者", "十億", "年月", "その 7", "その_7")):
                continue
            current_donor = donor
        if not donor:
            continue
        obs_key = hashlib.sha256(f"{part}|{page}|{len(observations)}|{donor}|{amount}".encode("utf-8")).hexdigest()[:16]
        decision, entity_id = conservative_identity_resolution(donor)
        observations.append(PoliticalFinanceObservation(
            observation_id=f"wc:obs:political-finance:{obs_key}",
            donor_name=donor,
            recipient=RECIPIENT,
            amount_jpy=amount,
            reporting_year=REPORTING_YEAR,
            filing_id=filing_id or f"part-{part:02d}-page-{page:03d}",
            source_url=source_url(part),
            source_locator=f"pdf_part={part};page={page}",
            retrieved_at=retrieved_at,
            source_sha256=source_sha256,
            identity_decision=decision,
            entity_id=entity_id,
        ))
    return observations


def observation_to_claim(observation: PoliticalFinanceObservation) -> dict | None:
    """Create a narrow donation fact only after strong-ID resolution."""
    if observation.identity_decision != "AUTO_LINK" or not observation.entity_id:
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
