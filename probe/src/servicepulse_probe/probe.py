"""
Poll internal HTTP URLs or databases; on success GET heartbeat URL.
stdlib: http, command, sqlite. Optional: DB drivers (requirements-*.txt).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def expand_env(obj: Any) -> Any:
    if isinstance(obj, str):
        def repl(m: re.Match[str]) -> str:
            key = m.group(1)
            return os.environ.get(key, "")

        return _ENV_PATTERN.sub(repl, obj)
    if isinstance(obj, list):
        return [expand_env(x) for x in obj]
    if isinstance(obj, dict):
        return {k: expand_env(v) for k, v in obj.items()}
    return obj


def ping_heartbeat(url: str, timeout_s: float) -> None:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            if r.status < 200 or r.status >= 300:
                body = r.read(200).decode(errors="replace")
                raise RuntimeError(f"Heartbeat HTTP {r.status}: {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"Heartbeat HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Heartbeat request failed: {e}") from e


def check_http(spec: dict[str, Any]) -> None:
    url = spec.get("url") or ""
    if not url:
        raise ValueError("http check requires url")
    method = (spec.get("method") or "GET").upper()
    expected = int(spec.get("expected_status", 200))
    timeout = float(spec.get("timeout_seconds", 10))
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != expected:
                raise RuntimeError(f"HTTP {r.status}, expected {expected}")
    except urllib.error.HTTPError as e:
        if e.code == expected:
            return
        raise RuntimeError(f"HTTP {e.code}, expected {expected}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request failed: {e}") from e


def check_postgres(spec: dict[str, Any]) -> None:
    try:
        import psycopg2
    except ImportError as e:
        raise SystemExit(
            "postgres check requires psycopg2-binary. Install: pip install -r requirements-db.txt"
        ) from e
    dsn = _dsn_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()
    finally:
        conn.close()


def check_mysql(spec: dict[str, Any]) -> None:
    try:
        import pymysql
    except ImportError as e:
        raise SystemExit(
            "mysql check requires pymysql. Install: pip install -r requirements-db.txt"
        ) from e
    dsn = _dsn_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    conn = pymysql.connect(**_mysql_kwargs_from_dsn(dsn))
    try:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()
    finally:
        conn.close()


def _params_json_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Connection kwargs as JSON in an environment variable (warehouse DB engines)."""
    key = spec.get("params_env")
    if not key:
        raise ValueError("params_env is required for this check type")
    raw = os.environ.get(str(key), "").strip()
    if not raw:
        raise ValueError(f"Environment variable {key!r} is empty or unset")
    try:
        out = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {key!r}: {e}") from e
    if not isinstance(out, dict):
        raise ValueError(f"{key!r} must be a JSON object")
    return out


def check_snowflake(spec: dict[str, Any]) -> None:
    try:
        import snowflake.connector
    except ImportError as e:
        raise SystemExit(
            "snowflake check requires snowflake-connector-python. "
            "Install: pip install -r requirements-warehouse.txt"
        ) from e
    params = _params_json_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    conn = snowflake.connector.connect(**params)
    try:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()
    finally:
        conn.close()


def check_databricks(spec: dict[str, Any]) -> None:
    try:
        from databricks import sql as dbsql
    except ImportError as e:
        raise SystemExit(
            "databricks check requires databricks-sql-connector. "
            "Install: pip install -r requirements-warehouse.txt"
        ) from e
    params = _params_json_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    with dbsql.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()


def check_sqlserver(spec: dict[str, Any]) -> None:
    try:
        import pymssql
    except ImportError as e:
        raise SystemExit(
            "sqlserver check requires pymssql. Install: pip install -r requirements-warehouse.txt"
        ) from e
    params = _params_json_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    conn = pymssql.connect(**params)
    try:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()
    finally:
        conn.close()


def check_oracle(spec: dict[str, Any]) -> None:
    try:
        import oracledb
    except ImportError as e:
        raise SystemExit(
            "oracle check requires oracledb. Install: pip install -r requirements-warehouse.txt"
        ) from e
    params = _params_json_from_spec(spec)
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    with oracledb.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
            cur.fetchone()


def check_sqlite(spec: dict[str, Any]) -> None:
    import sqlite3

    env_key = spec.get("path_env")
    if env_key:
        path = os.environ.get(str(env_key), "").strip()
        if not path:
            raise ValueError(f"Environment variable {env_key!r} is empty or unset")
    else:
        path = (spec.get("path") or "").strip()
        if not path:
            raise ValueError("sqlite check requires path or path_env")
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    conn = sqlite3.connect(path, timeout=float(spec.get("timeout_seconds", 10)))
    try:
        conn.execute(q).fetchone()
    finally:
        conn.close()


