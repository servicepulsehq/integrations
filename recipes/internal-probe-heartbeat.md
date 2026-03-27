# Recipe: Poll internal HTTP/DB without changing app code

Use **[`probe/`](../probe/)** (`servicepulse-probe`): it runs **inside your network**, hits private URLs or runs `SELECT 1`, and **GETs** your ServicePulse **heartbeat** URL only when the check succeeds.

1. Create one **Heartbeat** ping monitor per logical check in the app; copy each URL.
2. Put URLs in config via **`${ENV_VAR}`** (see [`config.example.json`](../probe/config.example.json)).
3. Schedule **`servicepulse-probe --config …`** (Cron, K8s `CronJob`, etc.) **more often** than the heartbeat interval.

No application code changes — only infra + secrets.

For HTTP-only checks you need **Python 3.9+** and no extra packages. For Postgres/MySQL, `pip install -r probe/requirements-db.txt`. For **Snowflake, Databricks, SQL Server, or Oracle**, add `requirements-warehouse.txt` and use **`params_env`** JSON — see [`../probe/README.md`](../probe/README.md) and [`../probe/config.example.warehouse.json`](../probe/config.example.warehouse.json). For **anything else**, use probe types **`command`** (any CLI, exit 0 = healthy), **`sqlalchemy`** + your driver URL, or **`sqlite`** — [`../probe/config.example.generic.json`](../probe/config.example.generic.json).

Full guide: [`../probe/README.md`](../probe/README.md).
