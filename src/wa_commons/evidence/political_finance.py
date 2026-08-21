from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import re
from typing import Iterable

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
    """M1 political-finance identity gate.

    Filings normally print names/addresses, not strong identifiers. Name similarity
    alone must never AUTO_LINK. A caller may supply a separately verified Japanese
    corporate number; only then can M1 create a deterministic entity key.
    """
    number = re.sub(r"\D", "", corporate_number or "")
    if len(number) == 13:
        return "AUTO_LINK", f"jp:corporate-number:{number}"
    return "UNRESOLVED", None


def observation_to_claim(observation: PoliticalFinanceObservation) -> dict | None:
    """Create a narrow donation fact only after strong-ID resolution.

    A donation never implies endorsement of a recipient ideology or every policy,
    and this adapter never creates PASS/WATCH/EXCLUDE.
    """
    if observation.identity_decision != "AUTO_LINK" or not observation.entity_id:
        return None
    key = hashlib.sha256(observation.observation_id.encode("utf-8")).hexdigest()[:16]
    return {
        "schema_version": "0.1",
        "claim_id": f"wc:claim:political-finance:{key}",
        "subject": {
            "entity_id": observation.entity_id,
            "entity_type": "company",
            "canonical_name": observation.donor_name,
            "jurisdiction": "JP",
            "identifiers": [],
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


def reject_personal_record(name: str) -> bool:
    """M1 minimization helper: only explicit corporate/organizational rows belong here.

    The extraction runner must positively identify the filing section as
    法人その他の団体; names alone are never used to infer donor type.
    """
    return not bool(normalize_text(name))
