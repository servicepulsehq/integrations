# Apache Airflow + ServicePulse — tutorial

This folder contains a **sample DAG**. The operator implementation lives in **[`libraries/airflow-servicepulse`](../../libraries/airflow-servicepulse/)** — read that README for parameters, Connection layout, and troubleshooting.

## What you will do

1. Install **`servicepulse-airflow`** into Airflow’s Python environment.
2. Configure a **Connection** (recommended) or **Variable** / env for the token.
3. Copy **`dag_vendor_gate.py`** into your **`dags/`** folder (or merge the operator into an existing DAG).
4. Trigger the DAG and confirm the gate task behaves as expected.

---

## Step 1 — Install

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=libraries/airflow-servicepulse"
```

Or from **`integrations/`** root:

```bash
pip install ./libraries/airflow-servicepulse
```

[`requirements.txt`](./requirements.txt) pins the same Git install for `pip install -r requirements.txt`.

Sanity check:

```bash
python -c "from servicepulse_airflow import ServicePulseVendorGateOperator; print('ok')"
```

---

## Step 2 — Credentials

### Option A — Connection (recommended)

1. In Airflow UI: **Admin → Connections → Add**.
2. **Conn Id:** e.g. `servicepulse_default`
3. **Conn Type:** `Generic` (or any type your policies allow; the operator only uses password + extra + host).
4. **Password:** your Personal API token `sp_…`  
   *or* leave password empty and set **Extra** (JSON):

   ```json
   {
     "api_token": "sp_your_token_here",
     "base_url": "https://servicepulse.dev"
   }
   ```

5. If you omit `base_url` in Extra, you can set **Host** to `servicepulse.dev` (hostname only is fine).

In **`dag_vendor_gate.py`**, add to the operator:

```python
ServicePulseVendorGateOperator(
    task_id="assert_vendors_operational",
    vendor_slugs=VENDOR_SLUGS,
    servicepulse_conn_id="servicepulse_default",
)
```

### Option B — Variable or environment

Leave **`servicepulse_conn_id`** unset (as in the committed example). Set:

- **Variable** `SERVICEPULSE_API_TOKEN` in Airflow, or env var `SERVICEPULSE_API_TOKEN` in your worker/scheduler environment.
- Optionally **Variable** / env **`SERVICEPULSE_BASE_URL`** (defaults to `https://servicepulse.dev` via the operator’s `base_url` default).

---

## Step 3 — DAG file

**[`dag_vendor_gate.py`](./dag_vendor_gate.py)** defines:

- **`ServicePulseVendorGateOperator`** first (gate)
- a placeholder **BashOperator** after it

Adjust **`VENDOR_SLUGS`** to match **tracked** vendors in ServicePulse.

Deploy: copy the file into the directory Airflow scans for DAGs, wait for the scheduler to parse it, then enable the DAG.

---

## Step 4 — Test

Trigger **`servicepulse_vendor_gate_example`** manually. Expect:

- **Gate succeeds** when ServicePulse reports required vendors as healthy for your rules.
- **Gate fails** when a vendor is in a blocking status — downstream task should not run (`skipped` or DAG marked failed depending on config).

---

## Do we need an Apache “provider” package?

No. This **`BaseOperator`** is enough for most teams. A formal **`apache-airflow-providers-servicepulse`** would be extra packaging and release overhead.

---

## Files here

| File | Role |
|------|------|
| **`dag_vendor_gate.py`** | Example DAG using **`servicepulse_airflow`**. |
| **`requirements.txt`** | Git install line for **`servicepulse-airflow`**. |
