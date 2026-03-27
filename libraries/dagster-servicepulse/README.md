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
export SERVICEPULSE_API_TOKEN="sp_..."
```

Optional: default base URL is `https://servicepulse.dev`. To use another host, override **`ServicePulseResource(base_url=...)`** in code or run config (the resource does **not** read `SERVICEPULSE_BASE_URL` unless you wire it).

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

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| Run fails immediately on gate | Token set? Slugs spelled like ServicePulse **tracked** vendors? |
| `StackNotHealthyError` | Vendor status not `operational` (or you disallowed `maintenance` / `unknown`). |
| Component / YAML not found | `pip show dagster-servicepulse` — is the package in the same env as `dagster dev`? |
| Custom token env var | Use YAML `api_token_env_var: MY_VAR` or `ServicePulseResource(api_token=EnvVar("MY_VAR"))`. |

---

## Related

- [Dagster community integrations](https://github.com/dagster-io/community-integrations) (pattern inspiration)
- [dagster-component-templates](https://github.com/eric-thomas-dagster/dagster-component-templates) (YAML component style)

## License

MIT (same as the parent integrations repository).
