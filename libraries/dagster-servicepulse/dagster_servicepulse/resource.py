from __future__ import annotations

from typing import Any

from dagster import ConfigurableResource, EnvVar
from pydantic import Field

from servicepulse_client import ServicePulseClient
from servicepulse_client.client import PushedStatus


class ServicePulseResource(ConfigurableResource):
    """
    ServicePulse client as a Dagster resource.

    Provides two capabilities:

    **Read** — check vendor health before running jobs/ops:
        ``api_token`` (``SERVICEPULSE_API_TOKEN``) is the Personal API token
        from ServicePulse → Settings → API Tokens.

    **Write** — push your service's own health back to ServicePulse:
        ``ingest_token`` (``SERVICEPULSE_INGEST_TOKEN``) is the push endpoint
        token from ServicePulse → Settings → Push Endpoints.
        Set ``service_id`` to the ServicePulse service you want to update, or
        pass it at call time via ``push_service_status(service_id=...)``.
    """

    api_token: str = Field(default=EnvVar("SERVICEPULSE_API_TOKEN"))
    base_url: str = "https://servicepulse.dev"
    timeout_s: float = 30.0

    # Push / write credentials (optional — only needed for push_service_status)
    ingest_token: str = Field(default="")
    service_id: str = Field(default="")

    def get_client(self) -> ServicePulseClient:
        return ServicePulseClient(
            api_token=self.api_token,
            base_url=self.base_url,
            timeout_s=self.timeout_s,
        )

    def push_service_status(
        self,
        status: PushedStatus,
        *,
        service_id: str | None = None,
        ingest_token: str | None = None,
        title: str | None = None,
        message: str | None = None,
    ) -> None:
        """
        Push this service's health status to ServicePulse.

        The pushed status is combined with vendor dependency status (worst-of),
        so a degraded pipeline surfaces on the status page even when all upstream
        vendors are operational.

        Args:
            status:       ``operational`` | ``degraded_performance`` |
                          ``partial_outage`` | ``major_outage`` | ``maintenance``
            service_id:   Override the resource-level ``service_id`` for this call.
            ingest_token: Override the resource-level ``ingest_token`` for this call.
            title:        Short description shown in the app / status page.
            message:      Longer detail string.
        """
        token = (ingest_token or self.ingest_token or "").strip()
        sid = (service_id or self.service_id or "").strip()
        self.get_client().push_service_status(
            token, sid, status, title=title, message=message
        )
