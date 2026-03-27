# servicepulse-airflow

Installable **`ServicePulseVendorGateOperator`** for **Apache Airflow 2.7+** — fails the task if ServicePulse reports that required vendors are not safe to proceed, so downstream tasks do not run.

Depends on **`servicepulse-client`** (declared in this package). **Not** an official `apache-airflow-providers-*` package; it is a small `BaseOperator` you install like any other dependency.

---

## Install

**Not on PyPI** — install from Git or a path checkout.

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=libraries/airflow-servicepulse"
```

From **`integrations/`** root:

```bash
pip install ./libraries/airflow-servicepulse
```

Install this into the **same Python environment** Airflow uses (Docker image, venv, or managed composer environment).

---

## Use it in 4 steps

### 1. Install the package

See above. Verify:

```bash
python -c "from servicepulse_airflow import ServicePulseVendorGateOperator; print('ok')"
```

### 2. Provide credentials (pick one)

**A — Airflow Connection (good for production)**  

Create a connection (e.g. id `servicepulse_default`). Then:

- Set **Password** to your `sp_…` token, **or** leave password empty and put the token in **Extra** as JSON: `{"api_token": "sp_…"}`.
- Optional **Extra**: `{"base_url": "https://servicepulse.dev"}`  
- Or set **Host** to `servicepulse.dev` (no scheme) — `https://` is added automatically.

In the DAG, pass:

```python
ServicePulseVendorGateOperator(
    task_id="vendor_gate",
    vendor_slugs=["stripe", "snowflake"],
    servicepulse_conn_id="servicepulse_default",
)
```

**B — Variable or environment**  

Do **not** set `servicepulse_conn_id`. Then the operator reads:

- **Token:** env `SERVICEPULSE_API_TOKEN` or Airflow Variable `SERVICEPULSE_API_TOKEN`
- **Base URL (optional):** env `SERVICEPULSE_BASE_URL` or Variable `SERVICEPULSE_BASE_URL`

### 3. Add a task to your DAG

```python
from servicepulse_airflow import ServicePulseVendorGateOperator

gate = ServicePulseVendorGateOperator(
    task_id="assert_vendors_operational",
    vendor_slugs=["stripe", "snowflake"],
    # servicepulse_conn_id="servicepulse_default",  # if using Connection
    # allow_maintenance=True,   # optional
    # timeout_s=60,
)

downstream = ...
gate >> downstream
```

**`vendor_slugs`:** must match **tracked** vendor slugs in ServicePulse. Omit or pass `None` to evaluate the **full** tracked stack (see client `assert_stack_healthy`).

### 4. Deploy the DAG

Place your DAG file where Airflow loads DAGs. Trigger a run; the gate task should succeed only when ServicePulse says the stack is healthy.

---

## Example DAG in this repo

See **[`examples/airflow/README.md`](../../examples/airflow/README.md)** and **[`examples/airflow/dag_vendor_gate.py`](../../examples/airflow/dag_vendor_gate.py)** for a full minimal DAG.

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| `RuntimeError` about token | Connection password / `api_token` in Extra, or Variable/env `SERVICEPULSE_API_TOKEN`. |
| Task fails with `StackNotHealthyError` | Vendor actually degraded/outage/maintenance; or tighten/loosen `allow_maintenance` / `allow_unknown`. |
| Import error | Package not installed in Airflow’s Python env (common with multiple venvs or custom images). |
| Wrong API host | Connection Extra `base_url` or Variable `SERVICEPULSE_BASE_URL`. |

---

## License

MIT (same as the parent integrations repository).
