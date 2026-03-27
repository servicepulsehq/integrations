from __future__ import annotations

from typing import Optional

from dagster import op

from dagster_servicepulse.resource import ServicePulseResource
from servicepulse_client import StackNotHealthyError


def build_vendor_gate_op(
    *,
    required_vendors: tuple[str, ...] = (),
    name: str = "vendor_gate",
    allow_maintenance: bool = False,
    allow_unknown: bool = False,
):
    """
    Factory for an op that fails the run if required tracked vendors are not safe to proceed.

    If ``required_vendors`` is empty, the entire tracked stack is checked (see ``assert_stack_healthy``).
    """

    @op(name=name)
    def _vendor_gate(context, servicepulse: ServicePulseResource) -> str:
        client = servicepulse.get_client()
        slugs: Optional[tuple[str, ...]] = required_vendors if required_vendors else None
        try:
            client.assert_stack_healthy(
                slugs,
                allow_maintenance=allow_maintenance,
                allow_unknown=allow_unknown,
            )
        except StackNotHealthyError as e:
            context.log.error(str(e))
            raise
        return "ok"

    return _vendor_gate