def check_command(spec: dict[str, Any]) -> None:
    """Run argv (no shell) — exit 0 means healthy. Most generic check."""
    raw_argv = spec.get("argv")
    if not isinstance(raw_argv, list) or not raw_argv:
        raise ValueError("command check requires argv: non-empty JSON array of strings")
    argv = [str(x) for x in raw_argv]
    timeout = float(spec.get("timeout_seconds", 60))
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"command timed out after {timeout}s") from e
    except FileNotFoundError as e:
        raise RuntimeError(f"executable not found: {argv[0]!r}") from e
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:500]
        raise RuntimeError(f"exit {proc.returncode}: {err or '(no output)'}")


def check_sqlalchemy(spec: dict[str, Any]) -> None:
    """Any database SQLAlchemy supports if you install the matching driver wheel."""
    try:
        from sqlalchemy import create_engine, text
    except ImportError as e:
        raise SystemExit(
            "sqlalchemy check requires SQLAlchemy 2.x. Install: pip install -r requirements-sqlalchemy.txt "
            "plus your engine driver (e.g. trino, google-cloud-bigquery, pyhive)."
        ) from e
    url_key = spec.get("url_env")
    if not url_key:
        raise ValueError("sqlalchemy check requires url_env (env var name holding the URL)")
    url = os.environ.get(str(url_key), "").strip()
    if not url:
        raise ValueError(f"Environment variable {url_key!r} is empty or unset")
    connect_args: dict[str, Any] = {}
    ca_key = spec.get("connect_args_env")
    if ca_key:
        raw = os.environ.get(str(ca_key), "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {ca_key!r}: {e}") from e
            if not isinstance(parsed, dict):
                raise ValueError(f"{ca_key!r} must be a JSON object")
            connect_args = parsed
    q = (spec.get("query") or "SELECT 1").strip() or "SELECT 1"
    engine = create_engine(url, connect_args=connect_args)
    with engine.connect() as conn:
        conn.execute(text(q))


def _dsn_from_spec(spec: dict[str, Any]) -> str:
    env_key = spec.get("dsn_env")
    if env_key:
        dsn = os.environ.get(str(env_key), "").strip()
        if not dsn:
            raise ValueError(f"Environment variable {env_key!r} is empty or unset")
        return dsn
    dsn = (spec.get("dsn") or "").strip()
    if not dsn:
        raise ValueError("postgres/mysql check requires dsn_env or dsn")
    return dsn


def _mysql_kwargs_from_dsn(dsn: str) -> dict[str, Any]:
    """Minimal mysql URL: mysql://user:pass@host:3306/dbname"""
    from urllib.parse import urlparse

    u = urlparse(dsn)
    if u.scheme not in ("mysql", "mariadb"):
        raise ValueError("mysql DSN must start with mysql:// or mariadb://")
    dbname = (u.path or "").strip("/")
    out: dict[str, Any] = {
        "host": u.hostname or "localhost",
        "port": u.port or 3306,
        "user": u.username or "",
        "password": u.password or "",
    }
    if dbname:
        out["database"] = dbname
    return out


def run_check(spec: dict[str, Any], heartbeat_timeout: float) -> None:
    name = spec.get("name") or "unnamed"
    kind = (spec.get("type") or "").lower()
    hb = (spec.get("heartbeat_url") or "").strip()
    if not hb:
        raise ValueError(f"check {name!r}: heartbeat_url is required")

    if kind == "http":
        check_http(spec)
    elif kind == "postgres":
        check_postgres(spec)
    elif kind in ("mysql", "mariadb"):
        check_mysql(spec)
    elif kind == "snowflake":
        check_snowflake(spec)
    elif kind == "databricks":
        check_databricks(spec)
    elif kind in ("sqlserver", "mssql"):
        check_sqlserver(spec)
    elif kind in ("oracle", "oracledb"):
        check_oracle(spec)
    elif kind == "sqlite":
        check_sqlite(spec)
    elif kind == "command":
        check_command(spec)
    elif kind in ("sqlalchemy", "sqla"):
        check_sqlalchemy(spec)
    else:
        raise ValueError(f"check {name!r}: unknown type {kind!r}")

    ping_heartbeat(hb, heartbeat_timeout)
    print(f"OK {name} → heartbeat pinged")


def main() -> None:
    p = argparse.ArgumentParser(description="Poll internal targets; ping ServicePulse heartbeats on success")
    p.add_argument("--config", required=True, help="Path to JSON config")
    p.add_argument(
        "--heartbeat-timeout",
        type=float,
        default=15.0,
        help="Timeout (seconds) for heartbeat GET",
    )
    args = p.parse_args()

    path = args.config
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    cfg = expand_env(raw)
    checks = cfg.get("checks")
    if not isinstance(checks, list) or not checks:
        print("No checks configured", file=sys.stderr)
        sys.exit(1)

    failed = 0
    for spec in checks:
        if not isinstance(spec, dict):
            failed += 1
            print("Invalid check entry (not an object)", file=sys.stderr)
            continue
        try:
            run_check(spec, args.heartbeat_timeout)
        except Exception as e:
            failed += 1
            n = spec.get("name", "?")
            print(f"FAIL {n}: {e}", file=sys.stderr)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
