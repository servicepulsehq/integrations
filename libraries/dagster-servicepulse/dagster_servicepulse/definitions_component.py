"""
YAML-configurable Dagster Component for ServicePulse (vendor gate job + optional transition sensor).

Fits the same pattern as community templates such as
https://github.com/eric-thomas-dagster/dagster-component-templates — declare in ``defs.yaml`` with
``type: dagster_servicepulse.ServicePulseDefinitionsComponent``.
"""

from __future__ import annotations

from dagster import Component, ComponentLoadContext, Definitions, EnvVar, Model, Resolvable
from pydantic import Field

from dagster_servicepulse.build_defs import build_servicepulse_defs
from dagster_servicepulse.resource import ServicePulseResource


class ServicePulseDefinitionsComponent(Component, Model, Resolvable):
    """
    Bundle a ``ServicePulseResource``, a vendor gate job, and optionally a transition sensor.

    Configure vendor slugs, API token env var, and sensor behavior from YAML attributes.
    """

    required_vendors: list[str] = Field(
        default_factory=list,
        description="Slugs to gate on; leave empty to require the full tracked stack to be healthy.",
    )
    api_token_env_var: str = Field(
        default="SERVICEPULSE_API_TOKEN",
        description="Environment variable name holding the Personal API token (sp_…).",
    )
    base_url: str = Field(
        default="https://servicepulse.dev",
        description="ServicePulse API base URL.",
    )
    timeout_s: float = Field(default=30.0, description="HTTP client timeout in seconds.")
    include_transition_sensor: bool = Field(
        default=True,
        description="If true, poll for operational → non-operational transitions and request runs.",
    )
    transition_sensor_name: str = Field(
        default="vendor_operational_sensor",
        description="Dagster sensor definition name.",
    )
    sensor_minimum_interval_seconds: int = Field(
        default=180,
        description="Minimum seconds between sensor evaluations.",
    )
    allow_maintenance: bool = Field(
        default=False,
        description="If true, maintenance status does not fail the gate.",
    )
    allow_unknown: bool = Field(
        default=False,
        description="If true, unknown vendor status does not fail the gate.",
    )

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        normalized = tuple(
            s.strip().lower() for s in self.required_vendors if (s or "").strip()
        )
        resource = ServicePulseResource(
            api_token=EnvVar(self.api_token_env_var),
            base_url=self.base_url,
            timeout_s=self.timeout_s,
        )
        return build_servicepulse_defs(
            required_vendors=normalized,
            sensor_minimum_interval_seconds=self.sensor_minimum_interval_seconds,
            include_sensor=self.include_transition_sensor,
            transition_sensor_name=self.transition_sensor_name,
            resource=resource,
            allow_maintenance=self.allow_maintenance,
            allow_unknown=self.allow_unknown,
        )
