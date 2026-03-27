# YAML starter: `servicepulse_definitions`

These files live **next to** the **`dagster-servicepulse`** Python package (`libraries/dagster-servicepulse/`). Only **`definitions_component.py`** in that package implements **`ServicePulseDefinitionsComponent`**.

## `defs.yaml`

Dagster component projects keep declarations under a **`defs/`** tree; the file is **`defs.yaml`** (not `example.yaml`). Copy **[`defs.yaml`](./defs.yaml)** into your project, for example:

- `my_project/defs/defs.yaml` — single-file defs root, or  
- `my_project/defs/components/servicepulse/defs.yaml` — component-scoped folder, depending on how you structure **`load_from_defs_folder`**.

Then run **`dagster dev`** / **`dg dev`** the way your project expects.

| File | Purpose |
|------|---------|
| **`defs.yaml`** | Component declaration: `type` + `attributes` for **`ServicePulseDefinitionsComponent`**. |
| **`requirements.txt`** | Pip install line(s) for **`dagster-servicepulse`**. |
| **`schema.json`** | Registry / catalog metadata (optional for custom UIs). |
| **`README.md`** | This reference. |

## Attributes (`defs.yaml`)

| Attribute | Description |
|-----------|-------------|
| `required_vendors` | List of vendor slugs; `[]` gates on the **full** tracked stack. |
| `api_token_env_var` | Name of env var holding the Personal API token (`sp_…`). Default `SERVICEPULSE_API_TOKEN`. |
| `base_url` | ServicePulse API base URL. |
| `timeout_s` | HTTP timeout (seconds). |
| `include_transition_sensor` | Poll for operational → non-operational and request runs. |
| `transition_sensor_name` | Dagster sensor name. |
| `sensor_minimum_interval_seconds` | Sensor poll interval. |
| `allow_maintenance` | If true, maintenance does not fail the gate. |
| `allow_unknown` | If true, unknown status does not fail the gate. |

## State vs live API

The sensor **cursor** only remembers last-seen statuses to detect **transitions**; each evaluation still calls the live API.

## Product

[servicepulse.dev](https://servicepulse.dev) · [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations).
