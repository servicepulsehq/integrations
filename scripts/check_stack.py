#!/usr/bin/env python3
"""Fail if tracked vendors are unsafe — stdlib only (CI runners: GitHub, GitLab, Azure, etc.)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

_DEFAULT_BAD = frozenset(
    {
        "degraded_performance",
        "partial_outage",
        "major_outage",
        "maintenance",
    }
)


def main() -> None:
    token = os.environ.get("SERVICEPULSE_TOKEN", "").strip()
    if not token:
        print("SERVICEPULSE_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    base = os.environ.get("SERVICEPULSE_BASE_URL", "https://servicepulse.dev").rstrip("/")
    slugs_raw = os.environ.get("SERVICEPULSE_VENDOR_SLUGS", "").strip()
    allow_maint = os.environ.get("SERVICEPULSE_ALLOW_MAINTENANCE", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    allow_unknown = os.environ.get("SERVICEPULSE_ALLOW_UNKNOWN", "false").lower() in (
        "1",
        "true",
        "yes",
    )

    bad = set(_DEFAULT_BAD)
    if allow_maint:
        bad.discard("maintenance")

    req = urllib.request.Request(
        f"{base}/api/v1/tracked-vendors",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        print(f"ServicePulse HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ServicePulse request failed: {e}", file=sys.stderr)
        sys.exit(1)

    rows: list = data.get("vendors") or []
    by_slug: dict[str, dict] = {}
    for row in rows:
        v = row.get("vendor") or {}
        slug = (v.get("slug") or "").strip().lower()
        if slug:
            by_slug[slug] = v

    if slugs_raw:
        slugs_to_check = [s.strip().lower() for s in slugs_raw.split(",") if s.strip()]
    else:
        slugs_to_check = sorted(by_slug.keys())

    unhealthy: list[tuple[str, str]] = []
    missing: list[str] = []
    for slug in slugs_to_check:
        if slug not in by_slug:
            missing.append(slug)
            continue
        v = by_slug[slug]
        status = (v.get("currentStatus") or "").strip() or "unknown"
        if status == "unknown" and not allow_unknown:
            unhealthy.append((slug, status))
            continue
        if status in bad:
            unhealthy.append((slug, status))

    if unhealthy or missing:
        parts: list[str] = []
        if unhealthy:
            parts.append("Unhealthy: " + ", ".join(f"{s}={st}" for s, st in unhealthy))
        if missing:
            parts.append("Not on your tracked stack: " + ", ".join(sorted(set(missing))))
        print("\n".join(parts), file=sys.stderr)
        sys.exit(1)

    print(f"ServicePulse OK — checked {len(slugs_to_check)} vendor(s).")


if __name__ == "__main__":
    main()
