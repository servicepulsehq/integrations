from __future__ import annotations

import json

from dagster import JobDefinition, RunRequest, SensorEvaluationContext, SensorResult, sensor

from dagster_servicepulse.resource import ServicePulseResource


def build_vendor_transition_sensor(
    *,
    job: JobDefinition,
    required_vendors: tuple[str, ...],
    name: str = "vendor_operational_sensor",
    minimum_interval_seconds: int = 180,
):
    """
    Poll tracked vendors and request a run when any *required* vendor leaves ``operational``.

    Cursor stores the last known status map (JSON). Health is always read from the API on
    each tick; the cursor is only for deduplicating transitions, not as a source of truth.
    """

    @sensor(
        job=job,
        name=name,
        minimum_interval_seconds=minimum_interval_seconds,
        required_resource_keys={"servicepulse"},
    )
    def _sensor(context: SensorEvaluationContext) -> SensorResult:
        sp_resource: ServicePulseResource = context.resources.servicepulse  # type: ignore[assignment]
        sp = sp_resource.get_client()

        prev: dict[str, str] = {}
        if context.cursor:
            try:
                prev = json.loads(context.cursor)
            except json.JSONDecodeError:
                prev = {}

        data = sp.get_tracked_vendors()
        now: dict[str, str] = {}
        for row in data.get("vendors") or []:
            v = row.get("vendor") or {}
            slug = (v.get("slug") or "").strip().lower()
            if not slug:
                continue
            if required_vendors and slug not in required_vendors:
                continue
            now[slug] = (v.get("currentStatus") or "unknown").strip() or "unknown"

        transitioned_slug: str | None = None
        transitioned_st: str | None = None
        for slug, st in now.items():
            old = prev.get(slug)
            if old == "operational" and st != "operational":
                transitioned_slug = slug
                transitioned_st = st
                break

        new_cursor = json.dumps(now)
        if transitioned_slug is not None:
            return SensorResult(
                run_requests=[
                    RunRequest(run_key=f"vendor-transition-{transitioned_slug}-{transitioned_st}"),
                ],
                cursor=new_cursor,
            )
        return SensorResult(skip_reason="No vendor health transition", cursor=new_cursor)

    return _sensor
