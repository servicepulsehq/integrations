from __future__ import annotations

from typing import Any, Iterable, Sequence

import httpx

DEFAULT_BASE_URL = "https://servicepulse.dev"

# Aligned with ServicePulse VendorStatus; only clearly healthy for pipelines.
_DEFAULT_BAD: frozenset[str] = frozenset(
    {
        "degraded_performance",
        "partial_outage",
        "major_outage",
        "maintenance",
    }
)


class ServicePulseError(Exception):
    """HTTP or API errors from ServicePulse."""


class StackNotHealthyError(ServicePulseError):
    """Raised when assert_stack_healthy finds a blocking vendor status."""

    def __init__(self, message: str, *, unhealthy: list[dict[str, Any]], missing_slugs: list[str]):
        super().__init__(message)
        self.unhealthy = unhealthy
        self.missing_slugs = missing_slugs


class ServicePulseClient:
    """Personal API client (Bearer sp_…)."""

    def __init__(self, api_token: str, base_url: str = DEFAULT_BASE_URL, timeout_s: float = 30.0):
        token = (api_token or "").strip()
        if not token:
            raise ValueError("api_token is required")
        self._base = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}
        self._timeout = timeout_s

    def get_tracked_vendors(self) -> dict[str, Any]:
        url = f"{self._base}/api/v1/tracked-vendors"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.get(url, headers=self._headers)
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ServicePulseError(
                f"ServicePulse API error {e.response.status_code}: {e.response.text[:500]}"
            ) from e
        except httpx.RequestError as e:
            raise ServicePulseError(f"ServicePulse request failed: {e}") from e
        return r.json()

    def assert_stack_healthy(
        self,
        vendor_slugs: Sequence[str] | None = None,
        *,
        allow_maintenance: bool = False,
        allow_unknown: bool = False,
        extra_bad_statuses: Iterable[str] | None = None,
    ) -> None:
        """
        Raise StackNotHealthyError if any selected vendor is not safe to proceed.

        - vendor_slugs: if set, only these slugs are checked; each must exist on your stack.
        - allow_maintenance: if True, maintenance is not treated as blocking.
        - allow_unknown: if False, unknown status blocks (conservative for pipelines).
        """
        bad = set(_DEFAULT_BAD)
        if allow_maintenance:
            bad.discard("maintenance")
        if extra_bad_statuses:
            bad.update(extra_bad_statuses)

        data = self.get_tracked_vendors()
        rows: list[dict[str, Any]] = data.get("vendors") or []

        by_slug: dict[str, dict[str, Any]] = {}
        for row in rows:
            v = row.get("vendor") or {}
            slug = (v.get("slug") or "").strip().lower()
            if slug:
                by_slug[slug] = v

        if vendor_slugs is not None:
            slugs_to_check = [s.strip().lower() for s in vendor_slugs if s.strip()]
        else:
            slugs_to_check = sorted(by_slug.keys())

        unhealthy: list[dict[str, Any]] = []
        missing_slugs: list[str] = []

        for slug in slugs_to_check:
            if slug not in by_slug:
                missing_slugs.append(slug)
                continue
            v = by_slug[slug]
            status = (v.get("currentStatus") or "").strip() or "unknown"
            if status == "unknown" and not allow_unknown:
                unhealthy.append({"slug": slug, "name": v.get("name"), "currentStatus": status})
                continue
            if status in bad:
                unhealthy.append({"slug": slug, "name": v.get("name"), "currentStatus": status})

        parts: list[str] = []
        if unhealthy:
            detail = ", ".join(f"{u['slug']}={u['currentStatus']}" for u in unhealthy)
            parts.append(f"Unhealthy vendors: {detail}")
        if missing_slugs:
            parts.append(f"Slugs not in tracked stack: {', '.join(sorted(set(missing_slugs)))}")

        if parts:
            raise StackNotHealthyError(
                "; ".join(parts),
                unhealthy=unhealthy,
                missing_slugs=sorted(set(missing_slugs)),
            )
