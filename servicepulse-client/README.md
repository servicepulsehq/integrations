# servicepulse-client

Minimal Python client for the ServicePulse **Personal API** (`Authorization: Bearer sp_…`).

## Install

**From GitHub** (installs the client only; no need to clone the repo):

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=servicepulse-client"
```

**From a local checkout** of the integrations repository:

```bash
pip install ./servicepulse-client
```

**From PyPI** (if a release is available there):

```bash
pip install servicepulse-client
```

`httpx` is pulled in automatically as a dependency.

## Usage

```python
from servicepulse_client import ServicePulseClient, StackNotHealthyError

client = ServicePulseClient(api_token="sp_xxx", base_url="https://servicepulse.dev")
client.assert_stack_healthy(vendor_slugs=["stripe", "snowflake"])
```

## API

- `GET {base_url}/api/v1/tracked-vendors` — vendor names, slugs, `currentStatus`.

Statuses from the API follow the product enum, e.g. `operational`, `degraded_performance`, `partial_outage`, `major_outage`, `maintenance`, `unknown`.
