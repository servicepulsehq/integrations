"""
Prefect 2.x block for ServicePulse Personal API credentials.
"""

from __future__ import annotations

try:
    from prefect.blocks.core import Block
    from pydantic import Field, SecretStr
except ImportError as e:  # pragma: no cover
    raise ImportError("Install prefect>=2 and pydantic") from e


class ServicePulseCredentials(Block):
    """
    Store `sp_…` token and API base URL for flows that gate on vendor health.
    """

    _block_type_name = "ServicePulse Credentials"

    api_token: SecretStr = Field(..., description="Personal API token (sp_…)")
    base_url: str = Field(default="https://servicepulse.dev", description="ServicePulse deployment URL")
    timeout_s: float = Field(default=30.0, description="HTTP client timeout in seconds")

    def get_client(self):
        from servicepulse_client import ServicePulseClient

        return ServicePulseClient(
            api_token=self.api_token.get_secret_value(),
            base_url=self.base_url,
            timeout_s=self.timeout_s,
        )
