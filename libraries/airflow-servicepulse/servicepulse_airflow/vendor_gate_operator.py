"""
ServicePulse vendor health gate operator for Airflow 2.x.
"""

from __future__ import annotations

from typing import Optional, Sequence

from airflow.models import BaseOperator
from airflow.utils.context import Context

from servicepulse_client import ServicePulseClient, StackNotHealthyError


class ServicePulseVendorGateOperator(BaseOperator):
    """
    Fail the task if ServicePulse reports non-operational status for tracked vendors.

    :param vendor_slugs: If set, only these vendor slugs are checked; must be on your stack.
    :param allow_maintenance: If True, maintenance is not treated as blocking.
    :param allow_unknown: If True, unknown status does not block (default False).
    :param servicepulse_conn_id: If set, load token and optional base_url from this Airflow
        Connection (password = token, or extra ``api_token``; extra ``base_url`` overrides host).
    :param timeout_s: HTTP timeout passed to ``ServicePulseClient``.
    """

    def __init__(
        self,
        *,
        vendor_slugs: Sequence[str] | None = None,
        allow_maintenance: bool = False,
        allow_unknown: bool = False,
        base_url: str = "https://servicepulse.dev",
        servicepulse_conn_id: Optional[str] = None,
        timeout_s: float = 30.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.vendor_slugs = list(vendor_slugs) if vendor_slugs else None
        self.allow_maintenance = allow_maintenance
        self.allow_unknown = allow_unknown
        self.base_url = base_url
        self.servicepulse_conn_id = servicepulse_conn_id
        self.timeout_s = timeout_s

    def execute(self, context: Context) -> str:
        import os

        from airflow.hooks.base import BaseHook
        from airflow.models import Variable

        if self.servicepulse_conn_id:
            conn = BaseHook.get_connection(self.servicepulse_conn_id)
            extra = conn.extra_dejson or {}
            token = (conn.password or extra.get("api_token") or "").strip()
            if not token:
                raise RuntimeError(
                    f"Airflow connection {self.servicepulse_conn_id!r}: set Connection password "
                    "or extra key api_token to your Personal API token (sp_…)"
                )
            base = (extra.get("base_url") or conn.host or self.base_url or "").strip()
            if base and not base.startswith(("http://", "https://")):
                base = f"https://{base}"
            if not base:
                base = self.base_url
        else:
            token = os.environ.get("SERVICEPULSE_API_TOKEN") or Variable.get(
                "SERVICEPULSE_API_TOKEN", default_var=""
            )
            if not (token or "").strip():
                raise RuntimeError(
                    "Set SERVICEPULSE_API_TOKEN (env or Airflow Variable), or pass servicepulse_conn_id="
                )

            base = (
                os.environ.get("SERVICEPULSE_BASE_URL")
                or Variable.get("SERVICEPULSE_BASE_URL", default_var=self.base_url)
            ).strip()

        client = ServicePulseClient(api_token=token.strip(), base_url=base, timeout_s=self.timeout_s)
        try:
            client.assert_stack_healthy(
                self.vendor_slugs,
                allow_maintenance=self.allow_maintenance,
                allow_unknown=self.allow_unknown,
            )
        except StackNotHealthyError as e:
            self.log.error(str(e))
            raise
        return "vendors_ok"
