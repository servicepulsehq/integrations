# Internal probe (poll → heartbeat)

Run **inside your network** (VM, Docker, **Kubernetes `CronJob`**, systemd timer, GitLab runner on-prem, etc.) to:

1. **Poll** private HTTP endpoints or a **database** (`SELECT 1`).
2. On **success**, **GET** your ServicePulse **heartbeat URL** (same as the copy-paste scripts in the app).
3. On **failure**, **do not** ping the heartbeat — the monitor goes overdue and alerts like any other heartbeat.

**No changes to application code** — only infra that runs this process on a schedule.

## Why this exists

ServicePulse **cannot** open connections to `http://10.x`, `*.internal`, or your RDS from the public app. **Heartbeat monitors** already model “something inside the network proves health.” This tool is a small **config-driven poller** so you don’t hand-write curl/bash for every service.

## Setup

1. In ServicePulse, create a **Ping monitor → Heartbeat**. Copy the heartbeat URL (`…/api/heartbeat/<token>`).
2. Copy [`config.example.json`](./config.example.json) to your secrets store / repo (mask tokens and DSNs).
3. Schedule `python3 probe.py --config /path/to/config.json` **more often** than the monitor’s **expected interval** (e.g. monitor expects every 5 min → run probe every 2–3 min).

## Config

- **`${ENV_VAR}`** in any string is expanded from the environment (use this for heartbeat URLs and DSNs instead of committing secrets).
- Each **`checks[]`** entry is independent: success ⇒ ping that entry’s `heartbeat_url`.

### `http`

| Field | Description |
|-------|-------------|
| `url` | Internal URL (http/https) |
| `method` | Optional, default `GET` |
| `expected_status` | Optional, default `200` |
| `timeout_seconds` | Optional, default `10` |
| `heartbeat_url` | Full heartbeat URL from the app |

### `postgres` / `mysql`

| Field | Description |
|-------|-------------|
| `dsn_env` | Name of env var holding the connection string (recommended) |
| `query` | SQL to run; must succeed |
| `heartbeat_url` | Full heartbeat URL |

Install drivers **only if** you use DB checks:

```bash
pip install -r requirements-db.txt
pip install -r requirements-warehouse.txt   # Snowflake, Databricks, SQL Server, Oracle
pip install -r requirements-sqlalchemy.txt  # generic SQLAlchemy (add engine drivers yourself)
```

HTTP-only runs with **Python 3.9+ stdlib** (no `pip install`).

### Generic: `command`, `sqlalchemy`, `sqlite`

| `type` | What it does |
|--------|----------------|
| **`command`** | Run **`argv`** (JSON array of strings) with **no shell**; exit code **0** ⇒ ping heartbeat. Use for **Redis** (`redis-cli`, `PING`), **MongoDB** (`mongosh --eval`), **Cassandra** (`cqlsh`), vendor CLIs, or **ODBC** wrappers. |
| **`sqlalchemy`** | `url_env` points to a [SQLAlchemy URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls); optional `connect_args_env` = JSON object for extra kwargs. Install **`sqlalchemy`** plus **whatever driver** your URL needs (`trino`, `pyhive`, `clickhouse-sqlalchemy`, `google-cloud-bigquery` + dialect, etc.). |
| **`sqlite`** | Local **`path`** or **`path_env`** to a file; **`query`** defaults to `SELECT 1`. Uses stdlib **`sqlite3`** only. |

Examples: [`config.example.generic.json`](./config.example.generic.json).

Engines we don’t ship first-class drivers for are usually covered by **SQLAlchemy + a driver** (e.g. **Trino/Presto**, **Hive**, **ClickHouse** SQL, **Cockroach** via Postgres URL) or by a **`command`** that shells out to your standard tooling.

### Snowflake / Databricks / SQL Server / Oracle

Use **`params_env`**: name of an environment variable whose value is a **JSON object** of keyword arguments for that vendor’s Python connector (same shapes as in the in-app **Database** scripts).

| `type` | `params_env` JSON keys (typical) |
|--------|----------------------------------|
| `snowflake` | `user`, `password`, `account`, `warehouse`, `role`, `database`, `schema` — see [Snowflake Python connector](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect) |
| `databricks` | `server_hostname`, `http_path`, `access_token` — [Databricks SQL connector](https://docs.databricks.com/en/dev-tools/python-sql-connector.html) |
| `sqlserver` / `mssql` | `server`, `user`, `password`, `database`, optional `port`, `tds_version` — [PyMSSQL](https://www.pymssql.org/en/stable/ref/pymssql.html) |
| `oracle` / `oracledb` | `user`, `password`, `dsn` (Easy Connect, e.g. `host:1521/service`) — [python-oracledb](https://python-oracledb.readthedocs.io/) |

Example entries: [`config.example.warehouse.json`](./config.example.warehouse.json).

**From the ServicePulse product:** we still **never** connect to your warehouse from our servers. You create a **heartbeat** (or **Database** tab — same outcome), run **`servicepulse-probe`** or the copy-paste script **inside your network**, and we only see the heartbeat pings.

## Examples

**Cron** (every 2 minutes):

```cron
*/2 * * * * SERVICEPULSE_HEARTBEAT_API=/run/secrets/hb-api python3 /opt/servicepulse-probe/probe.py --config /opt/servicepulse-probe/config.json
```

**Docker** — use the included [`Dockerfile`](./Dockerfile) (HTTP + common DB + SQLAlchemy baked in; add more drivers in a derived image if needed):

```bash
docker build -t servicepulse-probe:local .
docker run --rm \
  -v /secure/probe-config.json:/config.json:ro \
  -e SERVICEPULSE_HEARTBEAT_API='https://servicepulse.dev/api/heartbeat/…' \
  servicepulse-probe:local --config /config.json
```

For **Kubernetes**, use this image in a **`CronJob`**, mount the JSON from a **Secret** / **ConfigMap**, and set the same env vars as in [`config.example.json`](./config.example.json).

## Install from this repo

```bash
pip install "git+https://github.com/servicepulsehq/integrations.git#subdirectory=probe"
```

(Or copy `probe.py` + config — single file is fine.)

## License

[MIT](../LICENSE)
