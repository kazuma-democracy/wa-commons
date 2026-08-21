from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

import run_real_identity_pilot as pilot


def gleif_rows_for_targets(targets: set[str]) -> list[dict[str, str]]:
    """Exact Japanese corporate-number -> LEI lookup using GLEIF API v1 fields."""
    out: list[dict[str, str]] = []
    for number in sorted(targets):
        query = urllib.parse.urlencode({"filter[entity.registeredAs]": number})
        req = urllib.request.Request(
            f"{pilot.GLEIF_API}?{query}",
            headers={"User-Agent": "wa-commons-m1/0.1", "Accept": "application/vnd.api+json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                payload = json.load(resp)
        except Exception as exc:
            print(f"GLEIF lookup failed for {number}: {exc}")
            continue
        matches: set[str] = set()
        for item in payload.get("data", []):
            attrs = item.get("attributes", {})
            entity = attrs.get("entity", {})
            registered_at = entity.get("registeredAt") or {}
            if entity.get("registeredAs") != number:
                continue
            if registered_at.get("id") != "RA001075":
                continue
            lei = attrs.get("lei") or item.get("id")
            if lei:
                matches.add(lei)
        if len(matches) == 1:
            out.append({
                "LEI": next(iter(matches)),
                "Entity.RegistrationAuthority.RegistrationAuthorityEntityID": number,
            })
    return out


pilot.gleif_rows_for_targets = gleif_rows_for_targets

if __name__ == "__main__":
    pilot.main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/real-identity-pilot")
