"""
Dagster example: push your pipeline's own health back to ServicePulse.

This is separate from checking *upstream vendor* health (see definitions.py).
Use this pattern when your own ETL job, ML pipeline, or data product may be
degraded even when all upstream vendors are operational.

The pushed status is combined with vendor dependency status via worst-of
semantics — a degraded pipeline surfaces on your status page even if Stripe
and Snowflake are both green.

Requires:
  pip install -e ../../servicepulse-client
  pip install -e ../../libraries/dagster-servicepulse
  pip install dagster dagster-webserver

Environment variables:
  SERVICEPULSE_API_TOKEN    — Personal API token (Settings → API Tokens)
  SERVICEPULSE_INGEST_TOKEN — Push endpoint token (Settings → Push Endpoints)
  SERVICEPULSE_SERVICE_ID   — The service ID to update (My Services → copy ID)
"""

from __future__ import annotations

import os

from dagster import (
    Definitions,
    EnvVar,
    HookContext,
    failure_hook,
    job,
    op,
    success_hook,
)
from dagster_servicepulse import ServicePulseResource

# ---------------------------------------------------------------------------
# Hooks — run after every op in jobs that opt in
# ---------------------------------------------------------------------------

@success_hook(required_resource_keys={"servicepulse"})
def mark_operational(context: HookContext) -> None:
    """Reset service to operational after a successful run."""
    context.resources.servicepulse.push_service_status(
        "operational",
        title="ETL pipeline healthy",
    )


@failure_hook(required_resource_keys={"servicepulse"})
def mark_degraded(context: HookContext) -> None:
    """Mark service as degraded when a job fails."""
    exc = context.op_exception
    context.resources.servicepulse.push_service_status(
        "degraded_performance",
        title=f"ETL pipeline failed: {context.op.name}",
        message=str(exc) if exc else None,
    )


# ---------------------------------------------------------------------------
# Example job — hooks are attached at the job level
# ---------------------------------------------------------------------------

@op
def extract() -> list[dict]:
    # Replace with your real extraction logic
    return [{"id": 1, "value": 42}]


@op
def transform(rows: list[dict]) -> list[dict]:
    # Replace with your real transformation logic
    return [{"id": r["id"], "value": r["value"] * 2} for r in rows]


@op
def load(rows: list[dict]) -> None:
    # Replace with your real load logic
    print(f"Loaded {len(rows)} rows")


@job(hooks={mark_operational, mark_degraded})
def nightly_etl() -> None:
    """
    Nightly ETL job that pushes its health status back to ServicePulse.

    On success: service is set to `operational`.
    On failure: service is set to `degraded_performance`.
    """
    load(transform(extract()))


# ---------------------------------------------------------------------------
# Definitions
# ---------------------------------------------------------------------------

defs = Definitions(
    resources={
        "servicepulse": ServicePulseResource(
            api_token=EnvVar("SERVICEPULSE_API_TOKEN"),
            ingest_token=EnvVar("SERVICEPULSE_INGEST_TOKEN"),
            service_id=os.environ.get("SERVICEPULSE_SERVICE_ID", ""),
        )
    },
    jobs=[nightly_etl],
)
