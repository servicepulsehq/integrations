"""
Dagster example: thin entrypoint using the dagster-servicepulse library.

Requires:
  pip install -e ../../servicepulse-client
  pip install -e ../../libraries/dagster-servicepulse
  pip install dagster dagster-webserver

Env: SERVICEPULSE_API_TOKEN (required unless you override the resource in code / run config)
"""

from dagster_servicepulse import build_servicepulse_defs

# Slugs must match vendors you track in ServicePulse. () = check entire stack.
REQUIRED_VENDORS: tuple[str, ...] = ("stripe", "snowflake")

defs = build_servicepulse_defs(required_vendors=REQUIRED_VENDORS)
