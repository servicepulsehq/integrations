from __future__ import annotations

from dagster import Definitions, job

from dagster_servicepulse.ops import build_vendor_gate_op
from dagster_servicepulse.resource import ServicePulseResource
from dagster_servicepulse.sensors import build_vendor_transition_sensor


def build_servicepulse_defs(
    *,
    required_vendors: tuple[str, ...] = ("stripe", "snowflake"),
    sensor_minimum_interval_seconds: int = 180,
    include_sensor: bool = True,
    transition_sensor_name: str = "vendor_operational_sensor",
    resource: ServicePulseResource | None = None,
    allow_maintenance: bool = False,
    allow_unknown: bool = False,
) -> Definitions:
    """
    Opinionated ``Definitions`` bundle: resource, vendor gate job, and optional transition sensor.

    Pass ``required_vendors=()`` to evaluate the full tracked stack in the gate (and all vendors
    in the sensor when ``include_sensor`` is true).
    """
    sp_resource = resource or ServicePulseResource()
    gate_op = build_vendor_gate_op(
        required_vendors=required_vendors,
        allow_maintenance=allow_maintenance,
        allow_unknown=allow_unknown,
    )

    @job
    def pipeline_with_vendor_gate():
        gate_op()

    resources = {"servicepulse": sp_resource}
    sensors = []
    if include_sensor:
        sensors.append(
            build_vendor_transition_sensor(
                job=pipeline_with_vendor_gate,
                required_vendors=required_vendors,
                name=transition_sensor_name,
                minimum_interval_seconds=sensor_minimum_interval_seconds,
            )
        )

    return Definitions(
        resources=resources,
        jobs=[pipeline_with_vendor_gate],
        sensors=sensors,
    )
