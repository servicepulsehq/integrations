# ServicePulse integrations

Use **ServicePulse** from **pipelines**, **CI**, **GitOps**, and **your own services** to **stop work** when vendors you depend on are not in a safe status—without maintaining one-off status-page parsers.

**Product:** [servicepulse.dev](https://servicepulse.dev) · **API docs:** [servicepulse.dev/docs#api-rest-v1](https://servicepulse.dev/docs#api-rest-v1) · **Orchestrator overview:** [servicepulse.dev/orchestrators](https://servicepulse.dev/orchestrators)

---

## What you need first

1. Vendors **tracked** in the workspace your token uses.
2. A **Personal API token** (`sp_…`) from **Developers** in the app (for `GET /api/v1/tracked-vendors`).
3. Slugs in code (e.g. `stripe`) must match **tracked** vendors.

Most tools call **`GET /api/v1/tracked-vendors`** and read each vendor’s **`currentStatus`** (`operational`, `major_outage`, `maintenance`, etc.).

---

## Pick your surface

| You use… | Start here |
|----------|------------|
| **Airflow / Dagster / Prefect** | [examples/](./examples/) and [libraries/](./libraries/) below |
| **GitHub Actions** | [github-actions/](./github-actions/) |
| **GitLab CI** | [gitlab-ci/](./gitlab-ci/) |
| **Azure Pipelines** | [azure-pipelines/](./azure-pipelines/) |
| **Shared CI script (Python)** | [scripts/check_stack.py](./scripts/check_stack.py) |
| **Internal HTTP/DB poll → heartbeat** | [probe/](./probe/) (`servicepulse-probe`) |
| **Terraform** | [terraform/modules/stack_health](./terraform/modules/stack_health/) |
| **Argo CD / Flux** | [gitops/](./gitops/) |
| **Node / TypeScript** | [libraries/servicepulse-client-js](./libraries/servicepulse-client-js/) (`@servicepulsehq/client`) |
| **Go** | [libraries/servicepulse-client-go](./libraries/servicepulse-client-go/) |
| **Python (any)** | [servicepulse-client](./servicepulse-client/) |
| **Outbound webhooks (verify HMAC)** | [webhook-starters/](./webhook-starters/) |
| **OpenAPI → codegen** | [openapi/](./openapi/) (spec lives in the main app repo) |
| **Short how-tos** | [recipes/](./recipes/) |

### Orchestrators (Python)

| Stack | Tutorial | Package |
|-------|----------|---------|
| **Dagster** | [examples/dagster/README.md](./examples/dagster/README.md) · [libraries/dagster-servicepulse](./libraries/dagster-servicepulse/) | `dagster-servicepulse` |
| **Airflow** | [examples/airflow/README.md](./examples/airflow/README.md) · [libraries/airflow-servicepulse](./libraries/airflow-servicepulse/) | `servicepulse-airflow` |
| **Prefect** | [examples/prefect/README.md](./examples/prefect/README.md) | `servicepulse-client` + examples (no separate PyPI package) |

**Layout**

- **[`servicepulse-client`](./servicepulse-client/)** — shared Python client for Airflow/Dagster/Prefect and scripts.
- **[`scripts/`](./scripts/)** — `check_stack.py` used by GitHub Actions, GitLab, Azure (and easy to run anywhere with Python 3).
- **[`probe/`](./probe/)** — poll **private** URLs or databases from your network; ping **heartbeat** URLs when healthy (no app code changes).
- **[`libraries/dagster-servicepulse`](./libraries/dagster-servicepulse/)** — resource, gate op, sensor, YAML component; starter **`defs.yaml`** under **`docs/servicepulse_definitions/`**.
- **[`libraries/airflow-servicepulse`](./libraries/airflow-servicepulse/)** — `ServicePulseVendorGateOperator`.

---

## Install (Python)

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=servicepulse-client"
```

From a clone at **`integrations/`** root:

```bash
pip install ./servicepulse-client
```

## Install (Node)

From a clone:

```bash
npm install ./libraries/servicepulse-client-js
```

Built **`dist/`** is committed so Git installs work without running `tsc`.

---

## Raw Python

```python
from servicepulse_client import ServicePulseClient, StackNotHealthyError

client = ServicePulseClient(api_token="sp_your_token", base_url="https://servicepulse.dev")
client.assert_stack_healthy(["stripe", "snowflake"])
```

Options: `allow_maintenance`, `allow_unknown` — see [`servicepulse_client/client.py`](./servicepulse-client/src/servicepulse_client/client.py).

---

## PyPI

`servicepulse-client`, `dagster-servicepulse`, and `servicepulse-airflow` are **not on PyPI**; install from **Git** with `subdirectory=` (see each README) or path installs. **`@servicepulsehq/client`** is also **not** on npm; install from this repo. **`servicepulse-probe`** is the same — install from Git or copy the module.

Public mirror: [github.com/servicepulsehq/integrations](https://github.com/servicepulsehq/integrations). To refresh it from the monorepo, run [`publish.ps1`](./publish.ps1).

---

## Going further

- **Dashboards and in-app alerts** — main ServicePulse product.
- **Inbound push / status page APIs** — [servicepulse.dev/docs](https://servicepulse.dev/docs).

## License

[MIT](./LICENSE)
