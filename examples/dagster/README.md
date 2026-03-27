# Dagster + ServicePulse — tutorial

This folder is a **minimal runnable example**. The real library is **[`libraries/dagster-servicepulse`](../../libraries/dagster-servicepulse/)** — read that README for all options (custom jobs, YAML component, troubleshooting).

## What you will do

1. Install **`dagster-servicepulse`** and **Dagster**.
2. Set **`SERVICEPULSE_API_TOKEN`**.
3. Run **`dagster dev`** and open the UI.
4. Run the **`pipeline_with_vendor_gate`** job (or let the sensor fire if you keep it enabled).

The example **`definitions.py`** calls **`build_servicepulse_defs(required_vendors=...)`**, which registers:

- a **resource** `servicepulse`
- a **job** `pipeline_with_vendor_gate` with one gate op
- a **sensor** that can request runs when a vendor leaves `operational` (see library README to turn it off)

---

## Step 1 — Install

From the **`integrations/`** directory in a clone of [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations):

```bash
pip install ./servicepulse-client
pip install ./libraries/dagster-servicepulse
pip install dagster dagster-webserver
```

Or without cloning:

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=servicepulse-client"
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=libraries/dagster-servicepulse"
pip install dagster dagster-webserver
```

---

## Step 2 — Token and slugs

```bash
export SERVICEPULSE_API_TOKEN="sp_..."
```

Edit **`definitions.py`**: set **`REQUIRED_VENDORS`** to slugs you **track** in ServicePulse (e.g. `("stripe", "snowflake")`). Use `()` to require the **entire** tracked stack to be healthy.

Default API host is **`https://servicepulse.dev`**. To change it, stop using this thin example and pass **`ServicePulseResource(base_url="...")`** via **`build_servicepulse_defs(..., resource=...)`** (see library README).

---

## Step 3 — Run locally

```bash
cd examples/dagster
dagster dev -f definitions.py
```

Open the URL Dagster prints (usually **http://127.0.0.1:3000**).

- Go to **Jobs** → **`pipeline_with_vendor_gate`** → **Launchpad** → **Launch run** to test the gate.
- If the gate op **fails**, check the log: ServicePulse is blocking because a vendor is not `operational` (or unknown/maintenance if you disallow those).

---

## Step 4 — Use this in your own repo

1. Add **`dagster-servicepulse`** as a dependency (Git URL or path).
2. Create a module that defines **`defs`** (copy the pattern from **`definitions.py`** or compose with **`build_vendor_gate_op`** — see library README).
3. Point **`dagster dev`** / your deployment at that module, or use **`load_from_defs_folder`** if you adopt the YAML component under **`libraries/dagster-servicepulse/docs/servicepulse_definitions/`**.

---

## Files here

| File | Role |
|------|------|
| **`definitions.py`** | `defs = build_servicepulse_defs(required_vendors=REQUIRED_VENDORS)` |

YAML / Components (not used by this Python-only example): copy **`defs.yaml`** from **[`libraries/dagster-servicepulse/docs/servicepulse_definitions/`](../../libraries/dagster-servicepulse/docs/servicepulse_definitions/)** into your **`defs/`** tree.
