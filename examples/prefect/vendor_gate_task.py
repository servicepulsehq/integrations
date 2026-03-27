"""
Reusable Prefect task: fail if ServicePulse reports blocking vendor status.

Use with env vars or a ``ServicePulseCredentials`` block (see ``flow_example.py``).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from prefect import get_run_logger, task

if TYPE_CHECKING:
    from servicepulse_block import ServicePulseCredentials


@task
def assert_servicepulse_vendors_operational(
    vendor_slugs: list[str] | None = None,
    *,
    credentials: ServicePulseCredentials | None = None,
    allow_maintenance: bool = False,
    allow_unknown: bool = False,
) -> str:
    """Call ``assert_stack_healthy``; raises if the stack is not safe to proceed."""
    from servicepulse_client import ServicePulseClient, StackNotHealthyError

    logger = get_run_logger()
    if credentials is not None:
        client = credentials.get_client()
    else:
        token = os.environ.get("SERVICEPULSE_API_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "Set SERVICEPULSE_API_TOKEN or pass credentials=ServicePulseCredentials.load(...)"
            )
        base = os.environ.get("SERVICEPULSE_BASE_URL", "https://servicepulse.dev").strip()
        timeout_s = float(os.environ.get("SERVICEPULSE_TIMEOUT_S", "30"))
        client = ServicePulseClient(api_token=token, base_url=base, timeout_s=timeout_s)

    try:
        client.assert_stack_healthy(
            vendor_slugs,
            allow_maintenance=allow_maintenance,
            allow_unknown=allow_unknown,
        )
    except StackNotHealthyError as e:
        logger.error(str(e))
        raise
    return "ok"
