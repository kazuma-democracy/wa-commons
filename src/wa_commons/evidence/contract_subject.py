from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal
import hashlib
import re

from .mod_procurement import ProcurementObservation

RULE_VERSION = "contract-subject-v0.1"
Category = Literal["MILITARY_SPECIFIC", "DUAL_USE", "CIVILIAN", "UNKNOWN"]

# Intentionally narrow. A term must describe the procured subject, not merely the
# contracting authority. Generic defence-context words are not evidence here.
MILITARY_SPECIFIC_TERMS = (
    "誘導弾", "ミサイル", "弾薬", "砲弾", "実包", "魚雷", "爆雷",
    "小銃", "機関銃", "火砲", "迫撃砲", "戦車", "装甲車", "戦闘機",
    "軍用無線", "射撃統制", "火器管制", "武器システム", "武器等",
)

DUAL_USE_TERMS = (
    "情報システム", "システム運用", "システム保守", "ソフトウェア",
    "通信", "ネットワーク", "サーバ", "サイバー", "衛星", "無人機",
    "ドローン", "燃料", "軽油", "航空燃料", "物流", "輸送", "車両",
    "自動車", "医療", "検査装置", "測定器", "カメラ", "センサ",
)

CIVILIAN_TERMS = (
    "鉛筆", "ＰＰＣ", "PPC", "コピー用紙", "トイレットペーパー",
    "文房具", "事務用品", "机", "椅子", "什器", "空調", "清掃",
    "クリーニング", "発送", "印刷", "製本", "飲料", "弁当", "食料",
    "花", "植栽", "害虫", "廃棄物", "一般廃棄物", "自動車修理",
)


def normalize_subject(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "")).upper()


def _hits(subject: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    normalized = normalize_subject(subject)
    return tuple(term for term in terms if normalize_subject(term) in normalized)


@dataclass(frozen=True)
class SubjectClassification:
    category: Category
    confidence: float
    rule_version: str
    matched_terms: tuple[str, ...]
    review_required: bool
    reasoning: str

    def to_dict(self) -> dict:
        return asdict(self)


def classify_contract_subject(subject: str) -> SubjectClassification:
    """Classify only the contract subject text using deterministic conservative rules.

    The caller must not pass the contracting authority as evidence. Conflicting
    semantic signals are routed to UNKNOWN instead of being resolved by priority.
    """
    military = _hits(subject, MILITARY_SPECIFIC_TERMS)
    dual = _hits(subject, DUAL_USE_TERMS)
    civilian = _hits(subject, CIVILIAN_TERMS)
    active = sum(bool(x) for x in (military, dual, civilian))

    if active > 1:
        return SubjectClassification(
            "UNKNOWN", 0.0, RULE_VERSION, military + dual + civilian, True,
            "Conflicting category signals in contract subject; manual review required.",
        )
    if military:
        return SubjectClassification(
            "MILITARY_SPECIFIC", 0.98, RULE_VERSION, military, False,
            "Contract subject explicitly names a narrowly military weapon/platform term.",
        )
    if civilian:
        return SubjectClassification(
            "CIVILIAN", 0.98, RULE_VERSION, civilian, False,
            "Contract subject explicitly names ordinary civilian goods/services.",
        )
    if dual:
        return SubjectClassification(
            "DUAL_USE", 0.85, RULE_VERSION, dual, False,
            "Contract subject names technology/service with substantial civilian and military uses.",
        )
    return SubjectClassification(
        "UNKNOWN", 0.0, RULE_VERSION, (), True,
        "No sufficiently specific deterministic rule matched the contract subject.",
    )


def classification_claim(observation: ProcurementObservation, classification: SubjectClassification) -> dict | None:
    """Create a narrow subject-semantics claim for an identity-resolved observation.

    The classification is not a PASS/WATCH/EXCLUDE decision and does not transform
    MILITARY_SPECIFIC into a generic weapons-activity accusation.
    """
    if observation.identity_decision != "AUTO_LINK" or not observation.entity_id:
        return None
    stable_key = hashlib.sha256((observation.observation_id + "|" + RULE_VERSION).encode("utf-8")).hexdigest()[:16]
    status = "unknown" if classification.category == "UNKNOWN" else "confirmed"
    return {
        "schema_version": "0.1",
        "claim_id": f"wc:claim:contract-subject:{stable_key}",
        "subject": {
            "entity_id": observation.entity_id,
            "entity_type": "company",
            "canonical_name": observation.supplier_name,
            "jurisdiction": "JP",
            "identifiers": [{"scheme": "corporate_number", "value": observation.corporate_number, "issuer": "National Tax Agency, Japan"}],
            "entity_resolution": {
                "method": "deterministic_identifier",
                "confidence": 1.0,
                "review_status": "not_required",
                "match_evidence": ["corporate_number", "wa-conservative-v0.2"],
            },
        },
        "claim": {
            "category": "military_contract",
            "predicate": "contract_subject_classification",
            "value": {
                "classification": classification.category.lower(),
                "contract_subject": observation.subject,
                "matched_terms": list(classification.matched_terms),
                "review_required": classification.review_required,
                "source_observation_id": observation.observation_id,
            },
            "effective_from": observation.contract_date,
            "effective_to": observation.contract_date,
        },
        "evidence": [{
            "evidence_id": f"wc:evidence:contract-subject:{stable_key}",
            "source_id": "jp-mod-procurement",
            "source_url": observation.source_url,
            "publisher": "Japan Ministry of Defense",
            "source_type": "official_contract",
            "publication_date": None,
            "evidence_date": observation.contract_date,
            "retrieved_at": observation.retrieved_at,
            "support": "context_only" if classification.category == "UNKNOWN" else "supports",
            "locator": observation.source_locator,
            "content_sha256": observation.source_sha256,
            "license_status": "review_required",
            "notes": "Classification uses contract subject text only. Contracting authority is not a classification feature and no policy decision is produced.",
        }],
        "adjudication": {
            "status": status,
            "confidence": classification.confidence,
            "reasoning_summary": classification.reasoning,
            "method": {"type": "deterministic_rule", "version": RULE_VERSION, "model": None},
            "rule_set_version": RULE_VERSION,
            "decided_at": observation.retrieved_at,
            "reviewer": None,
        },
        "policy_context": None,
        "correction_history": [],
        "provenance": {
            "created_at": observation.retrieved_at,
            "updated_at": observation.retrieved_at,
            "created_by": "wa-commons:contract-subject-classifier",
            "dataset_version": observation.snapshot_version,
        },
    }
