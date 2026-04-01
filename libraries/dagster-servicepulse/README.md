# dagster-servicepulse

Dagster integration for [ServicePulse](https://servicepulse.dev): check vendor health **before** downstream ops run, and optionally **react** when status changes.

## What this package gives you

| Piece | Use case |
|-------|----------|
| **`ServicePulseResource`** | `ConfigurableResource` wrapping `ServicePulseClient` (token from env by default). |
| **`build_vendor_gate_op`** | Factory for an op that **fails the run** if required vendors are not safe. |
| **`build_vendor_transition_sensor`** | Sensor that **requests a run** when a vendor goes from `operational` → something else. |
| **`build_servicepulse_defs`** | One-liner `Definitions` with resource + gate job + optional sensor. |
| **`ServicePulseDefinitionsComponent`** | Same bundle, driven from **YAML** (Dagster Components / `defs.yaml`). |
| **`resource.push_service_status()`** | Push **your own service's health** back to ServicePulse from any job or op. |

Health is always read from the **live API** on each run or sensor tick. The sensor **cursor** only stores last-seen statuses to detect **transitions**, not as source of truth.

---

## Install

**Requires Dagster 1.10+** and Python **3.9+**. Not on PyPI — use Git or a path install.

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=servicepulse-client"
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=libraries/dagster-servicepulse"
```

From a checkout (**`integrations/`** root):

```bash
pip install ./servicepulse-client
pip install ./libraries/dagster-servicepulse
pip install dagster dagster-webserver
```

---

## Use it in 3 steps

### 1. Set credentials

```bash
export SERVICEPULSE_API_TOKEN="sp_..."        # Personal API token — for reading vendor health
export SERVICEPULSE_INGEST_TOKEN="..."        # Push endpoint token — only needed for push_service_status
```

Optional: default base URL is `https://servicepulse.dev`. To use another host, override **`ServicePulseResource(base_url=...)`** in code or run config (the resource does **not** read `SERVICEPULSE_BASE_URL` unless you wire it).

The two tokens serve different purposes:
- **`SERVICEPULSE_API_TOKEN`** — your Personal API token (Settings → API Tokens). Read-only; used by `assert_stack_healthy` and the gate op.
- **`SERVICEPULSE_INGEST_TOKEN`** — the token from a Push Endpoint (Settings → Push Endpoints → copy token). Write-only; used by `push_service_status`. Create one push endpoint per service you want to push health from.

### 2. Point at your vendors

Use **slugs** that match vendors **tracked** in your ServicePulse workspace. Empty tuple `()` means “check the **entire** tracked stack.”

### 3. Expose `defs`

**Option A — minimal Python (recommended to start)**

```python
from dagster_servicepulse import build_servicepulse_defs

defs = build_servicepulse_defs(required_vendors=("stripe", "snowflake"))
```

**Option B — compose yourself**

```python
from dagster import Definitions, job
from dagster_servicepulse import (
    ServicePulseResource,
    build_vendor_gate_op,
    build_vendor_transition_sensor,
)

gate = build_vendor_gate_op(required_vendors=("stripe", "snowflake"))

@job
def nightly_with_gate():
    gate()

sensor = build_vendor_transition_sensor(
    job=nightly_with_gate,
    required_vendors=("stripe", "snowflake"),
    minimum_interval_seconds=300,
)

defs = Definitions(
    resources={"servicepulse": ServicePulseResource()},
    jobs=[nightly_with_gate],
    sensors=[sensor],
)
```

**Option C — YAML component (`defs.yaml`)**

1. Install this package (see above).
2. Copy [`docs/servicepulse_definitions/defs.yaml`](./docs/servicepulse_definitions/defs.yaml) into your project’s **`defs/`** tree as **`defs.yaml`** (e.g. `defs/defs.yaml` or `defs/components/servicepulse/defs.yaml` — match your layout).
3. Adjust `attributes` as needed; keep `type: dagster_servicepulse.ServicePulseDefinitionsComponent`.
4. Load with your normal Dagster entrypoint (`load_from_defs_folder`, `dg dev`, etc.).

Full attribute list: [`docs/servicepulse_definitions/README.md`](./docs/servicepulse_definitions/README.md).

---

## Run the bundled example

From the [integrations](https://github.com/servicepulsehq/integrations) repo, see **[`examples/dagster/README.md`](../../examples/dagster/README.md)** — it runs `dagster dev -f definitions.py` against a thin `build_servicepulse_defs` entrypoint.

---

## Push your service's own health back to ServicePulse

Reading vendor health is only half the picture. Your own pipeline may be degraded even when all upstream vendors are operational — a slow ETL job, a failed ML training run, a data product behind SLA. Use `push_service_status` to signal that directly from Dagster.

The pushed status is combined with vendor dependency status using **worst-of semantics**: if your pipeline reports `degraded_performance` while all vendors are green, the service shows as degraded on your status page.

### Quick example — mark degraded on failure, restore on success

```python
from dagster import job, op, success_hook, failure_hook, HookContext
from dagster_servicepulse import ServicePulseResource

@success_hook(required_resource_keys={"servicepulse"})
def mark_operational(context: HookContext):
    context.resources.servicepulse.push_service_status("operational", title="ETL pipeline healthy")

@failure_hook(required_resource_keys={"servicepulse"})
def mark_degraded(context: HookContext):
    context.resources.servicepulse.push_service_status(
        "degraded_performance",
        title="ETL pipeline failed",
        message=str(context.op_exception),
    )

@op
def run_etl():
    # ... your ETL logic ...
    pass

@job(hooks={mark_operational, mark_degraded})
def nightly_etl():
    run_etl()

defs = Definitions(
    resources={
        "servicepulse": ServicePulseResource(
            ingest_token=EnvVar("SERVICEPULSE_INGEST_TOKEN"),
            service_id="<your-service-id>",           # from ServicePulse → My Services → copy ID
        )
    },
    jobs=[nightly_etl],
)
```

See the full example in [`examples/dagster/push_status_example.py`](../../examples/dagster/push_status_example.py).

Valid statuses: `operational`, `degraded_performance`, `partial_outage`, `major_outage`, `maintenance`.

---

## Dagster+ alert webhooks → ServicePulse

If you use **Dagster+**, you can route its alert webhooks directly to a ServicePulse push endpoint. No custom code needed — ServicePulse auto-detects the Dagster+ payload format.

### Setup

1. In ServicePulse go to **Settings → Push Endpoints** and create a new endpoint. Copy the webhook URL:
   `https://servicepulse.dev/api/ingest/<token>`

2. In Dagster+ go to **Settings → Alert Policies** (or **Alerts**) and create a new policy:
   - **Notification channel**: Webhook
   - **URL**: paste the ServicePulse ingest URL above
   - **Trigger**: choose the events you want (job failure, asset check failure, etc.)

3. ServicePulse logs every alert as a push event. Optionally configure **rules** on the endpoint (Settings → Push Endpoints → Rules) to control severity and notifications per event type:

   | Pattern | Meaning |
   |---------|---------|
   | `dagster.failure` | Job or asset materialization failed |
   | `dagster.alert` | Alert policy triggered (generic) |
   | `dagster.success` | Job succeeded |
   | `dagster.*` | Any Dagster+ alert |

### Dagster+ webhook payload fields

ServicePulse extracts the following fields from Dagster+ alert payloads:

| Field | Type | Description |
|-------|------|-------------|
| `alert_summary` | string | Short summary of the alert (used as fallback title) |
| `alert_content` | string | Full alert message body |
| `alert_policy_name` | string | Name of the alert policy that fired (used as title when present) |
| `alert_policy_id` | string | UUID of the alert policy |
| `alert_policy_description` | string | Description of the alert policy |
| `alert_id` | string | Unique ID for this alert instance |
| `deployment_name` | string | Dagster+ deployment name (shown in parentheses next to policy name) |
| `deployment_url` | string | URL to the Dagster+ deployment UI |
| `notification_type` | string | Alert type — maps to `dagster.<notification_type>` event type in rules |
| `is_sample` | boolean | `true` when sent as a test/sample from Dagster+ UI |

The `notification_type` value drives rule matching. Common values: `failure`, `success`, `alert`.

### Combine with service status push

For the tightest integration, combine Dagster+ webhooks with explicit status push:
- Use the Dagster+ webhook for **event logging** (every failure gets recorded in the push event log).
- Use `push_service_status` in job hooks for **service health** (the status page reflects whether the pipeline is currently healthy).

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| Run fails immediately on gate | Token set? Slugs spelled like ServicePulse **tracked** vendors? |
| `StackNotHealthyError` | Vendor status not `operational` (or you disallowed `maintenance` / `unknown`). |
| Component / YAML not found | `pip show dagster-servicepulse` — is the package in the same env as `dagster dev`? |
| Custom token env var | Use YAML `api_token_env_var: MY_VAR` or `ServicePulseResource(api_token=EnvVar("MY_VAR"))`. |
| `push_service_status` returns 404 | Check `ingest_token` — it's the push endpoint token, not the Personal API token. |
| Status push has no effect on status page | Check that the `service_id` matches a service you own in ServicePulse (copy from My Services). |
| Dagster+ webhook not logged | Verify the webhook URL includes `/api/ingest/` not `/api/v1/`. Check the endpoint is active. |

---

## Related

- [Dagster community integrations](https://github.com/dagster-io/community-integrations) (pattern inspiration)
- [dagster-component-templates](https://github.com/eric-thomas-dagster/dagster-component-templates) (YAML component style)

## License

MIT (same as the parent integrations repository).
