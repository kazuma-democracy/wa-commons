from __future__ import annotations

import re
import unicodedata

_CORP_FORMS = (
    "株式会社", "（株）", "(株)", "有限会社", "合同会社",
    "ＣＯ．，ＬＴＤ．", "CO.,LTD.", "CO., LTD.", "CORPORATION", "CORP.",
)


def normalize_name(value: str) -> str:
    """Conservative comparison normalization; never used as sole identity proof."""
    value = unicodedata.normalize("NFKC", value).strip().upper()
    for token in _CORP_FORMS:
        value = value.replace(unicodedata.normalize("NFKC", token).upper(), "")
    value = re.sub(r"[\s\-‐‑–—・･,，.．()（）]+", "", value)
    return value


def normalize_security_code(value: object) -> str:
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(4) if text.isdigit() and len(text) <= 4 else text
