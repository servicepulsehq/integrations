"""
Prefect example: gate a flow on ServicePulse vendor health.

Usage:
  export SERVICEPULSE_API_TOKEN="sp_..."
  python flow_example.py

With a block (see README): pass ``credentials=`` into
``assert_servicepulse_vendors_operational`` from ``vendor_gate_task.py``.
"""

from __future__ import annotations

from prefect import flow

from vendor_gate_task import assert_servicepulse_vendors_operational

REQUIRED_SLUGS = ["stripe", "snowflake"]


@flow(name="servicepulse-gated-example")
def gated_pipeline(vendor_slugs: list[str] | None = None):
    """Replace downstream with your real tasks."""
    slugs = vendor_slugs or REQUIRED_SLUGS
    assert_servicepulse_vendors_operational(slugs)
    # add more tasks after the gate


if __name__ == "__main__":
    gated_pipeline()
