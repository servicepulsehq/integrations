# Prefect + ServicePulse — tutorial

Prefect does not have a separate **`prefect-servicepulse`** wheel in this repo yet. You use:

1. **`servicepulse-client`** — HTTP client and **`assert_stack_healthy`**
2. **`vendor_gate_task.py`** — a **`@task`** wrapper you copy into your project (or import from a shared package)
3. **`servicepulse_block.py`** (optional) — a **Prefect block** to store the token and base URL in Prefect instead of raw env vars

For orchestrator comparison, see the root **[`integrations/README.md`](../../README.md)**.

---

## What you will do

1. Install **Prefect** and **`servicepulse-client`**.
2. Either set **`SERVICEPULSE_API_TOKEN`** for local runs **or** create a **ServicePulseCredentials** block in Prefect.
3. Run **`flow_example.py`** or copy the task into your own flow.

---

## Step 1 — Install

```bash
pip install "prefect>=2.14"
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=servicepulse-client"
```

From **`integrations/`** root:

```bash
pip install ./servicepulse-client
pip install "prefect>=2.14"
```

[`requirements.txt`](./requirements.txt) lists Prefect; add the client via the Git line above or path install.

---

## Step 2A — Run with environment variables (quickest)

```bash
export SERVICEPULSE_API_TOKEN="sp_..."
# optional:
# export SERVICEPULSE_BASE_URL="https://servicepulse.dev"
# export SERVICEPULSE_TIMEOUT_S="45"
```

From **`examples/prefect/`**:

```bash
python flow_example.py
```

This runs **`gated_pipeline`**, which calls **`assert_servicepulse_vendors_operational`** with default slugs **`["stripe", "snowflake"]`**. Edit **`REQUIRED_SLUGS`** in **`flow_example.py`** to match your **tracked** vendors.

---

## Step 2B — Run with a Prefect block (better for deployed flows)

### Create the block once

**Option 1 — Python (run locally / in a notebook)**

```python
from servicepulse_block import ServicePulseCredentials

ServicePulseCredentials(
    api_token="sp_your_token",
    base_url="https://servicepulse.dev",
    timeout_s=30.0,
).save("servicepulse-prod", overwrite=True)
```

**Option 2 — Register the block type for the UI**

From **`examples/prefect/`** (so Python can import **`servicepulse_block`**):

```bash
prefect block register -m servicepulse_block
```

Then in **Prefect UI → Blocks → Add** → choose **ServicePulse Credentials** and fill token + URL.

### Use the block in a flow

```python
from prefect import flow
from servicepulse_block import ServicePulseCredentials
from vendor_gate_task import assert_servicepulse_vendors_operational

@flow(name="my-gated-flow")
def my_flow():
    creds = ServicePulseCredentials.load("servicepulse-prod")
    assert_servicepulse_vendors_operational(
        ["stripe", "snowflake"],
        credentials=creds,
    )
    # ... your tasks after the gate ...
```

**Deploying to Prefect Cloud / server:** ensure workers have **network egress** to ServicePulse and, if you use **env-based** auth, set **`SERVICEPULSE_API_TOKEN`** (and optional **`SERVICEPULSE_BASE_URL`**, **`SERVICEPULSE_TIMEOUT_S`**) on the work pool / job variables. If you use a **block**, workers only need permission to **load** that block (no token in env).

---

## Files in this folder

| File | Role |
|------|------|
| **`vendor_gate_task.py`** | **`assert_servicepulse_vendors_operational`** — env or **`credentials=`**. |
| **`servicepulse_block.py`** | **`ServicePulseCredentials`** block (`api_token`, `base_url`, `timeout_s`). |
| **`flow_example.py`** | Minimal flow using **env** only; extend with **`credentials=`** as above. |

### Reuse in your own project

Copy **`vendor_gate_task.py`** and (if needed) **`servicepulse_block.py`** into your package, or publish an internal wheel. Keep **`servicepulse-client`** as a dependency.

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| `RuntimeError` about token | Env **`SERVICEPULSE_API_TOKEN`** or **`credentials=`** with a loaded block. |
| Task fails / `StackNotHealthyError` | Vendor status in ServicePulse; **`allow_maintenance`** / **`allow_unknown`** on the task. |
| Block not found in UI | Run **`prefect block register -m servicepulse_block`** from a directory on **`PYTHONPATH`** that contains **`servicepulse_block.py`**. |
| Wrong slugs | Must match **tracked** vendors; pass **`None`** to check full stack (see client **`assert_stack_healthy`**). |

---

## Related

- **`servicepulse_client`** API: [`servicepulse-client/README.md`](../../servicepulse-client/README.md)
