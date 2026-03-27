from __future__ import annotations

from dagster import ConfigurableResource, EnvVar
from pydantic import Field

from servicepulse_client import ServicePulseClient


class ServicePulseResource(ConfigurableResource):
    """
    ServicePulse Personal API client as a Dagster resource.

    By default ``api_token`` is read from ``SERVICEPULSE_API_TOKEN`` at launch.
    Override in code or via run config when needed.
    """

    api_token: str = Field(default=EnvVar("SERVICEPULSE_API_TOKEN"))
    base_url: str = "https://servicepulse.dev"
    timeout_s: float = 30.0

    def get_client(self) -> ServicePulseClient:
        return ServicePulseClient(
            api_token=self.api_token,
            base_url=self.base_url,
            timeout_s=self.timeout_s,
        )
